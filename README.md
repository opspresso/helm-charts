# helm-charts

## usage

```bash
helm repo add opspresso https://opspresso.github.io/helm-charts/

helm search repo opspresso
```

## helm repo

```bash
cat repos.txt | xargs -I {} bash -c 'helm repo add {}'
```

## helm search

```bash
helm repo update

helm search repo "argo/argo-cd" -o json | jq .
helm search repo "autoscaler/cluster-autoscaler" -o json | jq .
helm search repo "aws-ebs-csi-driver/aws-ebs-csi-driver" -o json | jq .
helm search repo "dashboard/kubernetes-dashboard" -o json | jq .
helm search repo "eks/aws-load-balancer-controller" -o json | jq .
```

## download

```bash
python3 download.py
```

## login public.ecr.aws

```bash
aws ecr-public get-login-password \
     --region us-east-1 | helm registry login \
     --username AWS \
     --password-stdin public.ecr.aws
```

## versions

<!--- BEGIN_VERSION --->
| NAME | CURRENT | LATEST |
| --- | --- | --- |
| argo-cd | 6.7.2 | 7.6.10 (v2.12.4) |
| argo-events |  | 2.4.8 (v1.9.2) |
| argo-rollouts |  | 2.37.7 (v1.7.2) |
| argo-workflows |  | 0.42.5 (v3.5.11) |
| atlantis | 4.23.4 | 5.7.0 (v0.30.0) |
| aws-ebs-csi-driver | 2.28.1 | 2.36.0 (1.36.0) |
| aws-efs-csi-driver |  | 3.0.8 (2.0.7) |
| aws-load-balancer-controller | 1.7.1 | 1.9.1 (v2.9.1) |
| aws-node-termination-handler | 0.22.0 | 0.24.1 (1.22.1) |
| awx-operator |  |  |
| cert-manager | v1.14.4 | v1.16.1 (v1.16.1) |
| cluster-autoscaler | 9.35.0 | 9.43.0 (1.31.0) |
| cluster-overprovisioner |  | 0.7.11 (3.9) |
| coroot |  | 0.15.9 (1.5.8) |
| cost-analyzer |  | 2.4.1 (2.4.1) |
| datadog |  | 3.74.3 (7) |
| external-secrets | 0.9.13 | 0.10.4 (v0.10.4) |
| ingress-nginx |  | 4.11.3 (1.11.3) |
| istiod | 1.19.4 | 1.23.2 (1.23.2) |
| karpenter |  | 1.0.6 (1.0.6) |
| keda |  | 2.15.1 (2.15.1) |
| kubernetes-dashboard | 7.1.2 | 7.8.0 |
| metrics-server | 3.12.0 | 3.12.2 (0.7.2) |
| raw |  | 0.2.5 (0.2.3) |
<!--- END_VERSION --->
