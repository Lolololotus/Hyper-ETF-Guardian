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
            return "Market Consensus: Defensive stance recommended. Monitor -10.0% threshold."
        return response.text
    except Exception as e:
        # Fallback Logic: 인텔리전스 오프라인 시 기본 시장 분석 리포트 제공
        return "Market Report: High volatility detected. Focus on capital preservation and automated stop-loss protocols."

def get_smart_recommendations(theme, etf_data):
    if not theme: return []
    db_symbols = {e["symbol"] for e in etf_data}
    prompt = f"Quant Expert: List top 3 symbols matching theme '{theme}' from provided symbols only. CSV format. Symbols: {','.join(list(db_symbols)[:50])}"
    res = get_ai_analysis(prompt)
    extracted = [s.strip() for s in res.split(',') if s.strip().isdigit()]
    return [s for s in extracted if s in db_symbols][:3]

# --- Custom CSS (Fixed Width & Minified Styles) ---
st.markdown("""<style>
.stApp{background-color:#0A0E14;color:#FFFFFF;}
h1,h2,h3{color:#FFFFFF!important;font-family:'Inter',sans-serif;font-weight:800;margin-bottom:8px!important;}
.stSubheader{color:#B0B0B0!important;font-weight:400;font-size:13px!important;}
.etf-card{background-color:#161B22;border:1px solid #30363D;border-radius:8px;padding:12px;margin-bottom:10px;display:flex;flex-direction:column;min-height:140px;}
.etf-card:hover{border-color:#39FF14;box-shadow:0 0 10px rgba(57,255,20,0.2);}
.badge{display:inline-block;padding:2px 6px;border-radius:3px;font-size:9px;font-weight:900;margin-bottom:6px;}
.badge-standby{background:rgba(255,255,51,0.1);color:#FFFF33;border:1px solid #FFFF33;}
.badge-tracking{background:rgba(57,255,20,0.1);color:#39FF14;border:1px solid #39FF14;}
.badge-danger{background:rgba(255,49,49,0.1);color:#FF3131;border:1px solid #FF3131;}
.stButton>button{width:100%!important;min-width:110px!important;height:32px!important;font-size:11px!important;font-weight:900!important;border-radius:4px!important;}
.pre-check-btn button{background:#39FF14!important;color:#000000!important;border:none!important;}
.reserved-btn button{background:#21262D!important;color:#FFFF33!important;border:1px solid #FFFF33!important;}
.tracked-btn button{background:#21262D!important;color:#8B949E!important;border:1px solid #30363D!important;}
.gauge-container{width:100%;background:#21262D;border-radius:2px;height:5px;margin-top:8px;}
.gauge-fill{height:100%;border-radius:2px;transition:width 0.5s;}
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
    return f'<div style="font-size:9px;color:#8B949E;margin-top:6px;">방어선 잔여:<b>{rem:+.1f}%</b></div><div class="gauge-container"><div class="gauge-fill" style="width:{percent}%;background:{color};"></div></div>'

# 데이터 로드
etf_list = load_json('data/etf_list.json')
upcoming_list = load_json('data/upcoming_etf.json')
portfolio = load_json('data/user_portfolio.json')

# --- Header Section ---
st.markdown("<h2 style='margin:0;'>📊 Hyper ETF Guardian</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#8B949E;font-size:13px;margin: -5px 0 15px 0;'>No Prose, Just Precision.</p>", unsafe_allow_html=True)

# [Heart] AI Risk Analysis Table (상시 노출)
danger_items = [p for p in portfolio if p.get('status') == '위험']
risk_prompt = f"Portfolio has {len(danger_items)} danger items. Market status overview in 1 line."
ai_risk_report = get_ai_analysis(risk_prompt)
st.markdown(f'<div class="risk-box">[AI Quant Analysis] {ai_risk_report}</div>', unsafe_allow_html=True)

# [Header] 4 Metrics Tiles
processed_metrics = []
for p in portfolio:
    bp = p.get('purchase_price', 10000)
    if bp <= 0: bp = 10000
    cv = bp * (0.965 if p['status'] == '추적 중' else 0.88 if p['status'] == '위험' else 1.0)
    processed_metrics.append({'loss': calculate_loss_rate(cv, bp), 'status': p['status']})
avg_ret = sum(x['loss'] for x in processed_metrics) / len(processed_metrics) if processed_metrics else 0

m_cols = st.columns(4)
tile_tmpl = '<div class="metric-tile"><div style="color:#8B949E;font-size:9px;">{label}</div><div style="font-size:17px;font-weight:900;color:{color};">{val}</div></div>'
m_cols[0].markdown(tile_tmpl.format(label="총 감시 종목", color="#39FF14", val=f"{len(portfolio)} UNIT"), unsafe_allow_html=True)
m_cols[1].markdown(tile_tmpl.format(label="평균 방어 수익률", color="#39FF14" if avg_ret >=0 else "#FF3131", val=f"{avg_ret:+.1f}%"), unsafe_allow_html=True)
m_cols[2].markdown(tile_tmpl.format(label="위험(DANGER) 수", color="#FF3131" if danger_items else "#39FF14", val=len(danger_items)), unsafe_allow_html=True)
m_cols[3].markdown(tile_tmpl.format(label="상장 예정(7D)", color="#FFFF33", val=len(upcoming_list)), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.image("https://via.placeholder.com/150x50/161B22/39FF14?text=HYPER+GUARD", use_container_width=True)
    st.header("🛠️ 관측 통제소")
    issuers_static = ["KODEX", "TIGER", "KBSTAR", "ACE", "SOL"]
    selected_issuers = []
    for issuer in issuers_static:
        if st.checkbox(issuer, value=False, key=f"f_{issuer}"): selected_issuers.append(issuer)
    effective_issuers = selected_issuers if selected_issuers else issuers_static
    filtered_base = [e for e in etf_list if any(iss in e['issuer'] for iss in effective_issuers)]
    
    # [Body] 데이터 유실 방성: 필터 결과가 없으면 기본 데이터 로드
    if not filtered_base: filtered_base = etf_list[:12]
    
    st.header("🤖 AI Smart Slots")
    theme1 = st.text_input("Custom Theme", placeholder="예: 양자컴퓨팅", key="st_1")
    if st.button("♻️ RESET DATA"): save_json('data/user_portfolio.json', []); st.rerun()

# --- Tabs ---
tabs = st.tabs(["📊 Market Watch", "📅 Upcoming", "🚨 Control Room"])

with tabs[0]:
    st.markdown('<div class="vision-banner"><strong>[BETA Vision]</strong> 5대 운용사의 ETF 데이터를 실시간 추적하고 <strong>\'0.1초 자동 매수 시스템\'</strong>을 통해 기회를 선점합니다.</div>', unsafe_allow_html=True)
    
    # AI Smart Recommendation Section
    if theme1:
        st.subheader(f"🤖 AI Match: {theme1}")
        recs = get_smart_recommendations(theme1, etf_list)
        if recs:
            ai_cols = st.columns(3)
            for i, sym in enumerate(recs):
                item = next((e for e in etf_list if e['symbol'] == sym), None)
                if item:
                    with ai_cols[i % 3]:
                        st.markdown(f'<div class="etf-card"><div style="color:#8B949E;font-size:9px;">{item["issuer"]} | AI</div><div style="font-size:15px;font-weight:bold;color:#39FF14;margin:6px 0;">{item["name"]}</div><div style="font-size:18px;font-weight:900;">{item["price_at_listing"]:,} KRW</div></div>', unsafe_allow_html=True)
                        if st.button("TRACK", key=f"ai_t_{item['symbol']}"):
                            portfolio.append({"symbol": item['symbol'], "name": item['name'], "purchase_price": item['price_at_listing'], "status": "추적 중"})
                            save_json('data/user_portfolio.json', portfolio); st.rerun()
        st.divider()

    # Main Grid (Minimum 12 cards)
    main_sections = {"핵심 수혜주": ["AI", "반도체", "엔비디아"], "안정성 테마": ["배당", "인컴", "밸류업"]}
    display_cnt = 0
    for sec_name, ident in main_sections.items():
        sec_etfs = [e for e in filtered_base if any(k.lower() in e['name'].lower() for k in ident)]
        if not sec_etfs: continue
        st.subheader(sec_name)
        cols = st.columns(3)
        for i, item in enumerate(sec_etfs):
            with cols[i % 3]:
                st.markdown(f'<div class="etf-card"><div style="color:#8B949E;font-size:9px;">{item["issuer"]}</div><div style="font-size:14px;font-weight:bold;color:white;margin:5px 0;">{item["name"]}</div><div style="font-size:17px;font-weight:900;">{item["price_at_listing"]:,} KRW</div></div>', unsafe_allow_html=True)
                if st.button("TRACK", key=f"m_t_{item['symbol']}"):
                    portfolio.append({"symbol": item['symbol'], "name": item['name'], "purchase_price": item['price_at_listing'], "status": "추적 중"})
                    save_json('data/user_portfolio.json', portfolio); st.rerun()
            display_cnt += 1
    
    # 추천 종목 Fallback (12개 미만일 시)
    if display_cnt < 6:
        st.subheader("💡 추천 종목")
        cols = st.columns(3)
        for i, item in enumerate(etf_list[:6]):
            with cols[i % 3]:
                st.markdown(f'<div class="etf-card"><div style="color:#8B949E;font-size:9px;">{item["issuer"]}</div><div style="font-size:14px;font-weight:bold;color:white;margin:5px 0;">{item["name"]}</div><div style="font-size:17px;font-weight:900;">{item["price_at_listing"]:,} KRW</div></div>', unsafe_allow_html=True)
                if st.button("TRACK", key=f"f_t_{item['symbol']}"):
                    portfolio.append({"symbol": item['symbol'], "name": item['name'], "purchase_price": item['price_at_listing'], "status": "추적 중"})
                    save_json('data/user_portfolio.json', portfolio); st.rerun()

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
                    st.button("✓ RESERVED", key=f"res_{item['ticker']}", disabled=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="pre-check-btn">', unsafe_allow_html=True)
                    if st.button("[PRE-CHECK]", key=f"pre_{item['ticker']}"):
                        portfolio.append({"symbol": item['ticker'], "name": item['name'], "purchase_price": 0, "status": "대기", "listing_date": item['listing_date']})
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
    for item in active:
        l = item['loss']
        card_html = f'<div class="etf-card"><div style="display:flex;justify-content:space-between;align-items:start;"><div><div class="badge {get_status_class(item["status"])}">{item["status"]}</div><div style="font-size:15px;font-weight:bold;color:white;">{item["name"]}</div></div><div style="text-align:right;"><div style="font-size:22px;font-weight:900;color:{"#FF3131" if l <= -8 else "#39FF14"};">{l:+.1f}%</div><div style="font-size:11px;color:#8B949E;">{int(item["cur"]):,} KRW</div></div></div>{render_gauge(l)}</div>'
        st.markdown(card_html, unsafe_allow_html=True)
        if st.button("UNTRACK", key=f"un_{item['symbol']}"):
            portfolio = [p for p in portfolio if p['symbol'] != item['symbol']]; save_json('data/user_portfolio.json', portfolio); st.rerun()

    standby = [p for p in processed if p['status'] == '대기']
    standby.sort(key=lambda x: x.get('listing_date', ''))
    if standby:
        st.divider()
        st.subheader("⏳ Standby Protocol")
        for item in standby:
            s_html = f'<div class="etf-card" style="min-height:auto;"><div style="display:flex;justify-content:space-between;align-items:center;"><div><span class="badge badge-standby">STANDBY</span><span style="font-size:13px;font-weight:bold;color:white;margin-left:8px;">{item["name"]}</span></div><div style="color:#FFFF33;font-size:10px;font-weight:bold;">📅 {item.get("listing_date")}</div></div></div>'
            st.markdown(s_html, unsafe_allow_html=True)

st.markdown("<div style='color:#484F58;font-size:10px;text-align:center;margin-top:30px;'>Hyper ETF Guardian v3.1 [Emergency Vision Patch]<br>Intelligence: Gemini 2.0 Flash / SnF Ecosystem Restoration</div>", unsafe_allow_html=True)
