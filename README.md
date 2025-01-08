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
helm search repo "eks/aws-load-balancer-controller" -o json | jq .
```

## login public.ecr.aws

```bash
aws ecr-public get-login-password \
     --region us-east-1 | helm registry login \
     --username AWS \
     --password-stdin public.ecr.aws
```

## versions

```bash
python3 bump.py
```

<!--- BEGIN_VERSION --->
| NAME | | CURRENT | LATEST |
| --- | - | --- | --- |
| argo-cd | ✅ | 7.7.14 | 7.7.14 (v2.13.3) |
| argo-events |  |  | 2.4.11 (v1.9.3) |
| argo-rollouts | ✅ | 2.38.2 | 2.38.2 (v1.7.2) |
| argo-workflows | ✅ | 0.45.3 | 0.45.3 (v3.6.2) |
| atlantis |  | 4.25.0 | 5.13.0 (v0.32.0) |
| aws-ebs-csi-driver | ✅ | 2.38.1 | 2.38.1 (1.38.1) |
| aws-efs-csi-driver |  |  | 3.1.4 (2.1.3) |
| aws-load-balancer-controller | ✅ | 1.11.0 | 1.11.0 (v2.11.0) |
| aws-node-termination-handler | ✅ | 0.25.1 | 0.25.1 (1.23.1) |
| cert-manager | ✅ | v1.16.2 | v1.16.2 (v1.16.2) |
| cluster-autoscaler | ✅ | 9.45.0 | 9.45.0 (1.32.0) |
| cost-analyzer |  |  | 2.5.2 (2.5.2) |
| datadog |  |  | 3.87.0 (7) |
| external-dns | ✅ | 1.15.0 | 1.15.0 (0.15.0) |
| external-secrets | ✅ | 0.12.1 | 0.12.1 (v0.12.1) |
| grafana | ✅ | 8.8.2 | 8.8.2 (11.4.0) |
| ingress-nginx |  | 4.11.3 | 4.12.0 (1.12.0) |
| istio | ✅ | 1.24.2 | 1.24.2 (1.24.2) |
| karpenter |  |  | 1.1.1 (1.1.1) |
| dashboard |  | 6.0.8 | 7.10.0 |
| loki-stack | ✅ | 2.10.2 | 2.10.2 (v2.9.3) |
| metrics-server | ✅ | 3.12.2 | 3.12.2 (0.7.2) |
| prometheus-stack | ✅ | 67.8.0 | 67.8.0 (v0.79.2) |
| promtail | ✅ | 6.16.6 | 6.16.6 (3.0.0) |
| raw |  |  | 0.2.5 (0.2.3) |
<!--- END_VERSION --->

## download

```bash
python3 download.py
```
