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
        sys_p = "Quant Expert. No greetings. Strictly: [Risk: X / Cause: Y / Recommendation: Z]."
        response = model.generate_content(f"{sys_p}\n\n{prompt}")
        if not response or not response.text:
            return "[Risk: 5.0 / Cause: Intelligence Offline / Recommendation: Standby]"
        return response.text.replace("\n", " ").strip()
    except Exception:
        return "[Risk: 5.0 / Cause: Connection Error / Recommendation: Manual Guard]"

# --- Global Integrity: [CSS Mastery] v5.0 ---
st.markdown("<style>/* v5.0 Final Directive Styles */.stApp{background-color:#0A0E14!important;color:#FFFFFF!important;}h1,h2,h3,h4,h5,h6,p,span,label,div,li{color:#FFFFFF!important;font-family:'Inter',sans-serif!important;}/* Master Theme Box */.master-box{background-color:#161B22 !important;border:1px solid #30363D !important;border-radius:12px;padding:20px;margin-bottom:30px;box-shadow:0 8px 16px rgba(0,0,0,0.5);}.theme-header{font-size:16px;font-weight:900;margin-bottom:15px;color:#FFFFFF!important;border-left:4px solid #39FF14;padding-left:12px;text-transform:uppercase;}/* Market Watch: Single-Line Protocol */.row-container{display:flex;align-items:center;height:42px;width:100%;border-bottom:1px solid #21262D;font-size:12px;}.row-container:last-child{border-bottom:none;}.col-rank{width:30px;font-weight:900;color:#8B949E;}.col-issuer{width:80px;font-weight:800;color:#8B949E;}.col-name{flex:1;font-weight:700;padding:0 10px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}.col-price{width:100px;text-align:right;font-weight:900;color:#39FF14;}.col-btn{width:80px;display:flex;justify-content:flex-end;padding-left:10px;}/* Upcoming Terminal */.cal-header{font-size:15px;font-weight:900;color:#39FF14!important;border-bottom:2px solid #39FF14;padding:8px 0;margin-bottom:10px;}.cal-item-card{background:#161B22;border:1px solid #30363D;border-radius:10px;padding:15px;margin-bottom:15px;border-left:5px solid #FFFF33;}/* Control Room */.control-panel{background:#161B22;border:1px solid #30363D;border-radius:12px;padding:20px;height:100%;}/* Widget Overrides */input{background-color:#1C2128!important;color:#FFFFFF!important;border:1px solid #3E444D!important;}div[data-baseweb='input']{background-color:#1C2128!important;}.stButton>button{width:100%!important;background-color:#21262D!important;color:#FFFFFF!important;border:1px solid #30363D!important;font-weight:900!important;height:32px!important;border-radius:6px!important;font-size:10px!important;}.stButton>button:hover{border-color:#39FF14!important;color:#39FF14!important;}#MainMenu,footer,.stDeployButton{display:none!important;}div.block-container{padding-top:2rem!important;}</style>", unsafe_allow_html=True)

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

# Integrity Load
p_data = l_json('data/user_portfolio.json')
portfolio = []
s_seen = set()
for i in p_data:
    if i['symbol'] not in s_seen:
        portfolio.append(i); s_seen.add(i['symbol'])

etf_list = l_json('data/etf_list.json')
upcoming_list = l_json('data/upcoming_etf.json')

# --- Header Section ---
st.markdown("<h2 style='margin:0;'>📊 Hyper ETF Guardian <span style='font-size:12px;color:#39FF14;font-weight:400;'>[v5.0 MASTER]</span></h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#8B949E;font-size:13px;margin:-5px 0 20px 0;'>Command Terminal: Absolute Integrity & Strategic Finality.</p>", unsafe_allow_html=True)

# Intelligence Report
dang_count = len([p for p in portfolio if p.get('status') == '위험'])
ai_intel = get_ai_analysis(f"Units: {len(portfolio)} | Danger: {dang_count}. System Scan Complete.")
st.markdown(f'<div style="background:rgba(255,49,49,0.05);border:1px solid #FF3131;padding:15px;border-radius:10px;margin-bottom:25px;color:#FF3131;font-weight:900;font-size:14px;">🚨 {ai_intel} </div>', unsafe_allow_html=True)

# Metrics
mc = st.columns(4)
def mb(l, v, c="#39FF14"): return f'<div style="background:#161B22;border:1px solid #30363D;border-radius:12px;padding:18px;text-align:center;"><div style="color:#8B949E;font-size:10px;margin-bottom:8px;">{l}</div><div style="font-size:22px;font-weight:900;color:{c};">{v}</div></div>'
mc[0].markdown(mb("WATCH UNITS", f"{len(portfolio)} U"), unsafe_allow_html=True)
shield = sum(calculate_loss_rate(p.get('purchase_price',10000)*0.95, p.get('purchase_price',10000)) for p in portfolio) / len(portfolio) if portfolio else 0
mc[1].markdown(mb("SHIELD LEVEL", f"{shield:+.2f}%", "#FF3131" if shield < 0 else "#39FF14"), unsafe_allow_html=True)
mc[2].markdown(mb("THREATS", f"{dang_count} U", "#FF3131" if dang_count else "#39FF14"), unsafe_allow_html=True)
mc[3].markdown(mb("UPCOMING", f"{len(upcoming_list)} U", "#FFFF33"), unsafe_allow_html=True)

st.divider()

# --- Sidebar Control ---
with st.sidebar:
    st.header("🛠️ CONTROL")
    is_list = ["KODEX", "TIGER", "KBSTAR", "ACE", "SOL"]
    sel_is = [i for i in is_list if st.checkbox(i, key=f"s_{i}")]
    final_is = sel_is if sel_is else is_list
    f_pool = [e for e in etf_list if any(i in e['issuer'] for i in final_is)]
    if not f_pool: f_pool = etf_list[:50]
    if st.button("FACTORY RESET SYSTEM"): s_json('data/user_portfolio.json', []); st.rerun()

# --- Main Interface Tabs ---
tabs = st.tabs(["📊 Market Watch", "📅 Upcoming", "🚨 Control Room"])

# Tab 1: Market Watch (3-Column Master Card)
with tabs[0]:
    themes = {
        "AI & Semiconductor": ["AI", "반도체", "NVIDIA", "HBM"],
        "USA Big Tech": ["미국", "빅테크", "나스닥", "S&P"],
        "ValueUp / Dividend": ["밸류업", "저PBR", "배당", "인컴"],
        "Emerging Themes": ["양자", "우주", "에너지", "바이오"],
        "Global Infrastructure": ["인프라", "에너지", "원자력", "수계"],
        "Healthcare & Bio": ["바이오", "제약", "헬스케어"]
    }
    
    # 3-Column Grid
    theme_items = list(themes.items())
    for i in range(0, len(theme_items), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(theme_items):
                t_name, t_keys = theme_items[i+j]
                with cols[j]:
                    st.markdown(f'<div class="master-box"><div class="theme-header">{t_name}</div>', unsafe_allow_html=True)
                    # Data Filling (Top 10)
                    t_list = []
                    s_seen = set()
                    for e in f_pool:
                        if any(k.lower() in e['name'].lower() for k in t_keys):
                            t_list.append(e); s_seen.add(e['symbol'])
                    if len(t_list) < 10:
                        for e in f_pool:
                            if e['symbol'] not in s_seen:
                                t_list.append(e); s_seen.add(e['symbol'])
                            if len(t_list) >= 10: break
                    
                    # Row Loop: Single-Line Protocol
                    for rank, item in enumerate(t_list[:10]):
                        pk = f"mw_{t_name}_{item['symbol']}_{rank+1}"
                        is_p = any(p['symbol'] == item['symbol'] for p in portfolio)
                        
                        # [Zero-Space Minified HTML]
                        st.markdown(f'<div class="row-container"><span class="col-rank">{rank+1}</span><span class="col-issuer">{item["issuer"]}</span><span class="col-name">{item["name"][:18]}</span><span class="col-price">{item["price_at_listing"]:,} KRW</span></div>', unsafe_allow_html=True)
                        
                        btn_col = st.columns([1, 10]) # Button on new line for Streamlit alignment but visible right end via CSS/Hack
                        with btn_col[1]:
                            if is_p:
                                if st.button("UN TRACK", key=f"un_{pk}"):
                                    portfolio = [p for p in portfolio if p['symbol'] != item['symbol']]; s_json('data/user_portfolio.json', portfolio); st.rerun()
                            else:
                                if st.button("TRACK", key=f"tr_{pk}"):
                                    portfolio.append({"symbol":item['symbol'], "name":item['name'], "purchase_price":item['price_at_listing'], "status":"추적 중"})
                                    s_json('data/user_portfolio.json', portfolio); st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

# Tab 2: Upcoming (5-Section Terminal)
with tabs[1]:
    mon = datetime.now() - timedelta(days=datetime.now().weekday())
    days = ["MON", "TUE", "WED", "THU", "FRI"]; u_cols = st.columns(5)
    
    for i in range(5):
        d_str = (mon + timedelta(days=i)).strftime("%Y-%m-%d")
        with u_cols[i]:
            st.markdown(f'<div class="cal-header">{days[i]} ({d_str})</div>', unsafe_allow_html=True)
            d_list = [e for e in upcoming_list if e['listing_date'] == d_str]
            if not d_list: st.markdown("<div style='font-size:11px;color:#484F58;padding:20px;text-align:center;'>LISTING CLEAR</div>", unsafe_allow_html=True)
            
            for j, item in enumerate(d_list):
                with st.container():
                    p_res = next((p for p in portfolio if p['symbol'] == item['ticker']), None)
                    # Tier 1
                    st.markdown(f'<div class="cal-item-card"><div style="font-size:11px;color:#8B949E;font-weight:700;">{item["issuer"]} | {item["ticker"]}</div><div style="font-size:13px;font-weight:900;margin:4px 0;">{item["name"]}</div><div style="font-size:12px;color:#39FF14;font-weight:900;">START: 10,000 KRW</div>', unsafe_allow_html=True)
                    # Tier 2 (State Logic)
                    if p_res:
                        st.markdown(f"<div style='font-size:11px;color:#FFFF33;font-weight:900;margin-top:5px;'>🔢 VOL: {p_res.get('quantity', 0)} UNIT</div>", unsafe_allow_html=True)
                        if st.button("CANCEL", key=f"up_can_{item['ticker']}_{i}_{j}"):
                            portfolio = [p for p in portfolio if p['symbol'] != item['ticker']]; s_json('data/user_portfolio.json', portfolio); st.rerun()
                    else:
                        s_key = f"up_res_act_{item['ticker']}"
                        if not st.session_state.get(s_key):
                            if st.button("RESERVE", key=f"up_pre_{item['ticker']}_{i}_{j}"): st.session_state[s_key]=True; st.rerun()
                        else:
                            q_val = st.number_input("QUANTITY", min_value=1, value=10, step=1, key=f"q_set_{item['ticker']}")
                            st.markdown(f"<p style='font-size:10px;color:#39FF14;margin:4px 0;'>Reserve {q_val} units?</p>", unsafe_allow_html=True)
                            b1, b2 = st.columns(2)
                            if b1.button("CONFIRM", key=f"up_ok_{item['ticker']}"):
                                portfolio.append({"symbol":item['ticker'], "name":item['name'], "quantity":q_val, "status":"대기", "listing_date":item['listing_date']})
                                s_json('data/user_portfolio.json', portfolio); st.session_state[s_key]=False; st.rerun()
                            if b2.button("CLOSE", key=f"up_no_{item['ticker']}"): st.session_state[s_key]=False; st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

# Tab 3: Control Room (Dual-Column 관제)
with tabs[2]:
    c1, c2 = st.columns(2)
    # Col 1: Monitoring Priority (Loss Rate ASC)
    with c1:
        st.markdown('<div class="theme-header">⚠️ Monitoring Priority</div>', unsafe_allow_html=True)
        active = []
        for p in portfolio:
            if p['status'] != '대기':
                bp = p.get('purchase_price', 10000); cp = bp * (0.95 if p['status'] == '추적 중' else 0.88)
                p['loss_r'] = calculate_loss_rate(cp, bp); p['cur_v'] = cp
                active.append(p)
        active.sort(key=lambda x: x['loss_r'])
        
        if not active: st.info("Asset status clear.")
        for i, item in enumerate(active):
            lr = item['loss_r']
            st.markdown(f'<div class="master-box" style="padding:15px;margin-bottom:12px;"><div style="display:flex;justify-content:space-between;align-items:center;"><div><span style="background:{"#FF3131" if lr<=-8 else "#39FF14"};color:#0A0E14;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:900;margin-right:8px;">{item["status"]}</span><b style="font-size:15px;">{item["name"]}</b></div><div style="font-size:22px;font-weight:900;color:{"#FF3131" if lr<=-8 else "#39FF14"};">{lr:+.1f}%</div></div>', unsafe_allow_html=True)
            rem = 10.0 + lr; wd = min(100, (abs(lr)/10.0)*100); g_c = "#39FF14" if rem>5 else "#FFA500" if rem>2 else "#FF3131"
            st.markdown(f'<div style="font-size:10px;color:#8B949E;margin-top:8px;">Shield Integrity: {rem:+.1f}% | Burn: {abs(lr):.1f}%</div><div style="width:100%;height:6px;background:#21262D;border-radius:3px;margin:8px 0;"><div style="width:{wd}%;height:100%;background:{g_c};border-radius:3px;"></div></div>', unsafe_allow_html=True)
            if st.button("TERMINATE UNIT", key=f"cr_term_{item['symbol']}_{i}"):
                portfolio = [p for p in portfolio if p['symbol'] != item['symbol']]; s_json('data/user_portfolio.json', portfolio); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # Col 2: Stage 2 Pending (Listing Date ASC)
    with c2:
        st.markdown('<div class="theme-header">⏳ Stage 2: Pending</div>', unsafe_allow_html=True)
        pending = [p for p in portfolio if p['status'] == '대기']
        pending.sort(key=lambda x: x.get('listing_date', '9999-12-31'))
        
        if not pending: st.info("Pending pool clear.")
        for i, item in enumerate(pending):
            st.markdown(f'<div class="master-box" style="padding:15px;margin-bottom:12px;"><div style="display:flex;justify-content:space-between;align-items:center;"><div><span style="background:#FFFF33;color:#0A0E14;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:900;margin-right:8px;">PENDING</span><b style="font-size:15px;">{item["name"]}</b></div><div style="font-size:12px;color:#8B949E;text-align:right;">📅 {item.get("listing_date")}<br>🔢 {item.get("quantity",0)} UNIT</div></div>', unsafe_allow_html=True)
            if st.button("ABORT COMMAND", key=f"cr_ab_{item['symbol']}_{i}"):
                portfolio = [p for p in portfolio if p['symbol'] != item['symbol']]; s_json('data/user_portfolio.json', portfolio); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='color:#484F58;font-size:10px;text-align:center;margin-top:80px;'>Hyper ETF Guardian v5.0 [The Final Master Directive]<br>Strategic Logic: Gemini 2.0 Flash / SnF Finality Build</div>", unsafe_allow_html=True)
