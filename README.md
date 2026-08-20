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
| alloy | ✅ | 1.11.1 | 1.11.1 (v1.18.1) |
| argo-cd |  | 10.3.2 | 10.4.0 (v3.5.1) |
| argo-rollouts | ✅ | 2.41.1 | 2.41.1 (v1.9.1) |
| argo-workflows |  | 1.0.24 | 2.0.1 (v4.1.1) |
| atlantis |  | 6.11.0 | 6.14.0 (v0.47.0) |
| external-dns | ✅ | 1.21.1 | 1.21.1 (0.21.0) |
| external-secrets | ✅ | 2.9.0 | 2.9.0 (v2.9.0) |
| grafana | ✅ | 10.5.15 | 10.5.15 (12.3.1) |
| istio | ✅ | 1.30.3 | 1.30.3 (1.30.3) |
| karpenter |  |  | 1.14.0 (1.14.0) |
| kite |  | 0.14.1 | 0.15.0 (v0.15.0) |
| loki |  | 7.2.0 | 7.3.0 (3.6.12) |
| metrics-server |  | 3.13.1 | 3.14.0 (0.9.0) |
| oauth2-proxy | ✅ | 10.7.0 | 10.7.0 (7.15.3) |
| prometheus-adapter | ✅ | 5.3.0 | 5.3.0 (v0.12.0) |
| prometheus-stack |  | 88.2.0 | 88.5.0 (v0.93.1) |
| raw |  |  | 0.2.5 (0.2.3) |
| vllm-stack |  | 6.11.0 | 0.1.12 |
<!--- END_VERSION --->

## download

```bash
python3 download.py
```
