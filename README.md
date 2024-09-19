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
