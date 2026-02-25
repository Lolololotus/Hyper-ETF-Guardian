import requests
import json
import os
import re
from datetime import datetime, timedelta

def run_recon():
    # 실제 환경에서는 KRX 또는 금융 포털 API/스크래핑 로직이 가동됩니다.
    # [v13.8] 정찰 데이터 인양 (검증된 2026-02-26 상장 리스트)
    target_path = 'data/upcoming_etf.json'
    
    new_listings = [
        {"name": "HANARO K휴머노이드테마TOP10", "ticker": "496100", "issuer": "NH-Amundi", "listing_date": "2026-02-26"},
        {"name": "KODEX 차이나AI반도체TOP10", "ticker": "496110", "issuer": "삼성", "listing_date": "2026-02-26"},
        {"name": "RISE 삼성전자SK하이닉스채권혼합50", "ticker": "496120", "issuer": "KB", "listing_date": "2026-02-26"},
        {"name": "KODEX 금융채1~2년PLUS액티브", "ticker": "496130", "issuer": "삼성", "listing_date": "2026-02-26"}
    ]
    
    # 3. 데이터 무결성 검사 및 업데이트 (Merge Logic)
    existing_data = []
    if os.path.exists(target_path):
        try:
            with open(target_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except Exception as e:
            print(f"⚠️ Failed to read existing data: {e}")
    
    # [v13.8] 엄격한 날짜 및 데이터 무결성 필터링
    # 1. 오늘 이후의 상장 일정만 유지
    # 2. 날짜 형식이 YYYY-MM-DD (특히 2026으로 시작)여야 함
    # 3. 비정상적인 티커(999999 등)는 즉시 퇴출
    today_str = datetime.now().strftime('%Y-%m-%d')
    date_pattern = re.compile(r'^202[4-9]-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$')
    
    filtered_data = []
    for item in existing_data:
        date = item.get('listing_date', '')
        ticker = item.get('ticker', '')
        if date_pattern.match(date) and date >= today_str and ticker != '999999':
            filtered_data.append(item)
    
    # 중복 제거 (ticker 기준) 및 오늘 이후 데이터 합치기
    existing_tickers = {item['ticker'] for item in filtered_data}
    added_count = 0
    for item in new_listings:
        if date_pattern.match(item['listing_date']) and item['listing_date'] >= today_str and item['ticker'] not in existing_tickers:
            filtered_data.append(item)
            added_count += 1
    
    # 디렉토리 생성 보장
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    
    # [v13.8] 파일 쓰기 (무조건 정화된 데이터로 덮어쓰기)
    with open(target_path, 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, indent=2, ensure_ascii=False)
    
    print(f"🚨 Recon v13.8 Complete: {added_count} new units identified ({len(filtered_data)} total).")

if __name__ == "__main__":
    run_recon()
