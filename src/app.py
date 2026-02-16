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
@st.cache_data
def load_etf_data():
    with open('data/etf_list.json', 'r', encoding='utf-8') as f:
        return json.load(f)

etf_data = load_etf_data()
df = pd.DataFrame(etf_data)

# 로고 및 타이틀
st.title("🛡️ Hyper ETF Guardian")
st.subheader("No Prose, Just Precision.")

col1, col2 = st.columns([1, 1])

with col1:
    st.header("📊 Market Watch")
    # 테이블 출력 및 구매 버튼 시뮬레이션
    for index, row in df.iterrows():
        c1, c2, c3 = st.columns([2, 2, 1])
        c1.write(f"**{row['name']}** ({row['symbol']})")
        c2.write(f"{row['price_at_listing']:,} KRW")
        if c3.button("TRACK", key=f"btn_{row['symbol']}"):
             st.success(f"{row['name']} 감시 시작!")
             # 포트폴리오 저장 로직 (MVP)
             portfolio = {"symbol": row['symbol'], "purchase_price": row['price_at_listing']}
             with open('data/user_portfolio.json', 'w') as f:
                 json.dump([portfolio], f)

with col2:
    st.header("📈 Technical Chart")
    # TradingView Widget (HTML)
    st.components.v1.html("""
        <!-- TradingView Widget BEGIN -->
        <div class="tradingview-widget-container">
          <div id="tradingview_chart"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
          <script type="text/javascript">
          new TradingView.MediumWidget(
          {
          "symbols": [
            [
              "KOSPI:069500|1D"
            ]
          ],
          "chartOnly": false,
          "width": "100%",
          "height": 400,
          "locale": "ko",
          "colorTheme": "dark",
          "gridLineColor": "rgba(42, 46, 57, 0)",
          "fontColor": "#787B86",
          "isTransparent": false,
          "autosize": true,
          "showFloatingTooltip": true,
          "showVolume": false,
          "scalePosition": "no",
          "scaleMode": "Normal",
          "fontFamily": "Trebuchet MS, sans-serif",
          "noTimeScale": false,
          "chartType": "Area",
          "lineColor": "#2962FF",
          "bottomColor": "rgba(41, 98, 255, 0)",
          "topColor": "rgba(41, 98, 255, 0.3)",
          "container_id": "tradingview_chart"
        }
          );
          </script>
        </div>
        <!-- TradingView Widget END -->
    """, height=450)

st.divider()

# My Defense Line & 시뮬레이션
st.header("🚨 My Defense Line")
if st.button("🔥 FORCE ALERT TEST", type="primary"):
    st.error("!!! [EMERGENCY] 손절가 도달 알림 시뮬레이션 작동 !!!")
    st.write("Telegram: [Hyper Guardian] KODEX 200 손절가(-10.5%) 도달. 즉시 대응 요망.")
    st.balloons()
