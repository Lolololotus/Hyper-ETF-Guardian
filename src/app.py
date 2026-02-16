import streamlit as st
import json, os, sys
import google.generativeai as genai
from datetime import datetime

# 1. [System] 레이아웃 및 폰트 절대 고정 (v8.4 Final)
st.set_page_config(page_title="Hyper ETF Guardian", layout="wide", initial_sidebar_state="collapsed")

# --- AI Intel Layer ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def get_ai_intel(prompt):
    if not GEMINI_API_KEY: return "[위험: 5.0 / 키 미설정]"
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(f"Financial analyst context. Max 10 words: {prompt}")
        return response.text.replace("\n", " ").strip() if response.text else "[대기 중]"
    except: return "[타임아웃]"

# 2. [UI/UX] 불사신 CSS (v8.4 대시보드 메트릭 및 블랙아웃)
st.markdown("""
    <style>
    /* 1. 불필요 요소 완전 숙청 */
    [data-testid="stSidebar"], [data-testid="stSidebarNav"], .stDeployButton { display: none !important; }
    
    /* 2. 전역 다크 락다운 */
    .stApp { background-color: #0A0E14 !important; color: #FFFFFF !important; }
    .block-container { padding: 2rem 4rem !important; max-width: 98% !important; }
    
    /* 3. [v8.4 핵심] 모든 버튼 시각적 암전 강제 고정 (Blackout Armor) */
    button[kind="secondary"], button[kind="primary"], .stButton>button, div[data-testid="stPopover"] button { 
        background-color: #0E1117 !important; 
        color: #39FF14 !important; 
        border: 1px solid #39FF14 !important; 
        font-weight: 900 !important; 
        width: 100% !important;
        height: 35px !important; 
        font-size: 11px !important;
        border-radius: 6px !important;
        transition: 0.2s !important;
        box-shadow: none !important;
    }
    button:hover { background-color: #39FF14 !important; color: #000 !important; box-shadow: 0 0 10px #39FF14 !important; }
    
    /* 4. 대시보드 메트릭 카드 */
    .metric-card { background:#161B22; border:1px solid #30363D; border-radius:12px; padding:20px; text-align:center; }
    .metric-label { color:#8B949E; font-size:10px; margin-bottom:8px; font-weight:700; text-transform:uppercase; }
    .metric-value { font-size:22px; font-weight:900; }

    /* 5. 손절 게이지 디자인 */
    .gauge-bg { width: 100%; background: #21262D; border-radius: 10px; height: 10px; margin: 10px 0; overflow: hidden; }
    .gauge-fill { height: 100%; border-radius: 10px; transition: width 0.8s ease; }
    
    /* 6. BETA 알림 박스 */
    .beta-notice { 
        background: rgba(57, 255, 20, 0.05); border: 1px solid #39FF14; 
        padding: 15px; border-radius: 8px; margin-bottom: 25px; 
        font-size: 12px; color: #39FF14; line-height: 1.6;
    }

    .v8-box { background-color: #161B22; border: 1px solid #30363D; border-radius: 12px; padding: 20px; margin-bottom: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
    .product-name { font-size: 15px !important; font-weight: 900; color: #FFFFFF; }
    .issuer-name { font-size: 13px !important; color: #8B949E; }
    .list-row { display: flex; align-items: center; height: 32px; gap: 10px; width: 100%; border-bottom: 1px solid #21262D; }

    div[data-testid="stPopoverContent"] {
        background-color: #161B22 !important;
        border: 1px solid #30363D !important;
        color: #FFFFFF !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. [Data] 데이터 엔진
P_FILE = 'data/user_portfolio.json'
ETF_FILE = 'data/etf_list.json'
UPC_FILE = 'data/upcoming_etf.json'

def load_data(p):
    if not os.path.exists(p): return []
    try:
        with open(p,'r',encoding='utf-8') as f: return json.load(f)
    except: return []

def save_p(d):
    with open(P_FILE,'w',encoding='utf-8') as f: json.dump(d, f, indent=2, ensure_ascii=False)

def handle_action(itm, action, qty=0):
    p = load_data(P_FILE)
    if action == "RESERVE":
        if not any(x['symbol'] == itm['ticker'] for x in p):
            p.append({"symbol": itm['ticker'], "name": itm['name'], "issuer": itm.get('issuer', 'HYPER'), "purchase_price": 10000, "current_price": 10000, "status": "예약 중", "qty": qty, "date": itm['listing_date']})
            st.toast("🚨 구매 예약이 확정되었습니다.")
    elif action == "CANCEL":
        target = itm.get('symbol') or itm.get('ticker')
        p = [x for x in p if x['symbol'] != target]
        st.toast("🗑️ 구매 예약이 취소되었습니다.")
    elif action == "TOGGLE":
        is_t = any(x['symbol'] == itm['symbol'] for x in p)
        if is_t: p = [x for x in p if x['symbol'] != itm['symbol']]
        else: p.append({"symbol": itm['symbol'], "name": itm['name'], "issuer": itm.get('issuer', 'HYPER'), "purchase_price": itm.get('price_at_listing', 10000), "current_price": itm.get('price_at_listing', 10000), "status": "라이브", "qty": 0})
    save_p(p)
    st.rerun()

# 4. [Header] 관제탑 헤더 및 메트릭 보드 복구
portfolio = load_data(P_FILE)
all_etfs = load_data(ETF_FILE)
upcs = sorted(load_data(UPC_FILE), key=lambda x: x.get('listing_date', '9999-12-31'))

st.markdown("<h2> 📊 하이퍼 ETF 가디언 <span style='font-size:12px;color:#39FF14;'>[v8.4 최종 무결성 빌드]</span></h2>", unsafe_allow_html=True)

# 메트릭 보드 인양
m1, m2, m3, m4 = st.columns(4)
avg_def = sum((x['current_price']-x['purchase_price'])/x['purchase_price']*100 for x in portfolio)/len(portfolio) if portfolio else 0
breach = sum(1 for x in portfolio if (x['current_price']-x['purchase_price'])/x.get('purchase_price', 1) <= -10)
upcoming_cnt = len(upcs)

m1.markdown(f'<div class="metric-card"><div class="metric-label">추적 자산</div><div class="metric-value" style="color:#39FF14;">{len(portfolio)} 유닛</div></div>', unsafe_allow_html=True)
m2.markdown(f'<div class="metric-card"><div class="metric-label">평균 방어력</div><div class="metric-value" style="color:{"#39FF14" if avg_def >= -5 else "#FF3131"};">{avg_def:+.2f}%</div></div>', unsafe_allow_html=True)
m3.markdown(f'<div class="metric-card"><div class="metric-label">방어선 돌파</div><div class="metric-value" style="color:{"#FF3131" if breach > 0 else "#39FF14"};">{breach} 유닛</div></div>', unsafe_allow_html=True)
m4.markdown(f'<div class="metric-card"><div class="metric-label">상장 예정</div><div class="metric-value" style="color:#FFD700;">{upcoming_cnt} 유닛</div></div>', unsafe_allow_html=True)

ai_rep = get_ai_intel(f"유닛: {len(portfolio)}. 메트릭 보드 및 가시성 락다운 완료.")
st.markdown(f'<div style="background:rgba(255,49,49,0.05); border:1px solid #FF3131; padding:20px; border-radius:10px; margin-top:20px; margin-bottom:35px; color:#FF3131; font-weight:900;">🚨 AI Intel: {ai_rep} </div>', unsafe_allow_html=True)

# 5. [Main] 관제 탭
tabs = st.tabs(["📊 시장 감시", "📅 상장 일정", "🚨 위험 통제"])

with tabs[0]: # Market Watch (6 themes x 10 items)
    st.markdown("<p style='font-size:11px;color:#8B949E;margin-bottom:15px;'>정렬 기준: 최근 수익률 높은 순</p>", unsafe_allow_html=True)
    themes = [{"n": "AI/반도체", "k": ["AI", "반도체"]}, {"n": "미국 빅테크", "k": ["미국", "빅테크"]}, {"n": "배당/밸류업", "k": ["배당", "밸류"]}, {"n": "국내 지수", "k": ["200", "코스피"]}, {"n": "글로벌 액티브", "k": ["글로벌"]}, {"n": "기술/소부장", "k": ["기술", "혁신"]}]
    row1, row2 = st.columns(3), st.columns(3)
    all_c = row1 + row2
    for idx, th in enumerate(themes):
        with all_c[idx]:
            st.markdown(f'<div class="v8-box"><div style="font-size:14px;font-weight:900;border-left:5px solid #39FF14;padding-left:10px;margin-bottom:15px;">{th["n"]} 전략</div>', unsafe_allow_html=True)
            tp = [e for e in all_etfs if any(k in e['name'] for k in th['k'])][:10]
            for r, itm in enumerate(tp):
                is_t = any(p['symbol'] == itm['symbol'] for p in portfolio)
                c_row = st.columns([7.8, 2.2])
                with c_row[0]: st.markdown(f"<div class='list-row'><span style='color:#8B949E;width:15px;font-size:10px;'>{r+1}</span><span class='issuer-name'>{itm.get('issuer', 'HYPER')}</span><span class='product-name' style='font-size:13px !important;'>{itm['name']}</span></div>", unsafe_allow_html=True)
                with c_row[1]: 
                    if st.button("해제" if is_t else "추적", key=f"tk_{idx}_{itm['symbol']}"): handle_action(itm, "TOGGLE")
            st.markdown("</div>", unsafe_allow_html=True)

with tabs[1]: # Upcoming
    st.markdown("<div class='beta-notice'><b>beta:</b> 추후 정식 업데이트를 통해 상장 즉시 <b>'0.1초 자동 매수'</b>하는 풀-오토 시스템을 제공합니다.</div>", unsafe_allow_html=True)
    cols = st.columns(4)
    for i, itm in enumerate(upcs):
        is_res = any(x['symbol'] == itm['ticker'] and x['status'] == "예약 중" for x in portfolio)
        with cols[i % 4]:
            st.markdown(f"<div style='background:#FFD700;color:#000;padding:2px 8px;border-radius:4px;font-weight:900;font-size:10px;width:fit-content;margin-bottom:5px;'>📅 {itm['listing_date']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='v8-box' style='padding:15px;border-left:5px solid #FFD700;'><span class='product-name'>{itm['name']}</span><br><small class='issuer-name'>{itm.get('issuer', 'HYPER')}</small></div>", unsafe_allow_html=True)
            if is_res:
                with st.popover("🚨 구매 예약 완료 ∨", use_container_width=True):
                    st.write("구매 예약을 취소하시겠습니까?")
                    if st.button("예, 예약을 취소합니다", key=f"can_{itm['ticker']}"): handle_action(itm, "CANCEL")
            else:
                with st.popover("상장 예약 ∨", use_container_width=True):
                    q = st.number_input("예약 수량", 1, 1000, 10, key=f"q_{itm['ticker']}")
                    if st.button("구매를 예약 하시겠습니까?", key=f"conf_{itm['ticker']}"): handle_action(itm, "RESERVE", q)

with tabs[2]: # Risk Control
    st.markdown("<div class='beta-notice' style='border-color:#FF3131;color:#FF3131;background:rgba(255,49,49,0.05);'><b>beta:</b> 원칙(-10.0%) 이탈 즉시 <b>'자동 매도'</b>하는 방어 시스템을 제공합니다.</div>", unsafe_allow_html=True)
    if not portfolio: st.info("추적 중인 자산이 없습니다.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 🛰️ 실시간 추적 자산")
            live_p = sorted([x for x in portfolio if x['status']=="라이브"], key=lambda x: (x['current_price']-x['purchase_price'])/x['purchase_price'])
            for p in live_p:
                l_r = ((p['current_price']-p['purchase_price'])/p['purchase_price']*100) if p['purchase_price']>0 else 0
                gauge_val = min(abs(min(l_r, 0)) * 10, 100)
                g_color = "#39FF14" if l_r >= 0 else ("#FFB800" if l_r > -5 else "#FF3131")
                st.markdown(f"""
                    <div class='v8-box' style='border-left: 5px solid {g_color}; padding: 15px;'>
                        <small>{p.get('issuer', 'HYPER')}</small><br>
                        <div style='display:flex;justify-content:space-between;align-items:center;'>
                            <b class='product-name'>{p['name']}</b>
                            <span style='color:{g_color}; font-weight:900; font-size:18px;'>{l_r:+.2f}%</span>
                        </div>
                        <div class='gauge-bg'><div class='gauge-fill' style='width:{gauge_val}%; background:{g_color}; box-shadow: 0 0 10px {g_color};'></div></div>
                    </div>
                """, unsafe_allow_html=True)
                if st.button("추적 해제", key=f"risk_del_{p['symbol']}"): handle_action(p, "TOGGLE")
        with c2:
            st.markdown("### 📅 상장 예정 예약")
            res_p = [x for x in portfolio if x['status']=="예약 중"]
            if not res_p: st.info("예약된 상장 예정 자산이 없습니다.")
            for p in res_p:
                st.markdown(f"""
                    <div class='v8-box' style='border-left: 5px solid #FFD700;'>
                        <small>{p.get('issuer', 'HYPER')} | {p.get('date', 'Unknown')}</small><br>
                        <b>{p['name']}</b><br>예약 수량: {p.get('qty', 0)}주
                    </div>
                """, unsafe_allow_html=True)
                with st.popover("🚨 구매 예약 완료 ∨", use_container_width=True):
                    st.write("정말 구매 예약을 취소 하시겠습니까?")
                    if st.button("예, 취소합니다", key=f"can_res_{p['symbol']}"): handle_action(p, "CANCEL")

st.markdown(f"<div style='text-align:center;margin-top:50px;font-size:10px;color:#484F58;'>Hyper ETF Guardian v8.4 | Mission Restored | 19h Miracle</div>", unsafe_allow_html=True)