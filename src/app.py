import streamlit as st
import json
import os
from monitor import calculate_loss_rate

# 페이지 설정
st.set_page_config(page_title="Hyper ETF Guardian", layout="wide", initial_sidebar_state="expanded")

# 커스텀 CSS (High-Density & Visual Authority 테마)
st.markdown("""
    <style>
    .stApp { background-color: #0A0E14; color: #FFFFFF; }
    h1, h2, h3 { color: #FFFFFF !important; font-family: 'Inter', sans-serif; font-weight: 800; }
    .stSubheader { color: #B0B0B0 !important; font-weight: 400; letter-spacing: 1px; }

    .etf-card {
        background-color: #161B22; border: 1px solid #30363D; border-radius: 12px;
        padding: 24px; margin-bottom: 20px; transition: transform 0.2s, box-shadow 0.2s;
        display: flex; flex-direction: column; height: 100%;
    }
    .etf-card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.5); }

    .badge {
        display: inline-block; padding: 4px 12px; border-radius: 20px;
        font-size: 11px; font-weight: bold; text-transform: uppercase; margin-bottom: 15px;
    }
    .badge-standby { background-color: rgba(255, 255, 51, 0.1); color: #FFFF33; border: 1px solid #FFFF33; }
    .badge-tracking { background-color: rgba(57, 255, 20, 0.1); color: #39FF14; border: 1px solid #39FF14; }
    .badge-danger { background-color: rgba(255, 49, 49, 0.1); color: #FF3131; border: 1px solid #FF3131; }
    
    .beta-tag { background-color: #39FF14; color: #000000; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 900; vertical-align: middle; margin-left: 10px; }

    .stButton>button {
        width: 100%; background-color: #39FF14 !important; color: #000000 !important;
        border: none !important; font-weight: bold !important; height: 45px; margin-top: auto;
    }
    
    .tracked-btn button { background-color: #21262D !important; color: #8B949E !important; border: 1px solid #30363D !important; }
    .cancel-btn button { background-color: rgba(255, 49, 49, 0.1) !important; color: #FF3131 !important; border: 1px solid #FF3131 !important; }
    
    .gauge-container { width: 100%; background-color: #21262D; border-radius: 5px; height: 12px; margin-top: 15px; position: relative; }
    .gauge-fill { height: 100%; border-radius: 5px; transition: width 0.5s ease-in-out; }
    
    .vision-banner { background-color: rgba(57, 255, 20, 0.03); border-left: 4px solid #39FF14; padding: 15px; border-radius: 4px; margin-bottom: 25px; color: #B0B0B0; font-size: 13px; line-height: 1.6; }
    [data-testid="stSidebar"] { background-color: #0D1117; border-right: 1px solid #30363D; }
    </style>
    """, unsafe_allow_html=True)

# 데이터 유틸리티
def load_json(path):
    if not os.path.exists(path): return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            return json.loads(content) if content else []
    except Exception: return []

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_status_class(status):
    if status == "대기": return "badge-standby"
    if status == "추적 중": return "badge-tracking"
    return "badge-danger"

etf_list = load_json('data/etf_list.json')
upcoming_list = load_json('data/upcoming_etf.json')
portfolio = load_json('data/user_portfolio.json')

def render_gauge(loss_rate):
    percent = min(100, max(0, (abs(loss_rate) / 10.0) * 100))
    color = "#39FF14" if abs(loss_rate) < 5 else "#FFA500" if abs(loss_rate) < 8 else "#FF3131"
    # 마크다운 오인식을 방지하기 위해 개행 및 인덴트가 없는 단일 라인 문자열로 반환
    html = f'<div style="font-size: 11px; color: #8B949E; margin-top: 15px;">📉 손절 방어선까지 남은 거리</div>'
    html += f'<div class="gauge-container"><div class="gauge-fill" style="width: {percent}%; background-color: {color};"></div></div>'
    html += f'<div style="display: flex; justify-content: space-between; font-size: 10px; margin-top:5px; color: #484F58; font-weight: bold;">'
    html += f'<span>SAFE (0%)</span><span style="color: #FF3131;">-10% (CRITICAL)</span></div>'
    return html

# --- Header ---
st.markdown(f"<h1>🛡️ Hyper ETF Guardian <span class='beta-tag'>BETA</span></h1>", unsafe_allow_html=True)
st.markdown("<p class='stSubheader'>No Prose, Just Precision.</p>", unsafe_allow_html=True)

# --- Navigation ---
tabs = st.tabs(["📊 Market Watch", "📅 Upcoming", "🚨 My Defense Line"])

with tabs[0]:
    st.markdown("### 실시간 시장 감시")
    cols = st.columns(3)
    for idx, item in enumerate(etf_list):
        existing_item = next((p for p in portfolio if p['symbol'] == item['symbol']), None)
        with cols[idx % 3]:
            # 카드 구조 무결성을 위해 단일 f-string 사용 (태그 쪼개지 않음)
            card_html = f'<div class="etf-card"><div style="color: #8B949E; font-size: 11px;">{item["issuer"]}</div>'
            card_html += f'<div style="font-size: 19px; font-weight: bold; margin-bottom: 15px;">{item["name"]}</div>'
            card_html += f'<div style="font-size: 24px; color: #FFFFFF; margin-bottom: 20px;">{item["price_at_listing"]:,} <span style="font-size: 13px; color: #8B949E;">KRW</span></div>'
            st.markdown(card_html, unsafe_allow_html=True)
            
            if existing_item:
                st.markdown('<div class="tracked-btn">', unsafe_allow_html=True)
                if st.button("✓ TRACKED", key=f"tracked_btn_{item['symbol']}"):
                    portfolio = [p for p in portfolio if p['symbol'] != item['symbol']]
                    save_json('data/user_portfolio.json', portfolio)
                    st.toast(f"❌ {item['name']} 추적 해제")
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                if st.button("TRACK", key=f"track_btn_{item['symbol']}"):
                    portfolio.append({"symbol": item['symbol'], "name": item['name'], "purchase_price": item['price_at_listing'], "status": "추적 중"})
                    save_json('data/user_portfolio.json', portfolio)
                    st.toast("✅ 트래킹 시작")
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True) # Closes the etf-card

with tabs[1]:
    st.markdown("""<div class="vision-banner"><strong>[BETA Vision]</strong> 현재 버전은 BETA 모드입니다. 추후 정식 업데이트를 통해 증권사 계좌와 직접 연동, 예약한 종목을 상장 즉시 <strong>'0.1초 자동 매수'</strong>하는 풀-오토 시스템을 제공할 예정입니다.</div>""", unsafe_allow_html=True)
    st.markdown("### 상장 대기 중 - 당신의 방어선을 예약하십시오.")
    cols = st.columns(3)
    for idx, item in enumerate(upcoming_list):
        is_reserved = any(p['symbol'] == item['ticker'] for p in portfolio)
        confirm_key = f"confirm_cancel_{item['ticker']}"
        with cols[idx % 3]:
            # 카드 구조 무결성 확보
            u_card = f'<div class="etf-card"><div class="badge badge-standby">STANDBY</div>'
            u_card += f'<div style="color: #8B949E; font-size: 11px;">{item["issuer"]} | {item["theme"]}</div>'
            u_card += f'<div style="font-size: 18px; font-weight: bold; margin-bottom: 10px;">{item["name"]}</div>'
            u_card += f'<div style="font-size: 13px; color: #FFFF33; margin-bottom: 15px;">📅 Listing: {item["listing_date"]}</div>'
            st.markdown(u_card, unsafe_allow_html=True)
            
            if is_reserved:
                if st.session_state.get(confirm_key, False):
                    st.info("⚠️ 예약을 취소하시겠습니까?")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("예약 취소 확정", key=f"btn_confirm_{item['ticker']}"):
                            portfolio = [p for p in portfolio if p['symbol'] != item['ticker']]
                            save_json('data/user_portfolio.json', portfolio)
                            st.session_state[confirm_key] = False
                            st.toast("❌ 예약 취소 완료")
                            st.rerun()
                    with c2:
                        if st.button("유지", key=f"btn_keep_{item['ticker']}"):
                            st.session_state[confirm_key] = False
                            st.rerun()
                else:
                    st.markdown('<div class="tracked-btn">', unsafe_allow_html=True)
                    if st.button("✓ RESERVED (Click to Cancel)", key=f"reserved_btn_{item['ticker']}"):
                        st.session_state[confirm_key] = True
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                if st.button("PRE-CHECK", key=f"pre_btn_{item['ticker']}"):
                    portfolio.append({"symbol": item['ticker'], "name": item['name'], "purchase_price": 0, "status": "대기", "listing_date": item['listing_date']})
                    save_json('data/user_portfolio.json', portfolio)
                    st.toast("📅 상장 예약 완료")
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True) # Closes the etf-card

with tabs[2]:
    st.markdown("""<div class="vision-banner"><strong>[BETA Vision]</strong> 현재 버전은 BETA 모드입니다. 추후 정식 업데이트를 통해 증권사 계좌와 직접 연동, 당신의 자산이 원칙(-10.0%)을 이탈한 즉시 <strong>'자동 매도'</strong>하는 Full-Auto 방어 시스템을 제공할 예정입니다.</div>""", unsafe_allow_html=True)
    st.markdown("""<div style="margin-bottom: 25px;"><h3 style="margin-bottom: 5px;">실시간 감시 통제실</h3><p style="color: #8B949E; font-size: 13px;">My Defense Line은 당신의 자산을 실시간으로 수호합니다.</p></div>""", unsafe_allow_html=True)
    if not portfolio:
        st.info("현재 감시 중인 종목이 없습니다.")
    else:
        for item in portfolio:
            purchase_price = item.get('purchase_price', 10000)
            if purchase_price == 0: purchase_price = 10000
            cur_price = purchase_price * (0.965 if item['status'] == '추적 중' else 0.88 if item['status'] == '위험' else 1.0)
            loss_rate = calculate_loss_rate(cur_price, purchase_price)
            # 인덴트 없이 단일 라인으로 카드 생성하여 ghost </div> 태그 완벽 방어
            m_card = f'<div class="etf-card"><div style="display: flex; justify-content: space-between; align-items: start;">'
            m_card += f'<div><div class="badge {get_status_class(item["status"])}">{item["status"]}</div>'
            m_card += f'<div style="font-size: 19px; font-weight: bold; color: #FFFFFF;">{item["name"]} <span style="font-size: 13px; color: #484F58;">({item["symbol"]})</span></div></div>'
            m_card += f'<div style="text-align: right;"><div style="font-size: 30px; font-weight: 900; color: {"#FF3131" if loss_rate <= -10 else "#39FF14"}; line-height: 1;">{loss_rate:+.1f}%</div>'
            m_card += f'<div style="font-size: 15px; font-weight: bold; color: #FFFFFF; margin-top: 5px;">{int(cur_price):,} KRW</div></div></div>'
            m_card += f'{render_gauge(loss_rate) if item["status"] != "대기" else ""}</div>'
            st.markdown(m_card, unsafe_allow_html=True)

with st.sidebar:
    st.image("https://via.placeholder.com/150x50/161B22/39FF14?text=HYPER+GUARD", use_container_width=True)
    st.header("🛠️ 제어 센터")
    with st.expander("시뮬레이션 제어"):
        if st.button("🔥 FORCE ALERT (DANGER)"):
            if portfolio: portfolio[0]['status'] = '위험'; save_json('data/user_portfolio.json', portfolio); st.rerun()
        if st.button("⚡ EXECUTE VIRTUAL BUY (Feb 18)"):
            mutated = False
            for p in portfolio:
                if p.get("status") == "대기" and p.get("listing_date") == "2026-02-18":
                    p["status"] = "추적 중"; p["purchase_price"] = 10000; mutated = True
            if mutated: save_json('data/user_portfolio.json', portfolio); st.rerun()
        if st.button("♻️ RESET PORTFOLIO"): save_json('data/user_portfolio.json', []); st.rerun()
    st.divider()
    st.header("📈 실시간 기술 차트")
    st.components.v1.html("""<div id="chart"></div><script src="https://s3.tradingview.com/tv.js"></script><script>new TradingView.MediumWidget({"symbols": [["KOSPI:069500|1D"]],"chartOnly": false,"width": "100%","height": 300,"locale": "ko","colorTheme": "dark","container_id": "chart"});</script>""", height=320)
    st.markdown("<div style='color: #484F58; font-size: 10px; text-align: center; margin-top: 20px;'>Hyper ETF Guardian v1.0<br>Built in 12 Hours with AI-Workforce</div>", unsafe_allow_html=True)
