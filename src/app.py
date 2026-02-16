import streamlit as st
import json, os, sys
import google.generativeai as genai
from datetime import datetime

# 1. [System] 레이아웃 및 폰트 시인성 극대화 (v7.9 Final)
st.set_page_config(page_title="Hyper ETF Guardian", layout="wide", initial_sidebar_state="collapsed")

# --- AI Intel Layer ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def get_ai_intel(prompt):
    if not GEMINI_API_KEY: return "[위험: 5.0 / 키 미설정]"
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(f"Financial analyst context. Max 10 words: {prompt}")
        return response.text.replace("\n", " ").strip() if response.text else "[대기 중]"
    except: return "[타임아웃]"

# 2. [UI/UX] 불사신 CSS: 절대 블랙아웃 (v7.9 Final Victory)
st.markdown("""
    <style>
    /* 1. 불필요 요소 박멸 */
    [data-testid="stSidebar"], [data-testid="stSidebarNav"], .stDeployButton { display: none !important; }
    
    /* 2. 전역 다크 락다운 */
    .stApp { background-color: #0A0E14 !important; color: #FFFFFF !important; }
    .block-container { padding: 2rem 3rem !important; max-width: 98% !important; }
    
    /* 3. [v7.9 최후 통첩] 모든 종류의 버튼 및 팝오버 트리거 시각적 봉쇄 */
    /* st.button, st.popover, secondary button 모두 타겟팅 */
    .stButton button, .stPopover button, div[data-testid="stPopover"] > button, .st-emotion-cache-19rxjzo { 
        background-color: #0E1117 !important; 
        color: #39FF14 !important; 
        border: 1px solid #39FF14 !important; 
        font-weight: 900 !important;
        border-radius: 6px !important; 
        width: 100% !important;
        height: 32px !important;
        font-size: 11px !important;
        box-shadow: none !important;
    }
    
    /* 호버 시 색상 반전 활성 */
    .stButton button:hover, .stPopover button:hover, div[data-testid="stPopover"] > button:hover { 
        background-color: #39FF14 !important; 
        color: #000000 !important; 
        border-color: #39FF14 !important;
    }

    /* 팝오버 내부 박스 전용 스타일 */
    div[data-testid="stPopoverContent"] {
        background-color: #161B22 !important;
        border: 1px solid #30363D !important;
        color: #FFFFFF !important;
    }
    
    /* 타이포그래피 인양 (v7.9) */
    .issuer-name { font-size: 13px !important; color: #8B949E; width: 85px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
    .product-name { font-size: 15px !important; font-weight: 900; color: #FFFFFF; flex-grow: 1; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
    
    .v7-box { background-color: #161B22; border: 1px solid #30363D; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 8px 16px rgba(0,0,0,0.5); }
    .v7-title { font-size: 14px; font-weight: 900; color: #FFFFFF; border-left: 5px solid #39FF14; padding-left: 10px; margin-bottom: 15px; text-transform: uppercase; }
    .list-row { display: flex; align-items: center; height: 32px; gap: 10px; width: 100%; border-bottom: 1px solid #21262D; }

    .stCaption { color: #8B949E !important; font-weight: 700 !important; }
    </style>
""", unsafe_allow_html=True)

# 3. [Data] 데이터 핸들러 (캐시 충돌 박멸)
P_FILE = 'data/user_portfolio.json'
ETF_FILE = 'data/etf_list.json'
UPC_FILE = 'data/upcoming_etf.json'

def load_j(path):
    if not os.path.exists(path): return []
    try:
        with open(path,'r',encoding='utf-8') as f: return json.load(f)
    except: return []

def save_p(d):
    with open(P_FILE,'w',encoding='utf-8') as f: json.dump(d, f, indent=2, ensure_ascii=False)

def handle_action(itm, action, qty=0):
    portfolio = load_j(P_FILE)
    if action == "TOGGLE":
        if any(p['symbol'] == itm['symbol'] for p in portfolio):
            portfolio = [p for p in portfolio if p['symbol'] != itm['symbol']]
        else:
            portfolio.append({"symbol": itm['symbol'], "name": itm['name'], "issuer": itm['issuer'], "purchase_price": itm.get('price_at_listing', 10000), "current_price": itm.get('price_at_listing', 10000), "status": "라이브", "qty": 0})
    elif action == "RESERVE":
        if not any(p['symbol'] == itm['ticker'] for p in portfolio):
            portfolio.append({"symbol": itm['ticker'], "name": itm['name'], "issuer": itm['issuer'], "purchase_price": 10000, "current_price": 10000, "status": "예약 중", "qty": qty, "date": itm['listing_date']})
            st.toast("🚨 상장 예약 성공")
    elif action == "CANCEL":
        target_symbol = itm.get('symbol') or itm.get('ticker')
        portfolio = [p for p in portfolio if p['symbol'] != target_symbol]
        st.toast("🗑️ 예약이 취소되었습니다.")
    
    save_p(portfolio)
    st.rerun()

# --- Main Command Center ---
st.markdown("<h2> 📊 하이퍼 ETF 가디언 <span style='font-size:12px;color:#39FF14;'>[v7.9 최후의 무결성 빌드]</span></h2>", unsafe_allow_html=True)
portfolio = load_j(P_FILE)
etfs = load_j(ETF_FILE)
upcs = sorted(load_j(UPC_FILE), key=lambda x: x.get('listing_date', '9999-12-31'))

ai_rep = get_ai_intel(f"유닛: {len(portfolio)}. 모든 화이트아웃 요소 숙청 완료.")
st.markdown(f'<div style="background:rgba(255,49,49,0.05); border:1px solid #FF3131; padding:20px; border-radius:10px; margin-bottom:35px; color:#FF3131; font-weight:900;">🚨 AI Intel: {ai_rep} </div>', unsafe_allow_html=True)

tabs = st.tabs(["📊 시장 감시", "📅 상장 일정", "🚨 위험 통제"])

with tabs[0]: # Market Watch (60 Unit Influx + Knife-Edge Alignment)
    st.markdown("<p style='font-size:11px;color:#8B949E;margin-bottom:15px;'>정렬 기준: 최근 수익률 높은 순</p>", unsafe_allow_html=True)
    themes = [{"n": "AI/반도체", "k": ["AI", "반도체"]}, {"n": "미국 빅테크", "k": ["미국", "빅테크"]}, {"n": "배당/밸류업", "k": ["배당", "밸류"]}, {"n": "국내 지수", "k": ["200", "코스피"]}, {"n": "글로벌 액티브", "k": ["글로벌"]}, {"n": "기술/소부장", "k": ["기술", "혁신"]}]
    row1, row2 = st.columns(3), st.columns(3)
    all_c = row1 + row2
    for idx, th in enumerate(themes):
        with all_c[idx]:
            st.markdown(f'<div class="v7-box"><div class="v7-title">{th["n"]} 전략</div>', unsafe_allow_html=True)
            tp = [e for e in etfs if any(k in e['name'] for k in th['k'])]
            seen = {e['symbol'] for e in tp}
            for e in etfs:
                if len(tp) >= 10: break
                if e['symbol'] not in seen: tp.append(e); seen.add(e['symbol'])
            for r, itm in enumerate(tp[:10]):
                is_t = any(p['symbol'] == itm['symbol'] for p in portfolio)
                c_row = st.columns([8.2, 1.8])
                with c_row[0]:
                    st.markdown(f"""
                        <div class="list-row">
                            <span style="color:#8B949E;width:15px;font-size:10px;">{r+1}</span>
                            <span class="issuer-name">{itm["issuer"]}</span>
                            <span class="product-name">{itm["name"]}</span>
                        </div>
                    """, unsafe_allow_html=True)
                with c_row[1]:
                    if st.button("해제" if is_t else "추적", key=f"tk_{idx}_{itm['symbol']}"): handle_action(itm, "TOGGLE")
            st.markdown("</div>", unsafe_allow_html=True)

with tabs[1]: # Upcoming (Ghost Prevention Logic)
    st.markdown("<div style='font-size:16px; font-weight:900; margin-bottom:20px;'>📅 하이퍼 자산 투하 일정 (v7.9 컬러 락다운)</div>", unsafe_allow_html=True)
    u_cols = st.columns(4)
    for i, itm in enumerate(upcs):
        is_reserved = any(p['symbol'] == itm['ticker'] and p['status'] == "예약 중" for p in portfolio)
        with u_cols[i % 4]:
            st.markdown(f"<div style='background:#FFD700;color:#000;padding:2px 8px;border-radius:4px;font-weight:900;font-size:10px;width:fit-content;margin-bottom:5px;'>📅 {itm['listing_date']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='v7-box' style='padding:15px;border-left:5px solid #FFD700;'><span class='product-name'>{itm['name']}</span><br><small class='issuer-name'>{itm['issuer']}</small></div>", unsafe_allow_html=True)
            if is_reserved:
                with st.popover("예약 관리", use_container_width=True):
                    st.write("이미 예약된 종목입니다. 취소하시겠습니까?")
                    if st.button("예, 예약을 취소합니다", key=f"can_upc_{itm['ticker']}"): handle_action({"symbol": itm['ticker']}, "CANCEL")
            else:
                with st.popover("상장 예약", use_container_width=True):
                    qty = st.number_input("수량(주)", 1, 1000, 10, key=f"qty_{itm['ticker']}")
                    if st.button("예약 확정", key=f"conf_{itm['ticker']}"): handle_action(itm, "RESERVE", qty)

with tabs[2]: # Risk Control (Commander Columns [5:5 Split])
    live_p = sorted([p for p in portfolio if p['status'] == "라이브"], key=lambda x: (x['current_price']-x['purchase_price'])/x['purchase_price'])
    res_p = [p for p in portfolio if p['status'] == "예약 중"]
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### 🛰️ 실시간 추적 (손절 위험순)")
        if not live_p: st.info("실시간 추적 중인 자산이 없습니다.")
        for p in live_p:
            l_r = ((p['current_price'] - p['purchase_price']) / p['purchase_price'] * 100) if p['purchase_price'] > 0 else 0
            st.markdown(f"""
                <div class="v7-box" style="border-left: 5px solid {'#FF3131' if l_r <= -10 else '#39FF14'}; padding: 15px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div>
                            <span class="issuer-name">{p.get('issuer', 'Unknown')}</span><br>
                            <span class="product-name">{p['name']}</span>
                        </div>
                        <div style="text-align:right;">
                            <span style="color:{'#FF3131' if l_r < 0 else '#39FF14'}; font-size:18px; font-weight:900;">{l_r:+.2f}%</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("추적 해제", key=f"del_live_{p['symbol']}"): handle_action(p, "TOGGLE")
            
    with col_b:
        st.markdown("### 📅 상장 예정 예약")
        if not res_p: st.info("예약된 상장 예정 자산이 없습니다.")
        for p in res_p:
            st.markdown(f"""
                <div class="v7-box" style="border-left: 5px solid #FFD700; padding: 15px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div>
                            <span class="issuer-name">{p.get('issuer', 'Unknown')} | {p.get('date', 'Unknown')}</span><br>
                            <span class="product-name">{p['name']}</span>
                        </div>
                        <div style="text-align:right;">
                            <span style="color:#FFD700; font-size:16px; font-weight:900;">{p.get('qty',0)}주</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            with st.popover("예약 취소", use_container_width=True):
                st.write("정말 예약을 취소하시겠습니까?")
                if st.button("예, 취소합니다", key=f"can_res_{p['symbol']}"): handle_action(p, "CANCEL")

st.markdown(f"<div style='text-align:center;margin-top:50px;font-size:10px;color:#484F58;'>Hyper ETF Guardian v7.9 | Final Integrity Build | Mission Optimized</div>", unsafe_allow_html=True)