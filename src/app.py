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
        sys_p = "Quant Expert. No greetings. Strictly: [Risk Index: X / Core Cause: Y / Recommendation: Z]."
        response = model.generate_content(f"{sys_p}\n\n{prompt}")
        if not response or not response.text:
            return "[Risk Index: 5.0 / Core Cause: Intelligence Offline / Recommendation: Standby]"
        return response.text.replace("\n", " ").strip()
    except Exception:
        return "[Risk Index: 5.0 / Core Cause: Connection Error / Recommendation: Manual Guard]"

# --- Absolute Mastery CSS (v4.3 Master Box Build) ---
st.markdown("<style>/* UI Base */.stApp{background-color:#0A0E14!important;color:#FFFFFF!important;}h1,h2,h3,h4,h5,h6,p,span,label,div,li{color:#FFFFFF!important;font-family:'Inter',sans-serif!important;}/* Master Box Styling */.master-box{background-color:#161B22 !important;border:1px solid #30363D !important;border-radius:12px;padding:25px;margin-bottom:40px;box-shadow:0 8px 16px rgba(0,0,0,0.4);}.theme-title{font-size:18px;font-weight:900;margin-bottom:20px;color:#FFFFFF!important;letter-spacing:1px;text-transform:uppercase;border-left:5px solid #39FF14;padding-left:15px;}/* Item Row Harmony */.row-data{font-size:13px;font-weight:600;display:flex;align-items:center;height:45px;color:#FFFFFF!important;}.list-divider{border-bottom:1px solid #21262D;margin:0;padding:0;}/* Inputs & Widgets */input{background-color:#1C2128!important;color:#FFFFFF!important;border:1px solid #3E444D!important;}div[data-baseweb='input']{background-color:#1C2128!important;}.stNumberInput div{background-color:#1C2128!important;}/* Strategic Button Styling */.stButton>button{width:100%!important;background-color:#21262D!important;color:#FFFFFF!important;border:1px solid #30363D!important;font-weight:900!important;height:34px!important;border-radius:6px!important;font-size:11px!important;letter-spacing:0.5px;transition:all 0.1s ease;}.stButton>button:hover{border-color:#39FF14!important;color:#39FF14!important;background-color:#1C2128!important;}/* Upcoming/Calendar Precision */.cal-header{font-size:16px;font-weight:900;color:#39FF14!important;padding:10px 0;margin-bottom:0px;border-bottom:2px solid #39FF14;}.cal-item{background:#161B22;border:1px solid #30363D;border-radius:10px;padding:15px;margin-top:12px;border-left:5px solid #FFFF33;overflow:hidden;}/* Tactical Badges */.badge{display:inline-block;padding:3px 8px;border-radius:4px;font-size:10px;font-weight:900;margin-right:10px;}.badge-tracking{background:rgba(57,255,20,0.1);color:#39FF14!important;border:1px solid #39FF14;}.badge-standby{background:rgba(255,255,51,0.1);color:#FFFF33!important;border:1px solid #FFFF33;}.badge-danger{background:rgba(255,49,49,0.1);color:#FF3131!important;border:1px solid #FF3131;}/* Risk Assessment Box */.risk-box{background:rgba(255,49,49,0.05);border:1px solid #FF3131;padding:20px;border-radius:10px;margin-bottom:30px;color:#FF3131!important;font-weight:900;font-size:14px;line-height:1.5;}/* Footer */#MainMenu,footer,.stDeployButton{display:none!important;}div.block-container{padding-top:2rem!important;}</style>", unsafe_allow_html=True)

# --- Data Engine ---
def l_json(p):
    if not os.path.exists(p): return []
    try:
        with open(p,'r',encoding='utf-8') as f:
            c=f.read().strip(); return json.loads(c) if c else []
    except Exception: return []

def s_json(p, d):
    with open(p,'w',encoding='utf-8') as f:
        json.dump(d, f, indent=2, ensure_ascii=False)

# Load context data
p_load = l_json('data/user_portfolio.json')
portfolio = []
s_seen = set()
for i in p_load:
    if i['symbol'] not in s_seen:
        portfolio.append(i); s_seen.add(i['symbol'])

etf_list = l_json('data/etf_list.json')
upcoming_list = l_json('data/upcoming_etf.json')

# --- Header Layer ---
st.markdown("<h2 style='margin:0;'>📊 Hyper ETF Guardian <span style='font-size:12px;color:#39FF14;font-weight:400;'>[v4.3 MASTER BOX]</span></h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#8B949E;font-size:13px;margin:-5px 0 20px 0;'>Strategic Asset Control. Zero Noise Environment.</p>", unsafe_allow_html=True)

# Global Intelligence Scan
dang_units = [p for p in portfolio if p.get('status') == '위험']
intel_rep = get_ai_analysis(f"Scanning {len(portfolio)} units. {len(dang_units)} critical breaches detected.")
st.markdown(f'<div class="risk-box">🚨 {intel_rep} </div>', unsafe_allow_html=True)

# Tactical Metrics
cols_m = st.columns(4)
def metric_box(lbl, val, clr="#39FF14"): return f'<div style="background:#161B22;border:1px solid #30363D;border-radius:12px;padding:20px;text-align:center;"><div style="color:#8B949E;font-size:11px;margin-bottom:8px;">{lbl}</div><div style="font-size:20px;font-weight:900;color:{clr};">{val}</div></div>'
cols_m[0].markdown(metric_box("🔍 WATCH UNITS", f"{len(portfolio)} UNIT"), unsafe_allow_html=True)
shield_val = sum(calculate_loss_rate(p.get('purchase_price',10000)*0.95, p.get('purchase_price',10000)) for p in portfolio) / len(portfolio) if portfolio else 0
cols_m[1].markdown(metric_box("🛡️ AVG SHIELD LEVEL", f"{shield_val:+.2f}%", "#FF3131" if shield_val < 0 else "#39FF14"), unsafe_allow_html=True)
cols_m[2].markdown(metric_box("⚠️ THREAT VECTORS", f"{len(dang_units)} UNIT", "#FF3131" if dang_units else "#39FF14"), unsafe_allow_html=True)
cols_m[3].markdown(metric_box("📅 EXPECTED LISTINGS", f"{len(upcoming_list)} UNIT", "#FFFF33"), unsafe_allow_html=True)

st.divider()

# --- Tactical Sidebar ---
with st.sidebar:
    st.header("🛠️ SYSTEM CONTROL")
    is_list = ["KODEX", "TIGER", "KBSTAR", "ACE", "SOL"]
    is_sel = [i for i in is_list if st.checkbox(i, key=f"is_{i}")]
    final_is = is_sel if is_sel else is_list
    f_pool = [e for e in etf_list if any(i in e['issuer'] for i in final_is)]
    if not f_pool: f_pool = etf_list[:50]
    if st.button("♻️ FACTORY RESET SYSTEM"): s_json('data/user_portfolio.json', []); st.rerun()

# --- Dashboard Hub ---
tabs = st.tabs(["📊 Market Watch", "📅 Upcoming", "🚨 Control Room"])

# Tab 1: Market Watch (MASTER BOX POLICY)
with tabs[0]:
    themes = {
        "AI & Semiconductor Strategy": ["AI", "반도체", "NVIDIA", "HBM"],
        "USA Big Tech Strategy": ["미국", "빅테크", "나스닥", "S&P"],
        "ValueUp / Dividend Strategy": ["밸류업", "저PBR", "배당", "인컴"],
        "Emerging Tech Strategy": ["양자", "우주", "에너", "바이오"]
    }
    
    for t_idx, (t_name, t_keys) in enumerate(themes.items()):
        st.markdown(f'<div class="theme-title">📌 {t_name}</div>', unsafe_allow_html=True)
        # Consolidation into a single master container
        with st.container():
            st.markdown('<div class="master-box">', unsafe_allow_html=True)
            
            # Data Concentration (Top 10)
            t_data = []
            s_set = set()
            for e in f_pool:
                if any(k.lower() in e['name'].lower() for k in t_keys):
                    t_data.append(e); s_set.add(e['symbol'])
            if len(t_data) < 10:
                for e in f_pool:
                    if e['symbol'] not in s_set:
                        t_data.append(e); s_set.add(e['symbol'])
                    if len(t_data) >= 10: break
            
            # Harmonic Row Execution
            for row_i, item in enumerate(t_data[:10]):
                is_p = any(p['symbol'] == item['symbol'] for p in portfolio)
                row_cols = st.columns([0.8, 1.5, 4, 1.5, 1.5])
                row_cols[0].markdown(f'<div class="row-data" style="color:#8B949E;">#{row_i+1:02d}</div>', unsafe_allow_html=True)
                row_cols[1].markdown(f'<div class="row-data" style="color:#8B949E;font-weight:900;">{item["issuer"]}</div>', unsafe_allow_html=True)
                row_cols[2].markdown(f'<div class="row-data" style="font-weight:900;">{item["name"][:20]}</div>', unsafe_allow_html=True)
                row_cols[3].markdown(f'<div class="row-data" style="color:#39FF14;font-weight:900;justify-content:flex-end;">{item["price_at_listing"]:,} KRW</div>', unsafe_allow_html=True)
                
                with row_cols[4]:
                    st.markdown('<div class="row-data" style="justify-content:center;">', unsafe_allow_html=True)
                    if is_p:
                        if st.button("UNTRACK", key=f"mw_rm_{item['symbol']}_{t_idx}_{row_i}"):
                            portfolio = [p for p in portfolio if p['symbol'] != item['symbol']]; s_json('data/user_portfolio.json', portfolio); st.rerun()
                    else:
                        if st.button("TRACK", key=f"mw_ad_{item['symbol']}_{t_idx}_{row_i}"):
                            portfolio.append({"symbol":item['symbol'], "name":item['name'], "purchase_price":item['price_at_listing'], "status":"추적 중"})
                            s_json('data/user_portfolio.json', portfolio); st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                
                if row_i < 9: st.markdown('<div class="list-divider"></div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

# Tab 2: Upcoming (Precision Calendar & Volume Command)
with tabs[1]:
    mon_ref = datetime.now() - timedelta(days=datetime.now().weekday())
    w_labels = ["MON", "TUE", "WED", "THU", "FRI"]; cal_grid = st.columns(5)
    
    for i in range(5):
        t_day = (mon_ref + timedelta(days=i)).strftime("%Y-%m-%d")
        with cal_grid[i]:
            st.markdown(f'<div class="cal-header">{w_labels[i]} ({t_day})</div>', unsafe_allow_html=True)
            u_itms = [e for e in upcoming_list if e['listing_date'] == t_day]
            if not u_itms: st.markdown("<div style='font-size:11px;color:#484F58;padding:20px;text-align:center;'>LISTING CLEAR</div>", unsafe_allow_html=True)
            
            for j, item in enumerate(u_itms):
                with st.container():
                    p_res = next((p for p in portfolio if p['symbol'] == item['ticker']), None)
                    st.markdown(f'<div class="cal-item"><span class="badge badge-standby">⏳ PENDING</span><div style="font-size:13px;font-weight:900;margin:6px 0;">{item["name"]}</div>', unsafe_allow_html=True)
                    if p_res:
                        st.markdown(f"<div style='font-size:11px;color:#FFFF33;font-weight:900;'>🔢 VOLUME: {p_res.get('quantity', 0)} UNIT</div>", unsafe_allow_html=True)
                        if st.button("ABORT", key=f"up_ab_{item['ticker']}_{i}_{j}"):
                            portfolio = [p for p in portfolio if p['symbol'] != item['ticker']]; s_json('data/user_portfolio.json', portfolio); st.rerun()
                    else:
                        res_k = f"res_t_{item['ticker']}"
                        if not st.session_state.get(res_k):
                            if st.button("INITIATE", key=f"up_in_{item['ticker']}_{i}_{j}"): st.session_state[res_k]=True; st.rerun()
                        else:
                            v_qty = st.number_input("UNITS", min_value=1, value=10, step=1, key=f"v_set_{item['ticker']}")
                            st.markdown(f"<p style='font-size:11px;color:#39FF14;margin:6px 0;'>Command: Buy {v_qty} Unit(s)?</p>", unsafe_allow_html=True)
                            b_ok, b_no = st.columns(2)
                            if b_ok.button("DEPLOY", key=f"up_ok_{item['ticker']}"):
                                portfolio.append({"symbol":item['ticker'], "name":item['name'], "quantity":v_qty, "status":"대기", "listing_date":item['listing_date']})
                                s_json('data/user_portfolio.json', portfolio); st.session_state[res_k]=False; st.rerun()
                            if b_no.button("HALT", key=f"up_no_{item['ticker']}"): st.session_state[res_k]=False; st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

# Tab 3: Control Room (Risk Superiority)
with tabs[2]:
    st.subheader("⚠️ Monitoring Priority (Risk Ascent)")
    a_pool = []
    for p in portfolio:
        if p['status'] != '대기':
            base_p = p.get('purchase_price', 10000); c_price = base_p * (0.95 if p['status'] == '추적 중' else 0.88)
            p['loss_r'] = calculate_loss_rate(c_price, base_p); p['c_val'] = c_price
            a_pool.append(p)
    a_pool.sort(key=lambda x: x['loss_r'])
    
    if not a_pool: st.info("Asset status clear.")
    for i, p in enumerate(a_pool):
        l_pct = p['loss_r']
        st.markdown(f'<div class="st-container master-box" style="padding:15px;margin-bottom:15px;height:auto;"><div style="display:flex;justify-content:space-between;align-items:center;"><div style="display:flex;align-items:center;"><span class="badge {"badge-danger" if l_pct <= -8 else "badge-tracking"}">{"⚠️ DANGER" if l_pct <= -8 else "🛡️ TRACKING"}</span><span style="font-weight:900;font-size:16px;">{p["name"]}</span></div><div style="font-size:24px;font-weight:900;color:{"#FF3131" if l_pct <= -8 else "#39FF14"};">{l_pct:+.1f}%</span></div></div>', unsafe_allow_html=True)
        rem_sh = 10.0 + l_pct; sh_clr = "#39FF14" if rem_sh > 5 else "#FFA500" if rem_sh > 2 else "#FF3131"; sh_wd = min(100, (abs(l_pct)/10.0)*100)
        st.markdown(f'<div style="font-size:11px;color:#8B949E;margin-top:10px;">Shield Depletion: <b>{abs(l_pct):.1f}%</b> | Integrity: <b>{rem_sh:+.1f}%</b></div><div style="width:100%;height:8px;background:#21262D;border-radius:4px;margin-top:10px;"><div style="width:{sh_wd}%;height:100%;background:{sh_clr};border-radius:4px;"></div></div>', unsafe_allow_html=True)
        st.markdown('<div style="height:15px;"></div>', unsafe_allow_html=True)
        if st.button("TERMINATE TRACKING UNIT", key=f"cr_kill_{p['symbol']}_{i}"):
            portfolio = [i for i in portfolio if i['symbol'] != p['symbol']]; s_json('data/user_portfolio.json', portfolio); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    st.subheader("⏳ Stage 2: Pending (Chronological Protocol)")
    p_pool = [p for p in portfolio if p['status'] == '대기']
    p_pool.sort(key=lambda x: x.get('listing_date', '9999-12-31'))
    for i, p in enumerate(p_pool):
        cl1, cl2, cl3 = st.columns([4, 2, 1.5])
        cl1.markdown(f'<div style="padding:15px;background:#161B22;border:1px solid #30363D;border-radius:10px;"><span class="badge badge-standby">⏳ PENDING</span><span style="font-weight:900;">{p["name"]}</span></div>', unsafe_allow_html=True)
        cl2.markdown(f'<div style="padding:15px;text-align:center;font-weight:700;">ETA: {p.get("listing_date")} | VOL: {p.get("quantity",0)} UNIT</div>', unsafe_allow_html=True)
        with cl3:
            st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)
            if st.button("ABORT COMMAND", key=f"cr_ab_{p['symbol']}_{i}"):
                portfolio = [i for i in portfolio if i['symbol'] != p['symbol']]; s_json('data/user_portfolio.json', portfolio); st.rerun()

st.markdown("<div style='color:#484F58;font-size:11px;text-align:center;margin-top:80px;'>Hyper ETF Guardian v4.3 [Master Box Overhaul]<br>Quant Intelligence: Gemini 2.0 Flash / Infrastructure Finality</div>", unsafe_allow_html=True)
