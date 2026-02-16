"""
Hyper ETF Guardian - Monitoring Module
Core Logic for Loss Rate Calculation
"""

def calculate_loss_rate(current_price, purchase_price):
    """
    수식 탑재: 알림 모듈의 핵심인 아래 수식을 로직에 반영
    Loss Rate = ((Current Price - Purchase Price) / Purchase Price) * 100
    """
    if purchase_price == 0:
        return 0
    
    loss_rate = ((current_price - purchase_price) / purchase_price) * 100
    return loss_rate

if __name__ == "__main__":
    # Test Logic
    print("Monitoring Module Initialized.")
