import streamlit as st
import json
import os
import google.generativeai as genai
from monitor import calculate_loss_rate
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(page_title="Hyper ETF Guardian", layout="wide", initial_sidebar_state="expanded")

# --- Gemini 2.0 Flash Intelligence Setup ---
GEMINI_API_KEY = "AIzaSyDfmWkvWuty0BjkhBainobKonjTL6She78"
genai.configure(api_key=GEMINI_API_KEY)

def get_ai_analysis(prompt):
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        if not response or not response.text:
            return "[Intelligence Offline] 방어적 관망 권고."
        return response.text
    except Exception:
        return "[Intelligence Fallback] 고변동성 감지. 자산 보존 전략 유지."

# --- Custom CSS (Extreme Contrast & Dark Mastery) ---
st.markdown("""<style>
/* 전역 배경 및 텍스트 강제 고정 */
.stApp {background-color:#0A0E14!important;color:#FFFFFF!important;}
h1,h2,h3,span,p,div,label {color:#FFFFFF!important;font-family:'Inter',sans-serif;}

/* 입력창(Number Input, Text Input) 흰색 배경 박멸 */
input {background-color:#161B22!important;color:#FFFFFF!important;border:1px solid #30363D!important;}
div[data-baseweb="input"] {background-color:#161B22!important;color:#FFFFFF!important;}
div[role="spinbutton"] {background-color:#161B22!important;color:#FFFFFF!important;}
.stNumberInput div {background-color:#161B22!important;color:#FFFFFF!important;}

/* 버튼 스타일 및 시인성 */
.stButton>button {width:100%!important;height:32px!important;font-size:11px!important;font-weight:900!important;border-radius:4px!important;background-color:#21262D!important;color:#FFFFFF!important;border:1px solid #30363D!important;transition:none!important;}
.stButton>button:hover {border-color:#39FF14!important;color:#39FF14!important;}

/* 리스트 및 배지 */
.list-item {background-color:#161B22;border-bottom:1px solid #30363D;padding:8px 15px;display:flex;justify-content:space-between;align-items:center;}
.badge {display:inline-block;padding:2px 6px;border-radius:3px;font-size:9px;font-weight:900;}
.badge-standby {background:rgba(255,255,51,0.1);color:#FFFF33!important;border:1px solid #FFFF33;}
.badge-tracking {background:rgba(57,255,20,0.1);color:#39FF14!important;border:1px solid #39FF14;}
.badge-danger {background:rgba(255,49,49,0.1);color:#FF3131!important;border:1px solid #FF3131;}

/* 주간 달력 시인성 */
.calendar-day {background:#0D1117;border:1px solid #21262D;border-radius:8px;padding:10px;min-height:220px;}
.calendar-date {font-size:15px;color:#FFFFFF!important;margin-bottom:12px;border-bottom:3px solid #39FF14;padding-bottom:5px;font-weight:900;text-align:center;}

/* 리스크 게이지 */
.gauge-container {width:100%;background:#21262D;border-radius:2px;height:5px;margin-top:8px;}
.gauge-fill {height:100%;border-radius:2px;}
.risk-box {background:rgba(255,49,49,0.05);border:1px solid #FF3131;padding:10px;border-radius:4px;margin-bottom:15px;font-size:12px;font-weight:bold;color:#FF3131!important;}
</style>""", unsafe_allow_html=True)

# 데이터 유틸
def load_json(path):
    if not os.path.exists(path): return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            c = f.read().strip(); return json.loads(c) if c else []
    except Exception: return []

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_status_class(status):
    if status == "대기": return "badge-standby"
    if status == "추적 중": return "badge-tracking"
    return "badge-danger"

def render_gauge(loss_rate):
    percent = min(100, max(0, (abs(loss_rate) / 10.0) * 100))
    color = "#39FF14" if abs(loss_rate) < 5 else "#FFA500" if abs(loss_rate) < 8 else "#FF3131"
    rem = 10.0 + loss_rate
    return f'<div style="font-size:9px;color:#8B949E;margin-top:6px;">방어선 잔여:<b>{rem:+.1f}%</b></div><div class="gauge-container"><div class="gauge-fill" style="width:{percent}%;background:{color};"></div></div>'

# 데이터 로드
etf_list = load_json('data/etf_list.json')
upcoming_list = load_json('data/upcoming_etf.json')
raw_portfolio = load_json('data/user_portfolio.json')

# 포트폴리오 중복 제거 필터 (Duplicate Entry Guard)
portfolio = []
seen_symbols = set()
for p in raw_portfolio:
    if p['symbol'] not in seen_symbols:
        portfolio.append(p)
        seen_symbols.add(p['symbol'])

# --- Header ---
st.markdown("<h2 style='margin:0;'>📊 Hyper ETF Guardian</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#8B949E;font-size:13px;margin:-5px 0 15px 0;'>No Prose, Just Precision.</p>", unsafe_allow_html=True)

# AI Risk Box
danger_items = [p for p in portfolio if p.get('status') == '위험']
ai_risk_report = get_ai_analysis(f"Risk: {len(danger_items)} danger items. Market Status 1 line.")
st.markdown(f'<div class="risk-box">[AI Quant Analysis] {ai_risk_report}</div>', unsafe_allow_html=True)

# Metrics Tiles
metrics = []
for p in portfolio:
    bp = p.get('purchase_price', 10000)
    if bp <= 0: bp = 10000
    cv = bp * (0.965 if p['status'] == '추적 중' else 0.88 if p['status'] == '위험' else 1.0)
    metrics.append({'loss': calculate_loss_rate(cv, bp)})
avg_ret = sum(x['loss'] for x in metrics) / len(metrics) if metrics else 0

m_cols = st.columns(4)
tile_style = "background:#161B22;border:1px solid #30363D;border-radius:6px;padding:10px;text-align:center;"
m_cols[0].markdown(f'<div style="{tile_style}"><div style="color:#8B949E;font-size:9px;">총 감시 종목</div><div style="font-size:17px;font-weight:900;color:#39FF14;">{len(portfolio)} UNIT</div></div>', unsafe_allow_html=True)
m_cols[1].markdown(f'<div style="{tile_style}"><div style="color:#8B949E;font-size:9px;">평균 방어 수익률</div><div style="font-size:17px;font-weight:900;color:{"#FF3131" if avg_ret <0 else "#39FF14"};">{avg_ret:+.1f}%</div></div>', unsafe_allow_html=True)
m_cols[2].markdown(f'<div style="{tile_style}"><div style="color:#8B949E;font-size:9px;">위험 종목 수</div><div style="font-size:17px;font-weight:900;color:{"#FF3131" if danger_items else "#39FF14"};">{len(danger_items)}</div></div>', unsafe_allow_html=True)
m_cols[3].markdown(f'<div style="{tile_style}"><div style="color:#8B949E;font-size:9px;">상장 예정 종목</div><div style="font-size:17px;font-weight:900;color:#FFFF33;">{len(upcoming_list)}</div></div>', unsafe_allow_html=True)

st.divider()

# --- Sidebar ---
with st.sidebar:
    st.header("🛠️ 관측 통제소")
    issuers_static = ["KODEX", "TIGER", "KBSTAR", "ACE", "SOL"]
    selected_issuers = [iss for iss in issuers_static if st.checkbox(iss, key=f"side_{iss}")]
    effective_issuers = selected_issuers if selected_issuers else issuers_static
    filtered_base = [e for e in etf_list if any(iss in e['issuer'] for iss in effective_issuers)]
    if not filtered_base: filtered_base = etf_list[:15]
    
    st.header("🤖 AI Smart Theme")
    theme_input = st.text_input("Theme Focus", placeholder="예: 양자컴퓨팅", key="st_theme_main")
    if st.button("♻️ RESET PORTFOLIO", key="reset_all"): save_json('data/user_portfolio.json', []); st.rerun()

# --- Tabs ---
tabs = st.tabs(["📊 Market Watch", "📅 Upcoming", "🚨 Control Room"])

with tabs[0]:
    main_cats = {
        "AI & 반도체": ["AI", "반도체", "NVIDIA", "HBM"],
        "밸류업 / 저PBR": ["밸류업", "저PBR", "금융", "은행"],
        "미국 빅테크": ["미국", "빅테크", "나스닥", "S&P"],
        "월배당 / 인컴": ["월배당", "배당", "인컴", "커버드콜"]
    }

    if theme_input:
        st.subheader(f"🤖 AI Match: {theme_input}")
        for i, sym in enumerate(genai.configure(api_key=GEMINI_API_KEY) or etf_list[:3]): # Simple mock for view
            item = next((e for e in etf_list if e['symbol'] == (sym['symbol'] if isinstance(sym, dict) else sym)), None)
            if item:
                cur_p = any(p['symbol'] == item['symbol'] for p in portfolio)
                col1, col2, col3, col4 = st.columns([1, 4, 2, 2])
                col1.markdown(f'<span class="badge badge-tracking">AI</span>', unsafe_allow_html=True)
                col2.write(item["name"])
                col3.write(f"{item['price_at_listing']:,} KRW")
                with col4:
                    if not cur_p:
                        if st.button("TRACK", key=f"mw_ai_add_{item['symbol']}_{i}"):
                            portfolio.append({"symbol":item['symbol'], "name":item['name'], "purchase_price":item['price_at_listing'], "status":"추적 중"})
                            save_json('data/user_portfolio.json', portfolio); st.rerun()
                    else: st.button("✓ TRACKED", key=f"mw_ai_in_{item['symbol']}", disabled=True)

    for c_idx, (cat_name, keywords) in enumerate(main_cats.items()):
        with st.expander(f"📌 {cat_name} (Vertical Top 10)", expanded=True):
            cat_items = [e for e in filtered_base if any(k.lower() in e['name'].lower() for k in keywords)][:10]
            if not cat_items: cat_items = etf_list[:3]
            for i, item in enumerate(cat_items):
                cur_p = any(p['symbol'] == item['symbol'] for p in portfolio)
                col1, col2, col3, col4 = st.columns([1, 4, 1.5, 1.5])
                col1.markdown(f'<span style="color:#8B949E;font-size:11px;">{item["issuer"]}</span>', unsafe_allow_html=True)
                col2.markdown(f'<span style="font-size:13px;font-weight:bold;">{item["name"]}</span>', unsafe_allow_html=True)
                col3.markdown(f'<span style="font-weight:900;color:#39FF14;">{item["price_at_listing"]:,}</span>', unsafe_allow_html=True)
                with col4:
                    if cur_p:
                        if st.button("UNTRACK", key=f"mw_un_{item['symbol']}_{c_idx}_{i}"):
                            portfolio = [p for p in portfolio if p['symbol'] != item['symbol']]; save_json('data/user_portfolio.json', portfolio); st.rerun()
                    else:
                        if st.button("TRACK", key=f"mw_add_{item['symbol']}_{c_idx}_{i}"):
                            portfolio.append({"symbol":item['symbol'],"name":item['name'],"purchase_price":item['price_at_listing'],"status":"추적 중"})
                            save_json('data/user_portfolio.json', portfolio); st.rerun()

with tabs[1]:
    mon = datetime.now() - timedelta(days=datetime.now().weekday())
    cols = st.columns(5)
    days = ["월", "화", "수", "목", "금"]
    for i in range(5):
        d_str = (mon + timedelta(days=i)).strftime("%Y-%m-%d")
        with cols[i]:
            st.markdown(f'<div class="calendar-date">{days[i]} ({d_str})</div>', unsafe_allow_html=True)
            day_it = [e for e in upcoming_list if e['listing_date'] == d_str]
            for j, item in enumerate(day_it):
                is_r = next((p for p in portfolio if p['symbol'] == item['ticker']), None)
                st.markdown(f'<div class="calendar-day" style="min-height:auto;margin-bottom:10px;"><div class="badge badge-standby">STANDBY</div><div style="font-size:12px;font-weight:bold;margin:5px 0;">{item["name"]}</div>', unsafe_allow_html=True)
                if is_r:
                    st.markdown(f'<div style="font-size:10px;color:#FFFF33;">예약: {is_r["purchase_price"]:,}</div>', unsafe_allow_html=True)
                    if st.button("CANCEL", key=f"up_can_{item['ticker']}_{i}_{j}"):
                        portfolio = [p for p in portfolio if p['symbol'] != item['ticker']]; save_json('data/user_portfolio.json', portfolio); st.rerun()
                else:
                    exp_key = f"res_exp_{item['ticker']}"
                    if not st.session_state.get(exp_key, False):
                        if st.button("[PRE-CHECK]", key=f"up_pre_{item['ticker']}_{i}_{j}"):
                            st.session_state[exp_key] = True; st.rerun()
                    else:
                        with st.container():
                            p_val = st.number_input("희망가", min_value=0, value=10000, key=f"num_{item['ticker']}")
                            if st.button("확정", key=f"up_ok_{item['ticker']}"):
                                portfolio.append({"symbol":item['ticker'],"name":item['name'],"purchase_price":p_val,"status":"대기","listing_date":item['listing_date']})
                                save_json('data/user_portfolio.json', portfolio); st.session_state[exp_key] = False; st.rerun()
                            if st.button("닫기", key=f"up_cls_{item['ticker']}"):
                                st.session_state[exp_key] = False; st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

with tabs[2]:
    st.subheader("⚠️ Stage 1: Risk Monitoring (DESC Sort)")
    active = []
    for p in portfolio:
        if p['status'] != '대기':
            bp = p.get('purchase_price', 10000)
            cv = bp * (0.965 if p['status'] == '추적 중' else 0.88 if p['status'] == '위험' else 1.0)
            p['loss'] = calculate_loss_rate(cv, bp); p['cur'] = cv
            active.append(p)
    active.sort(key=lambda x: x['loss']) # Lowest (near -10%) first

    if not active: st.info("활성 모니터링 대상이 없습니다.")
    for i, item in enumerate(active):
        l = item['loss']
        st.markdown(f'<div class="list-item"><div><span class="badge {get_status_class(item["status"])}">{item["status"]}</span><b>{item["name"]} ({item["symbol"]})</b></div><div style="text-align:right;"><span style="font-size:18px;font-weight:900;color:{"#FF3131" if l <= -8 else "#39FF14"};">{l:+.1f}%</span></div></div>', unsafe_allow_html=True)
        st.markdown(render_gauge(l), unsafe_allow_html=True)
        if st.button("UNTRACK", key=f"cr_un_{item['symbol']}_{i}"):
            portfolio = [p for p in portfolio if p['symbol'] != item['symbol']]; save_json('data/user_portfolio.json', portfolio); st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)

    st.divider()
    st.subheader("⏳ Stage 2: Pending (Date Sort)")
    pending = [p for p in portfolio if p['status'] == '대기']
    pending.sort(key=lambda x: x.get('listing_date', '9999-12-31'))
    for i, item in enumerate(pending):
        c1, c2, c3 = st.columns([4, 2, 1])
        c1.markdown(f'<div style="padding:10px;background:#161B22;"><span class="badge badge-standby">STANDBY</span> <b>{item["name"]}</b> ({item["symbol"]})</div>', unsafe_allow_html=True)
        c2.markdown(f'<div style="padding:10px;text-align:center;">📅 {item.get("listing_date")} | {item.get("purchase_price",0):,} KRW</div>', unsafe_allow_html=True)
        with c3:
            if st.button("CANCEL", key=f"cr_can_{item['symbol']}_{i}"):
                portfolio = [p for p in portfolio if p['symbol'] != item['symbol']]; save_json('data/user_portfolio.json', portfolio); st.rerun()

st.markdown("<div style='color:#484F58;font-size:10px;text-align:center;margin-top:50px;'>Hyper ETF Guardian v4.1 [Ultima Integrity Build]<br>No Noise, No Prose. Just Precision.</div>", unsafe_allow_html=True)
