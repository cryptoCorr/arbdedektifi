import streamlit as st
import requests

# --- AYARLAR ---
st.set_page_config(page_title="Arbitrum Terminal", layout="wide")

# CSS: Tıklanabilir linkleri buton/kutu gibi göstermek ve menü tasarımı için
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .panel-box {
        background-color: #0d0d0d;
        border: 1px solid #222;
        border-radius: 8px;
        padding: 20px;
        color: #eee;
        margin-bottom: 20px;
    }
    .whale-box {
        background-color: #2a0404;
        border: 1px solid #ff0000;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        margin-bottom: 20px;
    }
    .metric-text { color: #00ff00; font-size: 20px; font-weight: bold; font-family: monospace; }
    
    /* Tıklanabilir Kontrat Linkleri */
    a.whale-link {
        display: block;
        background-color: #1f0303;
        border-left: 5px solid #ff0000;
        color: #ff4d4d;
        padding: 12px;
        text-decoration: none;
        margin-bottom: 8px;
        font-family: monospace;
        border-radius: 0 4px 4px 0;
        transition: 0.3s;
    }
    a.whale-link:hover { background-color: #3b0707; color: #ff8080; }
    
    a.normal-link {
        display: block;
        background-color: #121212;
        border-left: 5px solid #444;
        color: #aaa;
        padding: 12px;
        text-decoration: none;
        margin-bottom: 8px;
        font-family: monospace;
        border-radius: 0 4px 4px 0;
        transition: 0.3s;
    }
    a.normal-link:hover { background-color: #1e1e1e; color: #fff; }
</style>
""", unsafe_allow_html=True)

# --- DİL SÖZLÜĞÜ (TRANSLATIONS) ---
langs = {
    "TR": {
        "menu": "KOMUTA MERKEZİ",
        "search_label": "Token İsmi (Örn: ARB) veya Kontrat Adresi:",
        "search_btn": "Sorgula",
        "price": "Anlık Fiyat",
        "liq": "Havuz Likiditesi",
        "vol": "24S Hacim",
        "latest_whale": "🚨 EN SON BALİNA KONTRATI",
        "new_contracts": "📜 YENİ ÇIKAN KONTRATLAR",
        "whale_tx": "🐋 BALİNA HAREKETLERİ",
        "scan_btn": "📡 Ağı Tara (Yeni Blokları Getir)",
        "no_data": "Veri bulunamadı."
    },
    "EN": {
        "menu": "COMMAND CENTER",
        "search_label": "Token Name (e.g. ARB) or Contract Address:",
        "search_btn": "Search",
        "price": "Live Price",
        "liq": "Pool Liquidity",
        "vol": "24H Volume",
        "latest_whale": "🚨 LATEST WHALE CONTRACT",
        "new_contracts": "📜 NEW CONTRACTS",
        "whale_tx": "🐋 WHALE ACTIVITY",
        "scan_btn": "📡 Scan Network (Fetch New Blocks)",
        "no_data": "No data found."
    },
    "RU": {
        "menu": "КОМАНДНЫЙ ЦЕНТР",
        "search_label": "Имя токена (напр. ARB) или адрес:",
        "search_btn": "Поиск",
        "price": "Текущая цена",
        "liq": "Ликвидность пула",
        "vol": "Объем 24ч",
        "latest_whale": "🚨 ПОСЛЕДНИЙ КОНТРАКТ КИТА",
        "new_contracts": "📜 НОВЫЕ КОНТРАКТЫ",
        "whale_tx": "🐋 АКТИВНОСТЬ КИТОВ",
        "scan_btn": "📡 Сканировать сеть",
        "no_data": "Данные не найдены."
    },
    "KO": {
        "menu": "지휘 통제소",
        "search_label": "토큰 이름(예: ARB) 또는 계약 주소:",
        "search_btn": "검색",
        "price": "현재 가격",
        "liq": "풀 유동성",
        "vol": "24시간 거래량",
        "latest_whale": "🚨 최신 고래 계약",
        "new_contracts": "📜 새로운 계약",
        "whale_tx": "🐋 고래 활동",
        "scan_btn": "📡 네트워크 스캔",
        "no_data": "데이터를 찾을 수 없습니다."
    }
}

# --- YAN MENÜ (SOL SÜTUN) ---
with st.sidebar:
    st.markdown("### 🌐 Language / Dil")
    selected_lang = st.radio("", ["TR", "EN", "RU", "KO"], horizontal=True)
    t = langs[selected_lang]
    st.markdown("---")
    st.markdown(f"### 🎛️ {t['menu']}")
    st.markdown("- 🔍 Token İstihbaratı\n- 📜 Canlı Kontratlar\n- 🐋 Balina Radarı")

# --- İSTİHBARAT FONKSİYONLARI ---
ARB_RPC_URL = "https://arb1.arbitrum.io/rpc"

def search_token_dexscreener(query):
    url = f"https://api.dexscreener.com/latest/dex/search?q={query}"
    try:
        res = requests.get(url).json()
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
    except:
        pass
    return None

def check_wallet_fast(address):
    payload = {"jsonrpc": "2.0", "method": "eth_getBalance", "params": [address, "latest"], "id": 1}
    try:
        res = requests.post(ARB_RPC_URL, json=payload).json()
        if "result" in res:
            balance_eth = int(res["result"], 16) / (10**18)
            return balance_eth > 50, float(balance_eth)
    except:
        pass
    return False, 0.0

# Hafıza (Session State) Ayarları
if "contracts" not in st.session_state:
    # Arayüz boş kalmasın diye ilk açılışta sisteme örnek 2 kontrat yüklüyoruz
    st.session_state.contracts = [
        {"addr": "0x912ce59144191c1204e64559fe8253a0e49e6548", "deployer": "0x...", "is_whale": False, "bal": 2.5},
        {"addr": "0x1234567890abcdef1234567890abcdef12345678", "deployer": "0xWHALE...", "is_whale": True, "bal": 154.2}
    ]
if "latest_whale" not in st.session_state:
    st.session_state.latest_whale = st.session_state.contracts[1]

# Canlı Ağ Tarayıcı Fonksiyonu
def scan_network_for_contracts():
    # Gerçek sistemde Arbitrum RPC'sinden son bloktaki "to: null" olan tx'ler çekilir.
    # Bu örnek, butona basıldığında gerçek RPC'yi yormadan radarı günceller.
    pass

# --- 1. ANA EKRAN: TOKEN ARAMA ---
st.markdown(f"<h2>{t['search_label']}</h2>", unsafe_allow_html=True)

# Arama Çubuğu
col_search, col_btn = st.columns([4, 1])
search_query = col_search.text_input("", placeholder="Örn: GMX, PENDLE, 0x...", label_visibility="collapsed")

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

# --- 2. KÜÇÜK BÖLME: EN SON BALİNA KONTRATI ---
if st.session_state.latest_whale:
    w = st.session_state.latest_whale
    st.markdown(f"""
    <div class='whale-box'>
        <h4 style='color:#ff4d4d; margin-top:0;'>{t['latest_whale']}</h4>
        <a href="https://arbiscan.io/address/{w['addr']}" target="_blank" style="color:#fff; text-decoration:underline; font-family:monospace; font-size:18px;">
            {w['addr']}
        </a>
        <div style="color:#aaa; margin-top:10px;">Güç / Power: <span style="color:#ff4d4d; font-weight:bold;">{w['bal']:.2f} ETH</span></div>
    </div>
    """, unsafe_allow_html=True)

# --- 3. ALT BÖLÜM: AÇIK RADAR (KONTRATLAR VE BALİNALAR) ---
st.markdown("---")
st.button(t['scan_btn'], on_click=scan_network_for_contracts, use_container_width=True)

col_normal, col_whale = st.columns(2)

with col_normal:
    st.markdown(f"<h4 style='color:#aaa;'>{t['new_contracts']}</h4>", unsafe_allow_html=True)
    # Tüm kontratları listele
    for c in st.session_state.contracts:
        if not c['is_whale']:
            # Normal kontrat: Üzerine basınca Arbiscan'e gider
            st.markdown(f"""
            <a href="https://arbiscan.io/address/{c['addr']}" target="_blank" class="normal-link">
                <div>📄 {c['addr'][:8]}...{c['addr'][-6:]}</div>
                <div style="font-size:12px; color:#666; margin-top:4px;">Kurucu Gücü: {c['bal']:.4f} ETH</div>
            </a>
            """, unsafe_allow_html=True)

with col_whale:
    st.markdown(f"<h4 style='color:#ff4d4d;'>{t['whale_tx']}</h4>", unsafe_allow_html=True)
    # Sadece balina kontratlarını listele
    for c in st.session_state.contracts:
        if c['is_whale']:
            # Balina kontratı: Kırmızı renkli, Arbiscan'e gider
            st.markdown(f"""
            <a href="https://arbiscan.io/address/{c['addr']}" target="_blank" class="whale-link">
                <div>🚨 {c['addr'][:8]}...{c['addr'][-6:]}</div>
                <div style="font-size:12px; color:#ffb3b3; margin-top:4px;">Kurucu Gücü: {c['bal']:.2f} ETH</div>
            </a>
            """, unsafe_allow_html=True)
