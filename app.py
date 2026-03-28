import streamlit as st
import requests
import time
import random

# --- AYARLAR ---
st.set_page_config(page_title="Arbitrum İstihbarat", layout="wide")

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .panel-box {
        background-color: #0d0d0d; border: 1px solid #222;
        border-radius: 8px; padding: 20px; color: #eee; margin-bottom: 20px;
    }
    .whale-box {
        background-color: #2a0404; border: 1px solid #ff0000;
        border-radius: 8px; padding: 15px; text-align: center; margin-bottom: 20px;
    }
    .metric-text { color: #00ff00; font-size: 20px; font-weight: bold; font-family: monospace; }
    
    /* Radar Link Tasarımları */
    a.whale-link {
        display: block; background-color: #1f0303; border-left: 5px solid #ff0000;
        color: #ff4d4d; padding: 12px; text-decoration: none; margin-bottom: 8px;
        font-family: monospace; border-radius: 0 4px 4px 0; transition: 0.3s;
        position: relative;
    }
    a.whale-link:hover { background-color: #3b0707; color: #ff8080; }
    
    a.normal-link {
        display: block; background-color: #121212; border-left: 5px solid #444;
        color: #aaa; padding: 12px; text-decoration: none; margin-bottom: 8px;
        font-family: monospace; border-radius: 0 4px 4px 0; transition: 0.3s;
        position: relative;
    }
    a.normal-link:hover { background-color: #1e1e1e; color: #fff; }
    
    .time-badge {
        position: absolute; right: 10px; top: 12px;
        font-size: 11px; color: #777;
    }
</style>
""", unsafe_allow_html=True)

# --- DİLLER ---
langs = {
    "TR": {
        "menu": "KOMUTA MERKEZİ", "search_label": "Hedef Token veya Adres:", "search_btn": "Sorgula",
        "price": "Anlık Fiyat", "liq": "Havuz Derinliği", "vol": "24S Hacim",
        "latest_whale": "🚨 EN SON BALİNA TESPİTİ", "new_contracts": "📜 SOKAK RADARI (Yeni Kontratlar)",
        "whale_tx": "🐋 BALİNA HAREKETLERİ", "scan_btn": "📡 Sokağı Dinle (Ağı Yenile)",
        "no_data": "İstihbarat bulunamadı.", "sec": "sn önce", "min": "dk önce"
    },
    "EN": {
        "menu": "COMMAND CENTER", "search_label": "Target Token or Address:", "search_btn": "Search",
        "price": "Live Price", "liq": "Pool Depth", "vol": "24H Volume",
        "latest_whale": "🚨 LATEST WHALE DETECTED", "new_contracts": "📜 STREET RADAR (New Contracts)",
        "whale_tx": "🐋 WHALE ACTIVITY", "scan_btn": "📡 Listen to Streets (Refresh)",
        "no_data": "No intel found.", "sec": "sec ago", "min": "min ago"
    },
    "RU": {
        "menu": "КОМАНДНЫЙ ЦЕНТР", "search_label": "Токен или адрес:", "search_btn": "Поиск",
        "price": "Цена", "liq": "Ликвидность", "vol": "Объем 24ч",
        "latest_whale": "🚨 ПОСЛЕДНИЙ КИТ", "new_contracts": "📜 РАДАР УЛИЦ",
        "whale_tx": "🐋 АКТИВНОСТЬ КИТОВ", "scan_btn": "📡 Обновить радар",
        "no_data": "Нет данных.", "sec": "сек назад", "min": "мин назад"
    },
    "KO": {
        "menu": "지휘 통제소", "search_label": "토큰 또는 주소:", "search_btn": "검색",
        "price": "현재 가격", "liq": "유동성", "vol": "24H 거래량",
        "latest_whale": "🚨 최신 고래", "new_contracts": "📜 거리 레이더",
        "whale_tx": "🐋 고래 활동", "scan_btn": "📡 레이더 새로고침",
        "no_data": "데이터 없음.", "sec": "초 전", "min": "분 전"
    }
}

with st.sidebar:
    st.markdown("### 🌐 Dil / Language")
    selected_lang = st.radio("", ["TR", "EN", "RU", "KO"], horizontal=True, label_visibility="collapsed")
    t = langs[selected_lang]
    st.markdown("---")
    st.markdown(f"### 🎛️ {t['menu']}")
    st.markdown("- 🔍 Hedef Analizi\n- 📜 Sokak Radarı\n- 🐋 Balina Takibi")

# --- İSTİHBARAT MOTORU ---
def search_token_dexscreener(query):
    try:
        res = requests.get(f"https://api.dexscreener.com/latest/dex/search?q={query}").json()
        if res.get("pairs"):
            arb_pairs = [p for p in res["pairs"] if p.get("chainId") == "arbitrum"]
            if arb_pairs:
                pair = arb_pairs[0]
                return {
                    "address": pair.get("baseToken", {}).get("address", ""),
                    "name": pair.get("baseToken", {}).get("name", ""),
                    "symbol": pair.get("baseToken", {}).get("symbol", ""),
                    "priceUsd": pair.get("priceUsd", "0"),
                    "liquidity": pair.get("liquidity", {}).get("usd", 0),
                    "volume24h": pair.get("volume", {}).get("h24", 0)
                }
    except: pass
    return None

def format_time(seconds_ago, lang_dict):
    """Zamanı saniye veya dakika olarak dillere göre formatlar"""
    if seconds_ago < 60:
        return f"{int(seconds_ago)} {lang_dict['sec']}"
    else:
        return f"{int(seconds_ago // 60)} {lang_dict['min']}"

def generate_random_address():
    return "0x" + "".join(random.choices("0123456789abcdef", k=40))

# --- HAFIZA VE SİMÜLASYON (15 Kontratlık Radar) ---
if "contracts" not in st.session_state:
    st.session_state.contracts = []
    current_time = time.time()
    # Arayüz dolu dursun diye başlangıçta 15 tane kontrat üretiyoruz
    for i in range(15):
        is_whale = random.choice([True, False, False, False]) # %25 ihtimalle balina
        bal = random.uniform(55.0, 300.0) if is_whale else random.uniform(0.1, 15.0)
        # Geçmişe dönük rastgele zamanlar (5 saniye ile 10 dakika arası)
        birth_time = current_time - random.randint(5, 600)
        st.session_state.contracts.append({
            "addr": generate_random_address(), "is_whale": is_whale, 
            "bal": bal, "birth": birth_time
        })
    st.session_state.contracts.sort(key=lambda x: x["birth"], reverse=True) # En yeniler üstte

def scan_network_for_contracts():
    """Ağı Tara butonuna basıldığında yeni kontratlar ekler, eskileri siler"""
    new_count = random.randint(1, 3) # 1 ile 3 arası yeni kontrat düştü varsayalım
    for _ in range(new_count):
        is_whale = random.choice([True, False, False, False, False])
        bal = random.uniform(51.0, 500.0) if is_whale else random.uniform(0.01, 8.0)
        st.session_state.contracts.insert(0, {
            "addr": generate_random_address(), "is_whale": is_whale, 
            "bal": bal, "birth": time.time() # Tam şu an eklendi
        })
    # Listeyi maksimum 25'te tut, ekran çok uzamasın
    st.session_state.contracts = st.session_state.contracts[:25]

# En son balinayı bul
latest_whale = next((c for c in st.session_state.contracts if c["is_whale"]), None)

# --- 1. ANA EKRAN: TOKEN ARAMA ---
st.markdown(f"<h2>{t['search_label']}</h2>", unsafe_allow_html=True)
search_query = st.text_input("", placeholder="Örn: ARB, PENDLE, 0x...", label_visibility="collapsed")

if search_query:
    with st.spinner("..."):
        token_data = search_token_dexscreener(search_query)
        if token_data:
            st.markdown("<div class='panel-box'>", unsafe_allow_html=True)
            st.markdown(f"<h3>{token_data['name']} <span style='color:#555;'>({token_data['symbol']})</span></h3>", unsafe_allow_html=True)
            st.markdown(f"<code style='color:#888;'>{token_data['address']}</code>", unsafe_allow_html=True)
            st.markdown("<hr style='border-color:#333; margin:15px 0px;'>", unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"<div style='color:#888; font-size:14px;'>{t['price']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='metric-text'>${float(token_data['priceUsd']):.6f}</div>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<div style='color:#888; font-size:14px;'>{t['liq']}</div>", unsafe_allow_html=True)
                liq_color = "#ff9900" if token_data['liquidity'] < 100000 else "#00ff00"
                st.markdown(f"<div class='metric-text' style='color:{liq_color};'>${token_data['liquidity']:,.0f}</div>", unsafe_allow_html=True)
            with c3:
                st.markdown(f"<div style='color:#888; font-size:14px;'>{t['vol']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='metric-text' style='color:#fff;'>${token_data['volume24h']:,.0f}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.error(t['no_data'])

# --- 2. EN SON BALİNA ALARMI ---
if latest_whale:
    st.markdown(f"""
    <div class='whale-box'>
        <h4 style='color:#ff4d4d; margin-top:0;'>{t['latest_whale']}</h4>
        <a href="https://arbiscan.io/address/{latest_whale['addr']}" target="_blank" style="color:#fff; text-decoration:underline; font-family:monospace; font-size:18px;">
            {latest_whale['addr']}
        </a>
        <div style="color:#aaa; margin-top:10px;">Cüzdan Gücü: <span style="color:#ff4d4d; font-weight:bold;">{latest_whale['bal']:.2f} ETH</span></div>
    </div>
    """, unsafe_allow_html=True)

# --- 3. AÇIK RADAR (15+ KONTRAT AKIŞI) ---
st.markdown("---")
st.button(t['scan_btn'], on_click=scan_network_for_contracts, use_container_width=True)

col_normal, col_whale = st.columns(2)
current_time = time.time()

with col_normal:
    st.markdown(f"<h4 style='color:#aaa;'>{t['new_contracts']}</h4>", unsafe_allow_html=True)
    for c in st.session_state.contracts:
        if not c['is_whale']:
            age_secs = current_time - c['birth']
            time_str = format_time(age_secs, t)
            st.markdown(f"""
            <a href="https://arbiscan.io/address/{c['addr']}" target="_blank" class="normal-link">
                <div>📄 {c['addr'][:12]}...{c['addr'][-4:]}</div>
                <div style="font-size:12px; color:#666; margin-top:4px;">Güç: {c['bal']:.4f} ETH</div>
                <span class="time-badge">{time_str}</span>
            </a>
            """, unsafe_allow_html=True)

with col_whale:
    st.markdown(f"<h4 style='color:#ff4d4d;'>{t['whale_tx']}</h4>", unsafe_allow_html=True)
    for c in st.session_state.contracts:
        if c['is_whale']:
            age_secs = current_time - c['birth']
            time_str = format_time(age_secs, t)
            st.markdown(f"""
            <a href="https://arbiscan.io/address/{c['addr']}" target="_blank" class="whale-link">
                <div>🚨 {c['addr'][:12]}...{c['addr'][-4:]}</div>
                <div style="font-size:12px; color:#ffb3b3; margin-top:4px;">Güç: {c['bal']:.2f} ETH</div>
                <span class="time-badge">{time_str}</span>
            </a>
            """, unsafe_allow_html=True)
