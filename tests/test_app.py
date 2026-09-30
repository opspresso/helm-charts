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
