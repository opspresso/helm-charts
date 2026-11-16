"""Opt-in live tests, confined to a dedicated kind cluster and disposable namespace.

KUBECONFIG=/path/to/kind-config python tests/statefulset_lifecycle.py
Never run against a shared or production cluster.
"""
import copy
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import uuid
import yaml

CHART = Path(__file__).resolve().parents[1] / 'charts/app'
CONTEXT = 'kind-app-statefulset-test'
NAMESPACE = 'app-chart-' + uuid.uuid4().hex[:10]


def run(*args):
    return subprocess.check_output(args, text=True).strip()


def kubectl(*args):
    return run('kubectl', '--context', CONTEXT, '-n', NAMESPACE, *args)


def get(kind, name=None):
    return json.loads(kubectl('get', kind, *([name] if name else []), '-o', 'json'))


def eventually(predicate, description, timeout=120):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(2)
    raise AssertionError(description)


def ready(count):
    pods = get('pods')['items']
    return len(pods) == count and all(any(c['type'] == 'Ready' and c['status'] == 'True'
                                        for c in p.get('status', {}).get('conditions', [])) for p in pods)


def install(values):
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'values.yaml'; path.write_text(yaml.safe_dump(values))
        run('helm', 'upgrade', '--install', 'app', str(CHART), '--kube-context', CONTEXT,
            '--namespace', NAMESPACE, '--reset-values', '-f', str(path), '--wait', '--timeout', '180s')


def uid(kind, name):
    return get(kind, name)['metadata']['uid']


def marker(pod):
    return kubectl('exec', pod, '--', 'cat', '/data/identity')


def main():
    if not os.environ.get('KUBECONFIG'):
        raise SystemExit('Set KUBECONFIG to the dedicated kind cluster config.')
    config = json.loads(run('kubectl', '--context', CONTEXT, 'config', 'view', '--minify', '-o', 'json'))
    if config['contexts'][0]['context']['cluster'] != CONTEXT:
        raise SystemExit('This test requires kind-app-statefulset-test.')
    kubectl('create', 'namespace', NAMESPACE)
    try:
        values = {'fullnameOverride': 'store', 'controller': {'kind': 'StatefulSet'}, 'replicaCount': 2,
                  'image': {'repository': 'busybox', 'tag': '1.37.0'}, 'service': {'enabled': False},
                  'command': ['sh', '-c', 'test -f /data/identity || hostname > /data/identity; exec sleep 3600'],
                  'readinessProbe': {'exec': {'command': ['test', '-f', '/data/identity']}},
                  'persistence': {'enabled': True, 'mode': 'perReplica', 'size': '1Gi'}}
        install(values)
        eventually(lambda: ready(2), 'two stateful Pods are Ready')
        claims = [uid('pvc', 'data-store-' + str(n)) for n in range(2)]
        assert len(set(claims)) == 2
        assert [marker('store-' + str(n)) for n in range(2)] == ['store-0', 'store-1']
        kubectl('exec', 'store-0', '--', 'nslookup', 'store-1.store-headless.' + NAMESPACE + '.svc.cluster.local')
        old = uid('pod', 'store-0')
        kubectl('delete', 'pod', 'store-0', '--wait=true')
        eventually(lambda: ready(2) and uid('pod', 'store-0') != old, 'replacement Pod has a new UID')
        assert marker('store-0') == 'store-0' and uid('pvc', 'data-store-0') == claims[0]
        print('PASS: ordinal DNS, separate claims, Pod replacement preserves data', flush=True)

        before = [uid('pod', 'store-' + str(n)) for n in range(2)]
        values['controller']['statefulSet'] = {'updateStrategy': {'type': 'RollingUpdate', 'rollingUpdate': {'partition': 1}}}
        values['env'] = [{'name': 'REVISION', 'value': 'two'}]
        install(values)
        assert uid('pod', 'store-0') == before[0] and uid('pod', 'store-1') != before[1]
        assert marker('store-1') == 'store-1'
        values['controller']['statefulSet'] = {'updateStrategy': {'type': 'OnDelete'}}
        values['env'] = [{'name': 'REVISION', 'value': 'three'}]
        before = [uid('pod', 'store-' + str(n)) for n in range(2)]
        install(values)
        assert [uid('pod', 'store-' + str(n)) for n in range(2)] == before
        print('PASS: partitioned RollingUpdate and OnDelete behavior', flush=True)

        values['replicaCount'] = 1; install(values)
        eventually(lambda: ready(1), 'scaled to one Pod')
        assert uid('pvc', 'data-store-1') == claims[1]
        values['replicaCount'] = 2; install(values)
        eventually(lambda: ready(2), 'scaled back to two Pods')
        assert uid('pvc', 'data-store-1') == claims[1] and marker('store-1') == 'store-1'
        run('helm', 'uninstall', 'app', '--kube-context', CONTEXT, '--namespace', NAMESPACE, '--wait')
        eventually(lambda: ready(0), 'Pods removed after uninstall')
        assert [uid('pvc', 'data-store-' + str(n)) for n in range(2)] == claims
        print('PASS: scale-down and uninstall retain per-replica PVCs by default', flush=True)

        # A chart-owned standalone PVC remains the same object during a stopped controller migration.
        shared = copy.deepcopy(values); shared['controller'] = {'kind': 'Deployment'}
        shared['replicaCount'] = 1; shared['persistence']['mode'] = 'shared'
        install(shared); eventually(lambda: ready(1), 'Deployment Pod ready')
        claim = uid('pvc', 'store'); pod = get('pods')['items'][0]['metadata']['name']
        original = marker(pod)
        shared['replicaCount'] = 0; install(shared); eventually(lambda: ready(0), 'old Deployment stopped')
        shared['controller'] = {'kind': 'StatefulSet'}; shared['replicaCount'] = 1
        install(shared); eventually(lambda: ready(1), 'StatefulSet started')
        assert uid('pvc', 'store') == claim and marker('store-0') == original
        assert get('deployments')['items'] == []
        print('PASS: stopped Deployment to StatefulSet migration preserves standalone PVC and data', flush=True)

        run('helm', 'uninstall', 'app', '--kube-context', CONTEXT, '--namespace', NAMESPACE, '--wait')
        eventually(lambda: ready(0), 'migration test stopped')
        disposable = copy.deepcopy(values)
        disposable['fullnameOverride'] = 'disposable'
        disposable['replicaCount'] = 2
        disposable['controller']['statefulSet'] = {
            'persistentVolumeClaimRetentionPolicy': {'whenDeleted': 'Delete', 'whenScaled': 'Delete'}}
        install(disposable); eventually(lambda: ready(2), 'disposable replicas ready')
        disposable['replicaCount'] = 1; install(disposable)
        eventually(lambda: all(p['metadata']['name'] != 'data-disposable-1' for p in get('pvc')['items']),
                   'whenScaled=Delete removes the scaled-down claim')
        run('helm', 'uninstall', 'app', '--kube-context', CONTEXT, '--namespace', NAMESPACE, '--wait')
        eventually(lambda: all(not p['metadata']['name'].startswith('data-disposable-') for p in get('pvc')['items']),
                   'whenDeleted=Delete removes the remaining claims')
        assert [uid('pvc', 'data-store-' + str(n)) for n in range(2)] == claims
        print('PASS: explicit Delete policies remove only their own scaled/deleted claims', flush=True)
    finally:
        kubectl('delete', 'namespace', NAMESPACE, '--wait=true', '--timeout=180s')


if __name__ == '__main__':
    main()
