import streamlit as st
import json
import os
import google.generativeai as genai
from monitor import calculate_loss_rate
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(page_title="Hyper ETF Guardian", layout="wide", initial_sidebar_state="expanded")

# --- Gemini 2.0 Flash Setup ---
GEMINI_API_KEY = "AIzaSyDfmWkvWuty0BjkhBainobKonjTL6She78"
genai.configure(api_key=GEMINI_API_KEY)

def get_ai_analysis(prompt):
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        sys_p = "Quant Expert. Strictly No greetings. Format: [위험 지수: X / 핵심 원인: Y / 권고 사항: Z]."
        response = model.generate_content(f"{sys_p}\n\n{prompt}")
        if not response or not response.text:
            return "[위험 지수: 5.0 / 핵심 원인: Intelligence Offline / 권고 사항: 원칙 기반 자동 손절 대기]"
        return response.text.replace("\n", " ").strip()
    except Exception:
        return "[위험 지수: 5.0 / 핵심 원인: Connection Error / 권고 사항: 자산 보존 프로토콜 가동]"

# --- Absolute Mastery CSS (Hard-coded Minification) ---
st.markdown("<style>/* CSS Start */.stApp{background-color:#0A0E14!important;color:#FFFFFF!important;}h1,h2,h3,h4,h5,h6,p,span,label,div,li{color:#FFFFFF!important;font-family:'Inter',sans-serif!important;}input{background-color:#161B22!important;color:#FFFFFF!important;border:1px solid #30363D!important;}div[data-baseweb='input']{background-color:#161B22!important;}div[role='spinbutton']{background-color:#161B22!important;}.stButton>button{width:100%!important;background-color:#21262D!important;color:#FFFFFF!important;border:1px solid #30363D!important;font-weight:900!important;height:32px!important;border-radius:4px!important;transition:none!important;}.stButton>button:hover{border-color:#39FF14!important;color:#39FF14!important;}.list-item{background-color:#161B22;border-bottom:1px solid #21262D;padding:8px 12px;display:flex;justify-content:space-between;align-items:center;min-height:50px;}.badge{display:inline-block;padding:2px 6px;border-radius:3px;font-size:9px;font-weight:900;margin-right:8px;}.badge-tracking{background:rgba(57,255,20,0.1);color:#39FF14!important;border:1px solid #39FF14;}.badge-standby{background:rgba(255,255,51,0.1);color:#FFFF33!important;border:1px solid #FFFF33;}.badge-danger{background:rgba(255,49,49,0.1);color:#FF3131!important;border:1px solid #FF3131;}.cal-card{background:#0D1117;border:1px solid #21262D;padding:12px;border-radius:8px;min-height:220px;}.cal-date{font-size:16px;font-weight:900;color:#FFFFFF!important;border-bottom:3px solid #39FF14;padding-bottom:5px;margin-bottom:12px;text-align:center;}.cal-entry{background:#161B22;padding:8px;border-radius:4px;margin-bottom:8px;border-left:3px solid #FFFF33;}.gauge-bg{width:100%;height:4px;background:#21262D;border-radius:2px;margin-top:6px;overflow:hidden;}.gauge-fill{height:100%;border-radius:2px;}.risk-box{background:rgba(255,49,49,0.05);border:1px solid #FF3131;padding:12px;border-radius:4px;margin-bottom:20px;color:#FF3131!important;font-weight:bold;font-size:12px;}#MainMenu,footer,.stDeployButton{display:none!important;}div.block-container{padding-top:2rem!important;}/* CSS End */</style>", unsafe_allow_html=True)

# --- Data Utility ---
def load_json(path):
    if not os.path.exists(path): return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            c = f.read().strip(); return json.loads(c) if c else []
    except Exception: return []

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Load data and ensure integrity
raw_port = load_json('data/user_portfolio.json')
portfolio = []
seen = set()
for item in raw_port:
    if item['symbol'] not in seen:
        portfolio.append(item)
        seen.add(item['symbol'])

etf_list = load_json('data/etf_list.json')
upcoming_list = load_json('data/upcoming_etf.json')

# --- Header Section ---
st.markdown("<h2 style='margin:0;'>📊 Hyper ETF Guardian <span style='font-size:12px;color:#39FF14;font-weight:400;'>[v4.0 MASTER]</span></h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#8B949E;font-size:13px;margin:-5px 0 20px 0;'>No Prose, Just Precision.</p>", unsafe_allow_html=True)

# Global AI Risk
danger_items = [p for p in portfolio if p.get('status') == '위험']
risk_prompt = f"Portfolio Situation: {len(portfolio)} tracked, {len(danger_items)} danger. Report concisely."
ai_report = get_ai_analysis(risk_prompt)
st.markdown(f'<div class="risk-box"> {ai_report} </div>', unsafe_allow_html=True)

# Metrics Grid
mcols = st.columns(4)
def tile(lbl, val, c="#39FF14"): return f'<div style="background:#161B22;border:1px solid #30363D;border-radius:6px;padding:12px;text-align:center;"><div style="color:#8B949E;font-size:10px;margin-bottom:4px;">{lbl}</div><div style="font-size:18px;font-weight:900;color:{c};">{val}</div></div>'
mcols[0].markdown(tile("총 감시 종목", f"{len(portfolio)} UNIT"), unsafe_allow_html=True)
avg_ret = calculate_loss_rate(sum(p.get('purchase_price',1) for p in portfolio)*0.95 if portfolio else 1, sum(p.get('purchase_price',1) for p in portfolio) if portfolio else 1)
mcols[1].markdown(tile("평균 방어 수익률", f"{avg_ret:+.1f}%", "#FF3131" if avg_ret < 0 else "#39FF14"), unsafe_allow_html=True)
mcols[2].markdown(tile("위험 프로토콜", f"{len(danger_items)}", "#FF3131" if danger_items else "#39FF14"), unsafe_allow_html=True)
mcols[3].markdown(tile("상장 예정(7D)", f"{len(upcoming_list)}", "#FFFF33"), unsafe_allow_html=True)

st.divider()

# --- Sidebar ---
with st.sidebar:
    st.header("🛠️ 관측 통제소")
    iss_all = ["KODEX", "TIGER", "KBSTAR", "ACE", "SOL"]
    sel_iss = [i for i in iss_all if st.checkbox(i, key=f"s_{i}")]
    final_iss = sel_iss if sel_iss else iss_all
    f_etfs = [e for e in etf_list if any(i in e['issuer'] for i in final_iss)]
    if not f_etfs: f_etfs = etf_list[:15]
    if st.button("♻️ RESET PORTFOLIO"): save_json('data/user_portfolio.json', []); st.rerun()

# --- Tabs ---
tabs = st.tabs(["📊 Market Watch", "📅 Upcoming", "🚨 Control Room"])

# Tab 1: Market Watch (Vertical Top 10)
with tabs[0]:
    cats = {
        "AI & 반도체": ["AI", "반도체", "NVIDIA", "HBM"],
        "밸류업 / 저PBR": ["밸류업", "저PBR", "금융", "은행"],
        "미국 빅테크": ["미국", "빅테크", "나스닥", "S&P"],
        "월배당 / 인컴": ["월배당", "배당", "인컴", "커버드콜"]
    }
    for c_idx, (c_name, kws) in enumerate(cats.items()):
        st.subheader(f"📌 {c_name} (Top 10)")
        itms = [e for e in f_etfs if any(k.lower() in e['name'].lower() for k in kws)][:10]
        if not itms: itms = etf_list[:3]
        for idx, item in enumerate(itms):
            is_p = any(p['symbol'] == item['symbol'] for p in portfolio)
            st.markdown(f'<div class="list-item"><div style="flex:1;color:#8B949E;font-size:11px;">{item["issuer"]}</div><div style="flex:4;font-size:13px;font-weight:bold;">{item["name"]}</div><div style="flex:2;font-size:13px;font-weight:900;color:#39FF14;text-align:center;">{item["price_at_listing"]:,}</div></div>', unsafe_allow_html=True)
            cc1, cc2, cc3, cc4 = st.columns([1, 5, 2, 2])
            with cc4:
                if is_p:
                    if st.button("UNTRACK", key=f"mw_un_{item['symbol']}_{c_idx}_{idx}"):
                        portfolio = [p for p in portfolio if p['symbol'] != item['symbol']]; save_json('data/user_portfolio.json', portfolio); st.rerun()
                else:
                    if st.button("TRACK", key=f"mw_add_{item['symbol']}_{c_idx}_{idx}"):
                        portfolio.append({"symbol":item['symbol'],"name":item['name'],"purchase_price":item['price_at_listing'],"status":"추적 중"})
                        save_json('data/user_portfolio.json', portfolio); st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)

# Tab 2: Upcoming (Interactive Reservation)
with tabs[1]:
    mon = datetime.now() - timedelta(days=datetime.now().weekday())
    days = ["월", "화", "수", "목", "금"]; u_cols = st.columns(5)
    for i in range(5):
        d_str = (mon + timedelta(days=i)).strftime("%Y-%m-%d")
        with u_cols[i]:
            st.markdown(f'<div class="cal-card"><div class="cal-date">{days[i]} ({d_str})</div>', unsafe_allow_html=True)
            d_itms = [e for e in upcoming_list if e['listing_date'] == d_str]
            for j, item in enumerate(d_itms):
                res = next((p for p in portfolio if p['symbol'] == item['ticker']), None)
                st.markdown(f'<div class="cal-entry"><span class="badge badge-standby">STANDBY</span><div style="font-size:12px;font-weight:bold;margin:4px 0;">{item["name"]}</div>', unsafe_allow_html=True)
                if res:
                    st.markdown(f"<div style='font-size:10px;color:#FFFF33;'>예약가: {res['purchase_price']:,} KRW</div>", unsafe_allow_html=True)
                    if st.button("CANCEL", key=f"up_can_{item['ticker']}_{i}_{j}"):
                        portfolio = [p for p in portfolio if p['symbol'] != item['ticker']]; save_json('data/user_portfolio.json', portfolio); st.rerun()
                else:
                    k = f"res_act_{item['ticker']}"
                    if not st.session_state.get(k):
                        if st.button("[PRE-CHECK]", key=f"up_pre_{item['ticker']}_{i}_{j}"): st.session_state[k]=True; st.rerun()
                    else:
                        p_val = st.number_input("희망가", min_value=0, value=10000, key=f"price_{item['ticker']}")
                        st.markdown(f"<div style='font-size:12px;color:#39FF14;'>{p_val:,}원에 예약하시겠습니까?</div>", unsafe_allow_html=True)
                        b1, b2 = st.columns(2)
                        if b1.button("확정", key=f"up_ok_{item['ticker']}"):
                            portfolio.append({"symbol":item['ticker'],"name":item['name'],"purchase_price":p_val,"status":"대기","listing_date":item['listing_date']})
                            save_json('data/user_portfolio.json', portfolio); st.session_state[k]=False; st.rerun()
                        if b2.button("닫기", key=f"up_cls_{item['ticker']}"): st.session_state[k]=False; st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# Tab 3: Control Room (Risk Monitoring & Pending)
with tabs[2]:
    st.subheader("⚠️ Monitoring Priority (Risk ASC)")
    active = []
    for p in portfolio:
        if p['status'] != '대기':
            bp = p.get('purchase_price', 10000); cv = bp * (0.95 if p['status'] == '추적 중' else 0.88)
            p['loss'] = calculate_loss_rate(cv, bp); p['cur'] = cv
            active.append(p)
    active.sort(key=lambda x: x['loss'])
    if not active: st.info("활성 모니터링 대상이 없습니다.")
    for i, item in enumerate(active):
        l = item['loss']
        st.markdown(f'<div class="list-item"><div><span class="badge {"badge-danger" if l <= -8 else "badge-tracking"}">{item["status"]}</span><b>{item["name"]} ({item["symbol"]})</b></div><div style="text-align:right;"><span style="font-size:18px;font-weight:900;color:{"#FF3131" if l <= -8 else "#39FF14"};">{l:+.1f}%</span><div style="font-size:10px;color:#8B949E;">{int(item["cur"]):,} KRW</div></div></div>', unsafe_allow_html=True)
        rem = 10.0 + l; clr = "#39FF14" if rem > 5 else "#FFA500" if rem > 2 else "#FF3131"; wd = min(100, (abs(l)/10.0)*100)
        st.markdown(f'<div style="font-size:10px;color:#8B949E;margin-top:8px;">방어선 잔여: <b>{rem:+.1f}%</b></div><div class="gauge-bg"><div class="gauge-fill" style="width:{wd}%;background:{clr};"></div></div>', unsafe_allow_html=True)
        if st.button("UNTRACK PROCEED", key=f"cr_un_{item['symbol']}_{i}"):
            portfolio = [p for p in portfolio if p['symbol'] != item['symbol']]; save_json('data/user_portfolio.json', portfolio); st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)

    st.divider()
    st.subheader("⏳ Stage 2: Pending (Date ASC)")
    pend = [p for p in portfolio if p['status'] == '대기']
    pend.sort(key=lambda x: x.get('listing_date', '9999-12-31'))
    for i, item in enumerate(pend):
        l1, l2, l3 = st.columns([4, 2, 1])
        l1.markdown(f'<div style="padding:10px;background:#161B22;border-radius:4px;"><span class="badge badge-standby">STANDBY</span> <b>{item["name"]}</b> <small>({item["symbol"]})</small></div>', unsafe_allow_html=True)
        l2.markdown(f'<div style="padding:10px;text-align:center;">📅 {item.get("listing_date")} | {item.get("purchase_price",0):,} KRW</div>', unsafe_allow_html=True)
        with l3: # Moved the button into the third column
            if st.button("CANCEL", key=f"cr_can_{item['symbol']}_{i}"):
                portfolio = [p for p in portfolio if p['symbol'] != item['symbol']]; save_json('data/user_portfolio.json', portfolio); st.rerun()

st.markdown("<div style='color:#484F58;font-size:10px;text-align:center;margin-top:60px;'>Hyper ETF Guardian v4.0 [The Final Master Build]<br>Intelligence: Gemini 2.0 Flash / SnF Final Restoration</div>", unsafe_allow_html=True)
