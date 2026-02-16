import streamlit as st
import json
import os
import google.generativeai as genai
from monitor import calculate_loss_rate
from datetime import datetime, timedelta

# Page Configuration
st.set_page_config(page_title="Hyper ETF Guardian", layout="wide", initial_sidebar_state="expanded")

# --- Gemini 2.0 Flash Setup ---
GEMINI_API_KEY = "AIzaSyDfmWkvWuty0BjkhBainobKonjTL6She78"
genai.configure(api_key=GEMINI_API_KEY)

def get_ai_analysis(prompt):
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        sys_p = "Quant Expert. No greetings. Strictly: [위험 지수: X / 핵심 원인: Y / 권고 사항: Z]."
        response = model.generate_content(f"{sys_p}\n\n{prompt}")
        if not response or not response.text:
            return "[위험 지수: 5.0 / 핵심 원인: Intelligence Offline / 권고 사항: 자산 보존 대기]"
        return response.text.replace("\n", " ").strip()
    except Exception:
        return "[위험 지수: 5.0 / 핵심 원인: Connection Error / 권고 사항: 수동 방어 가동]"

# --- Style Mastery: v4.2 Precision Build ---
# Focus: Absolute Legibility, Harmonic Alignment, No Emojis, No White Boxes.
st.markdown("<style>/* UI Base */.stApp{background-color:#0A0E14!important;color:#FFFFFF!important;}h1,h2,h3,h4,h5,h6,p,span,label,div,li{color:#FFFFFF!important;font-family:'Inter',sans-serif!important;}/* Card Container Styling */.precision-card{background-color:#161B22;border:1px solid #30363D;border-radius:12px;padding:20px 25px;margin-bottom:20px;box-shadow:0 4px 6px rgba(0,0,0,0.3);}.card-header{font-size:16px;font-weight:900;margin-bottom:15px;color:#FFFFFF!important;display:flex;justify-content:space-between;border-bottom:1px solid #30363D;padding-bottom:10px;}/* Item Row Alignment */.item-row-data{font-size:12px;display:flex;align-items:center;height:40px;border-bottom:1px solid #21262D;}.item-row-data:last-child{border-bottom:none;}/* Widget Styling */input{background-color:#1C2128!important;color:#FFFFFF!important;border:1px solid #3E444D!important;}div[data-baseweb='input']{background-color:#1C2128!important;}.stNumberInput div{background-color:#1C2128!important;}/* Button Styling - WATCH/REMOVE/TRACK/UNTRACK */.stButton>button{width:100%!important;background-color:#21262D!important;color:#FFFFFF!important;border:1px solid #30363D!important;font-weight:900!important;height:32px!important;border-radius:6px!important;font-size:10px!important;letter-spacing:0.5px;}.stButton>button:hover{border-color:#39FF14!important;color:#39FF14!important;}/* Upcoming/Calendar Alignment */.cal-header{font-size:15px;font-weight:900;color:#39FF14!important;padding:5px 0;margin-bottom:0px;border-bottom:2px solid #39FF14;}.cal-item{background:#161B22;border:1px solid #21262D;border-radius:8px;padding:12px;margin-top:10px;border-left:4px solid #FFFF33;overflow:hidden;}/* Badges */.badge{display:inline-block;padding:2px 6px;border-radius:3px;font-size:9px;font-weight:900;margin-right:8px;}.badge-tracking{background:rgba(57,255,20,0.1);color:#39FF14!important;border:1px solid #39FF14;}.badge-standby{background:rgba(255,255,51,0.1);color:#FFFF33!important;border:1px solid #FFFF33;}.badge-danger{background:rgba(255,49,49,0.1);color:#FF3131!important;border:1px solid #FF3131;}/* Risk Box */.risk-box{background:rgba(255,49,49,0.05);border:1px solid #FF3131;padding:15px;border-radius:8px;margin-bottom:25px;color:#FF3131!important;font-weight:900;font-size:13px;}/* Global Cleanup */#MainMenu,footer,.stDeployButton{display:none!important;}div.block-container{padding-top:2rem!important;}</style>", unsafe_allow_html=True)

# --- Data Utility ---
def l_json(p):
    if not os.path.exists(p): return []
    try:
        with open(p,'r',encoding='utf-8') as f:
            c=f.read().strip(); return json.loads(c) if c else []
    except Exception: return []

def s_json(p, d):
    with open(p,'w',encoding='utf-8') as f:
        json.dump(d, f, indent=2, ensure_ascii=False)

# Data Loading with Integrity Guards
p_raw = l_json('data/user_portfolio.json')
portfolio = []
seen = set()
for i in p_raw:
    if i['symbol'] not in seen:
        portfolio.append(i); seen.add(i['symbol'])

etf_list = l_json('data/etf_list.json')
upcoming_list = l_json('data/upcoming_etf.json')

# --- Header Layer ---
st.markdown("<h2 style='margin:0;'>Hyper ETF Guardian <span style='font-size:11px;color:#39FF14;font-weight:400;'>[v4.2 PRECISION]</span></h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#8B949E;font-size:12px;margin:-5px 0 15px 0;'>Command Protocol Activated. Zero Noise Interference.</p>", unsafe_allow_html=True)

# Global Intelligence Report
dang = [p for p in portfolio if p.get('status') == '위험']
ari = get_ai_analysis(f"Portfolio Status: {len(portfolio)} tracked, {len(dang)} danger items. Critical focus required.")
st.markdown(f'<div class="risk-box"> {ari} </div>', unsafe_allow_html=True)

# Performance Metrics
m_cols = st.columns(4)
def mt(l, v, c="#39FF14"): return f'<div style="background:#161B22;border:1px solid #30363D;border-radius:10px;padding:15px;text-align:center;"><div style="color:#8B949E;font-size:10px;margin-bottom:5px;">{l}</div><div style="font-size:18px;font-weight:900;color:{c};">{v}</div></div>'
m_cols[0].markdown(mt("WATCH UNITS", f"{len(portfolio)} UNIT"), unsafe_allow_html=True)
avg_lvl = sum(calculate_loss_rate(p.get('purchase_price',10000)*0.95, p.get('purchase_price',10000)) for p in portfolio) / len(portfolio) if portfolio else 0
m_cols[1].markdown(mt("AVG SHIELD LEVEL", f"{avg_lvl:+.1f}%", "#FF3131" if avg_lvl < 0 else "#39FF14"), unsafe_allow_html=True)
m_cols[2].markdown(mt("DANGER PROTOCOLS", f"{len(dang)} UNIT", "#FF3131" if dang else "#39FF14"), unsafe_allow_html=True)
m_cols[3].markdown(mt("PENDING LISTINGS", f"{len(upcoming_list)} UNIT", "#FFFF33"), unsafe_allow_html=True)

st.divider()

# --- Control Center Sidebar ---
with st.sidebar:
    st.header("CONTROL")
    iss_pool = ["KODEX", "TIGER", "KBSTAR", "ACE", "SOL"]
    sel_iss = [i for i in iss_pool if st.checkbox(i, key=f"s_{i}")]
    final_iss = sel_iss if sel_iss else iss_pool
    f_etfs = [e for e in etf_list if any(i in e['issuer'] for i in final_iss)]
    if not f_etfs: f_etfs = etf_list[:50]
    if st.button("FACTORY RESET SYSTEM"): s_json('data/user_portfolio.json', []); st.rerun()

# --- Main Dashboard Tabs ---
tabs = st.tabs(["Market Watch", "Upcoming", "Control Room"])

# Tab 1: Market Watch (Harmonic Precision Cards)
with tabs[0]:
    themes = {
        "AI & Semiconductor": ["AI", "반도체", "NVIDIA", "HBM"],
        "USA Big Tech": ["미국", "빅테크", "나스닥", "S&P"],
        "ValueUp / Dividend": ["밸류업", "저PBR", "배당", "인컴"],
        "Emerging Themes": ["양자", "우주", "에너지", "바이오"]
    }
    
    # 2x2 Precision Grid
    gr1_c1, gr1_c2 = st.columns(2)
    gr2_c1, gr2_c2 = st.columns(2)
    grid_map = [gr1_c1, gr1_c2, gr2_c1, gr2_c2]
    
    for c_idx, (th_name, keys) in enumerate(themes.items()):
        with grid_map[c_idx]:
            st.markdown(f'<div class="precision-card"><div class="card-header"><span>{th_name}</span><span style="font-size:9px;color:#8B949E;font-weight:400;">STRATEGIC TOP 10</span></div>', unsafe_allow_html=True)
            
            # Focused Data Retrieval (Top 10 Guaranteed)
            t_pool = []
            active_sym = set()
            for e in f_etfs:
                if any(k.lower() in e['name'].lower() for k in keys):
                    t_pool.append(e); active_sym.add(e['symbol'])
            # Fallback for Strategic Density
            if len(t_pool) < 10:
                for e in f_etfs:
                    if e['symbol'] not in active_sym:
                        t_pool.append(e); active_sym.add(e['symbol'])
                    if len(t_pool) >= 10: break
            
            # Harmonic Row Rendering
            for i, item in enumerate(t_pool[:10]):
                is_tracked = any(p['symbol'] == item['symbol'] for p in portfolio)
                # Labels for Columns [Issuer(1), Name(4), Price(1.5), Button(1.5)]
                row_cols = st.columns([1, 4, 1.5, 1.5])
                row_cols[0].markdown(f'<div class="item-row-data" style="color:#8B949E;font-weight:700;">{item["issuer"]}</div>', unsafe_allow_html=True)
                row_cols[1].markdown(f'<div class="item-row-data" style="font-weight:700;">{item["name"][:16]}</div>', unsafe_allow_html=True)
                row_cols[2].markdown(f'<div class="item-row-data" style="color:#39FF14;font-weight:900;justify-content:flex-end;">{item["price_at_listing"]:,}</div>', unsafe_allow_html=True)
                
                with row_cols[3]:
                    st.markdown('<div class="item-row-data" style="border:none;justify-content:center;">', unsafe_allow_html=True)
                    if is_tracked:
                        if st.button("UNTRACK", key=f"mw_un_{item['symbol']}_{c_idx}_{i}"):
                            portfolio = [p for p in portfolio if p['symbol'] != item['symbol']]; s_json('data/user_portfolio.json', portfolio); st.rerun()
                    else:
                        if st.button("TRACK", key=f"mw_tr_{item['symbol']}_{c_idx}_{i}"):
                            portfolio.append({"symbol":item['symbol'], "name":item['name'], "purchase_price":item['price_at_listing'], "status":"추적 중"})
                            s_json('data/user_portfolio.json', portfolio); st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# Tab 2: Upcoming (Calendar Alignment & Volume Command)
with tabs[1]:
    mon_day = datetime.now() - timedelta(days=datetime.now().weekday())
    week_days = ["MON", "TUE", "WED", "THU", "FRI"]; cal_cols = st.columns(5)
    
    for i in range(5):
        target_date = (mon_day + timedelta(days=i)).strftime("%Y-%m-%d")
        with cal_cols[i]:
            st.markdown(f'<div class="cal-header">{week_days[i]} ({target_date})</div>', unsafe_allow_html=True)
            day_items = [e for e in upcoming_list if e['listing_date'] == target_date]
            if not day_items: st.markdown("<div style='font-size:10px;color:#484F58;padding:15px;text-align:center;'>NO LISTINGS</div>", unsafe_allow_html=True)
            
            for j, item in enumerate(day_items):
                with st.container():
                    r_exist = next((p for p in portfolio if p['symbol'] == item['ticker']), None)
                    st.markdown(f'<div class="cal-item"><span class="badge badge-standby">STANDBY</span><div style="font-size:12px;font-weight:900;margin:5px 0;">{item["name"]}</div>', unsafe_allow_html=True)
                    if r_exist:
                        st.markdown(f"<div style='font-size:11px;color:#FFFF33;font-weight:700;'>VOLUME: {r_exist.get('quantity', 0)} UNIT</div>", unsafe_allow_html=True)
                        if st.button("CANCEL", key=f"up_can_{item['ticker']}_{i}_{j}"):
                            portfolio = [p for p in portfolio if p['symbol'] != item['ticker']]; s_json('data/user_portfolio.json', portfolio); st.rerun()
                    else:
                        r_key = f"r_act_{item['ticker']}"
                        if not st.session_state.get(r_key):
                            if st.button("PRE-CHECK", key=f"up_pre_{item['ticker']}_{i}_{j}"): st.session_state[r_key]=True; st.rerun()
                        else:
                            v_cmd = st.number_input("QUANTITY", min_value=1, value=10, step=1, key=f"v_set_{item['ticker']}")
                            st.markdown(f"<p style='font-size:10px;color:#39FF14;margin:4px 0;'>Reserve {v_cmd} Unit(s)?</p>", unsafe_allow_html=True)
                            b1, b2 = st.columns(2)
                            if b1.button("CONFIRM", key=f"up_ok_{item['ticker']}"):
                                portfolio.append({"symbol":item['ticker'], "name":item['name'], "quantity":v_cmd, "status":"대기", "listing_date":item['listing_date']})
                                s_json('data/user_portfolio.json', portfolio); st.session_state[r_key]=False; st.rerun()
                            if b2.button("CLOSE", key=f"up_cls_{item['ticker']}"): st.session_state[r_key]=False; st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

# Tab 3: Control Room (Strategic Priority)
with tabs[2]:
    st.subheader("Monitoring Priority (Risk Ascent)")
    active_pool = []
    for p in portfolio:
        if p['status'] != '대기':
            b_price = p.get('purchase_price', 10000); c_val = b_price * (0.95 if p['status'] == '추적 중' else 0.88)
            p['loss_rate'] = calculate_loss_rate(c_val, b_price); p['cur_val'] = c_val
            active_pool.append(p)
    active_pool.sort(key=lambda x: x['loss_rate'])
    
    if not active_pool: st.info("Active monitoring target null.")
    for i, p in enumerate(active_pool):
        l_r = p['loss_rate']
        st.markdown(f'<div class="item-row-data" style="background:#161B22;border-radius:10px;margin-bottom:10px;padding:0 15px;height:50px;"><div><span class="badge {"badge-danger" if l_r <= -8 else "badge-tracking"}">{p["status"]}</span><b>{p["name"]}</b></div><div style="text-align:right;"><span style="font-size:20px;font-weight:900;color:{"#FF3131" if l_r <= -8 else "#39FF14"};">{l_r:+.1f}%</span></div></div>', unsafe_allow_html=True)
        rem_l = 10.0 + l_r; g_clr = "#39FF14" if rem_l > 5 else "#FFA500" if rem_l > 2 else "#FF3131"; g_wd = min(100, (abs(l_r)/10.0)*100)
        st.markdown(f'<div style="font-size:10px;color:#8B949E;margin-top:2px;">Defense Threshold Remaining: <b>{rem_l:+.1f}%</b></div><div style="width:100%;height:6px;background:#21262D;border-radius:3px;margin:8px 0;"><div style="width:{g_wd}%;height:100%;background:{g_clr};border-radius:3px;"></div></div>', unsafe_allow_html=True)
        if st.button("TERMINATE TRACKING", key=f"cr_term_{p['symbol']}_{i}"):
            portfolio = [i for i in portfolio if i['symbol'] != p['symbol']]; s_json('data/user_portfolio.json', portfolio); st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)

    st.divider()
    st.subheader("Stage 2: Pending (Chronological Order)")
    pending_pool = [p for p in portfolio if p['status'] == '대기']
    pending_pool.sort(key=lambda x: x.get('listing_date', '9999-12-31'))
    for i, p in enumerate(pending_pool):
        pl1, pl2, pl3 = st.columns([4, 2, 1.5])
        pl1.markdown(f'<div style="padding:12px;background:#161B22;border:1px solid #21262D;border-radius:8px;"><span class="badge badge-standby">PENDING</span><b>{p["name"]}</b></div>', unsafe_allow_html=True)
        pl2.markdown(f'<div style="padding:12px;text-align:center;">Date: {p.get("listing_date")} | Vol: {p.get("quantity",0)} UNIT</div>', unsafe_allow_html=True)
        with pl3:
            st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)
            if st.button("ABORT", key=f"cr_abrt_{p['symbol']}_{i}"):
                portfolio = [i for i in portfolio if i['symbol'] != p['symbol']]; s_json('data/user_portfolio.json', portfolio); st.rerun()

st.markdown("<div style='color:#484F58;font-size:10px;text-align:center;margin-top:80px;'>Hyper ETF Guardian v4.2 [Zero-Noise Precision Build]<br>Intelligence Context: Gemini 2.0 Flash / Architectural Finality</div>", unsafe_allow_html=True)
