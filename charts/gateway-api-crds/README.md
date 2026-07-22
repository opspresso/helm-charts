# Gateway API CRDs Helm Chart

Kubernetes Gateway API CRD를 설치하는 Helm 차트입니다.

## 개요

이 차트는 [kubernetes-sigs/gateway-api](https://github.com/kubernetes-sigs/gateway-api) v1.6.1의 Standard Channel CRD를 설치합니다.

### 포함된 CRD

| CRD | 설명 |
|-----|------|
| `GatewayClass` | Gateway 구현체 정의 |
| `Gateway` | L4/L7 로드밸런서 설정 |
| `HTTPRoute` | HTTP 라우팅 규칙 |
| `GRPCRoute` | gRPC 라우팅 규칙 |
| `ReferenceGrant` | 크로스 네임스페이스 참조 권한 |
| `BackendTLSPolicy` | 백엔드 TLS 설정 |

## 버전 업그레이드

새 버전의 Gateway API가 릴리스되면:

1. [Gateway API Releases](https://github.com/kubernetes-sigs/gateway-api/releases) 확인
2. CRD 다운로드:
```bash
curl -sL https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.6.1/standard-install.yaml \
  -o charts/gateway-api-crds/templates/crds.yaml
```
3. `Chart.yaml`의 `version`과 `appVersion` 업데이트
4. PR 생성 및 ECR에 푸시

## 주의사항

- CRD는 클러스터 스코프 리소스입니다
- CRD 삭제 시 해당 타입의 모든 리소스가 삭제됩니다
- 다운그레이드는 권장하지 않습니다
