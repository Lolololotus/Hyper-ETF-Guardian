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
            return "[Intelligence Offline] 방어적 관망 및 원칙(-10.0%) 고수 권고."
        return response.text
    except Exception:
        return "[Intelligence Fallback] 고변동성 감지. 자산 보존 및 자동 손절 프로토콜 집중 필요."

def get_smart_recommendations(theme, etf_data):
    if not theme: return []
    db_symbols = {e["symbol"] for e in etf_data}
    prompt = f"Quant Expert: List top 3 symbols matching theme '{theme}' from provided symbols only. CSV format. Symbols: {','.join(list(db_symbols)[:40])}"
    res = get_ai_analysis(prompt)
    extracted = [s.strip() for s in res.split(',') if s.strip().isdigit()]
    return [s for s in extracted if s in db_symbols][:3]

# --- Custom CSS (Static & High-Contrast) ---
st.markdown("""<style>
.stApp{background-color:#0A0E14;color:#FFFFFF;}
h1,h2,h3{color:#FFFFFF!important;font-family:'Inter',sans-serif;font-weight:800;margin-bottom:8px!important;}
.stSubheader{color:#B0B0B0!important;font-weight:400;font-size:13px!important;}
.etf-card{background-color:#161B22;border:1px solid #30363D;border-radius:8px;padding:12px;margin-bottom:10px;display:flex;flex-direction:column;min-height:140px;}
.etf-card:hover{border-color:#39FF14;}
.badge{display:inline-block;padding:2px 6px;border-radius:3px;font-size:9px;font-weight:900;margin-bottom:6px;}
.badge-standby{background:rgba(255,255,51,0.1);color:#FFFF33;border:1px solid #FFFF33;}
.badge-tracking{background:rgba(57,255,20,0.1);color:#39FF14;border:1px solid #39FF14;}
.badge-danger{background:rgba(255,49,49,0.1);color:#FF3131;border:1px solid #FF3131;}
.stButton>button{width:100%!important;min-width:110px!important;height:34px!important;font-size:11px!important;font-weight:900!important;border-radius:4px!important;background-color:#21262D!important;color:#FFFFFF!important;border:1px solid #30363D!important;}
.stButton>button:hover{border-color:#39FF14!important;color:#39FF14!important;}
.pre-check-btn button{background-color:#39FF14!important;color:#000000!important;border:none!important;}
.reserved-btn button{background-color:#161B22!important;color:#FFFF33!important;border:1px solid #FFFF33!important;}
.tracked-btn button{background-color:#161B22!important;color:#8B949E!important;border:1px solid #30363D!important;}
.gauge-container{width:100%;background:#21262D;border-radius:2px;height:5px;margin-top:8px;}
.gauge-fill{height:100%;border-radius:2px;}
.vision-banner{background:rgba(57,255,20,0.02);border-left:3px solid #39FF14;padding:10px;border-radius:2px;margin-bottom:15px;color:#8B949E;font-size:11px;}
.risk-box{background:rgba(255,49,49,0.05);border:1px solid #FF3131;padding:10px;border-radius:4px;margin-bottom:15px;font-size:12px;font-weight:bold;color:#FF3131;}
.metric-tile{background:#161B22;border:1px solid #30363D;border-radius:6px;padding:10px;text-align:center;}
.calendar-day{background:#0D1117;border:1px solid #21262D;border-radius:6px;padding:8px;min-height:140px;}
.calendar-date{font-size:10px;color:#484F58;margin-bottom:6px;border-bottom:1px solid #21262D;font-weight:900;text-align:center;}
.cal-item{background:#161B22;padding:5px;border-radius:3px;margin-bottom:5px;border-left:2px solid #FFFF33;}
</style>""", unsafe_allow_html=True)

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
    # Extreme Minified String (No Spaces)
    return f'<div style="font-size:9px;color:#8B949E;margin-top:6px;">방어선 잔여:<b>{rem:+.1f}%</b></div><div class="gauge-container"><div class="gauge-fill" style="width:{percent}%;background:{color};"></div></div>'

# 데이터 로드
etf_list = load_json('data/etf_list.json')
upcoming_list = load_json('data/upcoming_etf.json')
portfolio = load_json('data/user_portfolio.json')

# --- Header ---
st.markdown("<h2 style='margin:0;'>📊 Hyper ETF Guardian</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#8B949E;font-size:13px;margin:-5px 0 15px 0;'>No Prose, Just Precision.</p>", unsafe_allow_html=True)

# AI Risk Box (Fallback)
danger_items = [p for p in portfolio if p.get('status') == '위험']
risk_prompt = f"Portfolio has {len(danger_items)} danger items. Market insight 1 line."
ai_risk_report = get_ai_analysis(risk_prompt)
st.markdown(f'<div class="risk-box">[AI Quant Analysis] {ai_risk_report}</div>', unsafe_allow_html=True)

# 4 Metrics Tiles
processed_metrics = []
for p in portfolio:
    bp = p.get('purchase_price', 10000)
    if bp <= 0: bp = 10000
    cv = bp * (0.965 if p['status'] == '추적 중' else 0.88 if p['status'] == '위험' else 1.0)
    processed_metrics.append({'loss': calculate_loss_rate(cv, bp)})
avg_ret = sum(x['loss'] for x in processed_metrics) / len(processed_metrics) if processed_metrics else 0

m_cols = st.columns(4)
tile_style = "background:#161B22;border:1px solid #30363D;border-radius:6px;padding:10px;text-align:center;"
m_cols[0].markdown(f'<div style="{tile_style}"><div style="color:#8B949E;font-size:9px;">총 감시 종목</div><div style="font-size:17px;font-weight:900;color:#39FF14;">{len(portfolio)} UNIT</div></div>', unsafe_allow_html=True)
m_cols[1].markdown(f'<div style="{tile_style}"><div style="color:#8B949E;font-size:9px;">평균 방어 수익률</div><div style="font-size:17px;font-weight:900;color:{"#FF3131" if avg_ret <0 else "#39FF14"};">{avg_ret:+.1f}%</div></div>', unsafe_allow_html=True)
m_cols[2].markdown(f'<div style="{tile_style}"><div style="color:#8B949E;font-size:9px;">위험(DANGER) 수</div><div style="font-size:17px;font-weight:900;color:{"#FF3131" if danger_items else "#39FF14"};">{len(danger_items)}</div></div>', unsafe_allow_html=True)
m_cols[3].markdown(f'<div style="{tile_style}"><div style="color:#8B949E;font-size:9px;">상장 예정(7D)</div><div style="font-size:17px;font-weight:900;color:#FFFF33;">{len(upcoming_list)}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.image("https://via.placeholder.com/150x50/161B22/39FF14?text=HYPER+GUARD", use_container_width=True)
    st.header("🛠️ 관측 통제소")
    issuers_static = ["KODEX", "TIGER", "KBSTAR", "ACE", "SOL"]
    selected_issuers = []
    for issuer in issuers_static:
        if st.checkbox(issuer, value=False, key=f"side_{issuer}"): selected_issuers.append(issuer)
    effective_issuers = selected_issuers if selected_issuers else issuers_static
    filtered_base = [e for e in etf_list if any(iss in e['issuer'] for iss in effective_issuers)]
    if not filtered_base: filtered_base = etf_list[:12]
    
    st.header("🤖 AI Smart Theme")
    theme_input = st.text_input("Theme Focus", placeholder="예: 양자컴퓨팅", key="st_theme_in")
    if st.button("♻️ RESET PORTFOLIO"): save_json('data/user_portfolio.json', []); st.rerun()

# --- Tabs ---
tabs = st.tabs(["📊 Market Watch", "📅 Upcoming", "🚨 Control Room"])

with tabs[0]:
    st.markdown('<div class="vision-banner"><strong>[BETA Vision]</strong> ETF 데이터를 실시간 추적하고 <strong>\'0.1초 자동 매수 시스템\'</strong>을 선점하십시오.</div>', unsafe_allow_html=True)
    
    # 4 Strategy Themes
    main_cats = {
        "AI & 반도체": ["AI", "반도체", "엔비디아", "NVIDIA"],
        "밸류업 / 저PBR": ["밸류업", "저PBR", "금융", "은행"],
        "미국 빅테크": ["미국", "빅테크", "나스닥", "S&P"],
        "월배당 / 인컴": ["월배당", "배당", "인컴", "커버드콜"]
    }
    
    if theme_input:
        st.subheader(f"🤖 AI Match: {theme_input}")
        recs = get_smart_recommendations(theme_input, etf_list)
        if recs:
            ai_cols = st.columns(3)
            for i, sym in enumerate(recs):
                item = next((e for e in etf_list if e['symbol'] == sym), None)
                if item:
                    cur_p = next((p for p in portfolio if p['symbol'] == item['symbol']), None)
                    with ai_cols[i % 3]:
                        st.markdown(f'<div class="etf-card"><div style="color:#8B949E;font-size:9px;">{item["issuer"]} | AI</div><div style="font-size:14px;font-weight:bold;color:#39FF14;margin:6px 0;">{item["name"]}</div><div style="font-size:17px;font-weight:900;">{item["price_at_listing"]:,} KRW</div></div>', unsafe_allow_html=True)
                        if cur_p:
                            st.markdown('<div class="tracked-btn">', unsafe_allow_html=True)
                            if st.button("✓ TRACKED", key=f"un_{item['symbol']}_AI_MATCH"):
                                portfolio = [p for p in portfolio if p['symbol'] != item['symbol']]; save_json('data/user_portfolio.json', portfolio); st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="pre-check-btn">', unsafe_allow_html=True)
                            if st.button("TRACK", key=f"add_{item['symbol']}_AI_MATCH"):
                                portfolio.append({"symbol":item['symbol'],"name":item['name'],"purchase_price":item['price_at_listing'],"status":"추적 중"})
                                save_json('data/user_portfolio.json', portfolio); st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)
        st.divider()

    for cat_name, keywords in main_cats.items():
        cat_items = [e for e in filtered_base if any(k.lower() in e['name'].lower() for k in keywords)]
        if not cat_items: cat_items = etf_list[:3]
        st.subheader(cat_name)
        cols = st.columns(3)
        for i, item in enumerate(cat_items[:3]):
            cur_p = next((p for p in portfolio if p['symbol'] == item['symbol']), None)
            with cols[i % 3]:
                st.markdown(f'<div class="etf-card"><div style="color:#8B949E;font-size:9px;">{item["issuer"]}</div><div style="font-size:14px;font-weight:bold;color:white;margin:5px 0;">{item["name"]}</div><div style="font-size:17px;font-weight:900;">{item["price_at_listing"]:,} KRW</div></div>', unsafe_allow_html=True)
                if cur_p:
                    st.markdown('<div class="tracked-btn">', unsafe_allow_html=True)
                    if st.button("✓ TRACKED", key=f"un_{item['symbol']}_{cat_name}_MW"):
                        portfolio = [p for p in portfolio if p['symbol'] != item['symbol']]; save_json('data/user_portfolio.json', portfolio); st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="pre-check-btn">', unsafe_allow_html=True)
                    if st.button("TRACK", key=f"add_{item['symbol']}_{cat_name}_MW"):
                        portfolio.append({"symbol":item['symbol'],"name":item['name'],"purchase_price":item['price_at_listing'],"status":"추적 중"})
                        save_json('data/user_portfolio.json', portfolio); st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

with tabs[1]:
    st.markdown('<div class="vision-banner"><strong>[BETA Vision]</strong> 상장 즉시 자동 체결 시스템을 통해 미래 자산을 선점하십시오.</div>', unsafe_allow_html=True)
    mon = datetime.now() - timedelta(days=datetime.now().weekday())
    cols = st.columns(5)
    for i, day in enumerate(["월", "화", "수", "목", "금"]):
        d = (mon + timedelta(days=i)).strftime("%Y-%m-%d")
        with cols[i]:
            st.markdown(f'<div class="calendar-day"><div class="calendar-date">{day} ({d})</div>', unsafe_allow_html=True)
            day_it = [e for e in upcoming_list if e['listing_date'] == d]
            if not day_it: st.markdown('<div style="background:#161B22;border-radius:4px;padding:15px;text-align:center;color:#484F58;font-size:9px;margin-top:10px;">EMPTY</div>', unsafe_allow_html=True)
            for item in day_it:
                is_r = any(p['symbol'] == item['ticker'] for p in portfolio)
                st.markdown(f'<div class="cal-item"><div class="badge badge-standby">STANDBY</div><div style="font-size:10px;font-weight:bold;color:white;">{item["name"]}</div></div>', unsafe_allow_html=True)
                if is_r:
                    st.markdown('<div class="reserved-btn">', unsafe_allow_html=True)
                    if st.button("✓ RESERVED", key=f"un_{item['ticker']}_UP"):
                        portfolio = [p for p in portfolio if p['symbol'] != item['ticker']]; save_json('data/user_portfolio.json', portfolio); st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="pre-check-btn">', unsafe_allow_html=True)
                    if st.button("[PRE-CHECK]", key=f"add_{item['ticker']}_UP"):
                        portfolio.append({"symbol":item['ticker'],"name":item['name'],"purchase_price":0,"status":"대기","listing_date":item['listing_date']})
                        save_json('data/user_portfolio.json', portfolio); st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

with tabs[2]:
    st.markdown('<div class="vision-banner"><strong>[BETA Vision]</strong> 원칙 이탈(-10%) 즉시 <strong>\'Full-Auto 자동 매도\'</strong>를 집행하여 자산을 보호합니다.</div>', unsafe_allow_html=True)
    processed = []
    for p in portfolio:
        bp = p.get('purchase_price', 10000)
        if bp <= 0: bp = 10000
        cv = bp * (0.965 if p['status'] == '추적 중' else 0.88 if p['status'] == '위험' else 1.0)
        p['loss'] = calculate_loss_rate(cv, bp); p['cur'] = cv
        processed.append(p)
    
    active = [p for p in processed if p['status'] != '대기']
    active.sort(key=lambda x: x['loss'])
    st.subheader("🔥 Risk Priority Control")
    if not active: st.info("활성화된 감시 프로토콜이 없습니다.")
    for item in active:
        l = item['loss']
        st.markdown(f'<div class="etf-card"><div style="display:flex;justify-content:space-between;align-items:start;"><div><div class="badge {get_status_class(item["status"])}">{item["status"]}</div><div style="font-size:15px;font-weight:bold;color:white;">{item["name"]}</div></div><div style="text-align:right;"><div style="font-size:22px;font-weight:900;color:{"#FF3131" if l <= -8 else "#39FF14"};">{l:+.1f}%</div><div style="font-size:11px;color:#8B949E;">{int(item["cur"]):,} KRW</div></div></div>{render_gauge(l)}</div>', unsafe_allow_html=True)
        if st.button("UNTRACK", key=f"un_{item['symbol']}_CR"):
            portfolio = [p for p in portfolio if p['symbol'] != item['symbol']]; save_json('data/user_portfolio.json', portfolio); st.rerun()

    standby = [p for p in processed if p['status'] == '대기']
    standby.sort(key=lambda x: x.get('listing_date', ''))
    if standby:
        st.divider()
        st.subheader("⏳ Standby Protocol")
        for item in standby:
            st.markdown(f'<div class="etf-card" style="min-height:auto;"><div style="display:flex;justify-content:space-between;align-items:center;"><div><span class="badge badge-standby">STANDBY</span><span style="font-size:13px;font-weight:bold;color:white;margin-left:8px;">{item["name"]}</span></div><div style="color:#FFFF33;font-size:10px;font-weight:bold;">📅 {item.get("listing_date")}</div></div></div>', unsafe_allow_html=True)
            if st.button("CANCEL RESERVATION", key=f"un_{item['symbol']}_CR_ST"):
                portfolio = [p for p in portfolio if p['symbol'] != item['symbol']]; save_json('data/user_portfolio.json', portfolio); st.rerun()

st.markdown("<div style='color:#484F58;font-size:10px;text-align:center;margin-top:40px;'>Hyper ETF Guardian v3.4 [Zero-Noise Build]<br>Intelligence: Gemini 2.0 Flash / SnF Ecosystem Restoration</div>", unsafe_allow_html=True)
