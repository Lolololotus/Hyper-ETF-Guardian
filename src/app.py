import streamlit as st
import pandas as pd
import json
import os
from monitor import calculate_loss_rate

# 페이지 설정
st.set_page_config(page_title="Hyper ETF Guardian", layout="wide", initial_sidebar_state="expanded")

# 커스텀 CSS (High-Density & Visual Authority 테마)
st.markdown("""
    <style>
    /* 배경 및 기본 텍스트 */
    .stApp {
        background-color: #0A0E14;
        color: #FFFFFF;
    }
    
    /* 헤더 스타일 */
    h1, h2, h3 {
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif;
        font-weight: 800;
    }
    
    .stSubheader {
        color: #B0B0B0 !important;
        font-weight: 400;
        letter-spacing: 1px;
    }

    /* 카드 스타일 */
    .etf-card {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .etf-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.5);
    }

    /* 네온 글로우 뱃지 */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        text-transform: uppercase;
        margin-bottom: 10px;
    }
    .badge-standby {
        background-color: rgba(255, 255, 51, 0.1);
        color: #FFFF33;
        border: 1px solid #FFFF33;
        box-shadow: 0 0 10px rgba(255, 255, 51, 0.3);
    }
    .badge-tracking {
        background-color: rgba(57, 255, 20, 0.1);
        color: #39FF14;
        border: 1px solid #39FF14;
        box-shadow: 0 0 10px rgba(57, 255, 20, 0.3);
    }
    .badge-danger {
        background-color: rgba(255, 49, 49, 0.1);
        color: #FF3131;
        border: 1px solid #FF3131;
        box-shadow: 0 0 10px rgba(255, 49, 49, 0.3);
    }

    /* 버튼 스타일 */
    .stButton>button {
        width: 100%;
        background-color: #39FF14 !important;
        color: #000000 !important;
        border: none !important;
        font-weight: bold !important;
        height: 45px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #32CD32 !important;
        transform: scale(1.02);
    }
    
    /* 비활성화/추적된 버튼 스타일 */
    .tracked-btn>button {
        background-color: #21262D !important;
        color: #8B949E !important;
        border: 1px solid #30363D !important;
    }
    
    /* 게이지바 커스텀 */
    .gauge-container {
        width: 100%;
        background-color: #21262D;
        border-radius: 5px;
        height: 12px;
        margin-top: 15px;
        position: relative;
    }
    .gauge-fill {
        height: 100%;
        border-radius: 5px;
        transition: width 0.5s ease-in-out;
    }
    
    .beta-banner {
        background-color: rgba(57, 255, 20, 0.05);
        border: 1px solid #39FF14;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 25px;
        color: #B0B0B0;
        font-size: 14px;
    }

    /* 사이드바 */
    [data-testid="stSidebar"] {
        background-color: #0D1117;
        border-right: 1px solid #30363D;
    }
    </style>
    """, unsafe_allow_html=True)

# 데이터 유틸리티
def load_json(path):
    if not os.path.exists(path): return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content: return []
            return json.loads(content)
    except Exception: return []

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# 데이터 로드
etf_list = load_json('data/etf_list.json')
upcoming_list = load_json('data/upcoming_etf.json')
portfolio = load_json('data/user_portfolio.json')

# 헬퍼 함수
def get_status_class(status):
    if status == "대기": return "badge-standby"
    if status == "추적 중": return "badge-tracking"
    return "badge-danger"

def render_gauge(loss_rate):
    # -10%면 100%, 0%면 0%로 표현 (방어선 근접도)
    percent = min(100, max(0, (abs(loss_rate) / 10.0) * 100))
    color = "#39FF14" if abs(loss_rate) < 5 else "#FFA500" if abs(loss_rate) < 8 else "#FF3131"
    return f"""
        <div style="font-size: 12px; color: #B0B0B0; margin-top: 10px;">📉 손절 방어선까지 남은 거리</div>
        <div class="gauge-container">
            <div class="gauge-fill" style="width: {percent}%; background-color: {color};"></div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 11px; margin-top:5px; color: #8B949E; font-weight: bold;">
            <span>SAFE (0%)</span>
            <span style="color: #FF3131;">-10% (CRITICAL)</span>
        </div>
    """

# --- Header ---
st.title("🛡️ Hyper ETF Guardian")
st.markdown("<p class='stSubheader'>No Prose, Just Precision.</p>", unsafe_allow_html=True)

# --- Navigation ---
tabs = st.tabs(["📊 Market Watch", "📅 Upcoming", "🚨 My Defense Line"])

with tabs[0]:
    st.markdown("### 실시간 시장 감시")
    cols = st.columns(3)
    for idx, item in enumerate(etf_list):
        is_tracked = any(p['symbol'] == item['symbol'] for p in portfolio)
        with cols[idx % 3]:
            st.markdown(f"""
                <div class="etf-card">
                    <div style="color: #8B949E; font-size: 12px;">{item['issuer']}</div>
                    <div style="font-size: 20px; font-weight: bold; margin-bottom: 8px;">{item['name']}</div>
                    <div style="font-size: 24px; color: #FFFFFF; margin-bottom: 4px;">{item['price_at_listing']:,} <span style="font-size: 14px; color: #8B949E;">KRW</span></div>
                </div>
            """, unsafe_allow_html=True)
            
            btn_label = "✓ TRACKED" if is_tracked else "TRACK"
            btn_key = f"track_{item['symbol']}"
            
            if is_tracked:
                st.markdown(f'<div class="tracked-btn">', unsafe_allow_html=True)
                st.button(btn_label, key=btn_key, disabled=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                if st.button(btn_label, key=btn_key):
                    portfolio.append({
                        "symbol": item['symbol'],
                        "name": item['name'],
                        "purchase_price": item['price_at_listing'],
                        "status": "추적 중"
                    })
                    save_json('data/user_portfolio.json', portfolio)
                    st.toast("✅ 트래킹이 시작되었습니다.")
                    st.rerun()

with tabs[1]:
    st.markdown("""
        <div class="beta-banner">
            <strong>[BETA 명세]</strong><br>
            현재 버전은 BETA 모드입니다. 추후 정식 업데이트를 통해 증권사 계좌와 직접 연동, 
            예약한 종목을 상장 즉시 '0.1초 자동 매수'하는 풀-오토 시스템을 제공할 예정입니다.
        </div>
    """, unsafe_allow_html=True)
    st.markdown("### 상장 대기 중 - 당신의 방어선을 예약하십시오.")
    cols = st.columns(3)
    for idx, item in enumerate(upcoming_list):
        is_reserved = any(p['symbol'] == item['ticker'] for p in portfolio)
        with cols[idx % 3]:
            st.markdown(f"""
                <div class="etf-card">
                    <div class='badge badge-standby'>STANDBY</div>
                    <div style="color: #8B949E; font-size: 12px;">{item['issuer']} | {item['theme']}</div>
                    <div style="font-size: 18px; font-weight: bold; margin-bottom: 8px;">{item['name']}</div>
                    <div style="font-size: 14px; color: #FFFF33;">📅 Listing: {item['listing_date']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            btn_label = "✓ RESERVED" if is_reserved else "PRE-CHECK"
            btn_key = f"pre_{item['ticker']}"
            
            if is_reserved:
                st.markdown(f'<div class="tracked-btn">', unsafe_allow_html=True)
                st.button(btn_label, key=btn_key, disabled=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                if st.button(btn_label, key=btn_key):
                    portfolio.append({
                        "symbol": item['ticker'],
                        "name": item['name'],
                        "purchase_price": 0,
                        "status": "대기",
                        "listing_date": item['listing_date']
                    })
                    save_json('data/user_portfolio.json', portfolio)
                    st.toast("📅 상장 예약이 완료되었습니다.")
                    st.rerun()

with tabs[2]:
    st.markdown("""
        <div style="margin-bottom: 20px;">
            <h3 style="margin-bottom: 5px;">실시간 감시 통제실</h3>
            <p style="color: #8B949E; font-size: 14px;">My Defense Line은 당신의 자산이 원칙(-10%)을 이탈하는지 실시간으로 감시하는 통제실입니다.</p>
        </div>
    """, unsafe_allow_html=True)
    
    if not portfolio:
        st.info("현재 감시 중인 종목이 없습니다.")
    else:
        for item in portfolio:
            # 가상 변동률 생성 (시뮬레이션용)
            purchase_price = item.get('purchase_price', 10000)
            if purchase_price == 0: purchase_price = 10000 # 대기 종목 가상 가격
            
            cur_price = purchase_price
            if item['status'] == '추적 중':
                 cur_price = purchase_price * 0.965 # -3.5% 상황 연출
            elif item['status'] == '위험':
                 cur_price = purchase_price * 0.88 # -12.0% 상황 연출
            
            loss_rate = calculate_loss_rate(cur_price, purchase_price)
            
            st.markdown(f"""
                <div class="etf-card">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <div class='badge {get_status_class(item['status'])}'>{item['status']}</div>
                            <div style="font-size: 20px; font-weight: bold;">{item['name']} <span style="font-size: 14px; color: #8B949E;">({item['symbol']})</span></div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 28px; font-weight: 900; color: {'#FF3131' if loss_rate <= -10 else '#39FF14'};">{loss_rate:+.1f}%</div>
                            <div style="font-size: 16px; font-weight: bold; color: #FFFFFF;">{int(cur_price):,} KRW</div>
                        </div>
                    </div>
                    {render_gauge(loss_rate) if item['status'] != '대기' else ''}
                </div>
            """, unsafe_allow_html=True)

# --- Sidebar (Admin & Charts) ---
with st.sidebar:
    st.image("https://via.placeholder.com/150x50/161B22/39FF14?text=HYPER+GUARD", use_container_width=True)
    st.header("🛠️ 제어 센터")
    
    with st.expander("시뮬레이션 제어"):
        if st.button("🔥 FORCE ALERT (DANGER)"):
            if portfolio:
                portfolio[0]['status'] = '위험'
                save_json('data/user_portfolio.json', portfolio)
                st.error("!!! EMERGENCY ALERT EMITTED !!!")
                st.rerun()

        if st.button("⚡ EXECUTE VIRTUAL BUY (Feb 18)"):
            mutated = False
            for p in portfolio:
                if p.get("status") == "대기" and p.get("listing_date") == "2026-02-18":
                    p["status"] = "추적 중"
                    p["purchase_price"] = 10000
                    mutated = True
            if mutated:
                save_json('data/user_portfolio.json', portfolio)
                st.success("2/18 종목 자동 매수 전환 완료")
                st.rerun()
        
        if st.button("♻️ RESET PORTFOLIO"):
            save_json('data/user_portfolio.json', [])
            st.warning("포트폴리오가 초기화되었습니다.")
            st.rerun()

    st.divider()
    st.header("📈 실시간 기술 차트")
    st.components.v1.html("""
        <div id="tradingview_chart"></div>
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.MediumWidget({"symbols": [["KOSPI:069500|1D"]],"chartOnly": false,"width": "100%","height": 300,"locale": "ko","colorTheme": "dark","container_id": "tradingview_chart"});
        </script>
    """, height=320)
    
    st.markdown("<br><br><div style='color: #484F58; font-size: 10px; text-align: center;'>Hyper ETF Guardian v1.0<br>Built in 12 Hours with AI-Workforce</div>", unsafe_allow_html=True)
