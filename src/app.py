import streamlit as st
import json
import os
import sys
import google.generativeai as genai
from datetime import datetime

# 1. [System] 레이아웃 최적화 (v7.1)
st.set_page_config(page_title="Hyper ETF Guardian", layout="wide", initial_sidebar_state="collapsed")

# --- AI Intelligence Layer ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
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

# 2. [UI/UX] 정밀 정렬 및 스타일 (v7.1 Ultimate)
st.markdown("""
    <style>
    [data-testid="stSidebar"], [data-testid="stSidebarNav"], .stDeployButton { display: none !important; }
    .stApp { background-color: #0A0E14 !important; color: #FFFFFF !important; }
    .block-container { padding: 2rem 4rem !important; max-width: 98% !important; }
    
    /* v7.1 칼정렬 박스 및 타이포그래피 */
    .v7-box { background-color: #161B22; border: 1px solid #30363D; border-radius: 12px; padding: 25px; margin-bottom: 25px; box-shadow: 0 8px 16px rgba(0,0,0,0.5); }
    .v7-title { font-size: 14px; font-weight: 900; margin-bottom: 20px; color: #FFFFFF; padding-left: 12px; border-left: 5px solid #39FF14; text-transform: uppercase; }
    
    /* 버튼 정렬 무결성 (Knife-Edge Alignment) */
    .stButton>button { width: 100% !important; height: 32px !important; font-size: 11px !important; font-weight: 900 !important; border-radius: 6px !important; }
    .stPopover>button { width: 100% !important; height: 32px !important; font-size: 11px !important; background: #FFD700 !important; color: #000 !important; border-radius: 6px !important; font-weight: 900 !important; }
    
    .list-row-info { display: flex; align-items: center; width: 100%; height: 32px; gap: 12px; }
    .issuer-tag { color: #8B949E; font-size: 10px; width: 85px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
    
    /* 위험 통제 레이아웃 */
    .risk-card { background: #161B22; border: 1px solid #30363D; padding: 20px; border-radius: 12px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; }
    </style>
""", unsafe_allow_html=True)

# 3. [Data] 데이터 엔진
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

# 4. [Logic] 통합 액션 핸들러 (v7.1)
def handle_track(itm):
    global portfolio
    is_t = any(p['symbol'] == itm['symbol'] for p in portfolio)
    if is_t: portfolio = [p for p in portfolio if p['symbol'] != itm['symbol']]
    else: portfolio.append({"symbol": itm['symbol'], "name": itm['name'], "issuer": itm['issuer'], "purchase_price": itm['price_at_listing'], "current_price": itm['price_at_listing'], "qty": 0, "status": "라이브"})
    s_j(p_file, portfolio); st.rerun()

def handle_reserve(itm, qty):
    global portfolio
    if not any(p['symbol'] == itm['ticker'] for p in portfolio):
        portfolio.append({"symbol": itm['ticker'], "name": itm['name'], "issuer": itm['issuer'], "purchase_price": 10000, "current_price": 10000, "qty": qty, "status": "예약 중", "listing_date": itm['listing_date']})
        s_j(p_file, portfolio); st.toast(f"🚨 {itm['name']} {qty}주 예약 완료."); st.rerun()

# 5. [Header] 헤더 및 AI 통찰
st.markdown("<h2> 📊 하이퍼 ETF 가디언 <span style='font-size:12px;color:#39FF14;'>[v7.1 최종 무결성 마스터]</span></h2>", unsafe_allow_html=True)
ai_rep = get_ai_intel(f"유닛: {len(portfolio)}. 정밀 정렬 및 수량 예약 시스템 가동.")
st.markdown(f'<div style="background:rgba(255,49,49,0.05); border:1px solid #FF3131; padding:20px; border-radius:10px; margin-bottom:35px; color:#FF3131; font-weight:900;">🚨 AI Intel: {ai_rep} </div>', unsafe_allow_html=True)

# 6. [Main] 관제 탭
tabs = st.tabs(["📊 시장 감시", "📅 상장 일정", "🚨 위험 통제"])

with tabs[0]: # Market Watch (Knife-Edge Alignment)
    row1, row2 = st.columns(3), st.columns(3)
    grid_cols = row1 + row2
    themes = [
        {"n": "AI/반도체", "k": ["AI", "반도체"]}, {"n": "미국 빅테크", "k": ["미국", "빅테크"]}, 
        {"n": "배당/밸류업", "k": ["배당", "밸류"]}, {"n": "국내 지수", "k": ["200", "코스피"]}, 
        {"n": "글로벌 전략", "k": ["글로벌"]}, {"n": "기술/혁신", "k": ["기술", "혁신"]}
    ]
    
    for idx, th in enumerate(themes):
        with grid_cols[idx]:
            st.markdown(f'<div class="v7-box"><div class="v7-title">{th["n"]} 전략</div>', unsafe_allow_html=True)
            tp = [e for e in etfs if any(k in e['name'] for k in th['k'])][:10]
            for r, itm in enumerate(tp):
                is_t = any(p['symbol'] == itm['symbol'] for p in portfolio)
                c_row = st.columns([8.0, 2.0]) # Knife-Edge Ratio
                with c_row[0]:
                    st.markdown(f"""
                        <div class="list-row-info">
                            <span style="color:#8B949E;width:15px;font-size:11px;">{r+1}</span>
                            <span class="issuer-tag">{itm["issuer"]}</span>
                            <span style="font-weight:700;flex-grow:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-size:11px;">{itm["name"]}</span>
                        </div>
                    """, unsafe_allow_html=True)
                with c_row[1]:
                    if st.button("추적 해제" if is_t else "추적 시작", key=f"tk_{idx}_{itm['symbol']}"): handle_track(itm)
            st.markdown("</div>", unsafe_allow_html=True)

with tabs[1]: # Upcoming (Popover Reserve System)
    u_cols = st.columns(4)
    for i, itm in enumerate(upcs):
        with u_cols[i % 4]:
            st.markdown(f"<div style='background:#FFD700;color:#000;padding:2px 10px;border-radius:4px;font-weight:900;font-size:11px;width:fit-content;margin-bottom:5px;'>📅 {itm['listing_date']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='v7-box' style='padding:15px;border-left:5px solid #FFD700;'><b>{itm['name']}</b><br><small style='color:#8B949E;'>{itm['issuer']}</small></div>", unsafe_allow_html=True)
            with st.popover("상장 예약"):
                q = st.number_input("예약 수량(주)", min_value=1, value=10, key=f"q_{itm['ticker']}")
                if st.button("예약 확정", key=f"rb_{itm['ticker']}"): handle_reserve(itm, q)

with tabs[2]: # Risk Control (Division by Zero Prevention)
    if not portfolio: st.info("추적 중인 자산이 없습니다.")
    for p in portfolio:
        p_p = p.get('purchase_price', 10000)
        c_p = p.get('current_price', 10000)
        l_r = ((c_p - p_p) / p_p * 100) if p_p > 0 else 0
        st.markdown(f"""
            <div class="risk-card" style="border-color: {'#FF3131' if l_r <= -10 else '#30363D'};">
                <div><small style='color:#8B949E;'>{p.get('issuer', 'Unknown')} | {p['status']} ({p.get('qty', 0)}주)</small><br><b style='font-size:18px;'>{p['name']}</b></div>
                <div style='text-align:right;'><span style='color:{'#FF3131' if l_r <= -10 else '#39FF14'}; font-size:24px; font-weight:900;'>{l_r:+.2f}%</span></div>
            </div>
        """, unsafe_allow_html=True)

st.markdown(f"<div style='color:#484F58; font-size:11px; text-align:center; margin-top:50px;'>Hyper ETF Guardian v7.1 | Precision Recovery Active | Gemini 2.0 Flash</div>", unsafe_allow_html=True)
