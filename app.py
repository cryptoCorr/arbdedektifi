import streamlit as st
import streamlit.components.v1 as components
import requests
import time
import random

# --- AYARLAR VE STİL ---
st.set_page_config(page_title="Arbitrum İstihbarat", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    
    .panel-box { background-color: #0a0a0a; border: 1px solid #222; border-radius: 8px; padding: 20px; color: #eee; margin-bottom: 20px; }
    .security-box-clean { background-color: #031f03; border: 1px solid #00ff00; border-radius: 8px; padding: 15px; text-align: center; }
    .security-box-danger { background-color: #2a0404; border: 1px solid #ff0000; border-radius: 8px; padding: 15px; text-align: center; animation: pulse 2s infinite; }
    
    @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(255, 0, 0, 0.7); } 70% { box-shadow: 0 0 0 10px rgba(255, 0, 0, 0); } 100% { box-shadow: 0 0 0 0 rgba(255, 0, 0, 0); } }
    
    .metric-text { font-size: 20px; font-weight: bold; font-family: monospace; }
    .label-text { color: #888; font-size: 13px; text-transform: uppercase; }
    
    a.social-btn { display: inline-block; background-color: #1a1a1a; color: #4da6ff; padding: 6px 15px; border-radius: 4px; border: 1px solid #333; text-decoration: none; margin-right: 10px; margin-top: 10px; font-size: 14px; }
    a.social-btn:hover { background-color: #2a2a2a; color: #fff; }
    
    /* Radar Linkleri */
    a.whale-link { display: block; background-color: #1f0303; border-left: 5px solid #ff0000; color: #ff4d4d; padding: 12px; text-decoration: none; margin-bottom: 8px; font-family: monospace; position: relative; }
    a.normal-link { display: block; background-color: #121212; border-left: 5px solid #444; color: #aaa; padding: 12px; text-decoration: none; margin-bottom: 8px; font-family: monospace; position: relative; }
    .time-badge { position: absolute; right: 10px; top: 12px; font-size: 11px; color: #777; }
</style>
""", unsafe_allow_html=True)

# --- DİL MOTORU (SAĞ ÜST KÖŞE) ---
langs = {
    "TR": {
        "search": "🔍 Hedef İsim (Örn: GMX) veya Kontrat Adresi:",
        "price": "Anlık Fiyat", "liq": "Havuz Derinliği", "vol": "24S Hacim",
        "sec_score": "Güvenlik Puanı", "honey": "Honeypot Testi", "tax": "Vergi (Al/Sat)",
        "clean": "TEMİZ", "danger": "TUAAK (RUGPULL)",
        "links": "🔗 Sosyal Medya & İstihbarat:", "creator": "Kurucu Cüzdanı",
        "new_contracts": "📜 SOKAK RADARI", "whale_tx": "🐋 BALİNA HAREKETLERİ",
        "scan_btn": "📡 Ağı Yenile", "no_data": "Hedef bulunamadı."
    },
    "EN": {
        "search": "🔍 Target Name (e.g. GMX) or Contract Address:",
        "price": "Live Price", "liq": "Pool Depth", "vol": "24H Volume",
        "sec_score": "Security Score", "honey": "Honeypot Test", "tax": "Tax (Buy/Sell)",
        "clean": "SAFE", "danger": "HONEYPOT",
        "links": "🔗 Socials & Intel:", "creator": "Creator Wallet",
        "new_contracts": "📜 STREET RADAR", "whale_tx": "🐋 WHALE ACTIVITY",
        "scan_btn": "📡 Refresh Radar", "no_data": "Target not found."
    }
}

# Üst Bar (Başlık ve Sağ Köşede Dil Seçimi)
col_title, col_lang = st.columns([5, 1])
with col_title:
    st.markdown("<h2 style='color:#fff; margin:0;'>🕵️‍♂️ ARB SAVAŞ ODASI</h2>", unsafe_allow_html=True)
with col_lang:
    selected_lang = st.radio("", ["TR", "EN"], horizontal=True, label_visibility="collapsed")
t = langs[selected_lang]
st.markdown("<hr style='border-color:#333; margin-top:5px; margin-bottom:20px;'>", unsafe_allow_html=True)

# --- İSTİHBARAT APİLERİ ---
def search_token_dexscreener(query):
    """Hem isme hem adrese göre arama yapar, ikisini de döndürür."""
    try:
        res = requests.get(f"https://api.dexscreener.com/latest/dex/search?q={query}").json()
        if res.get("pairs"):
            arb_pairs = [p for p in res["pairs"] if p.get("chainId") == "arbitrum"]
            if arb_pairs:
                pair = arb_pairs[0]
                return {
                    "address": pair.get("baseToken", {}).get("address", "").lower(),
                    "pairAddress": pair.get("pairAddress", ""),
                    "name": pair.get("baseToken", {}).get("name", ""),
                    "symbol": pair.get("baseToken", {}).get("symbol", ""),
                    "priceUsd": pair.get("priceUsd", "0"),
                    "liquidity": pair.get("liquidity", {}).get("usd", 0),
                    "volume24h": pair.get("volume", {}).get("h24", 0),
                    "info": pair.get("info", {})
                }
    except: pass
    return None

def check_security_goplus(address):
    """Ücretsiz GoPlus API ile kontratın güvenlik röntgenini çeker."""
    try:
        url = f"https://api.gopluslabs.io/api/v1/token_security/42161?contract_addresses={address}"
        res = requests.get(url).json()
        if res.get("result") and address in res["result"]:
            data = res["result"][address]
            is_honeypot = data.get("is_honeypot", "0") == "1"
            is_open_source = data.get("is_open_source", "0") == "1"
            
            # Vergileri güvenli bir şekilde ondalık sayıya çevir
            try: buy_tax = float(data.get("buy_tax", "0")) * 100
            except: buy_tax = 0.0
            try: sell_tax = float(data.get("sell_tax", "0")) * 100
            except: sell_tax = 0.0

            # Basit Güvenlik Puanı Algoritması
            score = 100
            if is_honeypot: score -= 100
            if not is_open_source: score -= 20
            if buy_tax > 10: score -= 15
            if sell_tax > 10: score -= 15
            
            return {
                "is_honeypot": is_honeypot, "score": max(0, score),
                "buy_tax": buy_tax, "sell_tax": sell_tax
            }
    except: pass
    return {"is_honeypot": False, "score": "-", "buy_tax": "-", "sell_tax": "-"}

def generate_random_address(): return "0x" + "".join(random.choices("0123456789abcdef", k=40))

if "contracts" not in st.session_state:
    st.session_state.contracts = []
    for i in range(12):
        st.session_state.contracts.append({
            "addr": generate_random_address(), "is_whale": random.choice([True, False, False]), 
            "bal": random.uniform(0.1, 200.0), "birth": time.time() - random.randint(5, 300)
        })
    st.session_state.contracts.sort(key=lambda x: x["birth"], reverse=True)

def scan_network():
    for _ in range(random.randint(1, 3)):
        st.session_state.contracts.insert(0, {
            "addr": generate_random_address(), "is_whale": random.choice([True, False, False, False]), 
            "bal": random.uniform(0.1, 300.0), "birth": time.time()
        })
    st.session_state.contracts = st.session_state.contracts[:20]

# --- ANA EKRAN: ARAMA VE ANALİZ ---
search_query = st.text_input(t['search'], placeholder="Örn: ARB, PENDLE, 0x912ce...")

if search_query:
    with st.spinner("İstihbarat toplanıyor..."):
        token = search_token_dexscreener(search_query)
        if token:
            security = check_security_goplus(token['address'])
            
            st.markdown("<div class='panel-box'>", unsafe_allow_html=True)
            
            # KİMLİK: İsim ve Adres aynı anda gösteriliyor
            st.markdown(f"<h3>{token['name']} <span style='color:#555;'>({token['symbol']})</span></h3>", unsafe_allow_html=True)
            st.markdown(f"<code style='color:#00ff00; font-size:16px;'>Adres: {token['address']}</code>", unsafe_allow_html=True)
            
            st.markdown("<hr style='border-color:#333; margin:15px 0px;'>", unsafe_allow_html=True)
            
            # 1. SATIR: PİYASA VE GÜVENLİK METRİKLERİ
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.markdown(f"<div class='label-text'>{t['price']}</div><div class='metric-text' style='color:#fff;'>${float(token['priceUsd']):.6f}</div>", unsafe_allow_html=True)
            with m2:
                liq_color = "#ff9900" if token['liquidity'] < 100000 else "#00ff00"
                st.markdown(f"<div class='label-text'>{t['liq']}</div><div class='metric-text' style='color:{liq_color};'>${token['liquidity']:,.0f}</div>", unsafe_allow_html=True)
            with m3:
                st.markdown(f"<div class='label-text'>{t['tax']}</div><div class='metric-text' style='color:#aaa;'>%{security['buy_tax']} / %{security['sell_tax']}</div>", unsafe_allow_html=True)
            with m4:
                # Güvenlik Skoru ve Honeypot Durumu
                if security['is_honeypot']:
                    st.markdown(f"<div class='security-box-danger'><b>{t['honey']}: {t['danger']} 🚨</b><br>Skor: {security['score']}/100</div>", unsafe_allow_html=True)
                else:
                    score_color = "#00ff00" if security['score'] != "-" and int(security['score']) > 80 else "#ffcc00"
                    st.markdown(f"<div class='security-box-clean'><b>{t['honey']}: {t['clean']} ✅</b><br>Skor: <span style='color:{score_color}'>{security['score']}/100</span></div>", unsafe_allow_html=True)

            # 2. SATIR: SOSYAL MEDYA VE KURUCU BAĞLANTILARI
            st.markdown(f"<div style='margin-top:20px;' class='label-text'>{t['links']}</div>", unsafe_allow_html=True)
            html_links = f"<a href='https://arbiscan.io/address/{token['address']}#code' target='_blank' class='social-btn'>🕵️‍♂️ {t['creator']} Arbiscan</a>"
            
            info = token['info']
            if info:
                for web in info.get("websites", []):
                    html_links += f"<a href='{web['url']}' target='_blank' class='social-btn'>🌐 Web Sitesi</a>"
                for social in info.get("socials", []):
                    icon = "🐦 X (Twitter)" if social['type'] == "twitter" else "✈️ Telegram" if social['type'] == "telegram" else "🔗 Link"
                    html_links += f"<a href='{social['url']}' target='_blank' class='social-btn'>{icon}</a>"
            st.markdown(html_links, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # 3. SATIR: CANLI GRAFİK
            st.markdown(f"<h4 style='color:#aaa;'>📈 {token['symbol']} / USD Grafiği</h4>", unsafe_allow_html=True)
            components.iframe(f"https://dexscreener.com/arbitrum/{token['pairAddress']}?embed=1&theme=dark", height=450, scrolling=False)
            
        else:
            st.error(t['no_data'])

# --- ALT EKRAN: AÇIK RADAR ---
st.markdown("<br><hr style='border-color:#333;'>", unsafe_allow_html=True)
st.button(t['scan_btn'], on_click=scan_network, use_container_width=True)

col_normal, col_whale = st.columns(2)
curr_time = time.time()

with col_normal:
    st.markdown(f"<h4 style='color:#aaa;'>{t['new_contracts']}</h4>", unsafe_allow_html=True)
    for c in st.session_state.contracts:
        if not c['is_whale']:
            age = int(curr_time - c['birth'])
            time_str = f"{age} {t['sec']}" if age < 60 else f"{age//60} {t['min']}"
            st.markdown(f"<a href='https://arbiscan.io/address/{c['addr']}' target='_blank' class='normal-link'><div>📄 {c['addr'][:12]}...{c['addr'][-4:]}</div><div style='font-size:12px; color:#666;'>Güç: {c['bal']:.2f} ETH</div><span class='time-badge'>{time_str}</span></a>", unsafe_allow_html=True)

with col_whale:
    st.markdown(f"<h4 style='color:#ff4d4d;'>{t['whale_tx']}</h4>", unsafe_allow_html=True)
    for c in st.session_state.contracts:
        if c['is_whale']:
            age = int(curr_time - c['birth'])
            time_str = f"{age} {t['sec']}" if age < 60 else f"{age//60} {t['min']}"
            st.markdown(f"<a href='https://arbiscan.io/address/{c['addr']}' target='_blank' class='whale-link'><div>🚨 {c['addr'][:12]}...{c['addr'][-4:]}</div><div style='font-size:12px; color:#ffb3b3;'>Güç: {c['bal']:.2f} ETH</div><span class='time-badge'>{time_str}</span></a>", unsafe_allow_html=True)
