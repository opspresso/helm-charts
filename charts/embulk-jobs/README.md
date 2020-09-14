# embulk-jobs

## usage

```bash
helm repo add opspresso https://opspresso.github.io/helm-charts/
helm repo update && helm search repo opspresso

helm template capri-migration opspresso/embulk-jobs -f values.yaml

helm delete capri-migration && \
helm install capri-migration opspresso/embulk-jobs -f values.yaml

helm delete capri-migration
```
