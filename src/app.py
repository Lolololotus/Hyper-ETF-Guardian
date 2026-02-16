import streamlit as st
import json
import os
import sys
import google.generativeai as genai
from datetime import datetime, timedelta

# Ensure src is in path for imports
sys.path.append(os.path.join(os.path.dirname(__file__)))
from monitor import calculate_loss_rate

# 1. [v6.7 Master] 최상단 레이아웃 설정
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

# 2. [v6.7 Master] 사이드바 완전 박멸 및 UI 최적화 CSS
st.markdown("""
    <style>
    /* 사이드바 원천 차단 */
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    
    /* 글로벌 락다운 */
    .stApp { background-color: #0A0E14 !important; color: #FFFFFF !important; }
    h1,h2,h3,h4,h5,h6,p,span,label,div,li { color: #FFFFFF !important; font-family: 'Inter', sans-serif !important; letter-spacing: -0.5px !important; }
    
    /* 메인 컨테이너 여백 최적화 (Maximized Space) */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 95% !important;
    }

    /* 디자인 시스템 v6.7 */
    .v6-box { background-color: #161B22 !important; border: 1px solid #30363D !important; border-radius: 12px; padding: 25px !important; margin-bottom: 80px !important; box-shadow: 0 8px 16px rgba(0,0,0,0.5); }
    .v6-title { font-size: 16px; font-weight: 900; margin-bottom: 25px; color: #FFFFFF !important; border-left: 5px solid #39FF14; padding-left: 15px; text-transform: uppercase; }
    
    .stButton>button { background-color: #1E2329 !important; color: #FFFFFF !important; border: 1px solid #484F58 !important; font-weight: 900 !important; min-height: 34px !important; border-radius: 6px !important; font-size: 11px !important; letter-spacing: -0.8px !important; width: 100% !important; }
    .stButton>button:hover { background-color: #30363D !important; border-color: #39FF14 !important; color: #39FF14 !important; }
    
    .risk-box { background: rgba(255,49,49,0.05); border: 1px solid #FF3131; padding: 20px; border-radius: 10px; margin-bottom: 35px; color: #FF3131 !important; font-weight: 900; font-size: 14px; }
    .cal-item { background: #161B22; border: 1px solid #30363D; border-radius: 10px; padding: 22px; margin-top: 15px; border-left: 5px solid #FFFF33; min-height: 190px; }

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
upcs = l_j('data/upcoming_etf.json')

# --- Header Layer ---
st.markdown(f"<h2> 📊 하이퍼 ETF 가디언 <span style='font-size:12px;color:#39FF14;'>[v6.7 최종 마스터]</span></h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#8B949E;font-size:13px;margin:-5px 0 20px 0;'>정비 완료. 한국형 자산 방어 관제탑 v6.7.</p>", unsafe_allow_html=True)

d_c = sum(1 for p in portfolio if calculate_loss_rate(p.get('purchase_price',0), p.get('current_price',0)) <= -10)
ai_rep = get_ai_intel(f"유닛: {len(portfolio)} | 위험 자산: {d_c}. 현지화 완료.")
st.markdown(f'<div class="risk-box">🚨 {ai_rep} </div>', unsafe_allow_html=True)

met = st.columns(4)
def m_b(l,v,c="#39FF14"): return f'<div style="background:#161B22;border:1px solid #30363D;border-radius:12px;padding:20px;text-align:center;"><div style="color:#8B949E;font-size:10px;margin-bottom:8px;font-weight:700;">{l}</div><div style="font-size:22px;font-weight:900;color:{c};">{v}</div></div>'
met[0].markdown(m_b("추적 자산", f"{len(portfolio)} 유닛"), unsafe_allow_html=True)
avg_d = sum(calculate_loss_rate(p.get('purchase_price',0), p.get('current_price',1)) for p in portfolio)/len(portfolio) if portfolio else 0
met[1].markdown(m_b("평균 방어력", f"{avg_d:+.2f}%", "#FF3131" if avg_d < 0 else "#39FF14"), unsafe_allow_html=True)
met[2].markdown(m_b("방어선 돌파", f"{d_c} 유닛", "#FF3131" if d_c else "#39FF14"), unsafe_allow_html=True)
met[3].markdown(m_b("상장 예정", f"{len(upcs)} 유닛", "#FFFF33"), unsafe_allow_html=True)

st.divider()

# --- Strategic Dashboard (Tabs) ---
pool = etfs
tabs = st.tabs(["📊 시장 감시", "📅 상장 일정", "🚨 위험 통제"])

# Tab 1: Market Watch
with tabs[0]:
    themes = {
        "AI 및 반도체 핵심 전략": ["AI", "반도체", "NVIDIA", "HBM"],
        "미국 빅테크 핵심 자산": ["미국", "빅테크", "나스닥", "S&P"],
        "밸류업 및 배당 가치 전략": ["밸류업", "저PBR", "배당", "인컴"]
    }
    th_l = list(themes.items())
    cols = st.columns(3)
    for j in range(3):
        tn, tk = th_l[j]
        with cols[j]:
            st.markdown('<div class="v6-box"><div class="v6-title">' + tn + '</div>', unsafe_allow_html=True)
            tp = []
            se_e = set()
            for e in pool:
                if any(k.lower() in e['name'].lower() for k in tk): tp.append(e); se_e.add(e['symbol'])
            for r, itm in enumerate(tp[:10]):
                pk = f"mw_{tn}_{itm['symbol']}_{r+1}"
                is_t = any(p['symbol'] == itm['symbol'] for p in portfolio)
                rc = st.columns([0.3, 2.0, 3.8, 1.3, 1.4])
                with rc[0]:
                    st.markdown(f'<div style="height:36px;display:flex;align-items:center;font-weight:900;color:#8B949E;font-size:12px;">{r+1}</div>', unsafe_allow_html=True)
                with rc[1]:
                    st.markdown(f'<div style="height:36px;display:flex;align-items:center;font-weight:900;color:#8B949E;font-size:11px;">{itm["issuer"]}</div>', unsafe_allow_html=True)
                with rc[2]:
                    st.markdown(f'<div style="height:36px;display:flex;align-items:center;font-weight:700;font-size:12px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{itm["name"][:20]}</div>', unsafe_allow_html=True)
                with rc[3]:
                    st.markdown(f'<div style="height:36px;display:flex;align-items:center;justify-content:flex-end;font-weight:900;color:#39FF14;font-size:12px;">{itm["price_at_listing"]:,}</div>', unsafe_allow_html=True)
                with rc[4]:
                    if is_t:
                        if st.button("추적 해제", key=f"utk_{pk}"):
                            portfolio = [p for p in portfolio if p['symbol'] != itm['symbol']]; s_j('data/user_portfolio.json', portfolio); st.rerun()
                    else:
                        if st.button("추적 시작", key=f"tk_{pk}"):
                            portfolio.append({"symbol":itm['symbol'], "name":itm['name'], "purchase_price":itm['price_at_listing'], "current_price":itm['price_at_listing']})
                            s_j('data/user_portfolio.json', portfolio); st.rerun()
                if r < 9: st.markdown('<div style="border-bottom:1px solid #282E36;margin:0;"></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# Tab 2: Upcoming
with tabs[1]:
    st.markdown("<div class='cal-header'>상장 예정 하이퍼 자산 (NEXT 7 DAYS)</div>", unsafe_allow_html=True)
    c2 = st.columns(4)
    for i, itm in enumerate(upcs[:8]):
        with c2[i%4]:
            st.markdown(f'<div class="cal-item"><div style="font-size:10px;color:#8B949E;font-weight:700;">{itm["issuer"]} | {itm["ticker"]}</div><div style="font-size:14px;font-weight:900;margin:8px 0;height:40px;overflow:hidden;">{itm["name"]}</div><div style="font-size:12px;color:#39FF14;font-weight:900;">시작가: 10,000원</div><div style="font-size:11px;color:#FFFF33;margin-top:10px;">상장일: {itm["listing_date"]}</div></div>', unsafe_allow_html=True)

# Tab 3: Risk Control Room
with tabs[2]:
    if not portfolio: st.info("추적 중인 자산이 없습니다. 시장 감시 탭에서 자산을 추가하십시오.")
    for p in portfolio:
        l_r = calculate_loss_rate(p.get('purchase_price',0), p.get('current_price',0))
        st.markdown(f"<div style='background:#161B22;border:1px solid {'#FF3131' if l_r <= -10 else '#30363D'};padding:15px;border-radius:10px;margin-bottom:10px;display:flex;justify-content:space-between;align-items:center;'><div><span style='color:#8B949E;font-size:12px;'>{p.get('issuer','Unknown')}</span><br><b style='font-size:16px;'>{p['name']}</b></div><div style='text-align:right;'><span style='color:{'#FF3131' if l_r <= -10 else '#39FF14'};font-size:20px;font-weight:900;'>{l_r:.2f}%</span><br><span style='font-size:12px;color:#8B949E;'>상태: {'긴급 대응 요구' if l_r <= -10 else '안정권'}</span></div></div>", unsafe_allow_html=True)

# Footer
st.markdown("<div style='color:#484F58;font-size:11px;text-align:center;margin-top:100px;'>하이퍼 ETF 가디언 v6.7 [최종 마스터 빌드]<br>숙청 완료: 사이드바 제거 / 지휘소 무결성 복구 완료 / 지능: 제미나이 2.0 플래시</div>", unsafe_allow_html=True)
