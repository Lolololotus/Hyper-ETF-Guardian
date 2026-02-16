import streamlit as st
import json
import os
import sys
import google.generativeai as genai
from datetime import datetime, timedelta

# Ensure src is in path for imports
sys.path.append(os.path.join(os.path.dirname(__file__)))
from monitor import calculate_loss_rate

# Final Mastery Configuration
st.set_page_config(page_title="Hyper ETF Guardian", layout="wide", initial_sidebar_state="expanded")

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
        # Optimized for Vercel 10s Timeout: Zero-Latency Prompting
        sys_p = "Expert. Response: [R:X/C:Y/R:Z]. Max 15 words."
        response = model.generate_content(f"{sys_p}\n\n{prompt}")
        if not response or not response.text: return "[위험: 5.0 / 원인: 대기 중 / 권고: 수동 확인]"
        return response.text.replace("\n", " ").strip()
    except Exception: return "[위험: 5.0 / 원인: 타임아웃 / 권고: 수동 확인]"

# --- Absolute Physical Constraint Mastery: [v6.5 FULL LOCALIZATION] ---
def m(h): return h.replace("\n", "").strip()

st.markdown(m(f"""
<style>
/* Global Lockdown & Typography */
.stApp {{background-color: #0A0E14 !important; color: #FFFFFF !important;}}
h1,h2,h3,h4,h5,h6,p,span,label,div,li {{color: #FFFFFF !important; font-family: 'Inter', sans-serif !important; letter-spacing: -0.5px !important;}}

/* Master Box: Final Space Liberation v6.4 (Legacy) / v6.5 Refined */
.v6-box {{background-color: #161B22 !important; border: 1px solid #30363D !important; border-radius: 12px; padding: 25px !important; margin-bottom: 80px !important; box-shadow: 0 8px 16px rgba(0,0,0,0.5); overflow: hidden !important;}}
.v6-title {{font-size: 16px; font-weight: 900; margin-bottom: 25px; color: #FFFFFF !important; border-left: 5px solid #39FF14; padding-left: 15px; text-transform: uppercase; white-space: nowrap !important;}}

/* Row Protocol: Physical No-Wrap */
.v6-row {{display: flex; justify-content: space-between; align-items: center; width: 100%; height: 44px; white-space: nowrap !important; overflow: hidden !important;}}
.v6-item {{display: flex; align-items: center; white-space: nowrap !important; overflow: hidden !important; height: 36px;}}
.v6-ellipsis {{overflow: hidden !important; text-overflow: ellipsis !important; white-space: nowrap !important;}}

/* Button Force: v6.5 Localization Optimization */
.stButton>button {{background-color: #1E2329 !important; color: #FFFFFF !important; border: 1px solid #484F58 !important; font-weight: 900 !important; min-height: 34px !important; border-radius: 6px !important; font-size: 10px !important; letter-spacing: -0.8px !important; transition: all 0.1s ease; width: 100% !important; min-width: 90px !important; padding: 0 8px !important; white-space: nowrap !important; overflow: visible !important;}}
.stButton>button:hover {{background-color: #30363D !important; border-color: #39FF14 !important; color: #39FF14 !important; opacity: 0.9;}}

/* Upcoming Terminal */
.cal-header {{font-size: 16px; font-weight: 900; color: #39FF14 !important; border-bottom: 2px solid #39FF14; padding: 12px 0; margin-bottom: 0px;}}
.cal-item {{background: #161B22; border: 1px solid #30363D; border-radius: 10px; padding: 22px; margin-top: 15px; border-left: 5px solid #FFFF33; min-height: 190px; overflow: hidden;}}

/* Risk Panel */
.risk-box {{background: rgba(255,49,49,0.05); border: 1px solid #FF3131; padding: 20px; border-radius: 10px; margin-bottom: 35px; color: #FF3131 !important; font-weight: 900; font-size: 14px;}}

#MainMenu, footer, .stDeployButton {{display: none !important;}}
div.block-container {{padding-top: 2rem !important;}}
</style>
"""), unsafe_allow_html=True)

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
st.markdown(m("<h2 style='margin:0;'>📊 하이퍼 ETF 가디언 <span style='font-size:12px;color:#39FF14;font-weight:400;'>[v6.5 최종 마스터]</span></h2>"), unsafe_allow_html=True)
st.markdown(m("<p style='color:#8B949E;font-size:13px;margin:-5px 0 20px 0;'>정비 완료. 한국형 자산 방어 관제탑 v6.5.</p>"), unsafe_allow_html=True)

d_c = len([p for p in portfolio if p.get('status') == '위험'])
ai_rep = get_ai_intel(f"유닛: {len(portfolio)} | 위험 자산: {d_c}. 현지화 완료.")
st.markdown(m(f'<div class="risk-box">🚨 {ai_rep} </div>'), unsafe_allow_html=True)

met = st.columns(4)
def m_b(l,v,c="#39FF14"): return f'<div style="background:#161B22;border:1px solid #30363D;border-radius:12px;padding:20px;text-align:center;"><div style="color:#8B949E;font-size:10px;margin-bottom:8px;font-weight:700;">{l}</div><div style="font-size:22px;font-weight:900;color:{c};">{v}</div></div>'
met[0].markdown(m(m_b("추적 자산", f"{len(portfolio)} 유닛")), unsafe_allow_html=True)
sh = sum(calculate_loss_rate(p.get('purchase_price',10000)*0.95, p.get('purchase_price',10000)) for p in portfolio) / len(portfolio) if portfolio else 0
met[1].markdown(m(m_b("평균 방어력", f"{sh:+.2f}%", "#FF3131" if sh<0 else "#39FF14")), unsafe_allow_html=True)
met[2].markdown(m(m_b("방어선 돌파", f"{d_c} 유닛", "#FF3131" if d_c else "#39FF14")), unsafe_allow_html=True)
met[3].markdown(m(m_b("상장 예정", f"{len(upcs)} 유닛", "#FFFF33")), unsafe_allow_html=True)

st.divider()

# --- Sidebar ---
with st.sidebar:
    st.header("🛠️ 시스템 관제")
    isrs = ["KODEX", "TIGER", "KBSTAR", "ACE", "SOL"]
    s_is = [i for i in isrs if st.checkbox(i, key=f"s_{i}")]
    f_is = s_is if s_is else isrs
    pool = [e for e in etfs if any(i in e['issuer'] for i in f_is)]
    if not pool: pool = etfs[:50]
    if st.button("데이터 초기화"): s_j('data/user_portfolio.json', []); st.rerun()

# --- Strategic Dashboard (Tabs) ---
tabs = st.tabs(["📊 시장 감시", "📅 상장 일정", "🚨 위험 통제"])

# Tab 1: Market Watch (5-Stage Master Ratio Protocol)
with tabs[0]:
    themes = {
        "AI 및 반도체 핵심 전략": ["AI", "반도체", "NVIDIA", "HBM"],
        "미국 빅테크 핵심 자산": ["미국", "빅테크", "나스닥", "S&P"],
        "밸류업 및 배당 가치 전략": ["밸류업", "저PBR", "배당", "인컴"],
        "미래 기술 혁신 전략": ["양자", "우주", "에너지", "바이오"],
        "글로벌 인프라 및 에너지": ["인프라", "원자력", "에너지"],
        "바이오 및 헬스케어 전략": ["바이오", "제약", "헬스케어"]
    }
    th_l = list(themes.items())
    for i in range(0, len(th_l), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(th_l):
                tn, tk = th_l[i+j]
                with cols[j]:
                    st.markdown(m(f'<div class="v6-box"><div class="v6-title">{tn}</div>'), unsafe_allow_html=True)
                    tp = []
                    se_e = set()
                    for e in pool:
                        if any(k.lower() in e['name'].lower() for k in tk): tp.append(e); se_e.add(e['symbol'])
                    if len(tp) < 10:
                        for e in pool:
                            if e['symbol'] not in se_e: tp.append(e); se_e.add(e['symbol'])
                            if len(tp) >= 10: break
                    
                    for r, itm in enumerate(tp[:10]):
                        pk = f"mw_{tn}_{itm['symbol']}_{r+1}"
                        is_t = any(p['symbol'] == itm['symbol'] for p in portfolio)
                        rc = st.columns([0.3, 2.0, 3.5, 1.5, 1.5])
                        rc[0].markdown(m(f'<div style="height:36px;display:flex;align-items:center;font-weight:900;color:#8B949E;font-size:12px;">{r+1}</div>'), unsafe_allow_html=True)
                        rc[1].markdown(m(f'<div style="height:36px;display:flex;align-items:center;font-weight:900;color:#8B949E;font-size:11px;">{itm["issuer"]}</div>'), unsafe_allow_html=True)
                        rc[2].markdown(m(f'<div style="height:36px;display:flex;align-items:center;font-weight:700;font-size:12px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{itm["name"][:16]}</div>'), unsafe_allow_html=True)
                        rc[3].markdown(m(f'<div style="height:36px;display:flex;align-items:center;justify-content:flex-end;font-weight:900;color:#39FF14;font-size:12px;">{itm["price_at_listing"]:,}</div>'), unsafe_allow_html=True)
                        with rc[4]:
                            if is_t:
                                if st.button("추적 해제", key=f"utk_{pk}"):
                                    portfolio = [p for p in portfolio if p['symbol'] != itm['symbol']]; s_j('data/user_portfolio.json', portfolio); st.rerun()
                            else:
                                if st.button("추적 시작", key=f"tk_{pk}"):
                                    portfolio.append({"symbol":itm['symbol'], "name":itm['name'], "purchase_price":itm['price_at_listing'], "status":"추적 중"})
                                    s_j('data/user_portfolio.json', portfolio); st.rerun()
                        if r < 9: st.markdown(m('<div style="border-bottom:1px solid #282E36;margin:0;"></div>'), unsafe_allow_html=True)
                    st.markdown(m('</div>'), unsafe_allow_html=True)

# Tab 2: Upcoming (5-Section Terminal)
with tabs[1]:
    m_st = datetime.now() - timedelta(days=datetime.now().weekday())
    w_d = ["월요일", "화요일", "수요일", "목요일", "금요일"]; u_g = st.columns(5)
    for k in range(5):
        dv = (m_st + timedelta(days=k)).strftime("%Y-%m-%d")
        with u_g[k]:
            st.markdown(m(f'<div class="cal-header">{w_d[k]} ({dv})</div>'), unsafe_allow_html=True)
            ui = [e for e in upcs if e['listing_date'] == dv]
            if not ui: st.markdown(m("<div style='font-size:11px;color:#484F58;padding:40px;text-align:center;'>상장 일정 없음</div>"), unsafe_allow_html=True)
            for m_i, itm in enumerate(ui):
                with st.container():
                    pr = next((p for p in portfolio if p['symbol'] == itm['ticker']), None)
                    st.markdown(m(f'<div class="cal-item"><div style="font-size:10px;color:#8B949E;font-weight:700;">{itm["issuer"]} | {itm["ticker"]}</div><div style="font-size:14px;font-weight:900;margin:8px 0;height:40px;overflow:hidden;">{itm["name"]}</div><div style="font-size:12px;color:#39FF14;font-weight:900;">시작가: 10,000원</div>'), unsafe_allow_html=True)
                    if pr:
                        st.markdown(m(f"<div style='font-size:11px;color:#FFFF33;font-weight:900;margin-top:10px;'>🔢 예약 수량: {pr.get('quantity', 0)} 주</div>"), unsafe_allow_html=True)
                        if st.button("예약 취소", key=f"can_{itm['ticker']}_{k}"):
                            portfolio = [p for p in portfolio if p['symbol'] != itm['ticker']]; s_j('data/user_portfolio.json', portfolio); st.rerun()
                    else:
                        rk = f"r_a_{itm['ticker']}"
                        if not st.session_state.get(rk):
                            if st.button("상장 예약", key=f"pre_{itm['ticker']}_{k}"): st.session_state[rk]=True; st.rerun()
                        else:
                            qv = st.number_input("수량(주)", min_value=1, value=10, step=1, key=f"q_{itm['ticker']}")
                            b1, b2 = st.columns(2)
                            if b1.button("예약 확정", key=f"d1_{itm['ticker']}"):
                                portfolio.append({"symbol":itm['ticker'], "name":itm['name'], "quantity":qv, "status":"대기", "listing_date":itm['listing_date']})
                                s_j('data/user_portfolio.json', portfolio); st.session_state[rk]=False; st.rerun()
                            if b2.button("뒤로", key=f"d2_{itm['ticker']}"): st.session_state[rk]=False; st.rerun()
                    st.markdown(m('</div>'), unsafe_allow_html=True)

# Tab 3: Control Room
with tabs[2]:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(m('<div style="font-size:16px;font-weight:900;margin-bottom:20px;border-left:5px solid #FF3131;padding-left:12px;">⚠️ 집중 감시 자산</div>'), unsafe_allow_html=True)
        au = []
        for p in portfolio:
            if p['status'] != '대기':
                bp = p.get('purchase_price', 10000); cp = bp * (0.95 if p['status'] == '추적 중' else 0.88)
                p['lr'] = calculate_loss_rate(cp, bp); p['cv'] = cp
                au.append(p)
        au.sort(key=lambda x: x['lr'])
        if not au: st.info("활성 위험 유닛 없음.")
        for idx, itm in enumerate(au):
            lr = itm['lr']
            st.markdown(m(f'<div class="v6-box" style="padding:22px;margin-bottom:20px;"><div style="display:flex;justify-content:space-between;align-items:center;"><div><span style="background:{"#FF3131" if lr<=-8 else "#39FF14"};color:#0A0E14;padding:2px 8px;border-radius:4px;font-size:10px;font-weight:900;margin-right:12px;">{itm["status"]}</span><b style="font-size:16px;">{itm["name"]}</b></div><div style="font-size:24px;font-weight:900;color:{"#FF3131" if lr<=-8 else "#39FF14"};">{lr:+.1f}%</div></div>'), unsafe_allow_html=True)
            rs = 10.0 + lr; wf = min(100, (abs(lr)/10.0)*100); rc = "#39FF14" if rs>5 else "#FFA500" if rs>2 else "#FF3131"
            st.markdown(m(f'<div style="font-size:10px;color:#8B949E;margin-top:10px;">방어선 잠식: {abs(lr):.1f}% | 건전성: {rs:+.1f}%</div><div style="width:100%;height:8px;background:#21262D;border-radius:4px;margin-top:8px;"><div style="width:{wf}%;height:100%;background:{rc};border-radius:4px;"></div></div>'), unsafe_allow_html=True)
            if st.button("감시 종료", key=f"ki_{itm['symbol']}"):
                portfolio = [p for p in portfolio if p['symbol'] != itm['symbol']]; s_j('data/user_portfolio.json', portfolio); st.rerun()
            st.markdown(m('</div>'), unsafe_allow_html=True)
    with c2:
        st.markdown(m('<div style="font-size:16px;font-weight:900;margin-bottom:20px;border-left:5px solid #FFFF33;padding-left:12px;">⏳ 예약 대기 유닛</div>'), unsafe_allow_html=True)
        pu = [p for p in portfolio if p['status'] == '대기']
        pu.sort(key=lambda x: x.get('listing_date', '9999-12-31'))
        if not pu: st.info("대기 큐 비어있음.")
        for idx, itm in enumerate(pu):
            st.markdown(m(f'<div class="v6-box" style="padding:22px;margin-bottom:20px;"><div style="display:flex;justify-content:space-between;align-items:center;"><div><span style="background:#FFFF33;color:#0A0E14;padding:2px 8px;border-radius:4px;font-size:10px;font-weight:900;margin-right:12px;">상장 대기</span><b style="font-size:16px;">{itm["name"]}</b></div><div style="font-size:12px;color:#8B949E;text-align:right;">📅 일자: {itm.get("listing_date")}<br>🔢 수량: {itm.get("quantity",0)} 주</div></div>'), unsafe_allow_html=True)
            if st.button("예약 취소", key=f"ab_{itm['symbol']}"):
                portfolio = [p for p in portfolio if p['symbol'] != itm['symbol']]; s_j('data/user_portfolio.json', portfolio); st.rerun()
            st.markdown(m('</div>'), unsafe_allow_html=True)

st.markdown(m("<div style='color:#484F58;font-size:11px;text-align:center;margin-top:100px;'>하이퍼 ETF 가디언 v6.5 [최종 마스터 빌드]<br>마스터 비율 레이아웃 / 지능: 제미나이 2.0 플래시</div>"), unsafe_allow_html=True)
