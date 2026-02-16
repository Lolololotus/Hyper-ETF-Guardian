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
        sys_p = "Quant Expert. No greetings. Strictly: [위험 지수: X / 핵심 원인: Y / 권고 사항: Z]."
        response = model.generate_content(f"{sys_p}\n\n{prompt}")
        if not response or not response.text:
            return "[위험 지수: 5.0 / 핵심 원인: Intelligence Offline / 권고 사항: 자산 보존 대기]"
        return response.text.replace("\n", " ").strip()
    except Exception:
        return "[위험 지수: 5.0 / 핵심 원인: Connection Error / 권고 사항: 수동 방어 가동]"

# --- Absolute Mastery CSS (v4.1 Precision Dashboard) ---
# Fixing the 'Content Outside Card' issue by using solid container styling.
st.markdown("<style>/* v4.1 UI Master */.stApp{background-color:#0A0E14!important;color:#FFFFFF!important;}h1,h2,h3,h4,h5,h6,p,span,label,div,li{color:#FFFFFF!important;font-family:'Inter',sans-serif!important;}/* Precision Card Style */.item-row{background-color:#161B22;border:1px solid #21262D;padding:12px 15px;margin-bottom:2px;display:flex;justify-content:space-between;align-items:center;}.item-row:hover{background-color:#1C2128;}/* Inputs & Widgets */input{background-color:#1C2128!important;color:#FFFFFF!important;border:1px solid #3E444D!important;}div[data-baseweb='input']{background-color:#1C2128!important;}.stNumberInput div{background-color:#1C2128!important;}/* Buttons */.stButton>button{width:100%!important;background-color:#21262D!important;color:#FFFFFF!important;border:1px solid #30363D!important;font-weight:900!important;height:28px!important;border-radius:4px!important;font-size:9px!important;padding:0!important;}.stButton>button:hover{border-color:#39FF14!important;color:#39FF14!important;}/* Upcoming Layout Fix */.cal-header{font-size:15px;font-weight:900;color:#39FF14!important;margin-bottom:8px;border-bottom:2px solid #39FF14;padding-bottom:5px;}.cal-item{background:#161B22;border:1px solid #21262D;border-radius:6px;padding:10px;margin-bottom:10px;border-left:4px solid #FFFF33;overflow:hidden;}/* Badges */.badge{display:inline-block;padding:2px 6px;border-radius:3px;font-size:8px;font-weight:900;margin-right:5px;}.badge-tracking{background:rgba(57,255,20,0.1);color:#39FF14!important;border:1px solid #39FF14;}.badge-standby{background:rgba(255,255,51,0.1);color:#FFFF33!important;border:1px solid #FFFF33;}.badge-danger{background:rgba(255,49,49,0.1);color:#FF3131!important;border:1px solid #FF3131;}/* Risk Gauge */.g-bg{width:100%;height:4px;background:#21262D;border-radius:2px;margin-top:6px;}.g-fill{height:100%;border-radius:2px;}.risk-box{background:rgba(255,49,49,0.05);border:1px solid #FF3131;padding:12px;border-radius:6px;margin-bottom:20px;color:#FF3131!important;font-weight:900;font-size:12px;}#MainMenu,footer,.stDeployButton{display:none!important;}div.block-container{padding-top:1.5rem!important;}</style>", unsafe_allow_html=True)

# --- Data Utility ---
def load_json(p):
    if not os.path.exists(p): return []
    try:
        with open(p, 'r', encoding='utf-8') as f:
            c = f.read().strip(); return json.loads(c) if c else []
    except Exception: return []

def save_json(p, d):
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(d, f, indent=2, ensure_ascii=False)

# Load data and ensure integrity
p_raw = load_json('data/user_portfolio.json')
portfolio = []
seen = set()
for item in p_raw:
    if item['symbol'] not in seen:
        portfolio.append(item); seen.add(item['symbol'])

etf_list = load_json('data/etf_list.json')
upcoming_list = load_json('data/upcoming_etf.json')

# --- Header ---
st.markdown("<h2 style='margin:0;'>📊 Hyper ETF Guardian <span style='font-size:11px;color:#39FF14;font-weight:400;'>[v4.1 PRECISION]</span></h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#8B949E;font-size:12px;margin:-5px 0 15px 0;'>Command Center: No Noise, Just Assets.</p>", unsafe_allow_html=True)

# Risk Report
dang = [p for p in portfolio if p.get('status') == '위험']
rep = get_ai_analysis(f"Port:{len(portfolio)}, Danger:{len(dang)}.")
st.markdown(f'<div class="risk-box"> {rep} </div>', unsafe_allow_html=True)

# Metrics
mcols = st.columns(4)
def t(l, v, c="#39FF14"): return f'<div style="background:#161B22;border:1px solid #30363D;border-radius:8px;padding:12px;text-align:center;"><div style="color:#8B949E;font-size:9px;margin-bottom:4px;">{l}</div><div style="font-size:17px;font-weight:900;color:{c};">{v}</div></div>'
mcols[0].markdown(t("감시 유닛", f"{len(portfolio)} UNITS"), unsafe_allow_html=True)
avg_l = sum(calculate_loss_rate(p.get('purchase_price',10000)*0.95, p.get('purchase_price',10000)) for p in portfolio) / len(portfolio) if portfolio else 0
mcols[1].markdown(t("평균 방어선", f"{avg_l:+.1f}%", "#FF3131" if avg_l < 0 else "#39FF14"), unsafe_allow_html=True)
mcols[2].markdown(t("위기 대응", f"{len(dang)} 건", "#FF3131" if dang else "#39FF14"), unsafe_allow_html=True)
mcols[3].markdown(t("상장 예정", f"{len(upcoming_list)} 건", "#FFFF33"), unsafe_allow_html=True)

st.divider()

# --- Sidebar ---
with st.sidebar:
    st.header("🛠️ 통제 옵션")
    iss_all = ["KODEX", "TIGER", "KBSTAR", "ACE", "SOL"]
    sel_iss = [i for i in iss_all if st.checkbox(i, key=f"s_{i}")]
    final_iss = sel_iss if sel_iss else iss_all
    f_etfs = [e for e in etf_list if any(i in e['issuer'] for i in final_iss)]
    if not f_etfs: f_etfs = etf_list[:50]
    if st.button("♻️ RESET PORTFOLIO"): save_json('data/user_portfolio.json', []); st.rerun()

# --- Tabs ---
tabs = st.tabs(["📊 Market Watch", "📅 Upcoming", "🚨 Control Room"])

# Tab 1: Market Watch (Precision Card Layout)
with tabs[0]:
    themes = {
        "AI & 반도체": ["AI", "반도체", "NVIDIA", "HBM"],
        "미국 빅테크": ["미국", "빅테크", "나스닥", "S&P"],
        "밸류업 / 배당": ["밸류업", "저PBR", "배당", "인컴"],
        "신흥 테마": ["양자", "우주", "에너지", "바이오"]
    }
    
    # 2x2 Layout
    r1 = st.columns(2); r2 = st.columns(2)
    card_grids = [r1[0], r1[1], r2[0], r2[1]]
    
    for c_idx, (t_name, kws) in enumerate(themes.items()):
        with card_grids[c_idx]:
            st.markdown(f'<h4 style="margin:5px 0 10px 0;font-size:14px;color:#FFFFFF!important;">📌 {t_name} <span style="font-size:9px;color:#8B949E;margin-left:8px;">TOP 10</span></h4>', unsafe_allow_html=True)
            # 데이터 수집 (Filter + Fallback to Top 10)
            t_itms = []
            seen_cat = set()
            # Theme first
            for e in f_etfs:
                if any(k.lower() in e['name'].lower() for k in kws):
                    t_itms.append(e); seen_cat.add(e['symbol'])
            # Fill up to 10
            if len(t_itms) < 10:
                for e in f_etfs:
                    if e['symbol'] not in seen_cat:
                        t_itms.append(e); seen_cat.add(e['symbol'])
                        if len(t_itms) >= 10: break
            
            for i, item in enumerate(t_itms[:10]):
                is_p = any(p['symbol'] == item['symbol'] for p in portfolio)
                # Render each row as a contained block
                st.markdown(f'<div class="item-row"><div><span style="color:#8B949E;font-size:10px;display:block;line-height:1;">{item["issuer"]}</span><span style="font-weight:700;font-size:12px;">{item["name"][:16]}</span></div><div style="text-align:right;"><span style="color:#39FF14;font-weight:900;font-size:13px;display:block;">{item["price_at_listing"]:,}</span></div></div>', unsafe_allow_html=True)
                # Operation Line
                cc1, cc2 = st.columns([5, 1.5])
                with cc2:
                    if is_p:
                        if st.button("UN", key=f"mw_u_{item['symbol']}_{c_idx}_{i}"):
                            portfolio = [p for p in portfolio if p['symbol'] != item['symbol']]; save_json('data/user_portfolio.json', portfolio); st.rerun()
                    else:
                        if st.button("TR", key=f"mw_t_{item['symbol']}_{c_idx}_{i}"):
                            portfolio.append({"symbol":item['symbol'], "name":item['name'], "purchase_price":item['price_at_listing'], "status":"추적 중"})
                            save_json('data/user_portfolio.json', portfolio); st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)

# Tab 2: Upcoming (Volume Logic & Alignment)
with tabs[1]:
    mon = datetime.now() - timedelta(days=datetime.now().weekday())
    days = ["월", "화", "수", "목", "금"]; ucols = st.columns(5)
    for i in range(5):
        d_str = (mon + timedelta(days=i)).strftime("%Y-%m-%d")
        with ucols[i]:
            st.markdown(f'<div class="cal-header">{days[i]} ({d_str})</div>', unsafe_allow_html=True)
            d_itms = [e for e in upcoming_list if e['listing_date'] == d_str]
            if not d_itms: st.markdown("<div style='font-size:10px;color:#484F58;padding:5px;'>O: NO LISTING</div>", unsafe_allow_html=True)
            for j, item in enumerate(d_itms):
                with st.container():
                    res = next((p for p in portfolio if p['symbol'] == item['ticker']), None)
                    st.markdown(f'<div class="cal-item"><span class="badge badge-standby">STANDBY</span><div style="font-size:11px;font-weight:800;margin:2px 0;">{item["name"]}</div>', unsafe_allow_html=True)
                    if res:
                        st.markdown(f"<div style='font-size:10px;color:#FFFF33;'>예약수량: {res.get('quantity', 0)} 주</div>", unsafe_allow_html=True)
                        if st.button("CANCEL", key=f"up_c_{item['ticker']}_{i}_{j}"):
                            portfolio = [p for p in portfolio if p['symbol'] != item['ticker']]; save_json('data/user_portfolio.json', portfolio); st.rerun()
                    else:
                        k = f"res_p_{item['ticker']}"
                        if not st.session_state.get(k):
                            if st.button("CHECK", key=f"up_p_{item['ticker']}_{i}_{j}"): st.session_state[k]=True; st.rerun()
                        else:
                            q_val = st.number_input("수량(주)", min_value=1, value=10, step=1, key=f"qty_{item['ticker']}")
                            st.markdown(f"<p style='font-size:10px;color:#39FF14;margin:2px 0;'>{q_val}주를 예약하시겠습니까?</p>", unsafe_allow_html=True)
                            c1, c2 = st.columns(2)
                            if c1.button("확정", key=f"up_o_{item['ticker']}"):
                                portfolio.append({"symbol":item['ticker'], "name":item['name'], "quantity":q_val, "status":"대기", "listing_date":item['listing_date']})
                                save_json('data/user_portfolio.json', portfolio); st.session_state[k]=False; st.rerun()
                            if c2.button("닫기", key=f"up_x_{item['ticker']}"): st.session_state[k]=False; st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

# Tab 3: Control Room (Risk Priority)
with tabs[2]:
    st.subheader("⚠️ Monitoring Priority (Risk ASC)")
    act = []
    for p in portfolio:
        if p['status'] != '대기':
            bp = p.get('purchase_price', 10000); cv = bp * (0.95 if p['status'] == '추적 중' else 0.88)
            p['loss'] = calculate_loss_rate(cv, bp); p['cur'] = cv
            act.append(p)
    act.sort(key=lambda x: x['loss'])
    if not act: st.info("감시 대상 없음.")
    for i, item in enumerate(act):
        l = item['loss']
        st.markdown(f'<div class="item-row" style="border-radius:6px;margin-bottom:8px;"><div><span class="badge {"badge-danger" if l <= -8 else "badge-tracking"}">{item["status"]}</span><b>{item["name"]}</b></div><div style="text-align:right;"><span style="font-size:18px;font-weight:900;color:{"#FF3131" if l <= -8 else "#39FF14"};">{l:+.1f}%</span></div></div>', unsafe_allow_html=True)
        rem = 10.0 + l; clr = "#39FF14" if rem > 5 else "#FFA500" if rem > 2 else "#FF3131"; wd = min(100, (abs(l)/10.0)*100)
        st.markdown(f'<div style="font-size:10px;color:#8B949E;margin-top:2px;">방어선 잔여: <b>{rem:+.1f}%</b></div><div class="g-bg"><div class="g-fill" style="width:{wd}%;background:{clr};"></div></div>', unsafe_allow_html=True)
        if st.button("UNTRACK", key=f"cr_u_{item['symbol']}_{i}"):
            portfolio = [p for p in portfolio if p['symbol'] != item['symbol']]; save_json('data/user_portfolio.json', portfolio); st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)

    st.divider()
    st.subheader("⏳ Stage 2: Pending (Date ASC)")
    pend = [p for p in portfolio if p['status'] == '대기']
    pend.sort(key=lambda x: x.get('listing_date', '9999-12-31'))
    for i, item in enumerate(pend):
        l1, l2, l3 = st.columns([4, 2, 1])
        l1.markdown(f'<div style="padding:10px;background:#161B22;border:1px solid #21262D;border-radius:6px;"><span class="badge badge-standby">STANDBY</span> <b>{item["name"]}</b></div>', unsafe_allow_html=True)
        l2.markdown(f'<div style="padding:10px;text-align:center;">📅 {item.get("listing_date")} | {item.get("quantity",0)} 주</div>', unsafe_allow_html=True)
        with l3:
            if st.button("CANCEL", key=f"cr_c_{item['symbol']}_{i}"):
                portfolio = [p for p in portfolio if p['symbol'] != item['symbol']]; save_json('data/user_portfolio.json', portfolio); st.rerun()

st.markdown("<div style='color:#484F58;font-size:9px;text-align:center;margin-top:60px;'>Hyper ETF Guardian v4.1 [Precision Dashboard]<br>Intelligence: Gemini 2.0 Flash / SnF Overhaul Build [v4.1.1]</div>", unsafe_allow_html=True)
