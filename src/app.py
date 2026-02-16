import streamlit as st
import json
import os
import sys
import google.generativeai as genai
from datetime import datetime

# 1. [System] 레이아웃 절대 고정
st.set_page_config(page_title="Hyper ETF Guardian", layout="wide", initial_sidebar_state="collapsed")

# --- AI Intelligence Layer ---
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
        response = model.generate_content(f"Expert financial response max 10 words: {prompt}")
        return response.text.replace("\n", " ").strip() if response.text else "[대기 중]"
    except: return "[타임아웃]"

# 2. [UI/UX] 불사신 CSS (테마 락다운 v7.5)
st.markdown("""
    <style>
    /* 1. 불필요 요소 완전 소멸 */
    [data-testid="stSidebar"], [data-testid="stSidebarNav"], .stDeployButton { display: none !important; }
    
    /* 2. 전역 다크 락다운 */
    .stApp { background-color: #0A0E14 !important; color: #FFFFFF !important; }
    .block-container { padding: 2rem 4rem !important; max-width: 98% !important; }
    
    /* 3. 버튼 시각적 봉쇄 (흰색 배경 원천 차단 !important) */
    button[kind="secondary"], .stButton>button { 
        background-color: #1E2329 !important; 
        color: #FFFFFF !important; 
        border: 1px solid #484F58 !important; 
        font-weight: 900 !important; 
        width: 100% !important; 
        height: 32px !important; 
        font-size: 11px !important;
        border-radius: 6px !important;
    }
    button:hover { border-color: #39FF14 !important; color: #39FF14 !important; background-color: #30363D !important; }
    
    /* 4. 예약 확정 버튼 (형광 연두 강조) */
    div[data-testid="stPopover"] button { background-color: #39FF14 !important; color: #000 !important; border: 1px solid #39FF14 !important; }
    div[data-testid="stPopover"] button:hover { background-color: #32D912 !important; }

    .v7-box { background-color: #161B22; border: 1px solid #30363D; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 8px 16px rgba(0,0,0,0.5); }
    .v7-title { font-size: 14px; font-weight: 900; color: #FFFFFF; border-left: 5px solid #39FF14; padding-left: 10px; margin-bottom: 15px; text-transform: uppercase; }
    .list-row { display: flex; align-items: center; height: 32px; gap: 10px; width: 100%; border-bottom: 1px solid #21262D; }
    
    /* 캡션 스타일 보강 */
    .stCaption { color: #8B949E !important; font-weight: 700 !important; font-size: 12px !important; }
    </style>
""", unsafe_allow_html=True)

# 3. [Data] 데이터 정제 및 동기화 엔진
p_file = 'data/user_portfolio.json'

def l_j(path=p_file):
    if not os.path.exists(path): return []
    try:
        with open(path,'r',encoding='utf-8') as f: return json.load(f)
    except: return []

def s_j(d):
    with open(p_file,'w',encoding='utf-8') as f: json.dump(d, f, indent=2, ensure_ascii=False)

portfolio = l_j()
etfs = l_j('data/etf_list.json')
upcs = sorted(l_j('data/upcoming_etf.json'), key=lambda x: x.get('listing_date', '9999-12-31'))

def handle_action(itm, action, qty=0):
    current_p = l_j() # 최신 데이터 로드
    if action == "TOGGLE":
        is_t = any(p['symbol'] == itm['symbol'] for p in current_p)
        if is_t: current_p = [p for p in current_p if p['symbol'] != itm['symbol']]
        else: current_p.append({"symbol": itm['symbol'], "name": itm['name'], "issuer": itm['issuer'], "purchase_price": itm['price_at_listing'], "current_price": itm['price_at_listing'], "qty": 0, "status": "라이브"})
    elif action == "RESERVE":
        if not any(p['symbol'] == itm['ticker'] for p in current_p):
            current_p.append({"symbol": itm['ticker'], "name": itm['name'], "issuer": itm['issuer'], "purchase_price": 10000, "current_price": 10000, "qty": qty, "status": "예약 중", "listing_date": itm['listing_date']})
            st.toast(f"🚨 {itm['name']} 예약 완료.")
    
    s_j(current_p)
    st.rerun() # 즉시 반영 (Atomic Rerun)

# 4. [Header] 관제탑 메인 헤더
st.markdown("<h2> 📊 하이퍼 ETF 가디언 <span style='font-size:12px;color:#39FF14;'>[v7.5 최종 승전 빌드]</span></h2>", unsafe_allow_html=True)
ai_rep = get_ai_intel(f"유닛: {len(portfolio)}. 무결성 가동 완료.")
st.markdown(f'<div style="background:rgba(255,49,49,0.05); border:1px solid #FF3131; padding:20px; border-radius:10px; margin-bottom:35px; color:#FF3131; font-weight:900;">🚨 AI Intel: {ai_rep} </div>', unsafe_allow_html=True)

# 5. [Main] 지휘 탭
tabs = st.tabs(["📊 시장 감시", "📅 상장 일정", "🚨 위험 통제"])

with tabs[0]: # Market Watch (Knife-Edge Alignment [8.2, 1.8])
    themes = [{"n": "AI/반도체", "k": ["AI", "반도체"]}, {"n": "미국 빅테크", "k": ["미국", "빅테크"]}, {"n": "배당/밸류업", "k": ["배당", "밸류"]}, {"n": "국내 지수", "k": ["200", "코스피"]}, {"n": "글로벌 액티브", "k": ["글로벌"]}, {"n": "기술/소부장", "k": ["기술", "혁신"]}]
    row1, row2 = st.columns(3), st.columns(3)
    all_c = row1 + row2
    for idx, th in enumerate(themes):
        with all_c[idx]:
            st.markdown(f'<div class="v7-box"><div class="v7-title">{th["n"]} 전략</div>', unsafe_allow_html=True)
            # 60 Unit Influx Logic
            tp = [e for e in etfs if any(k in e['name'] for k in th['k'])]
            seen = {e['symbol'] for e in tp}
            for e in etfs:
                if len(tp) >= 10: break
                if e['symbol'] not in seen: tp.append(e); seen.add(e['symbol'])
            
            for r, itm in enumerate(tp[:10]):
                is_t = any(p['symbol'] == itm['symbol'] for p in portfolio)
                c_row = st.columns([8.2, 1.8]) # 최종 칼정렬 비율
                with c_row[0]:
                    st.markdown(f'<div class="list-row"><span style="color:#8B949E;width:15px;font-size:10px;">{r+1}</span><span style="color:#8B949E;font-size:10px;width:75px;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;">{itm["issuer"]}</span><span style="font-size:11px;font-weight:700;flex-grow:1;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;">{itm["name"]}</span></div>', unsafe_allow_html=True)
                with c_row[1]:
                    if st.button("해제" if is_t else "추적", key=f"tk_{idx}_{itm['symbol']}"): handle_action(itm, "TOGGLE")
            st.markdown("</div>", unsafe_allow_html=True)

with tabs[1]: # Upcoming (v7.5 수량 확정 복구)
    u_cols = st.columns(4)
    for i, itm in enumerate(upcs):
        with u_cols[i % 4]:
            st.markdown(f"<div style='background:#FFD700;color:#000;padding:2px 8px;border-radius:4px;font-weight:900;font-size:10px;width:fit-content;margin-bottom:5px;'>📅 {itm['listing_date']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='v7-box' style='padding:15px;border-left:5px solid #FFD700;'><b>{itm['name']}</b><br><small style='color:#8B949E;'>{itm['issuer']}</small></div>", unsafe_allow_html=True)
            with st.popover("상장 예약"):
                qty = st.number_input("수량(주)", min_value=1, value=10, key=f"q_{itm['ticker']}")
                if st.button("확정", key=f"cf_{itm['ticker']}"): handle_action(itm, "RESERVE", qty)

with tabs[2]: # Risk Control (칼럼 레이아웃 완벽 복원)
    if not portfolio: st.info("추적 중인 자산이 없습니다.")
    else:
        # 헤더 칼럼
        h_col = st.columns([1.5, 4.0, 1.2, 1.3, 1.0])
        with h_col[0]: st.caption("운용사")
        with h_col[1]: st.caption("상품명")
        with h_col[2]: st.caption("보유수량")
        with h_col[3]: st.caption("수익률")
        with h_col[4]: st.caption("지휘")
        st.divider()
        for p in portfolio:
            p_p, c_p = p.get('purchase_price', 10000), p.get('current_price', 10000)
            l_r = ((c_p - p_p) / p_p * 100) if p_p > 0 else 0
            r_col = st.columns([1.5, 4.0, 1.2, 1.3, 1.0])
            with r_col[0]: st.write(p.get('issuer', 'Unknown'))
            with r_col[1]: st.markdown(f"**{p['name']}**")
            with r_col[2]: st.write(f"{p.get('qty',0)}주")
            with r_col[3]: st.markdown(f"<span style='color:{'#FF3131' if l_r < 0 else '#39FF14'}; font-weight:900;'>{l_r:+.2f}%</span>", unsafe_allow_html=True)
            with r_col[4]:
                if st.button("해제", key=f"del_{p['symbol']}"): handle_action(p, "TOGGLE")

st.markdown("<div style='color:#484F58; font-size:10px; text-align:center; margin-top:50px;'>Hyper ETF Guardian v7.5 Final | Mission Accomplished | Gemini 2.0 Flash</div>", unsafe_allow_html=True)