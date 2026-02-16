import streamlit as st
import json
import os
import google.generativeai as genai
from monitor import calculate_loss_rate
from datetime import datetime, timedelta

# Absolute Physical Constraint Config
st.set_page_config(page_title="Hyper ETF Guardian", layout="wide", initial_sidebar_state="expanded")

# --- Intelligence Layer (Gemini 2.0 Flash) ---
GEMINI_API_KEY = "AIzaSyDfmWkvWuty0BjkhBainobKonjTL6She78"
genai.configure(api_key=GEMINI_API_KEY)

def get_ai_intel(prompt):
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        sys_p = "Quant Expert. Strictly: [Risk: X / Cause: Y / Recommendation: Z]."
        response = model.generate_content(f"{sys_p}\n\n{prompt}")
        if not response or not response.text:
            return "[Risk: 5.0 / Cause: Unknown / Recommendation: Standby]"
        return response.text.replace("\n", " ").strip()
    except Exception:
        return "[Risk: 5.0 / Cause: Error / Recommendation: Manual Guard]"

# --- Global Integrity Mastery: [v5.5 PHYSICAL SPEC] ---
# No-Break Rule, Harmonic Flex, Master Card Persistence.
st.markdown("<style>/* Global Force Override */.stApp{background-color:#0A0E14!important;color:#FFFFFF!important;}h1,h2,h3,h4,h5,h6,p,span,label,div,li{color:#FFFFFF!important;font-family:'Inter',sans-serif!important;white-space:nowrap!important;}/* Master Box: Physical Constaint */.master-box{background-color:#161B22!important;border:1px solid #30363D!important;border-radius:12px;padding:24px;margin-bottom:35px;box-shadow:0 10px 20px rgba(0,0,0,0.5);overflow:hidden!important;}.theme-title{font-size:17px;font-weight:900;margin-bottom:20px;color:#FFFFFF!important;border-left:5px solid #39FF14;padding-left:15px;text-transform:uppercase;letter-spacing:1px;}/* Market Watch: 5-Stage Sync */.row-master{display:flex;align-items:center;width:100%;height:44px;border-bottom:1px solid #21262D;white-space:nowrap!important;overflow:hidden!important;}.rank-box{min-width:30px;width:30px;font-weight:900;color:#8B949E;flex-shrink:0;}.issuer-box{min-width:80px;width:80px;font-weight:800;color:#8B949E;flex-shrink:0;text-align:left;}.name-box{flex-grow:1;font-weight:700;overflow:hidden!important;text-overflow:ellipsis!important;padding-right:15px;}.price-box{min-width:100px;width:100px;text-align:right;font-weight:900;color:#39FF14;flex-shrink:0;}/* Upcoming: 2-Tier Row */.cal-header{font-size:16px;font-weight:900;color:#39FF14!important;border-bottom:2px solid #39FF14;padding:10px 0;margin-bottom:0px;}.cal-item{background:#161B22;border:1px solid #30363D;border-radius:10px;padding:16px;margin-top:15px;border-left:5px solid #FFFF33;overflow:hidden;}/* Control Room */.panel-v5{background:#161B22;border:1px solid #30363D;border-radius:12px;padding:22px;}/* Widgets & Buttons */input{background-color:#1C2128!important;color:#FFFFFF!important;border:1px solid #3E444D!important;}div[data-baseweb='input']{background-color:#1C2128!important;}.stNumberInput div{background-color:#1C2128!important;}.stButton>button{width:100%!important;background-color:#21262D!important;color:#FFFFFF!important;border:1px solid #30363D!important;font-weight:900!important;height:34px!important;border-radius:6px!important;font-size:11px!important;margin:0!important;}.stButton>button:hover{border-color:#39FF14!important;color:#39FF14!important;}#MainMenu,footer,.stDeployButton{display:none!important;}div.block-container{padding-top:2rem!important;}</style>", unsafe_allow_html=True)

# --- Data Utility ---
def l_j(p):
    if not os.path.exists(p): return []
    try:
        with open(p,'r',encoding='utf-8') as f:
            c=f.read().strip(); return json.loads(c) if c else []
    except Exception: return []

def s_j(p, d):
    with open(p,'w',encoding='utf-8') as f:
        json.dump(d, f, indent=2, ensure_ascii=False)

# Load State
p_raw = l_j('data/user_portfolio.json')
portfolio = []
s_seen = set()
for i in p_raw:
    if i['symbol'] not in s_seen:
        portfolio.append(i); s_seen.add(i['symbol'])

etf_list = l_j('data/etf_list.json')
upcoming_list = l_j('data/upcoming_etf.json')

# --- Header Protocol ---
st.markdown("<h2 style='margin:0;'>📊 Hyper ETF Guardian <span style='font-size:12px;color:#39FF14;font-weight:400;'>[v5.5 PHYSICAL]</span></h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#8B949E;font-size:13px;margin:-5px 0 20px 0;'>Precise Alignment Unit. Zero Noise, Maximum Trust.</p>", unsafe_allow_html=True)

# Intel Report
d_cnt = len([p for p in portfolio if p.get('status') == '위험'])
intel = get_ai_intel(f"Units: {len(portfolio)} | Breach: {d_cnt}. Master build v5.5 active.")
st.markdown(f'<div style="background:rgba(255,49,49,0.05);border:1px solid #FF3131;padding:18px;border-radius:10px;margin-bottom:30px;color:#FF3131;font-weight:900;font-size:14px;">🚨 {intel} </div>', unsafe_allow_html=True)

# Metrics Grid
m_cols = st.columns(4)
def m_box(l, v, c="#39FF14"): return f'<div style="background:#161B22;border:1px solid #30363D;border-radius:12px;padding:20px;text-align:center;"><div style="color:#8B949E;font-size:10px;margin-bottom:8px;font-weight:700;">{l}</div><div style="font-size:22px;font-weight:900;color:{c};">{v}</div></div>'
m_cols[0].markdown(m_box("WATCH UNITS", f"{len(portfolio)} U"), unsafe_allow_html=True)
shield_lvl = sum(calculate_loss_rate(p.get('purchase_price',10000)*0.95, p.get('purchase_price',10000)) for p in portfolio) / len(portfolio) if portfolio else 0
m_cols[1].markdown(m_box("AVG SHIELD LEVEL", f"{shield_lvl:+.2f}%", "#FF3131" if shield_lvl < 0 else "#39FF14"), unsafe_allow_html=True)
m_cols[2].markdown(m_box("THREAT VECTORS", f"{d_cnt} U", "#FF3131" if d_cnt else "#39FF14"), unsafe_allow_html=True)
m_cols[3].markdown(m_box("PENDING LISTINGS", f"{len(upcoming_list)} U", "#FFFF33"), unsafe_allow_html=True)

st.divider()

# --- Sidebar Command ---
with st.sidebar:
    st.header("🛠️ CONTROL")
    is_list = ["KODEX", "TIGER", "KBSTAR", "ACE", "SOL"]
    s_is = [i for i in is_list if st.checkbox(i, key=f"s_{i}")]
    f_is = s_is if s_is else is_list
    f_pool = [e for e in etf_list if any(i in e['issuer'] for i in f_is)]
    if not f_pool: f_pool = etf_list[:50]
    if st.button("♻️ SYSTEM FACTORY RESET"): s_json('data/user_portfolio.json', []); st.rerun()

# --- Tab Interface ---
tabs = st.tabs(["📊 Market Watch", "📅 Upcoming", "🚨 Control Room"])

# Tab 1: Market Watch (3-Column Master Grid)
with tabs[0]:
    themes = {
        "AI & Semiconductor Strategy": ["AI", "반도체", "NVIDIA", "HBM"],
        "USA Big Tech Strategy": ["미국", "빅테크", "나스닥", "S&P"],
        "ValueUp / Dividend Strategy": ["밸류업", "저PBR", "배당", "인컴"],
        "Emerging Themes": ["양자", "우주", "에너지", "바이오"],
        "Global Infrastructure": ["인프라", "에너지", "원자력", "수계"],
        "Healthcare & Bio": ["바이오", "제약", "헬스케어"]
    }
    th_items = list(themes.items())
    for i in range(0, len(th_items), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(th_items):
                t_nm, t_ks = th_items[i+j]
                with cols[j]:
                    st.markdown(f'<div class="master-box"><div class="theme-title">{t_nm}</div>', unsafe_allow_html=True)
                    # Filter + Fallback (Top 10)
                    t_l = []
                    seen_s = set()
                    for e in f_pool:
                        if any(k.lower() in e['name'].lower() for k in t_ks):
                            t_l.append(e); seen_s.add(e['symbol'])
                    if len(t_l) < 10:
                        for e in f_pool:
                            if e['symbol'] not in seen_s:
                                t_l.append(e); seen_s.add(e['symbol'])
                            if len(t_l) >= 10: break
                    
                    # 5-Stage Sync Execution (Physical Fix)
                    for r, item in enumerate(t_l[:10]):
                        p_key = f"mw_{t_nm}_{item['symbol']}_{r+1}"
                        is_t = any(p['symbol'] == item['symbol'] for p in portfolio)
                        # Row Master Grid with Flex Simulation (st.columns with Fixed Proportions)
                        # Width mapping: 30(0.3) | 80(0.8) | Flex(4) | 100(1) | 70(0.7)
                        r_cols = st.columns([0.4, 1.2, 4.5, 1.6, 1.3])
                        r_cols[0].markdown(f'<div style="font-weight:900;color:#8B949E;height:34px;display:flex;align-items:center;font-size:12px;">{r+1}</div>', unsafe_allow_html=True)
                        r_cols[1].markdown(f'<div style="font-weight:800;color:#8B949E;height:34px;display:flex;align-items:center;font-size:11px;">{item["issuer"]}</div>', unsafe_allow_html=True)
                        r_cols[2].markdown(f'<div style="font-weight:700;height:34px;display:flex;align-items:center;font-size:12px;overflow:hidden;text-overflow:ellipsis;">{item["name"][:18]}</div>', unsafe_allow_html=True)
                        r_cols[3].markdown(f'<div style="font-weight:900;color:#39FF14;height:34px;display:flex;align-items:center;justify-content:flex-end;font-size:12px;">{item["price_at_listing"]:,}</div>', unsafe_allow_html=True)
                        with r_cols[4]:
                            st.markdown('<div style="height:34px;display:flex;align-items:center;">', unsafe_allow_html=True)
                            if is_t:
                                if st.button("UN", key=f"un_{p_key}", help="UNTRACK"):
                                    portfolio = [p for p in portfolio if p['symbol'] != item['symbol']]; s_j('data/user_portfolio.json', portfolio); st.rerun()
                            else:
                                if st.button("TR", key=f"tr_{p_key}", help="TRACK"):
                                    portfolio.append({"symbol":item['symbol'], "name":item['name'], "purchase_price":item['price_at_listing'], "status":"추적 중"})
                                    s_j('data/user_portfolio.json', portfolio); st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)
                        if r < 9: st.markdown('<div style="border-bottom:1px solid #21262D;margin:0;"></div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

# Tab 2: Upcoming (5-Section Terminal)
with tabs[1]:
    m_st = datetime.now() - timedelta(days=datetime.now().weekday())
    w_d = ["MON", "TUE", "WED", "THU", "FRI"]; u_grid = st.columns(5)
    for k in range(5):
        d_val = (m_st + timedelta(days=k)).strftime("%Y-%m-%d")
        with u_grid[k]:
            st.markdown(f'<div class="cal-header">{w_d[k]} ({d_val})</div>', unsafe_allow_html=True)
            u_l = [e for e in upcoming_list if e['listing_date'] == d_val]
            if not u_l: st.markdown("<div style='font-size:11px;color:#484F58;padding:25px;text-align:center;'>O : CLEAR</div>", unsafe_allow_html=True)
            for m, item in enumerate(u_l):
                with st.container():
                    p_res = next((p for p in portfolio if p['symbol'] == item['ticker']), None)
                    # Tier 1: Horizontal Info
                    st.markdown(f'<div class="cal-item"><div style="font-size:10px;color:#8B949E;font-weight:700;">{item["issuer"]} | {item["ticker"]}</div><div style="font-size:13px;font-weight:900;margin:6px 0;overflow:hidden;text-overflow:ellipsis;">{item["name"][:18]}</div><div style="font-size:12px;color:#39FF14;font-weight:900;">START: 10,000 KRW</div>', unsafe_allow_html=True)
                    # Tier 2: Button & State
                    if p_res:
                        st.markdown(f"<div style='font-size:11px;color:#FFFF33;font-weight:900;margin-top:8px;'>🔢 VOL: {p_res.get('quantity', 0)} UNIT</div>", unsafe_allow_html=True)
                        if st.button("CANCEL", key=f"up_ab_{item['ticker']}_{k}_{m}"):
                            portfolio = [p for p in portfolio if p['symbol'] != item['ticker']]; s_j('data/user_portfolio.json', portfolio); st.rerun()
                    else:
                        s_key = f"s_res_{item['ticker']}"
                        if not st.session_state.get(s_key):
                            if st.button("RESERVE", key=f"up_pre_{item['ticker']}_{k}_{m}"): st.session_state[s_key]=True; st.rerun()
                        else:
                            q_v = st.number_input("VOL(UNIT)", min_value=1, value=10, step=1, key=f"q_{item['ticker']}")
                            st.markdown(f"<p style='font-size:11px;color:#39FF14;margin:6px 0;'>Command: {q_v} Unit(s)?</p>", unsafe_allow_html=True)
                            bc1, bc2 = st.columns(2)
                            if bc1.button("DEPLOY", key=f"up_ok_{item['ticker']}"):
                                portfolio.append({"symbol":item['ticker'], "name":item['name'], "quantity":q_v, "status":"대기", "listing_date":item['listing_date']})
                                s_j('data/user_portfolio.json', portfolio); st.session_state[s_key]=False; st.rerun()
                            if bc2.button("HALT", key=f"up_no_{item['ticker']}"): st.session_state[s_key]=False; st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

# Tab 3: Control Room (Dual-Stage 관제)
with tabs[2]:
    p1, p2 = st.columns(2)
    # Stage 1: Active Monitoring (Loss ASC)
    with p1:
        st.markdown('<div class="theme-header">⚠️ Monitoring Priority (Loss ASC)</div>', unsafe_allow_html=True)
        act_l = []
        for p in portfolio:
            if p['status'] != '대기':
                b_p = p.get('purchase_price', 10000); c_p = b_p * (0.95 if p['status'] == '추적 중' else 0.88)
                p['ls'] = calculate_loss_rate(c_p, b_p); p['cv'] = c_p
                act_l.append(p)
        act_l.sort(key=lambda x: x['ls'])
        if not act_l: st.info("No active units scanned.")
        for idx, item in enumerate(act_l):
            ls_r = item['ls']
            st.markdown(f'<div class="master-box" style="padding:15px;margin-bottom:15px;"><div style="display:flex;justify-content:space-between;align-items:center;"><div><span style="background:{"#FF3131" if ls_r<=-8 else "#39FF14"};color:#0A0E14;padding:3px 8px;border-radius:4px;font-size:10px;font-weight:900;margin-right:10px;">{item["status"]}</span><b style="font-size:16px;">{item["name"]}</b></div><div style="font-size:24px;font-weight:900;color:{"#FF3131" if ls_r<=-8 else "#39FF14"};">{ls_r:+.1f}%</div></div>', unsafe_allow_html=True)
            rm_s = 10.0 + ls_r; w_f = min(100, (abs(ls_r)/10.0)*100); r_c = "#39FF14" if rm_s>5 else "#FFA500" if rm_s>2 else "#FF3131"
            st.markdown(f'<div style="font-size:11px;color:#8B949E;margin-top:10px;">Shield Depletion: {abs(ls_r):.1f}% | Integrity: {rm_s:+.1f}%</div><div style="width:100%;height:8px;background:#21262D;border-radius:4px;margin-top:8px;"><div style="width:{w_f}%;height:100%;background:{r_c};border-radius:4px;"></div></div>', unsafe_allow_html=True)
            st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)
            if st.button("TERMINATE TRACKING UNIT", key=f"cr_kill_{item['symbol']}_{idx}"):
                portfolio = [p for p in portfolio if p['symbol'] != item['symbol']]; s_j('data/user_portfolio.json', portfolio); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # Stage 2: Pending Command (Date ASC)
    with p2:
        st.markdown('<div class="theme-header">⏳ Stage 2: Pending Control</div>', unsafe_allow_html=True)
        pend_l = [p for p in portfolio if p['status'] == '대기']
        pend_l.sort(key=lambda x: x.get('listing_date', '9999-12-31'))
        if not pend_l: st.info("Pending pool clear.")
        for idx, item in enumerate(pend_l):
            st.markdown(f'<div class="master-box" style="padding:20px;margin-bottom:15px;"><div style="display:flex;justify-content:space-between;align-items:center;"><div><span style="background:#FFFF33;color:#0A0E14;padding:3px 8px;border-radius:4px;font-size:10px;font-weight:900;margin-right:10px;">PENDING</span><b style="font-size:16px;">{item["name"]}</b></div><div style="font-size:12px;color:#8B949E;text-align:right;line-height:1.4;">📅 {item.get("listing_date")}<br>🔢 {item.get("quantity",0)} UNIT</div></div>', unsafe_allow_html=True)
            st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)
            if st.button("ABORT COMMAND SEQUENCE", key=f"cr_ab_{item['symbol']}_{idx}"):
                portfolio = [p for p in portfolio if p['symbol'] != item['symbol']]; s_j('data/user_portfolio.json', portfolio); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='color:#484F58;font-size:11px;text-align:center;margin-top:100px;'>Hyper ETF Guardian v5.5 [Master Physical Spec]<br>Infrastructure Logic: Gemini 2.0 Flash / SnF Convergence Build</div>", unsafe_allow_html=True)
