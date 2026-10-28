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

    def test_worker_renders_its_own_objects_under_a_derived_name(self):
        metrics = [{'type': 'Resource', 'resource': {'name': 'cpu', 'target': {'type': 'Utilization', 'averageUtilization': 60}}}]
        docs = render({'workloads': {'queueWorker': {
            'service': {'enabled': False}, 'pdb': {'enabled': True},
            'configmap': {'enabled': True, 'data': {'QUEUE': 'jobs'}},
            'autoscaling': {'enabled': True, 'minReplicas': 2, 'maxReplicas': 4, 'metrics': metrics}}}})
        name = 'test-app-queue-worker'
        objects = {(d['kind'], d['metadata']['name']) for d in docs}
        for kind in ('Deployment', 'ConfigMap', 'HorizontalPodAutoscaler', 'PodDisruptionBudget'):
            self.assertIn((kind, name), objects)
        self.assertNotIn(('Service', name), objects)
        worker = next(d for d in docs if d['kind'] == 'Deployment' and d['metadata']['name'] == name)
        self.assertNotIn('replicas', worker['spec'])
        self.assertEqual(worker['spec']['template']['spec']['containers'][0]['envFrom'], [{'configMapRef': {'name': name}}])
        pdb = next(d for d in docs if d['kind'] == 'PodDisruptionBudget')
        self.assertEqual(pdb['spec']['selector']['matchLabels']['app.kubernetes.io/name'], name)

    def test_workload_names_must_be_unique(self):
        with self.assertRaises(subprocess.CalledProcessError):
            render({'workloads': {'worker': {'fullnameOverride': 'test-app'}}})
        with self.assertRaises(subprocess.CalledProcessError):
            render({'workloads': {'a': {'fullnameOverride': 'same'}, 'b': {'fullnameOverride': 'same'}}})
        shared = {'enabled': True, 'name': 'credentials', 'data': [{'key': '/k', 'name': 'K'}]}
        with self.assertRaises(subprocess.CalledProcessError):
            render({'service': {'enabled': False}, 'externalSecrets': shared,
                    'workloads': {'worker': {'service': {'enabled': False}, 'externalSecrets': shared}}})
        names = {d['metadata']['name'] for d in render({'fullnameOverride': 'x' * 63, 'service': {'enabled': False},
                                                        'workloads': {'a': {}, 'b': {}}})}
        self.assertEqual(len(names), 3)
        self.assertTrue(all(len(n) <= 63 for n in names))
        self.assertIn('x' * 61 + '-a', names)

    def test_main_app_can_be_omitted_while_workers_render(self):
        docs = render({'enabled': False, 'workloads': {'worker': {'service': {'enabled': False}}}})
        self.assertEqual([(d['kind'], d['metadata']['name']) for d in docs], [('Deployment', 'test-app-worker')])

    def test_service_exposes_extra_ports(self):
        extra = [{'name': 'metrics', 'port': 9090, 'targetPort': 'metrics', 'protocol': 'TCP'}]
        docs = render({'service': {'extraPorts': extra},
                       'extraPorts': [{'name': 'metrics', 'containerPort': 9090}]})
        service = next(d for d in docs if d['kind'] == 'Service')
        self.assertEqual([p['name'] for p in service['spec']['ports']], ['http', 'metrics'])
        self.assertEqual(service['spec']['ports'][1], extra[0])

    def test_routes_follow_path_and_reject_unknown_types(self):
        docs = render({'routing': {'istio': {'enabled': True}, 'path': '/api', 'pathType': 'Exact'}})
        service = next(d for d in docs if d['kind'] == 'VirtualService')
        self.assertEqual(service['spec']['http'][0]['match'], [{'uri': {'exact': '/api'}}])
        docs = render({'routing': {'istio': {'enabled': True}, 'path': '/api/'}})
        match = next(d for d in docs if d['kind'] == 'VirtualService')['spec']['http'][0]['match']
        self.assertEqual(match, [{'uri': {'exact': '/api'}}, {'uri': {'prefix': '/api/'}}])
        docs = render({'routing': {'istio': {'enabled': True}}})
        match = next(d for d in docs if d['kind'] == 'VirtualService')['spec']['http'][0]['match']
        self.assertEqual(match, [{'uri': {'prefix': '/'}}])
        with self.assertRaises(subprocess.CalledProcessError):
            render({'routing': {'httpRoute': {'enabled': True}, 'pathType': 'ImplementationSpecific'}})

    def test_connection_test_runs_unprivileged(self):
        pod = next(d for d in render({}) if d['kind'] == 'Pod')
        self.assertIs(pod['spec']['securityContext']['runAsNonRoot'], True)
        container = pod['spec']['containers'][0]
        self.assertEqual(container['image'], 'busybox:1.37')
        self.assertEqual(container['args'][-1], 'http://test-app:80')
        self.assertIs(container['securityContext']['readOnlyRootFilesystem'], True)

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

    def test_external_secrets_read_a_release_store_and_find_paths(self):
        values = {'path': '/apps/demo', 'externalSecrets': {
            'enabled': True, 'name': 'app-env', 'optional': True, 'refreshInterval': '5m',
            'secretStore': {'enabled': True, 'name': 'tenant', 'provider': {
                'aws': {'service': 'ParameterStore', 'region': '{{ .Values.region }}'}}},
            'dataFrom': [{'find': {'path': '{{ .Values.path }}', 'name': {'regexp': '.*'}}}]}, 'region': 'us-east-1'}
        docs = render(values)
        store = next(d for d in docs if d['kind'] == 'SecretStore')
        self.assertEqual(store['metadata']['name'], 'tenant')
        self.assertEqual(store['spec']['provider']['aws']['region'], 'us-east-1')
        secret = next(d for d in docs if d['kind'] == 'ExternalSecret')
        self.assertEqual(secret['metadata']['name'], 'app-env')
        self.assertEqual(secret['spec']['secretStoreRef'], {'kind': 'SecretStore', 'name': 'tenant'})
        self.assertEqual(secret['spec']['target'], {'name': 'app-env'})
        self.assertEqual(secret['spec']['dataFrom'][0]['find']['path'], '/apps/demo')
        self.assertNotIn('data', secret['spec'])
        container = next(d for d in docs if d['kind'] == 'Deployment')['spec']['template']['spec']['containers'][0]
        self.assertEqual(container['envFrom'], [{'secretRef': {'name': 'app-env', 'optional': True}}])
        with self.assertRaises(subprocess.CalledProcessError):
            render({'externalSecrets': {'enabled': True, 'secretStore': {'enabled': True}}})
        docs = render({'externalSecrets': {'enabled': True, 'name': '123', 'data': [{'key': 'k', 'name': 'K'}]}})
        self.assertEqual(next(d for d in docs if d['kind'] == 'ExternalSecret')['metadata']['name'], '123')

    def test_external_secret_annotations_keep_the_sync_wave(self):
        docs = render({'externalSecrets': {'enabled': True, 'annotations': {'force-sync': 'delivery-1'},
                                           'data': [{'key': '/k8s/demo', 'name': 'TOKEN'}]}})
        secret = next(d for d in docs if d['kind'] == 'ExternalSecret')
        self.assertEqual(secret['metadata']['annotations'], {'argocd.argoproj.io/sync-wave': '-1', 'force-sync': 'delivery-1'})

    def test_external_secrets_keep_the_cluster_store_and_default_name(self):
        docs = render({'externalSecrets': {'enabled': True, 'data': [{'key': '/k8s/demo', 'name': 'TOKEN'}]}})
        self.assertNotIn('SecretStore', {d['kind'] for d in docs})
        secret = next(d for d in docs if d['kind'] == 'ExternalSecret')
        self.assertEqual(secret['metadata']['name'], 'test-app-external')
        self.assertEqual(secret['spec']['secretStoreRef'], {'kind': 'ClusterSecretStore', 'name': 'parameter-store'})
        self.assertEqual(secret['spec']['data'], [{'remoteRef': {'key': '/k8s/demo'}, 'secretKey': 'TOKEN'}])
        container = next(d for d in docs if d['kind'] == 'Deployment')['spec']['template']['spec']['containers'][0]
        self.assertEqual(container['envFrom'], [{'secretRef': {'name': 'test-app-external'}}])

    def test_network_policy_selects_the_release_and_checks_directions(self):
        ingress = [{'from': [{'podSelector': {}}]}]
        egress = [{'to': [{'ipBlock': {'cidr': '0.0.0.0/0'}}], 'ports': [{'protocol': 'TCP', 'port': 443}]}]
        docs = render({'networkPolicy': {'enabled': True, 'policyTypes': ['Ingress', 'Egress'],
                                         'ingress': ingress, 'egress': egress},
                       'workloads': {'worker': {'service': {'enabled': False}}}})
        policy = next(d for d in docs if d['kind'] == 'NetworkPolicy')
        self.assertEqual(policy['spec']['podSelector'], {'matchLabels': {'app.kubernetes.io/instance': 'test'}})
        self.assertEqual(policy['spec']['ingress'], ingress)
        self.assertEqual(policy['spec']['egress'], egress)
        for deployment in (d for d in docs if d['kind'] == 'Deployment'):
            self.assertEqual(deployment['spec']['template']['metadata']['labels']['app.kubernetes.io/instance'], 'test')
        deny = next(d for d in render({'networkPolicy': {'enabled': True, 'policyTypes': ['Egress']}}) if d['kind'] == 'NetworkPolicy')
        self.assertEqual(deny['spec']['policyTypes'], ['Egress'])
        self.assertNotIn('egress', deny['spec'])
        with self.assertRaises(subprocess.CalledProcessError):
            render({'networkPolicy': {'enabled': True},
                    'workloads': {'worker': {'service': {'enabled': False}, 'namespaceOverride': 'other'}}})
        for policy in ({'egress': egress}, {'policyTypes': ['Ingress', 'Other']}, {'policyTypes': []}):
            with self.assertRaises(subprocess.CalledProcessError):
                render({'networkPolicy': {'enabled': True, **policy}})

    def test_resource_quota_requires_limits(self):
        hard = {'requests.cpu': '4', 'pods': '12'}
        quota = next(d for d in render({'resourceQuota': {'enabled': True, 'hard': hard}}) if d['kind'] == 'ResourceQuota')
        self.assertEqual(quota['spec']['hard'], hard)
        with self.assertRaises(subprocess.CalledProcessError):
            render({'resourceQuota': {'enabled': True}})

    def test_rbac_scope_follows_namespaced(self):
        rules = [{'apiGroups': [''], 'resources': ['configmaps'], 'verbs': ['get']}]
        account = {'serviceAccount': {'create': True}, 'rbac': {'create': True, 'rules': rules}}
        cluster = render(account)
        self.assertEqual({d['kind'] for d in cluster} & {'ClusterRole', 'ClusterRoleBinding', 'Role'}, {'ClusterRole', 'ClusterRoleBinding'})
        account['rbac']['namespaced'] = True
        docs = render(account)
        role = next(d for d in docs if d['kind'] == 'Role')
        binding = next(d for d in docs if d['kind'] == 'RoleBinding')
        self.assertEqual(role['rules'], rules)
        self.assertEqual(binding['roleRef'], {'apiGroup': 'rbac.authorization.k8s.io', 'kind': 'Role', 'name': 'test-app'})
        self.assertEqual(binding['subjects'][0]['name'], 'test-app')
        self.assertNotIn('ClusterRole', {d['kind'] for d in docs})
        with self.assertRaises(subprocess.CalledProcessError):
            render({'rbac': {'create': True, 'rules': rules}})

    def test_pdb_accepts_zero_and_one_budget(self):
        pdb = next(d for d in render({'pdb': {'enabled': True, 'minAvailable': 0}}) if d['kind'] == 'PodDisruptionBudget')
        self.assertEqual(pdb['spec']['minAvailable'], 0)
        pdb = next(d for d in render({'pdb': {'enabled': True}}) if d['kind'] == 'PodDisruptionBudget')
        self.assertEqual(pdb['spec']['maxUnavailable'], 1)
        with self.assertRaises(subprocess.CalledProcessError):
            render({'pdb': {'enabled': True, 'minAvailable': 1, 'maxUnavailable': 1}})

    def test_autoscaling_rejects_inverted_bounds(self):
        metrics = [{'type': 'Resource', 'resource': {'name': 'cpu', 'target': {'type': 'Utilization', 'averageUtilization': 60}}}]
        with self.assertRaises(subprocess.CalledProcessError):
            render({'autoscaling': {'enabled': True, 'minReplicas': 4, 'maxReplicas': 2, 'metrics': metrics}})

    def test_pod_dns_and_priority_are_optional(self):
        dns = {'options': [{'name': 'ndots', 'value': '2'}]}
        pod = next(d for d in render({'dnsConfig': dns, 'priorityClassName': 'high'}) if d['kind'] == 'Deployment')['spec']['template']['spec']
        self.assertEqual(pod['dnsConfig'], dns)
        self.assertEqual(pod['priorityClassName'], 'high')
        pod = next(d for d in render({'priorityClassName': '123'}) if d['kind'] == 'Deployment')['spec']['template']['spec']
        self.assertEqual(pod['priorityClassName'], '123')
        pod = next(d for d in render({}) if d['kind'] == 'Deployment')['spec']['template']['spec']
        self.assertNotIn('dnsConfig', pod)
        self.assertNotIn('priorityClassName', pod)

    def test_config_checksums_follow_only_the_data(self):
        def annotations(values):
            return next(d for d in render(values) if d['kind'] == 'Deployment')['spec']['template']['metadata']['annotations']
        base = {'configmap': {'enabled': True, 'data': {'A': '1'}}, 'secret': {'enabled': True, 'data': {'B': 'Mg=='}}}
        before = annotations(base)
        self.assertEqual(before, annotations({**base, 'additionalLabels': {'team': 'x'}}))
        after = annotations({**base, 'configmap': {'enabled': True, 'data': {'A': '2'}}})
        self.assertNotEqual(before['checksum/config'], after['checksum/config'])
        self.assertEqual(before['checksum/secret'], after['checksum/secret'])

if __name__ == '__main__':
    unittest.main()
