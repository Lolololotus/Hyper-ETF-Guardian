import streamlit as st
import json
import os
import sys
import google.generativeai as genai
from datetime import datetime

# 1. [System] 레이아웃 절대 고정
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
        response = model.generate_content(f"Expert financial analyst. Response max 10 words: {prompt}")
        return response.text.replace("\n", " ").strip() if response.text else "[대기 중]"
    except: return "[타임아웃]"

# 2. [UI/UX] 불사신 CSS (테마 무시 강제 적용)
st.markdown("""
    <style>
    /* 사이드바 및 불필요 요소 완전 박멸 */
    [data-testid="stSidebar"], [data-testid="stSidebarNav"], .stDeployButton { display: none !important; }
    
    /* 글로벌 다크 락다운 */
    .stApp { background-color: #0A0E14 !important; color: #FFFFFF !important; }
    .block-container { padding: 2rem 3rem !important; max-width: 98% !important; }
    
    /* [v7.3 핵심] 모든 버튼의 시각적 봉쇄 */
    .stButton>button { 
        background-color: #1E2329 !important; 
        color: #FFFFFF !important; 
        border: 1px solid #484F58 !important; 
        font-weight: 900 !important; 
        width: 100% !important; 
        height: 32px !important; 
        font-size: 11px !important;
        box-shadow: none !important;
        border-radius: 6px !important;
    }
    .stButton>button:hover { border-color: #39FF14 !important; color: #39FF14 !important; background-color: #30363D !important; }
    
    /* 예약 확정 버튼 특화 (가독성 극대화) */
    div[data-testid="stPopover"] button { 
        background-color: #39FF14 !important; 
        color: #000000 !important; 
        font-weight: 900 !important;
    }

    .v7-box { background-color: #161B22; border: 1px solid #30363D; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 8px 16px rgba(0,0,0,0.5); }
    .v7-title { font-size: 14px; font-weight: 900; color: #FFFFFF; border-left: 5px solid #39FF14; padding-left: 10px; margin-bottom: 15px; text-transform: uppercase; }
    .list-row { display: flex; align-items: center; height: 32px; gap: 10px; width: 100%; border-bottom: 1px solid #21262D; }
    
    /* 위험 통제 탭 레이아웃 보강 */
    .risk-row-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #161B22;
        border: 1px solid #30363D;
        padding: 15px 25px;
        border-radius: 12px;
        margin-bottom: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# 3. [Data] 데이터 정제 및 인양
def l_j(p):
    if not os.path.exists(p): return []
    try:
        with open(p,'r',encoding='utf-8') as f: return json.load(f)
    except: return []

def s_j(p, d):
    with open(p,'w',encoding='utf-8') as f: json.dump(d, f, indent=2, ensure_ascii=False)

p_file = 'data/user_portfolio.json'
portfolio = l_j(p_file)
etfs = l_j('data/etf_list.json')
upcs = sorted(l_j('data/upcoming_etf.json'), key=lambda x: x.get('listing_date', '9999-12-31'))

# 4. [Logic] 통합 액션 제어 센터
def handle_action(itm, action, qty=0):
    global portfolio
    if action == "TOGGLE_TRACK":
        is_t = any(p['symbol'] == itm['symbol'] for p in portfolio)
        if is_t: portfolio = [p for p in portfolio if p['symbol'] != itm['symbol']]
        else: portfolio.append({"symbol": itm['symbol'], "name": itm['name'], "issuer": itm['issuer'], "purchase_price": itm['price_at_listing'], "current_price": itm['price_at_listing'], "qty": 0, "status": "라이브"})
    elif action == "RESERVE":
        if not any(p['symbol'] == itm['ticker'] for p in portfolio):
            portfolio.append({"symbol": itm['ticker'], "name": itm['name'], "issuer": itm['issuer'], "purchase_price": 10000, "current_price": 10000, "qty": qty, "status": "예약 중", "listing_date": itm['listing_date']})
            st.toast(f"🚨 {itm['name']} {qty}주 예약 성공.")
    
    s_j(p_file, portfolio)
    st.rerun()

# 5. [Header] 관제탑 헤더 및 메트릭
st.markdown("<h2> 📊 하이퍼 ETF 가디언 <span style='font-size:12px;color:#39FF14;'>[v7.3 최종 무결성 빌드]</span></h2>", unsafe_allow_html=True)
ai_rep = get_ai_intel(f"유닛: {len(portfolio)}. 시각적 무결성 및 예약 시스템 최종 복구.")
st.markdown(f'<div style="background:rgba(255,49,49,0.05); border:1px solid #FF3131; padding:15px; border-radius:10px; margin-bottom:25px; color:#FF3131; font-weight:900;">🚨 AI Intel: {ai_rep} </div>', unsafe_allow_html=True)

# 6. [Main] 탭 기반 지휘 시스템
tabs = st.tabs(["📊 시장 감시", "📅 상장 일정", "🚨 위험 통제"])

with tabs[0]: # Market Watch (2x3 Grid)
    themes = [{"n": "AI/반도체", "k": ["AI", "반도체"]}, {"n": "미국 빅테크", "k": ["미국", "빅테크"]}, {"n": "배당/밸류업", "k": ["배당", "밸류"]}, {"n": "국내 지수", "k": ["200", "코스피"]}, {"n": "글로벌 액티브", "k": ["글로벌"]}, {"n": "기술/소부장", "k": ["기술", "혁신"]}]
    row1, row2 = st.columns(3), st.columns(3)
    all_c = row1 + row2
    for idx, th in enumerate(themes):
        with all_c[idx]:
            st.markdown(f'<div class="v7-box"><div class="v7-title">{th["n"]} 전략</div>', unsafe_allow_html=True)
            # 60 Unit Influx Logic (섹션당 10개 강제 채움)
            tp = [e for e in etfs if any(k in e['name'] for k in th['k'])]
            seen = {e['symbol'] for e in tp}
            for e in etfs:
                if len(tp) >= 10: break
                if e['symbol'] not in seen: tp.append(e); seen.add(e['symbol'])
            for r, itm in enumerate(tp[:10]):
                is_t = any(p['symbol'] == itm['symbol'] for p in portfolio)
                c_row = st.columns([7.2, 2.8])
                with c_row[0]:
                    st.markdown(f'<div class="list-row"><span style="color:#8B949E;width:15px;font-size:10px;">{r+1}</span><span style="color:#8B949E;font-size:10px;width:75px;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;">{itm["issuer"]}</span><span style="font-size:11px;font-weight:700;flex-grow:1;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;">{itm["name"]}</span></div>', unsafe_allow_html=True)
                with c_row[1]:
                    if st.button("해제" if is_t else "추적", key=f"tk_{idx}_{itm['symbol']}"): handle_action(itm, "TOGGLE_TRACK")
            st.markdown("</div>", unsafe_allow_html=True)

with tabs[1]: # Upcoming
    st.markdown("<div style='font-size:16px; font-weight:900; margin-bottom:20px;'>📅 하이퍼 자산 투하 일정 (v7.3 예약 시스템 복구)</div>", unsafe_allow_html=True)
    u_cols = st.columns(4)
    for i, itm in enumerate(upcs):
        with u_cols[i % 4]:
            st.markdown(f"<div style='background:#FFD700;color:#000;padding:2px 8px;border-radius:4px;font-weight:900;font-size:10px;width:fit-content;margin-bottom:5px;'>📅 {itm['listing_date']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='v7-box' style='padding:15px;border-left:5px solid #FFD700;'><b>{itm['name']}</b><br><small style='color:#8B949E;'>{itm['issuer']}</small></div>", unsafe_allow_html=True)
            with st.popover("상장 예약"):
                qty = st.number_input("수량(주)", min_value=1, value=10, key=f"qty_{itm['ticker']}")
                if st.button("예약 확정", key=f"conf_{itm['ticker']}"): handle_action(itm, "RESERVE", qty)

with tabs[2]: # Risk Control (v6.5 레이아웃 복원)
    if not portfolio: st.info("추적 중인 자산이 없습니다.")
    for p in portfolio:
        p_p, c_p = p.get('purchase_price', 10000), p.get('current_price', 10000)
        l_rate = ((c_p - p_p) / p_p * 100) if p_p > 0 else 0
        c_risk = st.columns([7.0, 3.0])
        with c_risk[0]:
            st.markdown(f"""
                <div class='risk-row-container' style='border-color: {'#FF3131' if l_rate <= -10 else '#30363D'};'>
                    <div>
                        <small style='color:#8B949E;'>{p.get('issuer','Unknown')} | {p.get('status','라이브')} ({p.get('qty',0)}주)</small><br>
                        <b style='font-size:16px;'>{p['name']}</b>
                    </div>
                    <div style='text-align:right;'>
                        <span style='color:{'#FF3131' if l_rate <= -10 else '#39FF14'}; font-size:22px; font-weight:900;'>{l_rate:+.2f}%</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        with c_risk[1]:
            st.markdown("<div style='padding-top:10px;'></div>", unsafe_allow_html=True)
            if st.button("추적 해제", key=f"risk_tk_{p['symbol']}"):
                portfolio = [item for item in portfolio if item['symbol'] != p['symbol']]
                s_j(p_file, portfolio); st.rerun()

st.markdown(f"<div style='color:#484F58; font-size:10px; text-align:center; margin-top:50px;'>Hyper ETF Guardian v7.3 | Absolute Integrity Build | Gemini 2.0 Flash</div>", unsafe_allow_html=True)