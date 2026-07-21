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
aws ecr-public get-login-password --region us-east-1 | \
     helm registry login --username AWS --password-stdin public.ecr.aws
```

## versions

```bash
python3 bump.py
```

<!--- BEGIN_VERSION --->
| NAME | | CURRENT | LATEST |
| --- | - | --- | --- |
| argo-cd | ✅ | 10.1.4 | 10.1.4 (v3.4.5) |
| argo-events |  |  | 2.4.23 (v1.9.11) |
| argo-rollouts | ✅ | 2.41.1 | 2.41.1 (v1.9.1) |
| argo-workflows | ✅ | 1.0.20 | 1.0.20 (v4.0.7) |
| atlantis | ✅ | 6.9.3 | 6.9.3 (v0.46.0) |
| aws-ebs-csi-driver | ✅ | 2.62.0 | 2.62.0 (1.62.0) |
| aws-load-balancer-controller | ✅ | 3.4.2 | 3.4.2 (v3.4.2) |
| aws-node-termination-handler | ✅ | 0.27.6 | 0.27.6 (1.25.6) |
| cert-manager | ✅ | v1.21.0 | v1.21.0 (v1.21.0) |
| cluster-autoscaler | ✅ | 9.58.0 | 9.58.0 (1.35.0) |
| cost-analyzer |  |  | 2.9.7 (2.9.7) |
| external-dns | ✅ | 1.21.1 | 1.21.1 (0.21.0) |
| external-secrets | ✅ | 2.8.0 | 2.8.0 (v2.8.0) |
| grafana | ✅ | 10.5.15 | 10.5.15 (12.3.1) |
| istio | ✅ | 1.30.3 | 1.30.3 (1.30.3) |
| karpenter |  |  | 1.14.0 (1.14.0) |
| loki-stack | ✅ | 2.10.3 | 2.10.3 (v2.9.3) |
| metrics-server | ✅ | 3.13.1 | 3.13.1 (0.8.1) |
| oauth2-proxy | ✅ | 10.7.0 | 10.7.0 (7.15.3) |
| prometheus-stack | ✅ | 87.18.0 | 87.18.0 (v0.92.1) |
| promtail | ✅ | 6.17.1 | 6.17.1 (3.5.1) |
| raw |  |  | 0.2.5 (0.2.3) |
<!--- END_VERSION --->

## download

```bash
python3 download.py
```
