"""
Hyper ETF Guardian - Monitoring Module
Core Logic for Loss Rate Calculation and Alert Trigger
"""

def Trigger_Alert(symbol, loss_rate):
    """
    알림 발생 함수: 특정 조건 도달 시 마케팅/전략적 알림 송출
    """
    print(f"[ALERT TRIGGERED] 종목: {symbol} | 손실률: {loss_rate:.2f}%")
    # 향후 Push API 연동 지점

def calculate_loss_rate(current_price, purchase_price):
    """
    수식: Loss Rate = ((Current Price - Purchase Price) / Purchase Price) * 100
    """
    if purchase_price == 0:
        return 0
    return ((current_price - purchase_price) / purchase_price) * 100

def monitor_etf(symbol, current_price, purchase_price):
    """
    가격 변동을 감시하고 -10% 도달 시 Trigger_Alert 호출
    """
    loss_rate = calculate_loss_rate(current_price, purchase_price)
    
    # -10% 이하일 때 트리거 실행
    if loss_rate <= -10:
        Trigger_Alert(symbol, loss_rate)
    
    return loss_rate

if __name__ == "__main__":
    # Test Scenario: 10% 하락 상황 가정
    sample_symbol = "KODEX 200"
    p_price = 10000
    c_price = 8900 # 11% 하락
    
    print(f"[{sample_symbol}] 모니터링 시작...")
    monitor_etf(sample_symbol, c_price, p_price)
