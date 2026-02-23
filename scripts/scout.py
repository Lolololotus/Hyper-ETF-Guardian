import requests
import json
import os
from datetime import datetime, timedelta

def run_recon():
    # 실제 환경에서는 KRX 또는 금융 포털 API/스크래핑 로직이 가동됩니다.
    # 여기서는 무결성 테스트를 위한 AI 정찰 로직을 시뮬레이션합니다.
    target_path = 'data/upcoming_etf.json'
    
    # 1. 일주일간의 날짜 범위 설정 (시뮬레이션용)
    # today = datetime.now()
    # next_week = today + timedelta(days=7)
    
    # 2. 정찰 데이터 인양 (샘플 데이터 로직)
    # 실제로는 requests를 통해 최신 공시 데이터를 긁어옵니다.
    new_listings = [
        {"name": "ACE 미국 빅테크 TOP7", "ticker": "491230", "issuer": "한투", "listing_date": "2026-02-24"},
        {"name": "KODEX 미국 반도체 가디언", "ticker": "495560", "issuer": "삼성", "listing_date": "2026-02-26"}
    ]
    
    # 3. 데이터 무결성 검사 및 업데이트 (Merge Logic)
    existing_data = []
    if os.path.exists(target_path):
        try:
            with open(target_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except Exception as e:
            print(f"⚠️ Failed to read existing data: {e}")
    
    # 중복 제거 (ticker 기준)
    existing_tickers = {item['ticker'] for item in existing_data}
    added_count = 0
    for item in new_listings:
        if item['ticker'] not in existing_tickers:
            existing_data.append(item)
            added_count += 1
    
    # 디렉토리 생성 보장
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    
    # 파일 쓰기
    with open(target_path, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, indent=2, ensure_ascii=False)
    
    print(f"🚨 Recon Complete: {added_count} new units identified ({len(existing_data)} total).")

if __name__ == "__main__":
    run_recon()
