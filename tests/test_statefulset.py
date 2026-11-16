"""Public StatefulSet contracts: identity, storage safety and shared Pod behavior."""
import copy
import subprocess
import unittest
from test_app import render


def state(values=None):
    result = copy.deepcopy(values or {})
    result.setdefault('controller', {})['kind'] = 'StatefulSet'
    return result


def workload(docs, kind='StatefulSet'):
    return next(d for d in docs if d['kind'] == kind)


class StatefulSetTests(unittest.TestCase):
    def test_default_identity_keeps_client_service_separate(self):
        docs = render(state())
        sts = workload(docs)
        self.assertNotIn('strategy', sts['spec'])
        self.assertEqual(sts['spec']['updateStrategy'], {'type': 'RollingUpdate'})
        self.assertEqual(sts['spec']['podManagementPolicy'], 'OrderedReady')
        self.assertNotIn('persistentVolumeClaimRetentionPolicy', sts['spec'])
        services = {s['metadata']['name']: s for s in docs if s['kind'] == 'Service'}
        governing = services[sts['spec']['serviceName']]
        self.assertEqual(governing['spec']['clusterIP'], 'None')
        self.assertFalse(governing['spec']['publishNotReadyAddresses'])
        self.assertEqual(governing['spec']['selector'], sts['spec']['selector']['matchLabels'])
        self.assertNotIn('clusterIP', services[sts['metadata']['name']]['spec'])

    def test_shared_pod_contract_is_identical_to_deployment_and_rollout(self):
        values = {'configmap': {'enabled': True, 'data': {'KEY': 'value'}},
                  'secret': {'enabled': True, 'data': {'SECRET': 'dmFsdWU='}},
                  'podAnnotations': {'custom': 'yes'}, 'podLabels': {'team': 'platform'},
                  'serviceAccount': {'create': True}, 'automountServiceAccountToken': False,
                  'initContainers': [{'name': 'init', 'image': 'busybox:1.37', 'command': ['true']}],
                  'sidecars': [{'name': 'sidecar', 'image': 'busybox:1.37'}],
                  'extraVolumes': [{'name': 'cache', 'emptyDir': {}}],
                  'extraVolumeMounts': [{'name': 'cache', 'mountPath': '/cache'}],
                  'readinessProbe': {'exec': {'command': ['true']}},
                  'securityContext': {'runAsNonRoot': True},
                  'nodeSelector': {'kubernetes.io/arch': 'arm64'},
                  'persistence': {'enabled': True, 'existingClaim': 'existing-data'}}
        expected = workload(render(values), 'Deployment')['spec']['template']
        self.assertEqual(workload(render(state(values)))['spec']['template'], expected)
        rollout = copy.deepcopy(values); rollout['controller'] = {'kind': 'Rollout'}
        self.assertEqual(workload(render(rollout), 'Rollout')['spec']['template'], expected)

    def test_existing_claim_is_never_recreated(self):
        docs = render(state({'persistence': {'enabled': True, 'existingClaim': 'nexus'}}))
        sts = workload(docs)
        self.assertNotIn('PersistentVolumeClaim', [d['kind'] for d in docs])
        self.assertNotIn('volumeClaimTemplates', sts['spec'])
        self.assertEqual(sts['spec']['template']['spec']['volumes'],
                         [{'name': 'data', 'persistentVolumeClaim': {'claimName': 'nexus'}}])

    def test_shared_standalone_claim_preserves_name(self):
        docs = render(state({'persistence': {'enabled': True}}))
        self.assertEqual(workload(docs, 'PersistentVolumeClaim')['metadata']['name'], 'test-app')
        self.assertNotIn('volumeClaimTemplates', workload(docs)['spec'])

    def test_per_replica_claims_are_not_pod_volume_references(self):
        values = state({'replicaCount': 3, 'persistence': {'enabled': True, 'mode': 'perReplica',
                           'size': '20Gi', 'storageClassName': 'gp3', 'mountPath': '/state',
                           'selectorLabels': {'disk': 'data'}},
                        'extraVolumes': [{'name': 'scratch', 'emptyDir': {}}]})
        docs = render(values); sts = workload(docs)
        self.assertNotIn('PersistentVolumeClaim', [d['kind'] for d in docs])
        claim = sts['spec']['volumeClaimTemplates'][0]
        self.assertEqual(claim['metadata']['name'], 'data')
        self.assertEqual(claim['spec'], {'accessModes': ['ReadWriteOnce'], 'storageClassName': 'gp3',
                          'resources': {'requests': {'storage': '20Gi'}}, 'selector': {'matchLabels': {'disk': 'data'}}})
        pod = sts['spec']['template']['spec']
        self.assertEqual(pod['volumes'], [{'name': 'scratch', 'emptyDir': {}}])
        self.assertEqual(pod['containers'][0]['volumeMounts'], [{'name': 'data', 'mountPath': '/state'}])

    def test_additional_claims_and_explicit_retention(self):
        claim = {'metadata': {'name': 'journal', 'annotations': {'backup': 'daily'}},
                 'spec': {'accessModes': ['ReadWriteOnce'], 'resources': {'requests': {'storage': '1Gi'}}}}
        values = state({'controller': {'statefulSet': {'volumeClaimTemplates': [claim],
                         'persistentVolumeClaimRetentionPolicy': {'whenDeleted': 'Retain', 'whenScaled': 'Delete'}}},
                        'extraVolumeMounts': [{'name': 'journal', 'mountPath': '/journal'}]})
        sts = workload(render(values))
        self.assertEqual(sts['spec']['volumeClaimTemplates'], [claim])
        self.assertEqual(sts['spec']['persistentVolumeClaimRetentionPolicy'], {'whenDeleted': 'Retain', 'whenScaled': 'Delete'})
        self.assertNotIn('volumes', sts['spec']['template']['spec'])

    def test_updates_and_external_governing_service(self):
        values = state({'controller': {'statefulSet': {'serviceName': 'external-headless',
                         'headlessService': {'enabled': False}, 'podManagementPolicy': 'Parallel',
                         'minReadySeconds': 10, 'updateStrategy': {'type': 'OnDelete'}}}, 'service': {'enabled': False}})
        docs = render(values); self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0]['spec']['serviceName'], 'external-headless')
        self.assertEqual(docs[0]['spec']['minReadySeconds'], 10)
        self.assertEqual(docs[0]['spec']['updateStrategy'], {'type': 'OnDelete'})
        partition = workload(render(state({'controller': {'statefulSet': {'updateStrategy': {'rollingUpdate': {'partition': 1}}}}})))
        self.assertEqual(partition['spec']['updateStrategy']['rollingUpdate'], {'partition': 1})

    def test_headless_service_without_client_ports(self):
        docs = render(state({'service': {'enabled': False}, 'controller': {'statefulSet': {
            'headlessService': {'publishNotReadyAddresses': True, 'annotations': {'dns': 'peers'}}}}}))
        service = workload(docs, 'Service')
        self.assertNotIn('ports', service['spec'])
        self.assertTrue(service['spec']['publishNotReadyAddresses'])
        self.assertEqual(service['metadata']['annotations'], {'dns': 'peers'})

    def test_hpa_targets_statefulset_and_owns_replicas(self):
        values = state({'autoscaling': {'enabled': True, 'minReplicas': 1, 'maxReplicas': 3,
                         'metrics': [{'type': 'Resource', 'resource': {'name': 'cpu', 'target': {'type': 'Utilization', 'averageUtilization': 60}}}]},
                        'persistence': {'enabled': True, 'mode': 'perReplica'}})
        docs = render(values)
        self.assertNotIn('replicas', workload(docs)['spec'])
        self.assertEqual(workload(docs, 'HorizontalPodAutoscaler')['spec']['scaleTargetRef'],
                         {'apiVersion': 'apps/v1', 'kind': 'StatefulSet', 'name': 'test-app'})

    def test_worker_uses_own_identity_and_storage(self):
        docs = render({'workloads': {'database': state({'persistence': {'enabled': True, 'mode': 'perReplica'}})}})
        sts = workload(docs)
        self.assertEqual(sts['metadata']['name'], 'test-app-database')
        self.assertEqual(sts['spec']['serviceName'], 'test-app-database-headless')
        self.assertEqual(workload(docs, 'Deployment')['metadata']['name'], 'test-app')

    def test_ordinal_hostname_length_is_checked_before_deployment(self):
        self.assertEqual(workload(render(state({'fullnameOverride': 'a' * 61, 'replicaCount': 10})))['spec']['replicas'], 10)
        for values in [{'fullnameOverride': 'a' * 62}, {'fullnameOverride': 'a' * 61, 'replicaCount': 11},
                       {'fullnameOverride': 'has.dot'}, {'replicaCount': -1},
                       {'replicaCount': 2, 'persistence': {'enabled': True, 'accessModes': ['ReadWriteOncePod']}}]:
            with self.subTest(values=values), self.assertRaises(subprocess.CalledProcessError):
                render(state(values))

    def test_invalid_configurations_fail_with_actionable_errors(self):
        cases = [
            ({'controller': {'kind': 'Statefulset'}}, 'kind'),
            ({'persistence': {'enabled': True, 'mode': 'perReplica'}}, 'requires StatefulSet'),
            (state({'persistence': {'mode': 'perReplica'}}), 'requires StatefulSet'),
            (state({'persistence': {'enabled': True, 'mode': 'perReplica', 'existingClaim': 'data'}}), 'existingClaim'),
            (state({'replicaCount': 2, 'persistence': {'enabled': True, 'existingClaim': 'shared'}}), 'ReadWriteOnce'),
            (state({'controller': {'strategy': {'type': 'Recreate'}}}), 'updateStrategy'),
            (state({'controller': {'statefulSet': {'headlessService': {'enabled': False}}}}), 'existing Service'),
            (state({'controller': {'statefulSet': {'serviceName': 'test-app'}}}), 'client Service'),
            (state({'controller': {'statefulSet': {'updateStrategy': {'type': 'OnDelete', 'rollingUpdate': {'partition': 0}}}}}), 'OnDelete'),
            (state({'controller': {'statefulSet': {'updateStrategy': {'rollingUpdate': {'partition': -1}}}}}), 'partition'),
            (state({'controller': {'statefulSet': {'persistentVolumeClaimRetentionPolicy': {'whenScaled': 'Destroy'}}}}), 'whenScaled'),
            (state({'persistence': {'enabled': True}, 'extraVolumes': [{'name': 'data', 'emptyDir': {}}]}), 'duplicate volume'),
            (state({'controller': {'statefulSet': {'volumeClaimTemplates': [{'metadata': {'name': 'data'}, 'spec': {}}]}}}), 'spec'),
            (state({'controller': {'statefulSet': {'podManagementPolicy': 'Random'}}}), 'podManagementPolicy'),
            (state({'controller': {'statefulSet': {'persistentVolumeClaimRetentionPolicy': {'whenDeleted': 'Delete'}}}}), 'shared PVC'),
        ]
        for values, message in cases:
            with self.subTest(values=values), self.assertRaises(subprocess.CalledProcessError) as error:
                render(values)
            self.assertIn(message, error.exception.stderr)


if __name__ == '__main__':
    unittest.main()
