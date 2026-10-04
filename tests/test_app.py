"""Render public app options with Helm; run with unittest and PyYAML installed."""
from pathlib import Path
import subprocess
import tempfile
import unittest

import yaml


CHART = Path(__file__).resolve().parents[1] / 'charts/app'


def render(values):
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'values.yaml'
        path.write_text(yaml.safe_dump(values))
        result = subprocess.run(['helm', 'template', 'test', str(CHART),
                                 '--api-versions', 'monitoring.coreos.com/v1',
                                 '-f', str(path)], check=True, capture_output=True, text=True)
    return [doc for doc in yaml.safe_load_all(result.stdout) if doc]


class AppTests(unittest.TestCase):
    def test_connection_probe_reserves_resources_only_on_reserved_platforms(self):
        resources = {'requests': {'cpu': '100m', 'memory': '128Mi'}, 'limits': {'memory': '256Mi'}}
        pod = next(d for d in render({'resources': resources}) if d['kind'] == 'Pod')
        self.assertEqual(pod['spec']['containers'][0]['resources'], {'requests': {'cpu': '10m', 'memory': '16Mi'}, 'limits': {'memory': '64Mi'}})
        pod = next(d for d in render({'resources': None}) if d['kind'] == 'Pod')
        self.assertNotIn('resources', pod['spec']['containers'][0])

    def test_additional_config_and_pod_annotations_follow_their_inputs(self):
        values = {'capacity': 8, 'raw': {'enabled': True, 'parentTemplates': [
            'apiVersion: v1\nkind: ConfigMap\nmetadata: {name: additional}\ndata: {CAPACITY: {{ .Values.capacity | quote }}}',
        ]}, 'podAnnotations': {'checksum/capacity': '{{ .Values.capacity | toString | sha256sum }}'}}
        before = render(values)
        values['capacity'] = 32
        after = render(values)
        config = next(d for d in after if d['kind'] == 'ConfigMap')
        self.assertEqual(config['data'], {'CAPACITY': '32'})
        old = next(d for d in before if d['kind'] == 'Deployment')['spec']['template']['metadata']['annotations']
        new = next(d for d in after if d['kind'] == 'Deployment')['spec']['template']['metadata']['annotations']
        self.assertNotEqual(old['checksum/capacity'], new['checksum/capacity'])

    def test_defaults_preserve_web_app(self):
        docs = render({})
        self.assertEqual({doc['kind'] for doc in docs}, {'Deployment', 'Service', 'Pod'})
        pod = next(d for d in docs if d['kind'] == 'Deployment')['spec']['template']['spec']
        self.assertNotIn('automountServiceAccountToken', pod)
        self.assertEqual(pod['containers'][0]['name'], 'app')
        self.assertEqual(pod['containers'][0]['image'], 'nginx:latest')

    def test_worker_disables_service_and_connection_test(self):
        refs = [{'secretRef': {'name': 'shared'}}, {'configMapRef': {'name': 'overrides'}}]
        image = 'registry.example:5000/worker@sha256:' + 'a' * 64
        docs = render({'service': {'enabled': False}, 'containerName': 'worker',
                       'automountServiceAccountToken': False, 'envFrom': refs,
                       'image': {'reference': image},
                       'controller': {'annotations': {'argocd.argoproj.io/sync-wave': '1'}}})
        self.assertEqual(len(docs), 1)
        deployment = docs[0]
        self.assertEqual(deployment['metadata']['annotations']['argocd.argoproj.io/sync-wave'], '1')
        pod = deployment['spec']['template']['spec']
        self.assertIs(pod['automountServiceAccountToken'], False)
        container = pod['containers'][0]
        self.assertEqual(container['name'], 'worker')
        self.assertEqual(container['image'], image)
        self.assertEqual(container['envFrom'], refs)
        self.assertNotIn('ports', container)

    def test_explicit_extra_ports_survive_without_service(self):
        ports = [{'name': 'metrics', 'containerPort': 9090}]
        docs = render({'service': {'enabled': False}, 'extraPorts': ports,
                       'automountServiceAccountToken': True})
        pod = docs[0]['spec']['template']['spec']
        self.assertEqual(pod['containers'][0]['ports'], ports)
        self.assertIs(pod['automountServiceAccountToken'], True)

    def test_controller_can_be_rendered_by_parent(self):
        self.assertEqual(render({'controller': {'enabled': False}, 'service': {'enabled': False}}), [])

    def test_extra_worker_tracks_image_without_inheriting_web_configuration(self):
        docs = render({'image': {'repository': 'example/app', 'tag': 'v9'},
                       'replicaCount': 4, 'configmap': {'enabled': True, 'data': {'WEB_ONLY': 'yes'}},
                       'readinessProbe': {'httpGet': {'path': '/ready', 'port': 3000}},
                       'workloads': {'worker': {'fullnameOverride': 'worker',
                                                'containerName': 'worker', 'service': {'enabled': False},
                                                'command': ['node', 'worker.js'],
                                                'overrides': 'image: {{ toYaml .Values.image | nindent 2 }}'}}})
        worker = next(d for d in docs if d['kind'] == 'Deployment' and d['metadata']['name'] == 'worker')
        self.assertEqual(worker['spec']['replicas'], 1)
        container = worker['spec']['template']['spec']['containers'][0]
        self.assertEqual(container['image'], 'example/app:v9')
        self.assertEqual(container['command'], ['node', 'worker.js'])
        self.assertNotIn('envFrom', container)
        self.assertNotIn('readinessProbe', container)
        self.assertNotIn('ports', container)

    def test_raw_uses_main_context_and_omits_disabled_documents(self):
        docs = render({'image': {'tag': 'v9'}, 'raw': {'enabled': True, 'parentTemplates': [
            'apiVersion: v1\nkind: ConfigMap\nmetadata: {name: extra}\ndata: {version: {{ .Values.image.tag | quote }}}',
            '{{ if false }}apiVersion: v1\nkind: ConfigMap{{ end }}',
        ]}})
        extra = next(d for d in docs if d['kind'] == 'ConfigMap')
        self.assertEqual(extra['data']['version'], 'v9')
        self.assertTrue(all('kind' in d and 'apiVersion' in d for d in docs))
        with self.assertRaises(subprocess.CalledProcessError):
            render({'raw': {'enabled': True, 'parentTemplates': ['broken: [']}})

    def test_monitor_keeps_authentication_and_optional_endpoint_fields(self):
        endpoints = [{'port': 'http', 'path': '/metrics', 'interval': '15s',
                      'authorization': {'type': 'Bearer', 'credentials': {'name': 'metrics', 'key': 'token'}},
                      'tlsConfig': {'serverName': 'metrics.example'}, 'scrapeTimeout': '5s',
                      'relabelings': [{'action': 'keep', 'sourceLabels': ['__name__'], 'regex': 'app_.*'}]}]
        docs = render({'serviceMonitor': {'enabled': True, 'endpoints': endpoints}})
        monitor = next(d for d in docs if d['kind'] == 'ServiceMonitor')
        self.assertEqual(monitor['spec']['endpoints'], endpoints)
        service = next(d for d in docs if d['kind'] == 'Service')
        self.assertLessEqual(monitor['spec']['selector']['matchLabels'].items(), service['metadata']['labels'].items())


if __name__ == '__main__':
    unittest.main()
