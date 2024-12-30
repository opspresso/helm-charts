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
| NAME | | CURRENT | LATEST |
| --- | - | --- | --- |
| argo-cd | ✅ | 7.7.11 | 7.7.11 (v2.13.2) |
| argo-events |  |  | 2.4.9 (v1.9.3) |
| argo-rollouts |  |  | 2.38.0 (v1.7.2) |
| argo-workflows |  |  | 0.45.2 (v3.6.2) |
| atlantis |  | 4.23.4 | 5.12.0 (v0.32.0) |
| aws-ebs-csi-driver |  | 2.28.1 | 2.38.1 (1.38.1) |
| aws-efs-csi-driver |  |  | 3.1.4 (2.1.3) |
| aws-load-balancer-controller |  | 1.7.1 | 1.11.0 (v2.11.0) |
| aws-node-termination-handler |  | 0.22.0 | 0.25.1 (1.23.1) |
| awx-operator |  |  | 2.19.1 (2.19.1) |
| cert-manager |  | v1.14.4 | v1.16.2 (v1.16.2) |
| cluster-autoscaler |  | 9.35.0 | 9.44.0 (1.31.0) |
| cluster-overprovisioner |  |  | 0.7.11 (3.9) |
| coroot |  |  | 0.16.11 (1.6.8) |
| cost-analyzer |  |  | 2.5.1 (2.5.1) |
| datadog |  |  | 3.87.0 (7) |
| external-dns |  | 1.14.3 | 1.15.0 (0.15.0) |
| external-secrets |  | 0.9.13 | 0.12.1 (v0.12.1) |
| ingress-nginx |  |  | 4.11.3 (1.11.3) |
| istio |  | 1.19.4 | 1.24.2 (1.24.2) |
| karpenter |  |  | 1.1.1 (1.1.1) |
| keda |  |  | 2.16.1 (2.16.1) |
| dashboard |  | 7.1.2 | 7.10.0 |
| metrics-server |  | 3.12.0 | 3.12.2 (0.7.2) |
| raw |  |  | 0.2.5 (0.2.3) |
<!--- END_VERSION --->
