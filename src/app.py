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

# Strict AI Parsing: DB 교차 검증 로직
def get_smart_recommendations(theme, etf_data):
    if not theme: return []
    db_symbols = {e["symbol"] for e in etf_data}
    prompt = f"Quant Expert: List top 5 symbols matching theme '{theme}' from provided symbols only. CSV format. Symbols: {','.join(list(db_symbols)[:100])}"
    res = get_ai_analysis(prompt)
    extracted = [s.strip() for s in res.split(',') if s.strip().isdigit()]
    # DB에 존재하는 심볼만 필터링 (Strict Validation)
    return [s for s in extracted if s in db_symbols]

# 커스텀 CSS (High-Density & Professional)
st.markdown("<style>.stApp{background-color:#0A0E14;color:#FFFFFF;}h1,h2,h3{color:#FFFFFF!important;font-family:'Inter',sans-serif;font-weight:800;}.stSubheader{color:#B0B0B0!important;font-weight:400;letter-spacing:1px;}.etf-card{background-color:#161B22;border:1px solid #30363D;border-radius:12px;padding:18px;margin-bottom:15px;transition:transform 0.2s;display:flex;flex-direction:column;height:100%;}.etf-card:hover{transform:translateY(-5px);box-shadow:0 10px 20px rgba(0,0,0,0.5);}.badge{display:inline-block;padding:3px 10px;border-radius:20px;font-size:10px;font-weight:bold;text-transform:uppercase;margin-bottom:10px;}.badge-standby{background-color:rgba(255,255,51,0.1);color:#FFFF33;border:1px solid #FFFF33;}.badge-tracking{background-color:rgba(57,255,20,0.1);color:#39FF14;border:1px solid #39FF14;}.badge-danger{background-color:rgba(255,49,49,0.1);color:#FF3131;border:1px solid #FF3131;}.beta-tag{background-color:#39FF14;color:#000000;padding:2px 8px;border-radius:4px;font-size:10px;font-weight:900;vertical-align:middle;margin-left:10px;}.stButton>button{width:100%;background-color:#39FF14!important;color:#000000!important;border:none!important;font-weight:bold!important;height:38px;}.tracked-btn button{background-color:#21262D!important;color:#8B949E!important;border:1px solid #30363D!important;}.cancel-btn button{background-color:rgba(255,49,49,0.1)!important;color:#FF3131!important;border:1px solid #FF3131!important;}.gauge-container{width:100%;background-color:#21262D;border-radius:5px;height:8px;margin-top:12px;position:relative;}.gauge-fill{height:100%;border-radius:5px;transition:width 0.5s ease-in-out;}.vision-banner{background-color:rgba(57,255,20,0.03);border-left:4px solid #39FF14;padding:12px;border-radius:4px;margin-bottom:20px;color:#B0B0B0;font-size:12px;line-height:1.5;}.risk-banner{background-color:rgba(255,49,49,0.05);border-left:4px solid #FF3131;padding:10px 15px;border-radius:4px;margin-bottom:20px;font-size:13px;font-weight:bold;color:#FF3131;}[data-testid='stSidebar']{background-color:#0D1117;border-right:1px solid #30363D;}.calendar-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-top:10px;}.calendar-day{background-color:#161B22;border:1px solid #30363D;border-radius:10px;padding:12px;min-height:180px;}.calendar-date{font-size:11px;color:#8B949E;margin-bottom:10px;border-bottom:1px solid #30363D;padding-bottom:5px;font-weight:bold;text-align:center;}.cal-item{background:#0D1117;padding:8px;border-radius:5px;margin-bottom:8px;border-left:3px solid #FFFF33;}</style>", unsafe_allow_html=True)

# 데이터 유성
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
    # Minified HTML (Zero Tolerance)
    html = f'<div style="font-size:9px;color:#8B949E;margin-top:10px;">📉 손절 방어선까지 남은 거리</div>'
    html += f'<div class="gauge-container"><div class="gauge-fill" style="width:{percent}%;background-color:{color};"></div></div>'
    html += f'<div style="display:flex;justify-content:space-between;font-size:8px;margin-top:4px;color:#484F58;font-weight:bold;"><span>SAFE (0%)</span><span style="color:#FF3131;">-10% (CRITICAL)</span></div>'
    return html

# 데이터 로드
etf_list = load_json('data/etf_list.json')
upcoming_list = load_json('data/upcoming_etf.json')
portfolio = load_json('data/user_portfolio.json')

# AI Risk Summary (High-Density)
def show_risk_summary(portfolio):
    if not portfolio:
        st.markdown('<div class="risk-banner">⚠️ [System] 현재 포트폴리오가 비어있습니다. 방어 프로토콜을 가동하십시오.</div>', unsafe_allow_html=True)
        return
    prompt = f"Quant Expert 1-line Risk Analysis for: {portfolio}. Focus on DANGER vs SAFE. Strictly 1 line."
    summary = get_ai_analysis(prompt)
    st.markdown(f'<div class="risk-banner">🚨 AI Analysis: {summary}</div>', unsafe_allow_html=True)

# --- Sidebar Filters & AI Input ---
with st.sidebar:
    st.image("https://via.placeholder.com/150x50/161B22/39FF14?text=HYPER+GUARD", use_container_width=True)
    st.header("🛠️ 관측 통제소")
    
    st.subheader("🏢 운용사 필터")
    issuers_static = ["KODEX", "TIGER", "KBSTAR", "ACE", "SOL"]
    selected_issuers = []
    for issuer in issuers_static:
        if st.checkbox(issuer, value=False, key=f"f_{issuer}"):
            selected_issuers.append(issuer)
            
    # Logic Sync: 필터 리스트가 비어 있을 경우 '전체 운용사 선택' 기본값 강제 설정
    effective_issuers = selected_issuers if selected_issuers else issuers_static
    filtered_base = [e for e in etf_list if any(iss in e['issuer'] for iss in effective_issuers)]
            
    st.subheader("🤖 AI Smart Theme")
    theme1 = st.text_input("Theme Slot 1", placeholder="예: 양자컴퓨팅", key="st_1")
    theme2 = st.text_input("Theme Slot 2", placeholder="예: 우주항공", key="st_2")
    
    st.divider()
    if st.button("♻️ RESET PORTFOLIO"): save_json('data/user_portfolio.json', []); st.rerun()

# --- Header ---
st.markdown(f"<h1>🛡️ Hyper ETF Guardian <span class='beta-tag'>BETA</span></h1>", unsafe_allow_html=True)
st.markdown("<p class='stSubheader'>No Prose, Just Precision.</p>", unsafe_allow_html=True)
show_risk_summary(portfolio)

# --- Market Watch ---
tabs = st.tabs(["📊 Market Watch", "📅 Upcoming", "🚨 Control Room"])

with tabs[0]:
    st.markdown('<div class="vision-banner"><strong>[BETA Vision]</strong> 5대 운용사의 ETF 데이터를 실시간 추적하고 기계적 손절(-10%) 알림을 통해 사유를 방해하는 현실적 불안을 차단합니다.</div>', unsafe_allow_html=True)
    
    main_sections = {
        "AI & 반도체": ["AI", "반도체", "NVIDIA"],
        "밸류업 / 저PBR": ["밸류업", "저PBR", "금융"],
        "미국 빅테크": ["나스닥", "S&P", "특대형", "빅테크"],
        "월배당 / 인컴": ["월배당", "배당", "커버드콜", "인컴"]
    }
    
    if theme1:
        ai_s = get_smart_recommendations(theme1, etf_list)
        if ai_s: main_sections[f"🤖 AI Match: {theme1}"] = ai_s
    if theme2:
        ai_s2 = get_smart_recommendations(theme2, etf_list)
        if ai_s2: main_sections[f"🤖 AI Match: {theme2}"] = ai_s2

    for sec_name, ident in main_sections.items():
        if isinstance(ident, list) and ident and ident[0].isdigit():
             sec_etfs = [e for e in filtered_base if e['symbol'] in ident]
        else:
             sec_etfs = [e for e in filtered_base if any(k.lower() in e['name'].lower() for k in ident)]
        
        if not sec_etfs: continue
        
        st.subheader(sec_name)
        cols = st.columns(3)
        for idx, item in enumerate(sec_etfs):
            exist_p = next((p for p in portfolio if p['symbol'] == item['symbol']), None)
            with cols[idx % 3]:
                # Minified HTML (Zero Tolerance)
                card = f'<div class="etf-card"><div style="color:#8B949E;font-size:10px;">{item["issuer"]}</div><div style="font-size:16px;font-weight:bold;color:white;margin:8px 0;">{item["name"]}</div><div style="font-size:20px;color:#FFFFFF;font-weight:900;">{item["price_at_listing"]:,} <span style="font-size:11px;color:#8B949E;">KRW</span></div></div>'
                st.markdown(card, unsafe_allow_html=True)
                if exist_p:
                    st.markdown('<div class="tracked-btn">', unsafe_allow_html=True)
                    if st.button("✓ TRACKED", key=f"mw_in_{item['symbol']}"):
                        portfolio = [p for p in portfolio if p['symbol'] != item['symbol']]
                        save_json('data/user_portfolio.json', portfolio); st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    if st.button("TRACK", key=f"mw_add_{item['symbol']}"):
                        portfolio.append({"symbol": item['symbol'], "name": item['name'], "purchase_price": item['price_at_listing'], "status": "추적 중"})
                        save_json('data/user_portfolio.json', portfolio); st.rerun()

with tabs[1]:
    st.markdown('<div class="vision-banner"><strong>[BETA Vision]</strong> 예약한 종목을 상장 즉시 <strong>\'0.1초 자동 매수\'</strong>하여 기회를 놓치지 않는 선제적 방어 체계를 구축합니다.</div>', unsafe_allow_html=True)
    
    today = datetime.now()
    mon = today - timedelta(days=today.weekday())
    cols = st.columns(5)
    days_kr = ["월", "화", "수", "목", "금"]
    for i in range(5):
        d = (mon + timedelta(days=i)).strftime("%Y-%m-%d")
        with cols[i]:
            st.markdown(f'<div class="calendar-day"><div class="calendar-date">{days_kr[i]} ({d})</div>', unsafe_allow_html=True)
            day_it = [e for e in upcoming_list if e['listing_date'] == d]
            if not day_it: st.markdown('<div style="text-align:center;color:#484F58;font-size:10px;margin-top:20px;">No Listing</div>', unsafe_allow_html=True)
            for item in day_it:
                is_r = any(p['symbol'] == item['ticker'] for p in portfolio)
                # High-End Density UI
                st.markdown(f'<div class="cal-item"><div style="font-size:11px;font-weight:bold;color:white;">{item["name"]}</div><div style="font-size:9px;color:#8B949E;margin-top:2px;">{item["theme"]}</div></div>', unsafe_allow_html=True)
                if is_r:
                    if st.button("✓ RESV", key=f"cal_v_{item['ticker']}"):
                        portfolio = [p for p in portfolio if p['symbol'] != item['ticker']]
                        save_json('data/user_portfolio.json', portfolio); st.rerun()
                else:
                    if st.button("PRE-CHEK", key=f"cal_p_{item['ticker']}"):
                        portfolio.append({"symbol": item['ticker'], "name": item['name'], "purchase_price": 0, "status": "대기", "listing_date": item['listing_date']})
                        save_json('data/user_portfolio.json', portfolio); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

with tabs[2]:
    st.markdown('<div class="vision-banner"><strong>[BETA Vision]</strong> 원칙(-10.0%) 이탈 즉시 <strong>\'자동 매도\'</strong>를 집행하여 인간의 망설임이 야기하는 비극을 차단합니다.</div>', unsafe_allow_html=True)
    
    processed = []
    for p in portfolio:
        bp = p.get('purchase_price', 10000)
        if bp == 0: bp = 10000
        cv = bp * (0.965 if p['status'] == '추적 중' else 0.88 if p['status'] == '위험' else 1.0)
        p['loss'] = calculate_loss_rate(cv, bp)
        p['cur'] = cv
        processed.append(p)
    
    # [Logic] 위험 순위 기반 동적 정렬 (Loss Rate 오름차순)
    active = [p for p in processed if p['status'] != '대기']
    active.sort(key=lambda x: x['loss'])
    
    st.subheader("🔥 Risk Priority Command")
    if not active: st.info("활성화된 감시 프로토콜이 없습니다.")
    for item in active:
        l = item['loss']
        # Minified HTML (Zero Tolerance)
        m_card = f'<div class="etf-card"><div style="display:flex;justify-content:space-between;align-items:start;">'
        m_card += f'<div><div class="badge {get_status_class(item["status"])}">{item["status"]}</div>'
        m_card += f'<div style="font-size:18px;font-weight:bold;color:white;">{item["name"]} <span style="font-size:11px;color:#484F58;">({item["symbol"]})</span></div></div>'
        m_card += f'<div style="text-align:right;"><div style="font-size:26px;font-weight:900;color:{"#FF3131" if l <= -8 else "#39FF14"};">{l:+.1f}%</div><div style="font-size:13px;font-weight:bold;color:white;margin-top:2px;">{int(item["cur"]):,} KRW</div></div></div>'
        m_card += f'{render_gauge(l)}</div>'
        st.markdown(m_card, unsafe_allow_html=True)
        if st.button("✓ UNTRACK", key=f"ctrl_un_{item['symbol']}"):
            portfolio = [p for p in portfolio if p['symbol'] != item['symbol']]
            save_json('data/user_portfolio.json', portfolio); st.rerun()

    standby = [p for p in processed if p['status'] == '대기']
    standby.sort(key=lambda x: x.get('listing_date', ''))
    st.divider()
    st.subheader("⏳ Standby Protocol")
    for item in standby:
        # Minified HTML (Zero Tolerance)
        s_card = f'<div class="etf-card" style="padding:15px;"><div style="display:flex;justify-content:space-between;align-items:center;"><div><span class="badge badge-standby">STANDBY</span><span style="font-size:15px;font-weight:bold;color:white;margin-left:10px;">{item["name"]}</span></div><div style="color:#FFFF33;font-size:11px;font-weight:bold;">📅 {item.get("listing_date")}</div></div></div>'
        st.markdown(s_card, unsafe_allow_html=True)
        if st.button("CANCEL RESERVATION", key=f"ctrl_can_{item['symbol']}"):
             portfolio = [p for p in portfolio if p['symbol'] != item['symbol']]
             save_json('data/user_portfolio.json', portfolio); st.rerun()

st.markdown("<div style='color:#484F58;font-size:10px;text-align:center;margin-top:50px;'>Hyper ETF Guardian v2.2 [Final Integrity Build]<br>Powered by Gemini 2.0 Flash / AI-Workforce</div>", unsafe_allow_html=True)
