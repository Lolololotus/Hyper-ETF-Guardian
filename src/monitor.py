import logging
import os

# 로깅 설정
logging.basicConfig(
    filename='monitor.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def Trigger_Alert(symbol, loss_rate):
    """
    알림 발생 함수: 특정 조건 도달 시 마케팅/전략적 알림 송출
    """
    alert_msg = f"[알림: -10% 손실 제한 초과] 종목: {symbol} | 현재 손실률: {loss_rate:.2f}%"
    print(f"--- 외부 알림 트리거 활성화 ---")
    print(f"텔레그램: {alert_msg}")
    print(f"이메일: [하이퍼 가디언] {symbol} 종목 긴급 손절 권고")
    print(f"---------------------------------------")
    logging.error(alert_msg)

def calculate_loss_rate(current_price, purchase_price):
    """
    수식: Loss Rate = ((Current Price - Purchase Price) / Purchase Price) * 100
    """
    if purchase_price <= 0:
        return 0
    return ((current_price - purchase_price) / purchase_price) * 100

def monitor_etf(item, current_price):
    """
    종목 객체와 현재가를 받아 상태에 따른 감시 수행
    status: [대기], [추적 중], [위험]
    """
    symbol = item.get("symbol")
    status = item.get("status", "추적 중")
    purchase_price = item.get("purchase_price", 0)

    if status == "대기":
        logging.info(f"건너뜀 {symbol}: 상태가 [대기]임 (상장 전 또는 매수 전)")
        return status

    if purchase_price <= 0:
        logging.warning(f"Skipping {symbol}: Purchase price is 0")
        return status

    loss_rate = calculate_loss_rate(current_price, purchase_price)
    msg = f"감시 중 {symbol}: 현재가={current_price}, 매수가={purchase_price}, 손실률={loss_rate:.2f}%"
    logging.info(msg)
    
    # -10% 이하일 때 트리거 및 상태 변경
    if loss_rate <= -10:
        Trigger_Alert(symbol, loss_rate)
        item["status"] = "위험"
    else:
        item["status"] = "추적 중"
    
    return item["status"]

if __name__ == "__main__":
    # Test Scenario: '추적 중' 종목이 -12% 하락 상황
    test_item = {
        "symbol": "500120",
        "name": "KODEX 미국 테크 밸류업",
        "purchase_price": 10000,
        "status": "추적 중"
    }
    print(f"--- Simulation Start: {test_item['name']} ---")
    new_status = monitor_etf(test_item, 8800)
    print(f"Final Status: [{new_status}]")
