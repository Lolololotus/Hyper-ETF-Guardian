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

@st.cache_data(ttl=3600)
def get_ai_analysis(prompt):
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception:
        return "Critical: AI Intelligence Offline."

def get_smart_recommendations(theme, etf_data):
    if not theme: return []
    db_symbols = {e["symbol"] for e in etf_data}
    prompt = f"Quant Expert: List top 3 symbols matching theme '{theme}' from provided symbols only. CSV format. Symbols: {','.join(list(db_symbols)[:100])}"
    res = get_ai_analysis(prompt)
    extracted = [s.strip() for s in res.split(',') if s.strip().isdigit()]
    return [s for s in extracted if s in db_symbols][:3]

# --- Custom CSS (High-End Blueprint) ---
st.markdown("""
<style>
.stApp{background-color:#0A0E14;color:#FFFFFF;}
h1,h2,h3{color:#FFFFFF!important;font-family:'Inter',sans-serif;font-weight:800;margin-bottom:10px!important;}
.stSubheader{color:#B0B0B0!important;font-weight:400;letter-spacing:1px;font-size:14px!important;}
.etf-card{background-color:#161B22;border:1px solid #30363D;border-radius:10px;padding:15px;margin-bottom:12px;transition:0.2s;display:flex;flex-direction:column;}
.etf-card:hover{transform:translateY(-3px);border-color:#39FF14;}
.badge{display:inline-block;padding:2px 8px;border-radius:4px;font-size:9px;font-weight:900;text-transform:uppercase;margin-bottom:8px;}
.badge-standby{background-color:rgba(255,255,51,0.1);color:#FFFF33;border:1px solid #FFFF33;}
.badge-tracking{background-color:rgba(57,255,20,0.1);color:#39FF14;border:1px solid #39FF14;}
.badge-danger{background-color:rgba(255,49,49,0.1);color:#FF3131;border:1px solid #FF3131;}
.stButton>button{width:100%;font-weight:bold!important;font-size:12px!important;}
.tracked-btn button{background-color:#21262D!important;color:#8B949E!important;border:1px solid #30363D!important;}
.pre-check-btn button{background-color:#39FF14!important;color:#000000!important;border:none!important;}
.reserved-btn button{background-color:#21262D!important;color:#FFFF33!important;border:1px solid #FFFF33!important;}
.gauge-container{width:100%;background-color:#21262D;border-radius:2px;height:6px;margin-top:10px;position:relative;}
.gauge-fill{height:100%;border-radius:2px;transition:width 0.5s ease-in-out;}
.vision-banner{background-color:rgba(57,255,20,0.03);border-left:4px solid #39FF14;padding:12px;border-radius:2px;margin-bottom:20px;color:#B0B0B0;font-size:12px;line-height:1.5;}
.risk-box{background-color:rgba(255,49,49,0.08);border:1px solid #FF3131;padding:10px 15px;border-radius:4px;margin-bottom:20px;font-size:13px;font-weight:bold;color:#FF3131;}
.metric-tile{background:#161B22;border:1px solid #30363D;border-radius:8px;padding:12px;text-align:center;}
.calendar-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;}
.calendar-day{background-color:#0D1117;border:1px solid #21262D;border-radius:8px;padding:10px;min-height:160px;}
.calendar-date{font-size:10px;color:#484F58;margin-bottom:8px;border-bottom:1px solid #21262D;padding-bottom:4px;font-weight:900;text-align:center;}
.cal-item{background:#161B22;padding:6px;border-radius:4px;margin-bottom:6px;border-left:2px solid #FFFF33;}
</style>
""", unsafe_allow_html=True)

# 데이터 유무니
def load_json(path):
    if not os.path.exists(path): return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            return json.loads(content) if content else []
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
    # Extreme Minification to prevent ghost tags
    html = f'<div style="font-size:9px;color:#8B949E;margin-top:8px;">방어선 잔여:<b>{rem:+.1f}%</b></div><div class="gauge-container"><div class="gauge-fill" style="width:{percent}%;background-color:{color};"></div></div><div style="display:flex;justify-content:space-between;font-size:8px;margin-top:4px;color:#484F58;font-weight:bold;"><span>0%</span><span style="color:#FF3131;">-10%</span></div>'
    return html

# 데이터 로드
etf_list = load_json('data/etf_list.json')
upcoming_list = load_json('data/upcoming_etf.json')
portfolio = load_json('data/user_portfolio.json')

# --- Header Section (Global) ---
header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.markdown("<h2 style='margin:0;'>📊 Hyper ETF Guardian</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#8B949E;font-size:14px;margin-top:-5px;'>No Prose, Just Precision.</p>", unsafe_allow_html=True)

# AI Risk Analysis (Red Box)
danger_items = [p for p in portfolio if p.get('status') == '위험']
tracking_cnt = len([p for p in portfolio if p.get('status') == '추적 중'])
risk_prompt = f"Quant Expert Analysis: Portfolio has {len(danger_items)} DANGER items and {tracking_cnt} tracking items. Summarize threat in 1 line."
ai_risk_report = get_ai_analysis(risk_prompt)
st.markdown(f'<div class="risk-box">[AI Quant Analysis] {ai_risk_report}</div>', unsafe_allow_html=True)

# Metric Tiles (New Columns 4)
processed_metrics = []
for p in portfolio:
    bp = p.get('purchase_price', 10000)
    if bp == 0: bp = 10000
    cv = bp * (0.965 if p['status'] == '추적 중' else 0.88 if p['status'] == '위험' else 1.0)
    processed_metrics.append({'loss': calculate_loss_rate(cv, bp), 'status': p['status']})

avg_ret = sum(x['loss'] for x in processed_metrics) / len(processed_metrics) if processed_metrics else 0
upcoming_7d = len(upcoming_list) # Simplified

m_cols = st.columns(4)
m_cols[0].markdown(f'<div class="metric-tile"><div style="color:#8B949E;font-size:10px;">총 감시 종목</div><div style="font-size:18px;font-weight:900;color:#39FF14;">{len(portfolio)} <span style="font-size:10px;">UNIT</span></div></div>', unsafe_allow_html=True)
m_cols[1].markdown(f'<div class="metric-tile"><div style="color:#8B949E;font-size:10px;">평균 방어 수익률</div><div style="font-size:18px;font-weight:900;color:{"#FF3131" if avg_ret < 0 else "#39FF14"};">{avg_ret:+.1f}%</div></div>', unsafe_allow_html=True)
m_cols[2].markdown(f'<div class="metric-tile"><div style="color:#8B949E;font-size:10px;">위험(DANGER) 수</div><div style="font-size:18px;font-weight:900;color:{"#FF3131" if len(danger_items) > 0 else "#39FF14"};">{len(danger_items)}</div></div>', unsafe_allow_html=True)
m_cols[3].markdown(f'<div class="metric-tile"><div style="color:#8B949E;font-size:10px;">상장 예정(7D)</div><div style="font-size:18px;font-weight:900;color:#FFFF33;">{upcoming_7d}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- Sidebar Filters ---
with st.sidebar:
    st.image("https://via.placeholder.com/150x50/161B22/39FF14?text=HYPER+GUARD", use_container_width=True)
    st.header("🛠️ 관측 통제소")
    issuers_static = ["KODEX", "TIGER", "KBSTAR", "ACE", "SOL"]
    selected_issuers = []
    for issuer in issuers_static:
        if st.checkbox(issuer, value=False, key=f"f_{issuer}"):
            selected_issuers.append(issuer)
    effective_issuers = selected_issuers if selected_issuers else issuers_static
    filtered_base = [e for e in etf_list if any(iss in e['issuer'] for iss in effective_issuers)]
    
    st.header("🤖 AI Smart Slots")
    theme1 = st.text_input("Custom Theme 1", placeholder="예: 양자컴퓨팅", key="st_1")
    theme2 = st.text_input("Custom Theme 2", placeholder="예: 우주항공", key="st_2")
    
    st.divider()
    if st.button("♻️ RESET PORTFOLIO"): save_json('data/user_portfolio.json', []); st.rerun()

# --- Tabs ---
tabs = st.tabs(["📊 Market Watch", "📅 Upcoming", "🚨 Control Room"])

with tabs[0]:
    st.markdown('<div class="vision-banner"><strong>[BETA Vision]</strong> 5대 운용사의 ETF 데이터를 실시간 추적하고 <strong>\'0.1초 자동 매수 시스템\'</strong>을 통해 기회를 선점합니다.</div>', unsafe_allow_html=True)
    
    # Priority AI Slot (Smart AI Slot)
    if theme1 or theme2:
        st.subheader("🤖 Smart AI Slot")
        ai_cols = st.columns(3)
        ai_idx = 0
        for t in [theme1, theme2]:
            if t:
                recs = get_smart_recommendations(t, etf_list)
                for sym in recs:
                    item = next((e for e in etf_list if e['symbol'] == sym), None)
                    if item:
                        with ai_cols[ai_idx % 3]:
                            card = f'<div class="etf-card"><div style="color:#8B949E;font-size:9px;">{item["issuer"]} | AI Match</div><div style="font-size:15px;font-weight:bold;color:#39FF14;margin:8px 0;">{item["name"]}</div><div style="font-size:18px;font-weight:900;">{item["price_at_listing"]:,} KRW</div></div>'
                            st.markdown(card, unsafe_allow_html=True)
                            if st.button("TRACK", key=f"ai_t_{item['symbol']}"):
                                portfolio.append({"symbol": item['symbol'], "name": item['name'], "purchase_price": item['price_at_listing'], "status": "추적 중"})
                                save_json('data/user_portfolio.json', portfolio); st.rerun()
                        ai_idx += 1
        st.divider()

    # Hierarchical Sections
    main_sections = {
        "AI & 반도체": ["AI", "반도체", "NVIDIA"],
        "밸류업 / 저PBR": ["밸류업", "저PBR", "금융"],
        "미국 빅테크": ["나스닥", "S&P", "빅테크"],
        "월배당 / 인컴": ["월배당", "배당", "커버드콜", "인컴"]
    }
    for sec_name, ident in main_sections.items():
        sec_etfs = [e for e in filtered_base if any(k.lower() in e['name'].lower() for k in ident)]
        if not sec_etfs: continue
        st.subheader(sec_name)
        cols = st.columns(3)
        for idx, item in enumerate(sec_etfs):
            exist_p = next((p for p in portfolio if p['symbol'] == item['symbol']), None)
            with cols[idx % 3]:
                card = f'<div class="etf-card"><div style="color:#8B949E;font-size:9px;">{item["issuer"]}</div><div style="font-size:15px;font-weight:bold;color:white;margin:8px 0;">{item["name"]}</div><div style="font-size:18px;font-weight:900;">{item["price_at_listing"]:,} KRW</div></div>'
                st.markdown(card, unsafe_allow_html=True)
                if exist_p:
                    st.markdown('<div class="tracked-btn">', unsafe_allow_html=True)
                    if st.button("✓ TRACKED", key=f"mw_in_{item['symbol']}"):
                        portfolio = [p for p in portfolio if p['symbol'] != item['symbol']]; save_json('data/user_portfolio.json', portfolio); st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    if st.button("TRACK", key=f"mw_add_{item['symbol']}"):
                        portfolio.append({"symbol": item['symbol'], "name": item['name'], "purchase_price": item['price_at_listing'], "status": "추적 중"})
                        save_json('data/user_portfolio.json', portfolio); st.rerun()

with tabs[1]:
    st.markdown('<div class="vision-banner"><strong>[BETA Vision]</strong> 상장 즉시 자동 체결 시스템을 통해 인간의 반응 속도를 넘어선 미래 자산을 선점하십시오.</div>', unsafe_allow_html=True)
    today = datetime.now()
    mon = today - timedelta(days=today.weekday())
    cols = st.columns(5)
    days_kr = ["월", "화", "수", "목", "금"]
    for i in range(5):
        d = (mon + timedelta(days=i)).strftime("%Y-%m-%d")
        with cols[i]:
            st.markdown(f'<div class="calendar-day"><div class="calendar-date">{days_kr[i]} ({d})</div>', unsafe_allow_html=True)
            day_it = [e for e in upcoming_list if e['listing_date'] == d]
            if not day_it: st.markdown('<div style="background:#161B22;border:1px dashed #30363D;border-radius:4px;padding:15px;text-align:center;color:#484F58;font-size:9px;margin-top:15px;">EMPTY</div>', unsafe_allow_html=True)
            for item in day_it:
                is_r = any(p['symbol'] == item['ticker'] for p in portfolio)
                st.markdown(f'<div class="cal-item"><div class="badge badge-standby">STANDBY</div><div style="font-size:11px;font-weight:bold;color:white;">{item["name"]}</div></div>', unsafe_allow_html=True)
                if is_r:
                    st.markdown('<div class="reserved-btn">', unsafe_allow_html=True)
                    if st.button("✓ RESERVED", key=f"cal_v_{item['ticker']}"):
                        st.session_state[f"confirm_cancel_{item['ticker']}"] = True
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    if st.session_state.get(f"confirm_cancel_{item['ticker']}", False):
                        if st.button("예약을 취소하시겠습니까?", key=f"alert_can_{item['ticker']}"):
                            portfolio = [p for p in portfolio if p['symbol'] != item['ticker']]; save_json('data/user_portfolio.json', portfolio)
                            del st.session_state[f"confirm_cancel_{item['ticker']}"]
                            st.rerun()
                else:
                    st.markdown('<div class="pre-check-btn">', unsafe_allow_html=True)
                    if st.button("[PRE-CHECK]", key=f"cal_p_{item['ticker']}"):
                        portfolio.append({"symbol": item['ticker'], "name": item['name'], "purchase_price": 0, "status": "대기", "listing_date": item['listing_date']})
                        save_json('data/user_portfolio.json', portfolio); st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

with tabs[2]:
    st.markdown('<div class="vision-banner"><strong>[BETA Vision]</strong> 원칙 이탈(-10%) 즉시 <strong>\'Full-Auto 자동 매도\'</strong>를 집행하여 인간의 망설임이 야기하는 비극을 차단합니다.</div>', unsafe_allow_html=True)
    
    processed = []
    for p in portfolio:
        bp = p.get('purchase_price', 10000)
        if bp == 0: bp = 10000
        cv = bp * (0.965 if p['status'] == '추적 중' else 0.88 if p['status'] == '위험' else 1.0)
        p['loss'] = calculate_loss_rate(cv, bp); p['cur'] = cv
        processed.append(p)
    
    # Risk Priority Ordering: Lowest loss first (ASC)
    active = [p for p in processed if p['status'] != '대기']
    active.sort(key=lambda x: x['loss'])
    
    st.subheader("🔥 실시간 감시 리스트 (Risk Priority)")
    if not active: st.info("활성화된 감시 프로토콜이 없습니다.")
    for item in active:
        l = item['loss']
        m_card = f'<div class="etf-card"><div style="display:flex;justify-content:space-between;align-items:start;">'
        m_card += f'<div><div class="badge {get_status_class(item["status"])}">{item["status"]}</div>'
        m_card += f'<div style="font-size:16px;font-weight:bold;color:white;">{item["name"]} <span style="font-size:10px;color:#484F58;">({item["symbol"]})</span></div></div>'
        m_card += f'<div style="text-align:right;"><div style="font-size:24px;font-weight:900;color:{"#FF3131" if l <= -8 else "#39FF14"};">{l:+.1f}%</div><div style="font-size:12px;font-weight:bold;color:white;">{int(item["cur"]):,} KRW</div></div></div>'
        m_card += f'{render_gauge(l)}</div>'
        st.markdown(m_card, unsafe_allow_html=True)
        if st.button("✓ UNTRACK", key=f"ctrl_un_{item['symbol']}"):
            portfolio = [p for p in portfolio if p['symbol'] != item['symbol']]; save_json('data/user_portfolio.json', portfolio); st.rerun()

    # Standby Protocol (Isolated & Sorted by Date)
    standby = [p for p in processed if p['status'] == '대기']
    standby.sort(key=lambda x: x.get('listing_date', ''))
    st.divider()
    st.subheader("⏳ Standby Protocol (상장 예정)")
    for item in standby:
        s_card = f'<div class="etf-card" style="padding:12px;"><div style="display:flex;justify-content:space-between;align-items:center;"><div><span class="badge badge-standby">STANDBY</span><span style="font-size:14px;font-weight:bold;color:white;margin-left:8px;">{item["name"]}</span></div><div style="color:#FFFF33;font-size:10px;font-weight:bold;">📅 {item.get("listing_date")}</div></div></div>'
        st.markdown(s_card, unsafe_allow_html=True)
        if st.button("CANCEL RESERVATION", key=f"ctrl_can_{item['symbol']}"):
             portfolio = [p for p in portfolio if p['symbol'] != item['symbol']]; save_json('data/user_portfolio.json', portfolio); st.rerun()

st.markdown("<div style='color:#484F58;font-size:10px;text-align:center;margin-top:40px;'>Hyper ETF Guardian v3.0 [Blueprint Master Build]<br>Intelligence: Gemini 2.0 Flash / SnF Ecosystem Restoration</div>", unsafe_allow_html=True)
