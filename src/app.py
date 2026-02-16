import streamlit as st
import json
import os
import sys
import google.generativeai as genai
from datetime import datetime

# Ensure src is in path for imports
sys.path.append(os.path.join(os.path.dirname(__file__)))
from monitor import calculate_loss_rate

# 1. [System] 최상단 레이아웃 및 보안 설정
st.set_page_config(page_title="Hyper ETF Guardian", layout="wide", initial_sidebar_state="collapsed")

# --- AI Intelligence Layer ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def get_ai_intel(prompt):
    if not GEMINI_API_KEY: return "[위험: 5.0 / 원인: 키 미설정 / 권고: 설정 확인]"
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        sys_p = "Expert. Response: [R:X/C:Y/R:Z]. Max 15 words."
        response = model.generate_content(f"{sys_p}\n\n{prompt}")
        if not response or not response.text: return "[위험: 5.0 / 원인: 대기 중 / 권고: 수동 확인]"
        return response.text.replace("\n", " ").strip()
    except Exception: return "[위험: 5.0 / 원인: 타임아웃 / 권고: 수동 확인]"

# 2. [UI/UX] 정밀 정렬 및 사이드바 박멸 CSS
st.markdown("""
    <style>
    /* 사이드바 및 불필요 요소 원친 차단 */
    [data-testid="stSidebar"], [data-testid="stSidebarNav"], .stDeployButton { display: none !important; }
    
    /* 글로벌 다크 테마 및 타이포그래피 */
    .stApp { background-color: #0A0E14 !important; color: #FFFFFF !important; }
    .block-container { padding: 2rem 3rem !important; max-width: 98% !important; }
    
    /* V7.0 Precision Box System */
    .v7-box { background-color: #161B22 !important; border: 1px solid #30363D !important; border-radius: 12px; padding: 20px !important; margin-bottom: 25px; box-shadow: 0 8px 16px rgba(0,0,0,0.5); }
    .v7-title { font-size: 14px; font-weight: 900; margin-bottom: 20px; color: #FFFFFF !important; padding-left: 12px; text-transform: uppercase; border-left: 5px solid #39FF14; }
    
    /* 버튼 칼정렬 프로토콜 (Knife-Edge Alignment) */
    .stButton>button { 
        background-color: #1E2329 !important; color: #FFFFFF !important; 
        border: 1px solid #484F58 !important; font-weight: 900 !important; 
        border-radius: 6px !important; font-size: 11px !important; 
        width: 100% !important; height: 32px !important;
        letter-spacing: -1px !important;
        white-space: nowrap !important;
    }
    .stButton>button:hover { border-color: #39FF14 !important; color: #39FF14 !important; background-color: #30363D !important; }
    
    /* 캘린더 배지 스타일 */
    .date-badge {
        background: #FFD700; color: #000; padding: 2px 10px; 
        border-radius: 4px; font-weight: 900; font-size: 11px; width: fit-content; 
        margin-bottom: -5px; position: relative; z-index: 10;
        box-shadow: 2px 2px 0px rgba(0,0,0,0.5);
    }
    .upcoming-card {
        border-left: 5px solid #FFD700 !important; background-color: #1A1C23 !important;
        padding: 20px !important; border-radius: 0 8px 8px 0 !important; margin-bottom: 15px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.4);
    }
    
    /* 위험 통제 박스 */
    .risk-box { background: rgba(255,49,49,0.05); border: 1px solid #FF3131; padding: 20px; border-radius: 10px; margin-bottom: 35px; color: #FF3131 !important; font-weight: 900; font-size: 14px; }
    
    /* 목록 행 정밀 정렬 */
    .list-row-info {
        display: flex;
        align-items: center;
        width: 100%;
        height: 32px;
        gap: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# 3. [Data] 데이터 인양 및 정렬 엔진
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

# 4. [Logic] 통합 액션 핸들러
def handle_action(itm, action_type):
    global portfolio
    if action_type == "RESERVE":
        if not any(p['symbol'] == itm['ticker'] for p in portfolio):
            portfolio.append({
                "symbol": itm['ticker'], "name": itm['name'], "issuer": itm['issuer'],
                "purchase_price": 10000, "current_price": 10000, "status": "예약 중", "listing_date": itm['listing_date']
            })
            st.toast(f"🚨 {itm['name']} 상장 예약 완료.")
    elif action_type == "TOGGLE_TRACK":
        is_t = any(p['symbol'] == itm['symbol'] for p in portfolio)
        if is_t: 
            portfolio = [p for p in portfolio if p['symbol'] != itm['symbol']]
        else: 
            portfolio.append({"symbol": itm['symbol'], "name": itm['name'], "issuer": itm['issuer'], "purchase_price": itm['price_at_listing'], "current_price": itm['price_at_listing'], "status": "라이브"})
    
    s_j(p_file, portfolio)
    st.rerun()

# 5. [Header] 관제탑 메인 헤더
st.markdown("<h2> 📊 하이퍼 ETF 가디언 <span style='font-size:12px;color:#39FF14;'>[v7.0 최종 무결성 마스터]</span></h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#8B949E;font-size:13px;margin:-5px 0 20px 0;'>정비 완료. 버튼 칼정렬 및 예약 동기화 시스템 v7.0.</p>", unsafe_allow_html=True)

d_c = sum(1 for p in portfolio if calculate_loss_rate(p.get('purchase_price',0), p.get('current_price',0)) <= -10)
ai_rep = get_ai_intel(f"유닛: {len(portfolio)} | 위험 자산: {d_c}. v7.0 무결성 집행.")
st.markdown(f'<div class="risk-box">🚨 {ai_rep} </div>', unsafe_allow_html=True)

# 메트릭 섹션
m_cols = st.columns(4)
def m_b(l,v,c="#39FF14"): return f'<div style="background:#161B22; border:1px solid #30363D; border-radius:12px; padding:20px; text-align:center;"><div style="color:#8B949E; font-size:10px; margin-bottom:8px; font-weight:700;">{l}</div><div style="font-size:22px; font-weight:900; color:{c};">{v}</div></div>'

m_cols[0].markdown(m_b("추적 자산", f"{len(portfolio)} 유닛"), unsafe_allow_html=True)
avg_d = sum(calculate_loss_rate(p.get('purchase_price',0), p.get('current_price',1)) for p in portfolio)/len(portfolio) if portfolio else 0
m_cols[1].markdown(m_b("평균 방어력", f"{avg_d:+.2f}%", "#39FF14" if avg_d >= -5 else "#FF3131"), unsafe_allow_html=True)
m_cols[2].markdown(m_b("방어선 돌파", f"{d_c} 유닛", "#FF3131" if d_c else "#39FF14"), unsafe_allow_html=True)
m_cols[3].markdown(m_b("상장 예정", f"{len(upcs)} 유닛", "#FFFF33"), unsafe_allow_html=True)

st.divider()

# 6. [Main] 탭 기반 관제 시스템
tabs = st.tabs(["📊 시장 감시", "📅 상장 일정", "🚨 위험 통제"])

with tabs[0]: # Market Watch (2x3 Grid with Knife-Edge Alignment)
    themes = [
        {"n": "AI 및 반도체 핵심 전략", "k": ["AI", "반도체", "NVIDIA", "HBM"], "c": "#39FF14"},
        {"n": "미국 빅테크 핵심 자산", "k": ["미국", "빅테크", "나스닥", "S&P"], "c": "#00D1FF"},
        {"n": "밸류업 및 배당 가치 전략", "k": ["밸류업", "저PBR", "배당", "인컴"], "c": "#FFB800"},
        {"n": "국내 대표 지수 추종 전략", "k": ["200", "코스피", "코스닥"], "c": "#FF3131"},
        {"n": "글로벌 액티브 & 전략", "k": ["글로벌", "유럽", "액티브"], "c": "#BC13FE"},
        {"n": "미래 기술 및 소부장 테마", "k": ["기술", "혁신", "소부장"], "c": "#00FFD1"}
    ]
    
    total_rendered = 0
    row1_cols = st.columns(3)
    row2_cols = st.columns(3)
    all_grid_cols = row1_cols + row2_cols
    
    for idx, th in enumerate(themes):
        with all_grid_cols[idx]:
            st.markdown(f'<div class="v7-box"><div class="v7-title" style="border-left: 5px solid {th["c"]};">{th["n"]}</div>', unsafe_allow_html=True)
            # 데이터 인양 (필터링 로직 제거)
            tp = [e for e in etfs if any(k.lower() in e['name'].lower() for k in th['k'])]
            seen = {e['symbol'] for e in tp}
            for e in etfs:
                if len(tp) >= 10: break
                if e['symbol'] not in seen: tp.append(e); seen.add(e['symbol'])
            
            for r, itm in enumerate(tp[:10]):
                total_rendered += 1
                is_t = any(p['symbol'] == itm['symbol'] for p in portfolio)
                
                # Knife-Edge Alignment: Flexbox Row
                c_row = st.columns([7.2, 2.8])
                with c_row[0]:
                    st.markdown(f"""
                        <div class="list-row-info">
                            <span style="color:#8B949E; font-size:11px; width:15px;">{r+1}</span>
                            <span style="color:#8B949E; font-size:10px; width:45px; overflow:hidden;">{itm['issuer'][:3]}</span>
                            <span style="font-size:11px; font-weight:700; flex-grow:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">{itm['name']}</span>
                            <span style="color:#39FF14; font-size:11px; font-weight:900; width:50px; text-align:right;">{itm['price_at_listing']:,}</span>
                        </div>
                    """, unsafe_allow_html=True)
                with c_row[1]:
                    if st.button("해제" if is_t else "추적", key=f"tk_{idx}_{itm['symbol']}"):
                        handle_action(itm, "TOGGLE_TRACK")
                st.markdown('<div style="border-bottom:1px solid #282E36; margin:0;"></div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

with tabs[1]: # Upcoming Calendar (Date Badge)
    st.markdown("<div style='font-size:18px; font-weight:900; margin-bottom:30px;'>📅 하이퍼 자산 투하 일정 (v7.0 정밀 복구)</div>", unsafe_allow_html=True)
    u_cols = st.columns(4)
    for i, itm in enumerate(upcs):
        with u_cols[i % 4]:
            st.markdown(f"<div class='date-badge'>📅 {itm['listing_date']}</div>", unsafe_allow_html=True)
            st.markdown(f"""
                <div class='upcoming-card'>
                    <div style='font-size:10px; color:#8B949E; font-weight:700; margin-bottom:5px;'>{itm['issuer']} | {itm['ticker']}</div>
                    <div style='font-size:14px; font-weight:900; height:40px; overflow:hidden;'>{itm['name']}</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("상장 예약", key=f"res_{itm['ticker']}"):
                handle_action(itm, "RESERVE")

with tabs[2]: # Control Room
    if not portfolio: st.info("추적 중인 자산이 없습니다.")
    for p in portfolio:
        l_rate = calculate_loss_rate(p.get('purchase_price',0), p.get('current_price',0))
        st.markdown(f"""
            <div style='background:#161B22; border:1px solid {'#FF3131' if l_rate <= -10 else '#30363D'}; padding:20px; border-radius:12px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center;'>
                <div>
                    <small style='color:#8B949E; font-weight:700;'>{p.get('issuer','Unknown')} | {p.get('status','라이브')}</small><br>
                    <b style='font-size:18px;'>{p['name']}</b>
                </div>
                <div style='text-align:right;'>
                    <span style='color:{'#FF3131' if l_rate <= -10 else '#39FF14'}; font-size:24px; font-weight:900;'>{l_rate:.2f}%</span><br>
                    <span style='font-size:12px; color:#8B949E;'>현재 정밀 추적 중</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

# Footer & Integrity Log
st.markdown(f"<div style='color:#484F58; font-size:11px; text-align:center; margin-top:100px;'>Hyper ETF Guardian v7.0 | Precision Alignment Protocol Active | Total: {total_rendered} Units | Gemini 2.0 Flash </div>", unsafe_allow_html=True)
