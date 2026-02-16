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
    prompt = f"Quant Expert: List top 3 symbols matching theme '{theme}' from provided symbols only. Symbols: {','.join(list(db_symbols)[:40])}. Return only CSV symbols."
    res = get_ai_analysis(prompt)
    extracted = [s.strip() for s in res.split(',') if s.strip().isdigit()]
    return [s for s in extracted if s in db_symbols][:3]

# --- Custom CSS (Static & Vertical Mastery) ---
st.markdown("""<style>
.stApp{background-color:#0A0E14;color:#FFFFFF;}
h1,h2,h3{color:#FFFFFF!important;font-family:'Inter',sans-serif;font-weight:800;margin-bottom:8px!important;}
.stSubheader{color:#B0B0B0!important;font-weight:400;font-size:14px!important;}
.list-item{background-color:#161B22;border-bottom:1px solid #30363D;padding:10px 15px;display:flex;justify-content:space-between;align-items:center;}
.list-item:hover{background-color:#1C2128;}
.badge{display:inline-block;padding:2px 6px;border-radius:3px;font-size:9px;font-weight:900;margin-right:8px;}
.badge-standby{background:rgba(255,255,51,0.1);color:#FFFF33;border:1px solid #FFFF33;}
.badge-tracking{background:rgba(57,255,20,0.1);color:#39FF14;border:1px solid #39FF14;}
.badge-danger{background:rgba(255,49,49,0.1);color:#FF3131;border:1px solid #FF3131;}
.stButton>button{width:100%!important;height:32px!important;font-size:11px!important;font-weight:900!important;border-radius:4px!important;background-color:#21262D!important;color:#FFFFFF!important;border:1px solid #30363D!important;}
.stButton>button:hover{border-color:#39FF14!important;color:#39FF14!important;}
.pre-check-btn button{background-color:#39FF14!important;color:#000000!important;border:none!important;}
.cancel-btn button{background-color:#161B22!important;color:#FF3131!important;border:1px solid #FF3131!important;}
.gauge-container{width:100%;background:#21262D;border-radius:2px;height:5px;margin-top:8px;}
.gauge-fill{height:100%;border-radius:2px;}
.risk-box{background:rgba(255,49,49,0.05);border:1px solid #FF3131;padding:10px;border-radius:4px;margin-bottom:15px;font-size:12px;font-weight:bold;color:#FF3131;}
.metric-tile{background:#161B22;border:1px solid #30363D;border-radius:6px;padding:10px;text-align:center;}
.calendar-day{background:#0D1117;border:1px solid #21262D;border-radius:8px;padding:10px;min-height:180px;}
.calendar-date{font-size:14px;color:#FFFFFF;margin-bottom:10px;border-bottom:2px solid #39FF14;padding-bottom:5px;font-weight:900;text-align:center;}
.cal-entry{background:#161B22;padding:8px;border-radius:4px;margin-bottom:8px;border-left:3px solid #FFFF33;}
.reservation-box{background:#1C2128;border:1px solid #39FF14;padding:15px;border-radius:8px;margin-top:10px;}
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

# --- Header ---
st.markdown("<h2 style='margin:0;'>📊 Hyper ETF Guardian</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#8B949E;font-size:13px;margin:-5px 0 15px 0;'>No Prose, Just Precision.</p>", unsafe_allow_html=True)

# Global AI Risk
danger_items = [p for p in portfolio if p.get('status') == '위험']
risk_prompt = f"Portfolio Risk: {len(danger_items)} danger items. Insight 1 line."
ai_risk_report = get_ai_analysis(risk_prompt)
st.markdown(f'<div class="risk-box">[AI Quant Analysis] {ai_risk_report}</div>', unsafe_allow_html=True)

# Metrics Tiles
metrics = []
for p in portfolio:
    bp = p.get('purchase_price', 1)
    if not bp or bp <= 0: bp = 10000
    cv = bp * (0.965 if p['status'] == '추적 중' else 0.88 if p['status'] == '위험' else 1.0)
    metrics.append({'loss': calculate_loss_rate(cv, bp)})
avg_ret = sum(x['loss'] for x in metrics) / len(metrics) if metrics else 0

m_cols = st.columns(4)
tile_style = "background:#161B22;border:1px solid #30363D;border-radius:6px;padding:10px;text-align:center;"
m_cols[0].markdown(f'<div style="{tile_style}"><div style="color:#8B949E;font-size:9px;">총 감시 종목</div><div style="font-size:17px;font-weight:900;color:#39FF14;">{len(portfolio)} UNIT</div></div>', unsafe_allow_html=True)
m_cols[1].markdown(f'<div style="{tile_style}"><div style="color:#8B949E;font-size:9px;">평균 방어 수익률</div><div style="font-size:17px;font-weight:900;color:{"#FF3131" if avg_ret <0 else "#39FF14"};">{avg_ret:+.1f}%</div></div>', unsafe_allow_html=True)
m_cols[2].markdown(f'<div style="{tile_style}"><div style="color:#8B949E;font-size:9px;">위험(DANGER) 수</div><div style="font-size:17px;font-weight:900;color:{"#FF3131" if danger_items else "#39FF14"};">{len(danger_items)}</div></div>', unsafe_allow_html=True)
m_cols[3].markdown(f'<div style="{tile_style}"><div style="color:#8B949E;font-size:9px;">상장 예정(7D)</div><div style="font-size:17px;font-weight:900;color:#FFFF33;">{len(upcoming_list)}</div></div>', unsafe_allow_html=True)

st.divider()

# --- Sidebar ---
with st.sidebar:
    st.header("🛠️ 관측 통제소")
    issuers_static = ["KODEX", "TIGER", "KBSTAR", "ACE", "SOL"]
    selected_issuers = []
    for issuer in issuers_static:
        if st.checkbox(issuer, value=False, key=f"side_{issuer}"): selected_issuers.append(issuer)
    effective_issuers = selected_issuers if selected_issuers else issuers_static
    filtered_base = [e for e in etf_list if any(iss in e['issuer'] for iss in effective_issuers)]
    if not filtered_base: filtered_base = etf_list[:20]
    
    st.header("🤖 AI Smart Theme")
    theme_input = st.text_input("Theme Focus", placeholder="예: AI 반도체", key="st_theme_main")
    if st.button("♻️ RESET PORTFOLIO"): save_json('data/user_portfolio.json', []); st.rerun()

# --- Tabs ---
tabs = st.tabs(["📊 Market Watch", "📅 Upcoming", "🚨 Control Room"])

with tabs[0]:
    st.markdown("<p style='color:#8B949E;font-size:12px;'><strong>[Vertical Strategy List]</strong> 테마별 Top 10 리스트를 통해 시장을 지휘하십시오.</p>", unsafe_allow_html=True)
    
    main_cats = {
        "AI & 반도체": ["AI", "반도체", "NVIDIA", "HBM"],
        "밸류업 / 저PBR": ["밸류업", "저PBR", "금융", "은행"],
        "미국 빅테크": ["미국", "빅테크", "나스닥", "S&P"],
        "월배당 / 인컴": ["월배당", "배당", "인컴", "커버드콜"]
    }

    if theme_input:
        st.subheader(f"🤖 AI Match: {theme_input}")
        recs = get_smart_recommendations(theme_input, etf_list)
        for sym in recs:
            item = next((e for e in etf_list if e['symbol'] == sym), None)
            if item:
                cur_p = any(p['symbol'] == item['symbol'] for p in portfolio)
                c1, c2, c3 = st.columns([1, 4, 1])
                c1.markdown(f'<span class="badge badge-tracking">AI</span> {item["issuer"]}', unsafe_allow_html=True)
                c2.markdown(f'<b>{item["name"]}</b>', unsafe_allow_html=True)
                c3.markdown(f'<b>{item["price_at_listing"]:,}</b>', unsafe_allow_html=True)
                if not cur_p:
                    if st.button("TRACK", key=f"mw_ai_{item['symbol']}"):
                        portfolio.append({"symbol":item['symbol'],"name":item['name'],"purchase_price":item['price_at_listing'],"status":"추적 중"})
                        save_json('data/user_portfolio.json', portfolio); st.rerun()
                else: st.button("✓ TRACKED", key=f"mw_ai_in_{item['symbol']}", disabled=True)
        st.divider()

    for cat_name, keywords in main_cats.items():
        with st.expander(f"📌 {cat_name} (Top 10)", expanded=True):
            cat_items = [e for e in filtered_base if any(k.lower() in e['name'].lower() for k in keywords)][:10]
            if not cat_items: cat_items = etf_list[:5] # Fallback
            for item in cat_items:
                cur_p = any(p['symbol'] == item['symbol'] for p in portfolio)
                col1, col2, col3, col4 = st.columns([1, 4, 2, 2])
                col1.markdown(f'<span style="color:#8B949E;font-size:11px;">{item["issuer"]}</span>', unsafe_allow_html=True)
                col2.markdown(f'<span style="font-size:13px;font-weight:bold;">{item["name"]}</span>', unsafe_allow_html=True)
                col3.markdown(f'<span style="font-size:13px;font-weight:900;color:#39FF14;">{item["price_at_listing"]:,} KRW</span>', unsafe_allow_html=True)
                with col4:
                    if cur_p:
                        if st.button("UNTRACK", key=f"mw_un_{item['symbol']}_{cat_name}"):
                            portfolio = [p for p in portfolio if p['symbol'] != item['symbol']]; save_json('data/user_portfolio.json', portfolio); st.rerun()
                    else:
                        if st.button("TRACK", key=f"mw_add_{item['symbol']}_{cat_name}"):
                            portfolio.append({"symbol":item['symbol'],"name":item['name'],"purchase_price":item['price_at_listing'],"status":"추적 중"})
                            save_json('data/user_portfolio.json', portfolio); st.rerun()

with tabs[1]:
    st.markdown("<p style='color:#8B949E;font-size:12px;'><strong>[Interactive Reservation]</strong> 상장 예정 종목의 구매 희망가를 설정하여 대기 리스트에 등록하십시오.</p>", unsafe_allow_html=True)
    mon = datetime.now() - timedelta(days=datetime.now().weekday())
    cols = st.columns(5)
    days = ["월", "화", "수", "목", "금"]
    
    for i in range(5):
        d_str = (mon + timedelta(days=i)).strftime("%Y-%m-%d")
        with cols[i]:
            st.markdown(f'<div class="calendar-date">{days[i]} ({d_str})</div>', unsafe_allow_html=True)
            day_it = [e for e in upcoming_list if e['listing_date'] == d_str]
            if not day_it: st.markdown('<div style="text-align:center;color:#484F58;font-size:10px;padding:20px;">NO LISTING</div>', unsafe_allow_html=True)
            for item in day_it:
                is_r = next((p for p in portfolio if p['symbol'] == item['ticker']), None)
                st.markdown(f'<div class="cal-entry"><div class="badge badge-standby">STANDBY</div><div style="font-size:11px;font-weight:bold;color:white;">{item["name"]}</div></div>', unsafe_allow_html=True)
                
                if is_r:
                    st.markdown(f'<div style="font-size:10px;color:#FFFF33;margin-bottom:5px;">예약가: {is_r.get("purchase_price", 0):,} KRW</div>', unsafe_allow_html=True)
                    if st.button("CANCEL", key=f"up_can_{item['ticker']}"):
                        portfolio = [p for p in portfolio if p['symbol'] != item['ticker']]; save_json('data/user_portfolio.json', portfolio); st.rerun()
                else:
                    if st.button("[PRE-CHECK]", key=f"up_pre_{item['ticker']}"):
                        st.session_state[f"res_flow_{item['ticker']}"] = True
                    
                    if st.session_state.get(f"res_flow_{item['ticker']}", False):
                        with st.form(key=f"form_{item['ticker']}"):
                            price = st.number_input("구매 희망가", min_value=0, value=10000, step=100)
                            st.markdown(f'<div style="font-size:11px;color:#39FF14;">{price:,}원에 예약하시겠습니까?</div>', unsafe_allow_html=True)
                            if st.form_submit_button("최종 확정"):
                                portfolio.append({"symbol":item['ticker'],"name":item['name'],"purchase_price":price,"status":"대기","listing_date":item['listing_date']})
                                save_json('data/user_portfolio.json', portfolio)
                                del st.session_state[f"res_flow_{item['ticker']}"]
                                st.rerun()
                            if st.form_submit_button("취소"):
                                del st.session_state[f"res_flow_{item['ticker']}"]
                                st.rerun()

with tabs[2]:
    st.markdown("<p style='color:#8B949E;font-size:12px;'><strong>[Dual-Stage Control]</strong> 위험 종목(ASC 정렬)과 상장 대기 종목을 분리하여 지휘하십시오.</p>", unsafe_allow_html=True)
    
    # Process Portfolio
    processed = []
    for p in portfolio:
        bp = p.get('purchase_price', 10000)
        if not bp or bp <= 0: bp = 10000
        # Simulated Current Value for tracking/danger
        cv = bp * (0.965 if p['status'] == '추적 중' else 0.88 if p['status'] == '위험' else 1.0)
        p['loss'] = calculate_loss_rate(cv, bp); p['cur'] = cv
        processed.append(p)

    # Stage 1: Active Monitoring (Risk Sort)
    active = [p for p in processed if p['status'] != '대기']
    active.sort(key=lambda x: x['loss']) # Lowest return first
    
    st.subheader("⚠️ Stage 1: Risk Monitoring")
    if not active: st.info("활성화된 감시 프로토콜이 없습니다.")
    for item in active:
        l = item['loss']
        st.markdown(f'<div class="list-item"><div><span class="badge {get_status_class(item["status"])}">{item["status"]}</span><span style="font-weight:bold;">{item["name"]} ({item["symbol"]})</span></div><div style="text-align:right;"><span style="font-size:18px;font-weight:900;color:{"#FF3131" if l <= -8 else "#39FF14"};">{l:+.1f}%</span><div style="font-size:10px;color:#8B949E;">{int(item["cur"]):,} KRW</div></div></div>', unsafe_allow_html=True)
        st.markdown(render_gauge(l), unsafe_allow_html=True)
        if st.button("UNTRACK", key=f"cr_un_{item['symbol']}"):
            portfolio = [p for p in portfolio if p['symbol'] != item['symbol']]; save_json('data/user_portfolio.json', portfolio); st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)

    # Stage 2: Pending (Date Sort)
    pending = [p for p in processed if p['status'] == '대기']
    pending.sort(key=lambda x: x.get('listing_date', '9999-12-31'))
    
    st.divider()
    st.subheader("⏳ Stage 2: Pending Reservation")
    if not pending: st.info("예약된 상장 대기 종목이 없습니다.")
    for item in pending:
        col1, col2, col3 = st.columns([4, 2, 1])
        with col1:
            st.markdown(f'<div style="padding:10px;background:#161B22;border-radius:4px;"><span class="badge badge-standby">STANDBY</span> <b>{item["name"]}</b> <span style="font-size:10px;color:#8B949E;">({item["symbol"]})</span></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div style="padding:10px;text-align:center;"><b>📅 {item.get("listing_date")}</b></div>', unsafe_allow_html=True)
        with col3:
            if st.button("CANCEL", key=f"cr_can_{item['symbol']}"):
                portfolio = [p for p in portfolio if p['symbol'] != item['symbol']]; save_json('data/user_portfolio.json', portfolio); st.rerun()

st.markdown("<div style='color:#484F58;font-size:10px;text-align:center;margin-top:50px;'>Hyper ETF Guardian v4.0 [The Guardian]<br>Intelligence: Gemini 2.0 Flash / SnF Overhaul Build</div>", unsafe_allow_html=True)
