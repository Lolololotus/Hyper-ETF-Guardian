# 🛡️ Hyper ETF Guardian (하이퍼 ETF 가디언)

> **"Built in 12 Hours with AI-Workforce"**
> 
> 2월 17일 오전 제출용 ETF 손절 알림 MVP 웹사이트입니다. "No Prose, Just Precision." 원칙에 따라 군더더기 없는 데이터와 정확한 알림을 제공합니다.

## 🚀 Key Workflow (Sequence Diagram)

```mermaid
sequenceDiagram
    participant User as 👤 유저
    participant DB as 📅 Upcoming List
    participant App as 🛡️ Hyper Guardian
    participant Monitor as 🚨 Monitor Engine

    User->>DB: 상장 예정 ETF 확인 (Pre-Check)
    User->>App: 예약 버튼 클릭 (Reserved)
    App->>App: 상장일 09:01 가상 자동 매수 실행
    App->>Monitor: 감시 모드 전환 (Tracking)
    Monitor->>Monitor: 실시간 가격 변동률 계산
    Note over Monitor: Loss Rate <= -10% 포착
    Monitor->>User: 즉각 손절 알림 트리거 (Alert!)
```

## 핵심 원칙
- **"No Prose, Just Precision."** (군더더기 없는 데이터와 정확한 알림)

## 폴더 구조
- `data/`: ETF 리스트 및 관련 데이터 (JSON)
- `src/`: 알림 로직 및 모니터링 소스 코드
- `assets/`: 정적 리소스 및 문서

## 기술 스택
- Python / Node.js
- FinanceDataReader
- GitHub Actions (예정)
