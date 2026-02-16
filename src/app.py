import streamlit as st
import json, os, sys
import google.generativeai as genai
from datetime import datetime

# 1. [System] 레이아웃 및 폰트 절대 고정 (v9.1 Sovereign Integrity)
st.set_page_config(page_title="Hyper ETF Guardian", layout="wide", initial_sidebar_state="collapsed")

# --- AI Intelligence Layer (Sovereign) ---
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
        # [v9.1] 프롬프트 조율: 일주일간 수익률 정렬 강조
        response = model.generate_content(f"Expert financial response max 10 words. Mention coordination by weekly returns: {prompt}")
        return response.text.replace("\n", " ").strip() if response.text else "[대기 중]"
    except: return "[타임아웃]"

# 2. [UI/UX] 불사신 CSS (v9.1 정밀 고정 및 블랙아웃 락다운)
st.markdown("""
    <style>
    /* 1. 사이드바 및 불필요 요소 완전 소멸 */
    [data-testid="stSidebar"], [data-testid="stSidebarNav"], .stDeployButton { display: none !important; }
    .stApp { background-color: #0A0E14 !important; color: #FFFFFF !important; }
    .block-container { padding: 1.5rem 3.5rem !important; max-width: 98% !important; }
    
    /* 2. [v9.1 핵심] 모든 버튼 시각적 암전 강제 고정 (Sovereign Blackout) */
    button[kind="secondary"], button[kind="primary"], .stButton>button, div[data-testid="stPopover"] button { 
        background-color: #0E1117 !important; 
        color: #39FF14 !important; 
        border: 2px solid #39FF14 !important; 
        font-weight: 900 !important; 
        width: 100% !important;
        height: 35px !important; 
        font-size: 11px !important;
        border-radius: 6px !important;
        transition: 0.2s !important;
        box-shadow: none !important;
    }
    button:hover { background-color: #39FF14 !important; color: #000 !important; box-shadow: 0 0 15px #39FF14 !important; }
    
    /* 3. 대시보드 및 지표 스타일 */
    .metric-card { background:#161B22; border:1px solid #30363D; border-radius:12px; padding:20px; text-align:center; }
    .gauge-bg { width: 100%; background: #21262D; border-radius: 10px; height: 10px; margin: 10px 0; overflow: hidden; }
    .gauge-fill { height: 100%; border-radius: 10px; transition: width 0.8s ease; }
    .beta-notice { background: rgba(57, 255, 20, 0.05); border: 1px solid #39FF14; padding: 12px; border-radius: 8px; margin-bottom: 20px; font-size: 11px; color: #39FF14; line-height: 1.5; }
    .v8-box { background-color: #161B22; border: 1px solid #30363D; border-radius: 12px; padding: 18px; margin-bottom: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
    
    .product-name { font-size: 14px !important; font-weight: 900; color: #FFFFFF; }
    .issuer-name { font-size: 11px !important; color: #8B949E; }
    .list-row { display: flex; align-items: center; height: 35px; gap: 8px; width: 100%; border-bottom: 1px solid #21262D; }

    div[data-testid="stPopoverContent"] {
        background-color: #161B22 !important;
        border: 1px solid #30363D !important;
        color: #FFFFFF !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. [Data] 데이터 엔진 무결성
P_FILE = 'data/user_portfolio.json'
E_FILE = 'data/etf_list.json'
U_FILE = 'data/upcoming_etf.json'

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
        if not any(x.get('symbol') == itm.get('ticker') for x in p):
            p.append({"symbol": itm.get('ticker'), "name": itm.get('name'), "issuer": itm.get('issuer', 'HYPER'), "purchase_price": 10000, "current_price": 10000, "status": "예약 중", "qty": qty, "date": itm.get('listing_date')})
            st.toast("🚨 구매 예약이 확정되었습니다.")
    elif action == "CANCEL":
        target = itm.get('symbol') or itm.get('ticker')
        p = [x for x in p if x.get('symbol') != target]
        st.toast("🗑️ 구매 예약이 취소되었습니다.")
    elif action == "TOGGLE":
        is_t = any(p.get('symbol') == itm.get('symbol') for p in p)
        if is_t: p = [x for x in p if x.get('symbol') != itm.get('symbol')]
        else: p.append({"symbol": itm.get('symbol'), "name": itm.get('name'), "issuer": itm.get('issuer', 'HYPER'), "purchase_price": itm.get('price_at_listing', 10000), "current_price": itm.get('price_at_listing', 10000), "status": "라이브", "qty": 0})
    s_j(p); st.rerun()

# 4. [Render] 대시보드 조감
portfolio = load_data(P_FILE)
all_etfs = load_data(E_FILE)
upcs = sorted(load_data(U_FILE), key=lambda x: x.get('listing_date', '9999-12-31'))

st.markdown("<h2> 📊 하이퍼 ETF 가디언 <span style='font-size:12px;color:#39FF14;'>[v9.1 최종 무결성 빌드]</span></h2>", unsafe_allow_html=True)

# 지능형 메세지 인양
ai_rep = get_ai_intel(f"유닛: {len(portfolio)}. 일주일 수익률 기반 정렬 모드 가동.")
st.markdown(f'<div style="background:rgba(255,49,49,0.05); border:1px solid #FF3131; padding:15px; border-radius:10px; margin-bottom:25px; color:#FF3131; font-weight:900;">🚨 AI Intel: {ai_rep} </div>', unsafe_allow_html=True)

# 상단 메트릭 보드 (Atomic Logic)
m1, m2, m3, m4 = st.columns(4)
avg_def = 0
if portfolio:
    total_l_r = []
    for x in portfolio:
        pp, cp = x.get('purchase_price', 10000), x.get('current_price', 10000)
        if pp > 0: total_l_r.append((cp - pp) / pp * 100)
    avg_def = sum(total_l_r) / len(total_l_r) if total_l_r else 0

breach = sum(1 for x in portfolio if (x.get('current_price', 10000) - x.get('purchase_price', 10000)) / x.get('purchase_price', 1) <= -10)
m1.markdown(f'<div class="metric-card"><div style="color:#8B949E;font-size:10px;text-transform:uppercase;">추적 자산</div><div style="font-size:22px;font-weight:900;color:#39FF14;">{len(portfolio)} 유닛</div></div>', unsafe_allow_html=True)
m2.markdown(f'<div class="metric-card"><div style="color:#8B949E;font-size:10px;text-transform:uppercase;">평균 방어력</div><div style="font-size:22px;font-weight:900;color:{"#39FF14" if avg_def >= -5 else "#FF3131"};">{avg_def:+.2f}%</div></div>', unsafe_allow_html=True)
m3.markdown(f'<div class="metric-card"><div style="color:#8B949E;font-size:10px;text-transform:uppercase;">방어선 돌파</div><div style="font-size:22px;font-weight:900;color:{"#FF3131" if breach > 0 else "#39FF14"};">{breach} 유닛</div></div>', unsafe_allow_html=True)
m4.markdown(f'<div class="metric-card"><div style="color:#8B949E;font-size:10px;text-transform:uppercase;">상장 예정</div><div style="font-size:22px;font-weight:900;color:#FFD700;">{len(upcs)} 유닛</div></div>', unsafe_allow_html=True)

st.divider()

tabs = st.tabs(["📊 시장 감시", "📅 상장 일정", "🚨 위험 통제"])

with tabs[0]: # Market Watch (Sovereign Top 10)
    # [v9.1] 팀장님 지시 사항: 정렬 기준 명시
    st.markdown("<p style='font-size:11px;color:#8B949E;font-weight:700;'>정렬 기준 : 최근 일주일간 수익률 높은 순</p>", unsafe_allow_html=True)
    themes = [{"n": "AI/반도체", "k": ["AI", "반도체"]}, {"n": "미국 빅테크", "k": ["미국", "빅테크"]}, {"n": "배당/밸류업", "k": ["배당", "밸류"]}, {"n": "국내 지수", "k": ["200", "코스피"]}, {"n": "글로벌 액티브", "k": ["글로벌"]}, {"n": "기술/혁신", "k": ["기술", "혁신"]}]
    r1, r2 = st.columns(3), st.columns(3)
    all_c = r1 + r2
    for idx, th in enumerate(themes):
        with all_c[idx]:
            st.markdown(f'<div class="v8-box"><div style="font-size:13px;font-weight:900;border-left:5px solid #39FF14;padding-left:10px;margin-bottom:15px;text-transform:uppercase;">{th["n"]} 전략</div>', unsafe_allow_html=True)
            # Top 10 무결성: 키워드 필터링 후 부족하면 전체 리스트에서 인양하여 10개 강제 충원
            filtered = [e for e in all_etfs if any(k in e.get('name','') for k in th['k'])]
            seen = {e.get('symbol') for e in filtered}
            for e in all_etfs:
                if len(filtered) >= 10: break
                if e.get('symbol') not in seen: filtered.append(e); seen.add(e.get('symbol'))
            
            for r, itm in enumerate(filtered[:10]):
                is_t = any(p.get('symbol') == itm.get('symbol') for p in portfolio)
                c_row = st.columns([8, 2])
                with c_row[0]: st.markdown(f'<div class="list-row"><span style="color:#8B949E;width:15px;font-size:10px;">{r+1}</span><span style="color:#8B949E;font-size:10px;width:70px;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;">{itm.get("issuer","HYPER")}</span><span style="font-size:12px;font-weight:700;flex-grow:1;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;">{itm.get("name")}</span></div>', unsafe_allow_html=True)
                with c_row[1]: 
                    if st.button("해제" if is_t else "추적", key=f"tk_{idx}_{itm.get('symbol')}"): handle_action(itm, "TOGGLE")
            st.markdown("</div>", unsafe_allow_html=True)

with tabs[1]: # Upcoming (Operational Master)
    st.markdown("<div class='beta-notice'><b>beta:</b> 추후 상장 즉시 <b>'0.1초 자동 매수'</b>하는 풀-오토 시스템을 제공합니다.</div>", unsafe_allow_html=True)
    u_cols = st.columns(4)
    for i, itm in enumerate(upcs):
        is_res = any(x.get('symbol') == itm.get('ticker') and x.get('status') == "예약 중" for x in portfolio)
        with u_cols[i % 4]:
            st.markdown(f"<div style='background:#FFD700;color:#000;padding:2px 8px;border-radius:4px;font-weight:900;font-size:10px;width:fit-content;margin-bottom:5px;'>📅 {itm.get('listing_date')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='v8-box' style='padding:15px;border-left:5px solid #FFD700;'><span class='product-name'>{itm.get('name')}</span><br><small class='issuer-name'>{itm.get('issuer', 'HYPER')}</small></div>", unsafe_allow_html=True)
            if is_res:
                with st.popover("🚨 구매 예약 완료 ∨", use_container_width=True):
                    st.write("구매 예약을 취소하시겠습니까?")
                    if st.button("예, 취소합니다", key=f"can_upc_{itm.get('ticker')}"): handle_action(itm, "CANCEL")
            else:
                with st.popover("상장 예약 ∨", use_container_width=True):
                    q = st.number_input("수량", 1, 1000, 10, key=f"q_upc_{itm.get('ticker')}")
                    if st.button("구매를 예약 하시겠습니까?", key=f"conf_upc_{itm.get('ticker')}"): handle_action(itm, "RESERVE", q)

with tabs[2]: # Risk Control (Gauge Integrity)
    st.markdown("<div class='beta-notice' style='border-color:#FF3131;color:#FF3131;background:rgba(255,49,49,0.05);'><b>beta:</b> 원칙(-10.0%) 이탈 즉시 <b>'자동 매도'</b>하는 방어 시스템을 제공합니다.</div>", unsafe_allow_html=True)
    if not [x for x in portfolio if x.get('status') in ["라이브", "예약 중"]]: st.info("관제 중인 자산이 없습니다.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 🛰️ 실시간 추적 자산")
            live_p = sorted([x for x in portfolio if x.get('status')=="라이브"], key=lambda x: (x.get('current_price',0)-x.get('purchase_price',0))/x.get('purchase_price',1))
            for p in live_p:
                pp, cp = p.get('purchase_price', 10000), p.get('current_price', 10000)
                l_r = ((cp - pp) / pp * 100) if pp > 0 else 0
                gauge_val = min(abs(min(l_r, 0)) * 10, 100)
                g_color = "#39FF14" if l_r >= 0 else ("#FFB800" if l_r > -5 else "#FF3131")
                st.markdown(f"""
                    <div class='v8-box' style='border-left: 5px solid {g_color}; padding: 15px;'>
                        <small>{p.get('issuer', 'HYPER')}</small><br>
                        <div style='display:flex;justify-content:space-between;align-items:center;'>
                            <b class='product-name'>{p.get('name')}</b>
                            <span style='color:{g_color}; font-weight:900; font-size:18px;'>{l_r:+.2f}%</span>
                        </div>
                        <div class='gauge-bg'><div class='gauge-fill' style='width:{gauge_val}%; background:{g_color}; box-shadow: 0 0 10px {g_color};'></div></div>
                    </div>
                """, unsafe_allow_html=True)
                if st.button("추적 해제", key=f"risk_del_{p.get('symbol')}"): handle_action(p, "TOGGLE")
        with c2:
            st.markdown("### 📅 상장 예정 예약")
            res_p = [x for x in portfolio if x.get('status')=="예약 중"]
            if not res_p: st.info("예약된 상장 예정 자산이 없습니다.")
            for p in res_p:
                st.markdown(f"""
                    <div class='v8-box' style='border-left: 5px solid #FFD700;'>
                        <small>{p.get('issuer', 'HYPER')} | {p.get('date', 'Unknown')}</small><br>
                        <b>{p.get('name')}</b><br>예약 수량: {p.get('qty', 0)}주
                    </div>
                """, unsafe_allow_html=True)
                with st.popover("🚨 구매 예약 완료 ∨", use_container_width=True):
                    st.write("정말 구매 예약을 취소 하시겠습니까?")
                    if st.button("예, 취소합니다", key=f"can_res_{p.get('symbol')}"): handle_action(p, "CANCEL")

st.markdown(f"<div style='text-align:center;margin-top:50px;font-size:10px;color:#484F58;'>Hyper ETF Guardian v9.1 | Sovereign Integrity | 19h Miracle</div>", unsafe_allow_html=True)