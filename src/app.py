import streamlit as st
import json
import os
import sys
import google.generativeai as genai
from datetime import datetime, timedelta

# Ensure src is in path for imports
sys.path.append(os.path.join(os.path.dirname(__file__)))
from monitor import calculate_loss_rate

# 1. [v6.9 Master] 최상단 레이아웃 설정
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

# 2. [v6.9 Master] 사이드바 완전 박멸 및 100% 가용 레이아웃 CSS
st.markdown("""
    <style>
    /* 사이드바 원천 차단 */
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    
    /* 글로벌 락다운 */
    .stApp { background-color: #0A0E14 !important; color: #FFFFFF !important; }
    h1,h2,h3,h4,h5,h6,p,span,label,div,li { color: #FFFFFF !important; font-family: 'Inter', sans-serif !important; letter-spacing: -0.5px !important; }
    
    /* 메인 컨테이너 여백 최적화 (Total Space Liberation) */
    .block-container {
        padding: 2rem 2rem !important;
        max-width: 98% !important;
    }

    /* 디자인 시스템 v6.9: Unique Color Identities & Recovery */
    .v6-box { background-color: #161B22 !important; border: 1px solid #30363D !important; border-radius: 12px; padding: 25px !important; margin-bottom: 25px !important; box-shadow: 0 8px 16px rgba(0,0,0,0.5); }
    .v6-title { font-size: 14px; font-weight: 900; margin-bottom: 20px; color: #FFFFFF !important; padding-left: 12px; text-transform: uppercase; }
    
    .stButton>button { background-color: #1E2329 !important; color: #FFFFFF !important; border: 1px solid #484F58 !important; font-weight: 900 !important; min-height: 32px !important; border-radius: 6px !important; font-size: 10px !important; letter-spacing: -1px !important; width: 100% !important; white-space: nowrap !important; }
    .stButton>button:hover { background-color: #30363D !important; border-color: #39FF14 !important; color: #39FF14 !important; }
    
    .risk-box { background: rgba(255,49,49,0.05); border: 1px solid #FF3131; padding: 20px; border-radius: 10px; margin-bottom: 35px; color: #FF3131 !important; font-weight: 900; font-size: 14px; }
    
    /* v6.9 캘린더 카드 복구 */
    .upcoming-card {
        border-left: 5px solid #FFD700 !important;
        background-color: #1A1C23 !important;
        padding: 20px !important;
        border-radius: 8px !important;
        margin-bottom: 15px !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }

    #MainMenu, footer, .stDeployButton { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# --- Data Engine ---
def l_j(p):
    if not os.path.exists(p): return []
    try:
        with open(p,'r',encoding='utf-8') as f:
            c = f.read().strip(); return json.loads(c) if c else []
    except Exception: return []

def s_j(p, d):
    with open(p,'w',encoding='utf-8') as f: json.dump(d, f, indent=2, ensure_ascii=False)

p_dat = l_j('data/user_portfolio.json')
portfolio = []
seen_p = set()
for i in p_dat:
    if i['symbol'] not in seen_p: portfolio.append(i); seen_p.add(i['symbol'])

etfs = l_j('data/etf_list.json')
upcs = sorted(l_j('data/upcoming_etf.json'), key=lambda x: x.get('listing_date', '9999-12-31'))

def deploy_logic(itm):
    if not any(p['symbol'] == itm['ticker'] for p in portfolio):
        portfolio.append({
            "symbol": itm['ticker'],
            "name": itm['name'],
            "issuer": itm['issuer'],
            "purchase_price": 10000,
            "current_price": 10000,
            "status": "예약 중",
            "listing_date": itm['listing_date']
        })
        s_j('data/user_portfolio.json', portfolio)
        st.toast(f"🚨 {itm['name']} 예약 시스템 가동 완료.")

# --- Header Layer ---
st.markdown(f"<h2> 📊 하이퍼 ETF 가디언 <span style='font-size:12px;color:#39FF14;'>[v6.9 마스터 빌드]</span></h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#8B949E;font-size:13px;margin:-5px 0 20px 0;'>정비 완료. 캘린더 스타일 및 예약 시스템 복구 v6.9.</p>", unsafe_allow_html=True)

d_c = sum(1 for p in portfolio if calculate_loss_rate(p.get('purchase_price',0), p.get('current_price',0)) <= -10)
ai_rep = get_ai_intel(f"유닛: {len(portfolio)} | 위험 자산: {d_c}. v6.9 복구 가동.")
st.markdown(f'<div class="risk-box">🚨 {ai_rep} </div>', unsafe_allow_html=True)

met = st.columns(4)
def m_b(l,v,c="#39FF14"): return f'<div style="background:#161B22;border:1px solid #30363D;border-radius:12px;padding:20px;text-align:center;"><div style="color:#8B949E;font-size:10px;margin-bottom:8px;font-weight:700;">{l}</div><div style="font-size:22px;font-weight:900;color:{c};">{v}</div></div>'
met[0].markdown(m_b("추적 자산", f"{len(portfolio)} 유닛"), unsafe_allow_html=True)
avg_d = sum(calculate_loss_rate(p.get('purchase_price',0), p.get('current_price',1)) for p in portfolio)/len(portfolio) if portfolio else 0
met[1].markdown(m_b("평균 방어력", f"{avg_d:+.2f}%", "#39FF14" if avg_d >= -5 else "#FF3131"), unsafe_allow_html=True)
met[2].markdown(m_b("방어선 돌파", f"{d_c} 유닛", "#FF3131" if d_c else "#39FF14"), unsafe_allow_html=True)
met[3].markdown(m_b("상장 예정", f"{len(upcs)} 유닛", "#FFFF33"), unsafe_allow_html=True)

st.divider()

# --- Strategic Dashboard (Tabs) ---
tabs = st.tabs(["📊 시장 감시", "📅 상장 일정", "🚨 위험 통제"])

# Tab 1: Market Watch (2x3 Grid)
with tabs[0]:
    themes = [
        {"name": "AI 및 반도체 핵심 전략", "keys": ["AI", "반도체", "NVIDIA", "HBM"], "color": "#39FF14"},
        {"name": "미국 빅테크 핵심 자산", "keys": ["미국", "빅테크", "나스닥", "S&P"], "color": "#00D1FF"},
        {"name": "밸류업 및 배당 가치 전략", "keys": ["밸류업", "저PBR", "배당", "인컴"], "color": "#FFB800"},
        {"name": "국내 대표 지수 추종 전략", "keys": ["200", "코스피", "코스닥"], "color": "#FF3131"},
        {"name": "글로벌 액티브 & 전략", "keys": ["글로벌", "유럽", "액티브"], "color": "#BC13FE"},
        {"name": "미래 기술 및 소부장 테마", "keys": ["기술", "혁신", "소부장"], "color": "#00FFD1"}
    ]
    
    total_rendered = 0
    cols = st.columns(3)
    cols2 = st.columns(3)
    all_cols = cols + cols2
    
    for idx, th in enumerate(themes):
        with all_cols[idx]:
            st.markdown(f'<div class="v6-box"><div class="v6-title" style="border-left: 5px solid {th["color"]};">{th["name"]}</div>', unsafe_allow_html=True)
            tp = [e for e in etfs if any(k.lower() in e['name'].lower() for k in th['keys'])]
            seen = {e['symbol'] for e in tp}
            for e in etfs:
                if len(tp) >= 10: break
                if e['symbol'] not in seen: tp.append(e); seen.add(e['symbol'])
            
            for r, itm in enumerate(tp[:10]):
                total_rendered += 1
                pk = f"mw_{idx}_{itm['symbol']}"
                is_t = any(p['symbol'] == itm['symbol'] for p in portfolio)
                rc = st.columns([0.3, 1.2, 3.0, 1.3, 3.0])
                with rc[0]: st.markdown(f'<div style="height:32px;display:flex;align-items:center;color:#8B949E;font-size:11px;">{r+1}</div>', unsafe_allow_html=True)
                with rc[1]: st.markdown(f'<div style="height:32px;display:flex;align-items:center;color:#8B949E;font-size:10px;">{itm["issuer"]}</div>', unsafe_allow_html=True)
                with rc[2]: st.markdown(f'<div style="height:32px;display:flex;align-items:center;font-size:11px;font-weight:700;overflow:hidden;white-space:nowrap;">{itm["name"]}</div>', unsafe_allow_html=True)
                with rc[3]: st.markdown(f'<div style="height:32px;display:flex;align-items:center;justify-content:flex-end;color:#39FF14;font-size:11px;font-weight:900;">{itm["price_at_listing"]:,}</div>', unsafe_allow_html=True)
                with rc[4]:
                    if st.button("추적 해제" if is_t else "추적 시작", key=pk):
                        if is_t: portfolio = [p for p in portfolio if p['symbol'] != itm['symbol']]
                        else: portfolio.append({"symbol": itm['symbol'], "name": itm['name'], "issuer": itm['issuer'], "purchase_price": itm['price_at_listing'], "current_price": itm['price_at_listing']})
                        s_j('data/user_portfolio.json', portfolio); st.rerun()
                if r < 9: st.markdown('<div style="border-bottom:1px solid #282E36;margin:5px 0;"></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# Tab 2: Upcoming (Calendar Card Recovery)
with tabs[1]:
    st.markdown("<div style='font-size:18px;font-weight:900;margin-bottom:20px;'>📅 상장 예정 하이퍼 자산 (달력 스타일 복구)</div>", unsafe_allow_html=True)
    c_up = st.columns(4)
    for i, itm in enumerate(upcs):
        with c_up[i % 4]:
            st.markdown(f"""
                <div class='upcoming-card'>
                    <div style='font-size:10px;color:#8B949E;font-weight:700;'>{itm['issuer']} | {itm['ticker']}</div>
                    <div style='font-size:13px;font-weight:900;margin:10px 0;height:35px;overflow:hidden;'>{itm['name']}</div>
                    <div style='font-size:11px;color:#FFD700;font-weight:900;'>상장일: {itm['listing_date']}</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("상장 예약", key=f"res_{itm['ticker']}"):
                deploy_logic(itm)
                st.rerun()

# Tab 3: Control Room
with tabs[2]:
    if not portfolio: st.info("추적 중인 자산이 없습니다. 시장 감시 탭에서 자산을 추가하십시오.")
    for p in portfolio:
        l_r = calculate_loss_rate(p.get('purchase_price',0), p.get('current_price',0))
        st.markdown(f"<div style='background:#161B22;border:1px solid {'#FF3131' if l_r <= -10 else '#30363D'};padding:15px;border-radius:10px;margin-bottom:10px;display:flex;justify-content:space-between;align-items:center;'><div><span style='color:#8B949E;font-size:12px;'>{p.get('issuer','Unknown')} | {'예약 중' if p.get('status')=='예약 중' else '라이브'}</span><br><b style='font-size:16px;'>{p['name']}</b></div><div style='text-align:right;'><span style='color:{'#FF3131' if l_r <= -10 else '#39FF14'};font-size:20px;font-weight:900;'>{l_r:.2f}%</span><br><span style='font-size:12px;color:#8B949E;'>상태: {p.get('status','정상')}</span></div></div>", unsafe_allow_html=True)

# Footer & Integrity Log
st.markdown(f"<div style='color:#484F58;font-size:11px;text-align:center;margin-top:100px;'>하이퍼 ETF 가디언 v6.9 마스터 빌드 | 캘린더 스타일 복구 완료 | 예약 시스템 가동 중 | 총 인양 유닛: {total_rendered} Units | 지능: Gemini 2.0 Flash</div>", unsafe_allow_html=True)
