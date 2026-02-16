import streamlit as st
import pandas as pd
import json
import os
from monitor import calculate_loss_rate

# 페이지 설정
st.set_page_config(page_title="Hyper ETF Guardian", layout="wide", initial_sidebar_state="collapsed")

# 커스텀 CSS (High-Density Discipline 테마)
st.markdown("""
    <style>
    .main {
        background-color: #121212;
        color: #e0e0e0;
    }
    .stButton>button {
        background-color: #00ff41;
        color: black;
        border-radius: 5px;
        font-weight: bold;
    }
    .alert-button>button {
        background-color: #ff0000 !important;
        color: white !important;
    }
    .stTable {
        background-color: #1e1e1e;
    }
    h1, h2, h3 {
        color: #00ff41;
    }
    </style>
    """, unsafe_allow_html=True)

# 데이터 로드
def load_json(path):
    if not os.path.exists(path): return []
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

etf_data = load_json('data/etf_list.json')
upcoming_data = load_json('data/upcoming_etf.json')
portfolio_data = load_json('data/user_portfolio.json')

# 로고 및 타이틀
st.title("🛡️ Hyper ETF Guardian")
st.subheader("No Prose, Just Precision.")

tabs = st.tabs(["📊 Market Watch", "📅 Upcoming", "🚨 My Defense Line"])

with tabs[0]:
    st.header("실시간 시장 감시")
    df = pd.DataFrame(etf_data)
    for index, row in df.iterrows():
        c1, c2, c3 = st.columns([3, 2, 1])
        c1.write(f"**{row['name']}** ({row['symbol']})")
        c2.write(f"{row['price_at_listing']:,} KRW")
        if c3.button("TRACK", key=f"market_{row['symbol']}"):
             # 즉시 추적 시작
             new_entry = {
                 "symbol": row['symbol'], 
                 "name": row['name'],
                 "purchase_price": row['price_at_listing'],
                 "status": "추적 중"
             }
             portfolio_data.append(new_entry)
             save_json('data/user_portfolio.json', portfolio_data)
             st.success(f"{row['name']} 추적 리스트 편입.")

with tabs[1]:
    st.header("상장 대기 중 - 당신의 방어선을 예약하십시오.")
    up_df = pd.DataFrame(upcoming_data)
    for index, row in up_df.iterrows():
        c1, c2, c3 = st.columns([3, 2, 1])
        c1.write(f"**{row['name']}** ({row['issuer']})")
        c2.write(f"📅 상장 예정일: {row['listing_date']}")
        if c3.button("PRE-CHECK", key=f"pre_{row['ticker']}"):
             # 예약 상태로 저장
             new_entry = {
                 "symbol": row['ticker'],
                 "name": row['name'],
                 "purchase_price": 0, # 상장 시 결정
                 "status": "대기",
                 "listing_date": row['listing_date']
             }
             portfolio_data.append(new_entry)
             save_json('data/user_portfolio.json', portfolio_data)
             st.info(f"{row['name']} 상장 예약 완료.")

with tabs[2]:
    st.header("실시간 감시 중 - 원칙 이탈 시 즉각 보고합니다.")
    if portfolio_data:
        p_df = pd.DataFrame(portfolio_data)
        st.table(p_df)
    else:
        st.write("감시 중인 포트폴리오가 없습니다.")

    st.divider()
    st.subheader("🛠️ Admin Simulation")
    col_sim1, col_sim2 = st.columns(2)
    
    if col_sim1.button("🔥 FORCE ALERT TEST"):
        st.error("!!! [EMERGENCY] 손절가 도달 알림 시뮬레이션 작동 !!!")
        st.balloons()
    
    if col_sim2.button("⚡ EXECUTE VIRTUAL BUY (Feb 18)"):
        # 2월 18일 상장 예정 종목을 '대기'에서 '추적 중'으로 전환
        mutated = False
        for item in portfolio_data:
            if item.get("status") == "대기" and item.get("listing_date") == "2026-02-18":
                item["status"] = "추적 중"
                item["purchase_price"] = 10000 # 가상 시초가
                mutated = True
        if mutated:
            save_json('data/user_portfolio.json', portfolio_data)
            st.success("2/18 상장 종목이 '추적 중' 상태로 자동 전환되었습니다. (시초가 10,000원 설정)")
            st.rerun()
        else:
            st.warning("예약된 2/18 종목이 없습니다.")

# Technical Chart Section (Sidebar or Bottom)
with st.sidebar:
    st.header("📈 Chart View")
    st.components.v1.html("""
        <div id="tradingview_chart"></div>
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.MediumWidget({"symbols": [["KOSPI:069500|1D"]],"chartOnly": false,"width": "100%","height": 400,"locale": "ko","colorTheme": "dark","container_id": "tradingview_chart"});
        </script>
    """, height=420)
