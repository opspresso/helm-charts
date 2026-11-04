"""Render the postgres and valkey charts with Helm; run with unittest and PyYAML installed."""
from pathlib import Path
import subprocess
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]


def render(chart, *settings):
    arguments = ['helm', 'template', 'main', str(ROOT / 'charts' / chart), '--namespace', 'app-todo-dev']
    for setting in settings:
        arguments += ['--set', setting]
    result = subprocess.run(arguments, check=True, capture_output=True, text=True)
    return {doc['kind']: doc for doc in yaml.safe_load_all(result.stdout) if doc}


class DataChartTests(unittest.TestCase):
    def test_server_keeps_the_password_out_of_the_pod_spec_and_deletes_data_with_the_release(self):
        for chart, key in (('postgres', 'MAIN_PGPASSWORD'), ('valkey', 'MAIN_VALKEY_PASSWORD')):
            with self.subTest(chart):
                server = render(chart, f'passwordSecret.key={key}')['StatefulSet']
                self.assertEqual(server['spec']['persistentVolumeClaimRetentionPolicy']['whenDeleted'], 'Delete')
                pod = server['spec']['template']['spec']
                self.assertFalse(pod['automountServiceAccountToken'])
                sources = [e['valueFrom']['secretKeyRef'] for e in pod['containers'][0]['env'] if 'valueFrom' in e]
                self.assertEqual(sources, [{'name': 'app-env', 'key': key}])

    def test_password_key_is_required(self):
        for chart in ('postgres', 'valkey'):
            with self.subTest(chart), self.assertRaises(subprocess.CalledProcessError):
                render(chart)

    def test_policy_allows_the_namespace_and_only_the_named_peer(self):
        for chart, port in (('postgres', 5432), ('valkey', 6379)):
            with self.subTest(chart):
                policy = render(chart, 'passwordSecret.key=K')['NetworkPolicy']
                self.assertEqual(policy['spec']['policyTypes'], ['Ingress', 'Egress'])
                self.assertEqual(policy['spec']['egress'], [])
                ingress = policy['spec']['ingress'][0]
                self.assertEqual(ingress['ports'], [{'protocol': 'TCP', 'port': port}])
                self.assertEqual(ingress['from'], [{'podSelector': {}}])
                policy = render(chart, 'passwordSecret.key=K', 'peer.enabled=true', 'peer.namespace=sandboxes')['NetworkPolicy']
                peers = policy['spec']['ingress'][0]['from']
                self.assertEqual(peers[0], {'podSelector': {}}, 'the app in the namespace stays allowed')
                self.assertEqual(peers[1]['namespaceSelector']['matchLabels'], {'kubernetes.io/metadata.name': 'sandboxes'})

    def test_fullname_override_names_every_object_and_selects_only_its_pods(self):
        for chart in ('postgres', 'valkey'):
            with self.subTest(chart):
                default = render(chart, 'passwordSecret.key=K')
                self.assertEqual({d['metadata']['name'] for d in default.values()}, {'main'})
                docs = render(chart, 'passwordSecret.key=K', f'fullnameOverride=main-{chart}')
                self.assertEqual({d['metadata']['name'] for d in docs.values()}, {f'main-{chart}'})
                server = docs['StatefulSet']['spec']
                self.assertEqual(server['serviceName'], f'main-{chart}')
                selector = server['selector']['matchLabels']
                self.assertEqual(selector['app.kubernetes.io/instance'], f'main-{chart}')
                self.assertEqual(docs['Service']['spec']['selector'], selector)

    def test_postgres_config_becomes_server_options(self):
        container = render('postgres', 'passwordSecret.key=K')['StatefulSet']['spec']['template']['spec']['containers'][0]
        self.assertNotIn('args', container, 'the image default command stays')
        container = render('postgres', 'passwordSecret.key=K', 'config.max_locks_per_transaction=128')['StatefulSet']['spec']['template']['spec']['containers'][0]
        self.assertEqual(container['args'], ['postgres', '-c', 'max_locks_per_transaction=128'])


if __name__ == '__main__':
    unittest.main()
