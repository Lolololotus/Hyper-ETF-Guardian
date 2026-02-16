import json
import os

def reset_portfolio():
    portfolio_path = 'data/user_portfolio.json'
    empty_portfolio = []
    
    # data 디렉토리가 없으면 생성
    if not os.path.exists('data'):
        os.makedirs('data')
        
    with open(portfolio_path, 'w', encoding='utf-8') as f:
        json.dump(empty_portfolio, f, indent=2, ensure_ascii=False)
    
    print(f"✅ {portfolio_path} has been initialized.")

if __name__ == "__main__":
    reset_portfolio()
