import streamlit as st
import json
import os
import google.generativeai as genai
from monitor import calculate_loss_rate
from datetime import datetime, timedelta

# Project Finality Configuration
st.set_page_config(page_title="Hyper ETF Guardian", layout="wide", initial_sidebar_state="expanded")

# --- AI Intelligence Layer (Gemini 2.0 Flash) ---
GEMINI_API_KEY = "AIzaSyDfmWkvWuty0BjkhBainobKonjTL6She78"
genai.configure(api_key=GEMINI_API_KEY)

def get_ai_intel(prompt):
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        sys_p = "Quant Expert. Strictly: [Risk: X / Cause: Y / Rec: Z]."
        response = model.generate_content(f"{sys_p}\n\n{prompt}")
        if not response or not response.text:
            return "[Risk: 5.0 / Cause: Standby / Rec: Manual Check]"
        return response.text.replace("\n", " ").strip()
    except Exception:
        return "[Risk: 5.0 / Cause: Error / Rec: Manual Check]"

# --- Global Style Mastery: [THE FINAL ULTIMATUM v6.0] ---
# purging technical negligence, forcing absolute legibility.
st.markdown("<style>/* Global Force Colors */.stApp{background-color:#0A0E14!important;color:#FFFFFF!important;}h1,h2,h3,h4,h5,h6,p,span,label,div,li{color:#FFFFFF!important;font-family:'Inter',sans-serif!important;}/* Master Box: Physical spec */.v6-card{background-color:#161B22;border:1px solid #30363D;border-radius:12px;padding:22px;margin-bottom:30px;box-shadow:0 8px 16px rgba(0,0,0,0.5);overflow:hidden;}/* No-Break Rule & Flex Implementation */.v6-row{display:flex;justify-content:space-between;align-items:center;height:42px;white-space:nowrap!important;}.v6-ellipsis{overflow:hidden!important;text-overflow:ellipsis!important;flex-grow:1;padding:0 12px;font-weight:700;}.v6-rank{width:30px;font-weight:900;color:#8B949E;}.v6-issuer{width:80px;font-weight:900;color:#8B949E;}.v6-price{width:100px;text-align:right;font-weight:900;color:#39FF14;}/* Button Rescue: Dark Mode Visibility */.stButton>button{background-color:#30363D!important;color:#FFFFFF!important;border:1px solid #484F58!important;font-weight:900!important;height:34px!important;border-radius:6px!important;font-size:11px!important;letter-spacing:0.5px;transition:all 0.1s ease;}.stButton>button:hover{background-color:#484F58!important;border-color:#39FF14!important;color:#39FF14!important;}/* Upcoming Terminal Stability */.cal-header{font-size:16px;font-weight:900;color:#39FF14!important;padding:10px 0;border-bottom:2px solid #39FF14;margin-bottom:0px;}.cal-item{background:#161B22;border:1px solid #30363D;border-radius:10px;padding:18px;margin-top:15px;border-left:5px solid #FFFF33;min-height:180px;}/* Risk Control UI */.risk-alert{background:rgba(255,49,49,0.05);border:1px solid #FF3131;padding:20px;border-radius:10px;margin-bottom:30px;color:#FF3131!important;font-weight:900;font-size:14px;line-height:1.5;}#MainMenu,footer,.stDeployButton{display:none!important;}div.block-container{padding-top:2rem!important;}</style>", unsafe_allow_html=True)

# --- Data Utility Layer ---
def load_json(p):
    if not os.path.exists(p): return []
    try:
        with open(p,'r',encoding='utf-8') as f:
            c=f.read().strip(); return json.loads(c) if c else []
    except Exception: return []

def save_json(p, d):
    with open(p,'w',encoding='utf-8') as f:
        json.dump(d, f, indent=2, ensure_ascii=False)

# Load context with integrity
p_raw = load_json('data/user_portfolio.json')
portfolio = []
seen_s = set()
for i in p_raw:
    if i['symbol'] not in seen_s:
        portfolio.append(i); seen_s.add(i['symbol'])

etf_list = load_json('data/etf_list.json')
upcoming_list = load_json('data/upcoming_etf.json')

# --- Header Layer ---
st.markdown("<h2 style='margin:0;'>📊 Hyper ETF Guardian <span style='font-size:12px;color:#39FF14;font-weight:400;'>[v6.0 ULTIMATUM]</span></h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#8B949E;font-size:13px;margin:-5px 0 20px 0;'>Command Center. Precise Asset Visibility Unit.</p>", unsafe_allow_html=True)

# Tactical Intelligence
d_cnt = len([p for p in portfolio if p.get('status') == '위험'])
intel_report = get_ai_intel(f"Units: {len(portfolio)} | Threat Level: {d_cnt}. Protocol v6.0 engaged.")
st.markdown(f'<div class="risk-alert">🚨 {intel_report} </div>', unsafe_allow_html=True)

# Dashboard Summary
mc = st.columns(4)
def mb(l, v, c="#39FF14"): return f'<div style="background:#161B22;border:1px solid #30363D;border-radius:12px;padding:20px;text-align:center;"><div style="color:#8B949E;font-size:11px;margin-bottom:8px;font-weight:700;">{l}</div><div style="font-size:22px;font-weight:900;color:{c};">{v}</div></div>'
mc[0].markdown(mb("WATCH LIST", f"{len(portfolio)} UNITS"), unsafe_allow_html=True)
shield = sum(calculate_loss_rate(p.get('purchase_price',10000)*0.95, p.get('purchase_price',10000)) for p in portfolio) / len(portfolio) if portfolio else 0
mc[1].markdown(mb("AVG SHIELD", f"{shield:+.2f}%", "#FF3131" if shield < 0 else "#39FF14"), unsafe_allow_html=True)
mc[2].markdown(mb("BREACHES", f"{d_cnt} UNITS", "#FF3131" if d_cnt else "#39FF14"), unsafe_allow_html=True)
mc[3].markdown(mb("UPCOMING", f"{len(upcoming_list)} UNITS", "#FFFF33"), unsafe_allow_html=True)

st.divider()

# --- Sidebar Control ---
with st.sidebar:
    st.header("🛠️ CONTROL PANEL")
    issuers = ["KODEX", "TIGER", "KBSTAR", "ACE", "SOL"]
    sel_iss = [i for i in issuers if st.checkbox(i, key=f"is_{i}")]
    final_iss = sel_iss if sel_iss else issuers
    pool = [e for e in etf_list if any(i in e['issuer'] for i in final_iss)]
    if not pool: pool = etf_list[:50]
    if st.button("RE-INITIALIZE SYSTEM"): save_json('data/user_portfolio.json', []); st.rerun()

# --- Strategic Dashboard (Tabs) ---
tabs = st.tabs(["📊 Market Watch", "📅 Upcoming", "🚨 Control Room"])

# Tab 1: Market Watch (5-Stage Single Line Protocol)
with tabs[0]:
    themes = {
        "AI & Semiconductor Strategy": ["AI", "반도체", "NVIDIA", "HBM"],
        "USA Big Tech Strategy": ["미국", "빅테크", "나스닥", "S&P"],
        "ValueUp / Dividend Strategy": ["밸류업", "저PBR", "배당", "인컴"],
        "Emerging Tech Strategy": ["양자", "우주", "에너지", "바이오"],
        "Global Infra & Energy": ["인프라", "원자력", "수계", "그린"],
        "Bio & Healthcare": ["바이오", "제약", "헬스케어"]
    }
    th_list = list(themes.items())
    for i in range(0, len(th_list), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(th_list):
                t_nm, t_ks = th_list[i+j]
                with cols[j]:
                    st.markdown(f'<div class="v6-card"><div style="font-size:16px;font-weight:900;margin-bottom:20px;color:#FFFFFF;border-left:5px solid #39FF14;padding-left:12px;">{t_nm}</div>', unsafe_allow_html=True)
                    # Data Selection (Top 10)
                    t_pool = []
                    seen_etf = set()
                    for e in pool:
                        if any(k.lower() in e['name'].lower() for k in t_ks):
                            t_pool.append(e); seen_etf.add(e['symbol'])
                    if len(t_pool) < 10:
                        for e in pool:
                            if e['symbol'] not in seen_etf:
                                t_pool.append(e); seen_etf.add(e['symbol'])
                            if len(t_pool) >= 10: break
                    
                    # Row Implementation (Physical Flex Protocol)
                    for r, item in enumerate(t_pool[:10]):
                        p_key = f"mw_{t_nm}_{item['symbol']}_{r+1}"
                        is_tracked = any(p['symbol'] == item['symbol'] for p in portfolio)
                        
                        # [Physical Column Alignment]
                        # Ratio: 30px | 80px | Flex | 100px | 80px
                        # Approximation: 0.4 | 1.1 | 5.0 | 1.3 | 1.1
                        rc = st.columns([0.4, 1.1, 5.0, 1.3, 1.1])
                        rc[0].markdown(f'<div style="height:34px;display:flex;align-items:center;font-weight:900;color:#8B949E;font-size:12px;">{r+1}</div>', unsafe_allow_html=True)
                        rc[1].markdown(f'<div style="height:34px;display:flex;align-items:center;font-weight:900;color:#8B949E;font-size:11px;">{item["issuer"]}</div>', unsafe_allow_html=True)
                        rc[2].markdown(f'<div style="height:34px;display:flex;align-items:center;font-weight:700;font-size:12px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{item["name"][:20]}</div>', unsafe_allow_html=True)
                        rc[3].markdown(f'<div style="height:34px;display:flex;align-items:center;justify-content:flex-end;font-weight:900;color:#39FF14;font-size:12px;">{item["price_at_listing"]:,}</div>', unsafe_allow_html=True)
                        with rc[4]:
                            if is_tracked:
                                if st.button("UNTRACK", key=f"ut_{p_key}", help="Stop tracking this unit"):
                                    portfolio = [p for p in portfolio if p['symbol'] != item['symbol']]; save_json('data/user_portfolio.json', portfolio); st.rerun()
                            else:
                                if st.button("TRACK", key=f"tk_{p_key}", help="Initialize tracking protocol"):
                                    portfolio.append({"symbol":item['symbol'], "name":item['name'], "purchase_price":item['price_at_listing'], "status":"추적 중"})
                                    save_json('data/user_portfolio.json', portfolio); st.rerun()
                        if r < 9: st.markdown('<div style="border-bottom:1px solid #282E36;margin:0;"></div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

# Tab 2: Upcoming (5-Section Command Terminal)
with tabs[1]:
    m_now = datetime.now() - timedelta(days=datetime.now().weekday())
    w_days = ["MON", "TUE", "WED", "THU", "FRI"]; u_grid = st.columns(5)
    for k in range(5):
        d_val = (m_now + timedelta(days=k)).strftime("%Y-%m-%d")
        with u_grid[k]:
            st.markdown(f'<div class="cal-header">{w_days[k]} ({d_val})</div>', unsafe_allow_html=True)
            u_itms = [e for e in upcoming_list if e['listing_date'] == d_val]
            if not u_itms: st.markdown("<div style='font-size:11px;color:#484F58;padding:40px;text-align:center;'>LISTING CLEAR</div>", unsafe_allow_html=True)
            for m, item in enumerate(u_itms):
                with st.container():
                    p_res = next((p for p in portfolio if p['symbol'] == item['ticker']), None)
                    # Tier 1 Info Card
                    st.markdown(f'<div class="cal-item"><div style="font-size:10px;color:#8B949E;font-weight:700;">{item["issuer"]} | {item["ticker"]}</div><div style="font-size:14px;font-weight:900;margin:8px 0;height:40px;overflow:hidden;">{item["name"]}</div><div style="font-size:12px;color:#39FF14;font-weight:900;">START: 10,000 KRW</div>', unsafe_allow_html=True)
                    # Tier 2 Interaction Terminal
                    if p_res:
                        st.markdown(f"<div style='font-size:11px;color:#FFFF33;font-weight:900;margin-top:10px;'>🔢 VOL: {p_res.get('quantity', 0)} UNIT</div>", unsafe_allow_html=True)
                        if st.button("ABORT", key=f"ua_{item['ticker']}_{k}"):
                            portfolio = [p for p in portfolio if p['symbol'] != item['ticker']]; save_json('data/user_portfolio.json', portfolio); st.rerun()
                    else:
                        r_key = f"res_act_{item['ticker']}"
                        if not st.session_state.get(r_key):
                            if st.button("RESERVE", key=f"ui_{item['ticker']}_{k}"): st.session_state[r_key]=True; st.rerun()
                        else:
                            # Fixed volume input to prevent layout shake
                            v_val = st.number_input("VOL", min_value=1, value=10, step=1, key=f"qv_{item['ticker']}")
                            b1, b2 = st.columns(2)
                            if b1.button("DEPLOY", key=f"ub1_{item['ticker']}"):
                                portfolio.append({"symbol":item['ticker'], "name":item['name'], "quantity":v_val, "status":"대기", "listing_date":item['listing_date']})
                                save_json('data/user_portfolio.json', portfolio); st.session_state[r_key]=False; st.rerun()
                            if b2.button("HALT", key=f"ub2_{item['ticker']}"): st.session_state[r_key]=False; st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

# Tab 3: Control Room (Dual Stage Observation)
with tabs[2]:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div style="font-size:16px;font-weight:900;margin-bottom:20px;border-left:5px solid #FF3131;padding-left:12px;">⚠️ MONITORING PRIORITY (Loss ASC)</div>', unsafe_allow_html=True)
        act_un = []
        for p in portfolio:
            if p['status'] != '대기':
                bp = p.get('purchase_price', 10000); cp = bp * (0.95 if p['status'] == '추적 중' else 0.88)
                p['lr'] = calculate_loss_rate(cp, bp); p['cv'] = cp
                act_un.append(p)
        act_un.sort(key=lambda x: x['lr'])
        if not act_un: st.info("No active threats detected.")
        for idx, item in enumerate(act_un):
            l_r = item['lr']
            st.markdown(f'<div class="v6-card" style="padding:18px;margin-bottom:15px;"><div style="display:flex;justify-content:space-between;align-items:center;"><div><span style="background:{"#FF3131" if l_r<=-8 else "#39FF14"};color:#0A0E14;padding:2px 8px;border-radius:4px;font-size:10px;font-weight:900;margin-right:12px;">🛡️ {item["status"]}</span><b style="font-size:16px;">{item["name"]}</b></div><div style="font-size:24px;font-weight:900;color:{"#FF3131" if l_r<=-8 else "#39FF14"};">{l_r:+.1f}%</div></div>', unsafe_allow_html=True)
            rm_s = 10.0 + l_r; w_f = min(100, (abs(l_r)/10.0)*100); r_clr = "#39FF14" if rm_s>5 else "#FFA500" if rm_s>2 else "#FF3131"
            st.markdown(f'<div style="font-size:10px;color:#8B949E;margin-top:10px;">Shield Depletion: {abs(l_r):.1f}% | Integrity: {rm_s:+.1f}%</div><div style="width:100%;height:8px;background:#21262D;border-radius:4px;margin-top:8px;"><div style="width:{w_f}%;height:100%;background:{r_clr};border-radius:4px;"></div></div>', unsafe_allow_html=True)
            st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
            if st.button("TERMINATE TRACKING UNIT", key=f"kill_{item['symbol']}"):
                portfolio = [p for p in portfolio if p['symbol'] != item['symbol']]; save_json('data/user_portfolio.json', portfolio); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div style="font-size:16px;font-weight:900;margin-bottom:20px;border-left:5px solid #FFFF33;padding-left:12px;">⏳ STAGE 2: PENDING CONTROL</div>', unsafe_allow_html=True)
        pend_un = [p for p in portfolio if p['status'] == '대기']
        pend_un.sort(key=lambda x: x.get('listing_date', '9999-12-31'))
        if not pend_un: st.info("Pending queue clear.")
        for idx, item in enumerate(pend_un):
            st.markdown(f'<div class="v6-card" style="padding:18px;margin-bottom:15px;"><div style="display:flex;justify-content:space-between;align-items:center;"><div><span style="background:#FFFF33;color:#0A0E14;padding:2px 8px;border-radius:4px;font-size:10px;font-weight:900;margin-right:12px;">PENDING</span><b style="font-size:16px;">{item["name"]}</b></div><div style="font-size:12px;color:#8B949E;text-align:right;">📅 {item.get("listing_date")}<br>🔢 {item.get("quantity",0)} UNIT</div></div>', unsafe_allow_html=True)
            st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
            if st.button("ABORT SEQUENCE", key=f"ab_{item['symbol']}"):
                portfolio = [p for p in portfolio if p['symbol'] != item['symbol']]; save_json('data/user_portfolio.json', portfolio); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='color:#484F58;font-size:11px;text-align:center;margin-top:100px;'>Hyper ETF Guardian v6.0 [The Final Ultimatum]<br>Security Hash: SnF Finality Build / Quant Intelligence: Gemini 2.0 Flash</div>", unsafe_allow_html=True)
