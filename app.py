import streamlit as st
import streamlit.components.v1 as components
import requests
import time
import random

# --- AYARLAR ---
st.set_page_config(page_title="Arbitrum İstihbarat", layout="wide", initial_sidebar_state="collapsed")

# --- ÜST BAR: DİL VE TEMA SEÇİMİ ---
col_title, col_theme, col_lang = st.columns([4, 1, 1])
with col_title:
    st.markdown("<h2 style='margin:0;'>🕵️‍♂️ ARB SAVAŞ ODASI</h2>", unsafe_allow_html=True)
with col_theme:
    theme_choice = st.radio("Tema", ["Karanlık (Göz Yormayan)", "Aydınlık (Beyaz)"], label_visibility="collapsed")
with col_lang:
    lang_choice = st.radio("Dil", ["TR", "EN"], horizontal=True, label_visibility="collapsed")

st.markdown("<hr style='margin-top:5px; margin-bottom:15px; border-color:#333;'>", unsafe_allow_html=True)

# --- DİNAMİK TEMA VE MOBİL UYUM (CSS) ---
if theme_choice == "Karanlık (Göz Yormayan)":
    bg_app = "#121212"    # Göz yormayan yumuşak karanlık
    bg_panel = "#1e1e1e"  # Hafif açık panel rengi
    text_main = "#e0e0e0"
    text_sub = "#999999"
    border_col = "#2a2a2a"
else:
    bg_app = "#f8f9fa"
    bg_panel = "#ffffff"
    text_main = "#111111"
    text_sub = "#555555"
    border_col = "#dddddd"

st.markdown(f"""
<style>
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} header {{visibility: hidden;}}
    .block-container {{ padding-top: 1rem; padding-bottom: 1rem; max-width: 1200px; }}
    
    /* Arka Planı Zorla Değiştir */
    [data-testid="stAppViewContainer"] {{ background-color: {bg_app}; color: {text_main}; }}
    [data-testid="stHeader"] {{ background-color: {bg_app}; }}
    
    .panel-box {{ background-color: {bg_panel}; border: 1px solid {border_col}; border-radius: 8px; padding: 15px; margin-bottom: 20px; word-wrap: break-word; }}
    
    .security-box-clean {{ background-color: rgba(0, 255, 0, 0.05); border: 1px solid #00aa00; border-radius: 6px; padding: 12px; text-align: center; color: {text_main}; }}
    .security-box-danger {{ background-color: rgba(255, 0, 0, 0.1); border: 1px solid #cc0000; border-radius: 6px; padding: 12px; text-align: center; color: {text_main}; animation: pulse 2s infinite; }}
    
    @keyframes pulse {{ 0% {{ box-shadow: 0 0 0 0 rgba(255, 0, 0, 0.3); }} 70% {{ box-shadow: 0 0 0 8px rgba(255, 0, 0, 0); }} 100% {{ box-shadow: 0 0 0 0 rgba(255, 0, 0, 0); }} }}
    
    .metric-val {{ font-size: 20px; font-weight: bold; font-family: monospace; color: {text_main}; }}
    .metric-label {{ color: {text_sub}; font-size: 12px; text-transform: uppercase; font-weight: bold; margin-bottom: 3px; }}
    
    /* Sosyal Medya Butonları - Token Altı İçin */
    .social-container {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; margin-bottom: 15px; }}
    a.social-btn {{ background-color: {bg_app}; color: #4da6ff; padding: 6px 12px; border-radius: 4px; border: 1px solid {border_col}; text-decoration: none; font-size: 13px; display: inline-flex; align-items: center; transition: 0.2s; }}
    a.social-btn:hover {{ background-color: #2a2a2a; color: #fff; }}
    
    /* Sade Radar Linkleri */
    a.radar-link {{ display: block; background-color: {bg_panel}; border: 1px solid {border_col}; color: {text_main}; padding: 12px; text-decoration: none; margin-bottom: 6px; border-radius: 6px; transition: 0.2s; position: relative; word-wrap: break-word; }}
    a.radar-link:hover {{ border-color: #555; }}
    .radar-whale {{ border-left: 4px solid #ff4444 !important; }}
    .radar-normal {{ border-left: 4px solid #4da6ff !important; }}
    
    .radar-top {{ display: flex; justify-content: space-between; font-family: monospace; font-size: 14px; margin-bottom: 4px; }}
    .radar-bottom {{ font-size: 12px; color: {text_sub}; display: flex; justify-content: space-between; }}
    .tx-buy {{ color: #00cc00; font-weight: bold; }}
    .tx-sell {{ color: #ff4444; font-weight: bold; }}
    .tx-deploy {{ color: #aaaaaa; font-weight: bold; }}
</style>
""", unsafe_allow_html=True)

# --- DİL SÖZLÜĞÜ ---
langs = {
    "TR": {
        "search": "🔍 Hedef Ara (Token İsmi veya 0x... Adresi):",
        "price": "FİYAT", "liq": "LİKİDİTE", "vol": "24S HACİM", "tax": "VERGİ (AL/SAT)",
        "sec_title": "GÜVENLİK PUANI (100 ÜZERİNDEN)", 
        "sec_desc": "Kriterler: Honeypot (Tuzak) riski, açık kaynak kod ve vergi (tax) oranları.",
        "honey": "Durum", "clean": "TEMİZ ✅", "danger": "TUZAK 🚨",
        "creator": "Kurucu Cüzdan", "web": "Web Sitesi",
        "radar_title": "📡 SOKAK RADARI (Alış, Satış ve Yeni Kontratlar)",
        "scan_btn": "🔄 Radarı Güncelle", "no_data": "Hedef bulunamadı."
    },
    "EN": {
        "search": "🔍 Search Target (Token Name or 0x... Address):",
        "price": "PRICE", "liq": "LIQUIDITY", "vol": "24H VOL", "tax": "TAX (B/S)",
        "sec_title": "SECURITY SCORE (OUT OF 100)", 
        "sec_desc": "Criteria: Honeypot risk, open-source code, and tax rates.",
        "honey": "Status", "clean": "SAFE ✅", "danger": "HONEYPOT 🚨",
        "creator": "Deployer", "web": "Website",
        "radar_title": "📡 STREET RADAR (Buys, Sells & Deploys)",
        "scan_btn": "🔄 Refresh Radar", "no_data": "Target not found."
    }
}
t = langs[lang_choice]

# --- İSTİHBARAT APİLERİ ---
def search_token_dexscreener(query):
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
    try:
        url = f"https://api.gopluslabs.io/api/v1/token_security/42161?contract_addresses={address}"
        res = requests.get(url).json()
        if res.get("result") and address in res["result"]:
            data = res["result"][address]
            is_honey = data.get("is_honeypot", "0") == "1"
            is_open = data.get("is_open_source", "0") == "1"
            try: b_tax = float(data.get("buy_tax", "0")) * 100
            except: b_tax = 0.0
            try: s_tax = float(data.get("sell_tax", "0")) * 100
            except: s_tax = 0.0

            score = 100
            if is_honey: score -= 100
            if not is_open: score -= 20
            if b_tax > 10: score -= 15
            if s_tax > 10: score -= 15
            
            return {"is_honeypot": is_honey, "score": max(0, score), "buy_tax": b_tax, "sell_tax": s_tax}
    except: pass
    return {"is_honeypot": False, "score": "-", "buy_tax": "-", "sell_tax": "-"}

# --- RADAR SİMÜLASYONU (ALIŞ, SATIŞ, YENİ KONTRAT) ---
tx_types = ["YENİ KONTRAT", "ALIŞ (BUY)", "SATIŞ (SELL)"]

def generate_tx():
    is_whale = random.choice([True, False, False])
    tx_type = random.choice(tx_types)
    addr = "0x" + "".join(random.choices("0123456789abcdef", k=40))
    bal = random.uniform(50.0, 500.0) if is_whale else random.uniform(0.1, 15.0)
    return {"addr": addr, "is_whale": is_whale, "type": tx_type, "bal": bal, "time": time.time()}

if "radar_txs" not in st.session_state:
    st.session_state.radar_txs = [generate_tx() for _ in range(10)]
    for tx in st.session_state.radar_txs:
        tx["time"] -= random.randint(5, 120)
    st.session_state.radar_txs.sort(key=lambda x: x["time"], reverse=True)

def update_radar():
    for _ in range(random.randint(1, 3)):
        st.session_state.radar_txs.insert(0, generate_tx())
    st.session_state.radar_txs = st.session_state.radar_txs[:15]

# --- ANA EKRAN: ARAMA VE ANALİZ ---
search_query = st.text_input("", placeholder=t['search'])

if search_query:
    with st.spinner("İstihbarat toplanıyor..."):
        token = search_token_dexscreener(search_query)
        if token:
            security = check_security_goplus(token['address'])
            
            st.markdown("<div class='panel-box'>", unsafe_allow_html=True)
            
            # KİMLİK BİLGİLERİ
            st.markdown(f"<h3 style='margin:0; color:{text_main};'>{token['name']} <span style='color:{text_sub};'>({token['symbol']})</span></h3>", unsafe_allow_html=True)
            st.markdown(f"<div style='color:#00cc00; font-family:monospace; font-size:14px; margin-top:5px; word-wrap:break-word;'>Adres: {token['address']}</div>", unsafe_allow_html=True)
            
            # X (TWITTER) VE DİĞER SOSYAL BAĞLANTILAR TAM BURADA
            html_links = f"<div class='social-container'>"
            html_links += f"<a href='https://arbiscan.io/address/{token['address']}#code' target='_blank' class='social-btn'>🕵️‍♂️ {t['creator']}</a>"
            
            info = token['info']
            if info:
                for web in info.get("websites", []):
                    html_links += f"<a href='{web['url']}' target='_blank' class='social-btn'>🌐 {t['web']}</a>"
                for social in info.get("socials", []):
                    icon = "🐦 X (Twitter)" if social['type'] == "twitter" else "✈️ Telegram" if social['type'] == "telegram" else "🔗 Link"
                    html_links += f"<a href='{social['url']}' target='_blank' class='social-btn'>{icon}</a>"
            html_links += "</div>"
            st.markdown(html_links, unsafe_allow_html=True)
            
            st.markdown(f"<hr style='border-color:{border_col}; margin:10px 0px 15px 0px;'>", unsafe_allow_html=True)
            
            # METRİKLER (Mobil için otomatik alt alta geçer)
            m1, m2, m3, m4 = st.columns(4)
            with m1: st.markdown(f"<div class='metric-label'>{t['price']}</div><div class='metric-val' style='color:#00cc00;'>${float(token['priceUsd']):.6f}</div>", unsafe_allow_html=True)
            with m2: st.markdown(f"<div class='metric-label'>{t['liq']}</div><div class='metric-val'>${token['liquidity']:,.0f}</div>", unsafe_allow_html=True)
            with m3: st.markdown(f"<div class='metric-label'>{t['vol']}</div><div class='metric-val'>${token['volume24h']:,.0f}</div>", unsafe_allow_html=True)
            with m4: st.markdown(f"<div class='metric-label'>{t['tax']}</div><div class='metric-val' style='color:#ffaa00;'>%{security['buy_tax']} / %{security['sell_tax']}</div>", unsafe_allow_html=True)

            st.markdown(f"<hr style='border-color:{border_col}; margin:15px 0px;'>", unsafe_allow_html=True)
            
            # GÜVENLİK PUANI (Açıklamalı)
            st.markdown(f"<div class='metric-label' style='font-size:14px;'>🛡️ {t['sec_title']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='color:{text_sub}; font-size:11px; margin-bottom:10px;'>{t['sec_desc']}</div>", unsafe_allow_html=True)
            
            if security['is_honeypot']:
                st.markdown(f"<div class='security-box-danger'><h3 style='margin:0; color:#ff3333;'>{t['danger']}</h3><div style='font-size:18px; font-weight:bold;'>Skor: {security['score']}/100</div></div>", unsafe_allow_html=True)
            else:
                score_color = "#00cc00" if security['score'] != "-" and int(security['score']) > 80 else "#ffcc00"
                st.markdown(f"<div class='security-box-clean'><h3 style='margin:0; color:#00cc00;'>{t['clean']}</h3><div style='font-size:18px; font-weight:bold;'>Skor: <span style='color:{score_color}'>{security['score']}/100</span></div></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # CANLI GRAFİK
            chart_theme = "dark" if theme_choice == "Karanlık (Göz Yormayan)" else "light"
            components.iframe(f"https://dexscreener.com/arbitrum/{token['pairAddress']}?embed=1&theme={chart_theme}", height=400, scrolling=False)
            
        else:
            st.error(t['no_data'])

# --- ALT EKRAN: SADE VE MOBİL UYUMLU RADAR ---
st.markdown(f"<br><h4 style='color:{text_main}; margin-bottom:10px;'>{t['radar_title']}</h4>", unsafe_allow_html=True)
st.button(t['scan_btn'], on_click=update_radar, use_container_width=True)

curr_time = time.time()

# Mobil uyumluluk için tek sütun veya iki sütun ayarı (Streamlit bunu mobilde otomatik alt alta dizer)
r1, r2 = st.columns(2)

for i, tx in enumerate(st.session_state.radar_txs):
    age = int(curr_time - tx['time'])
    time_str = f"{age} sn önce" if age < 60 else f"{age//60} dk önce"
    
    # Renk ve İkon Sınıflandırması
    radar_class = "radar-whale" if tx['is_whale'] else "radar-normal"
    whale_icon = "🚨 BALİNA" if tx['is_whale'] else "👤 Standart"
    
    tx_color_class = "tx-buy" if "BUY" in tx['type'] or "ALIŞ" in tx['type'] else "tx-sell" if "SELL" in tx['type'] or "SATIŞ" in tx['type'] else "tx-deploy"
    
    card_html = f"""
    <a href='https://arbiscan.io/address/{tx['addr']}' target='_blank' class='radar-link {radar_class}'>
        <div class='radar-top'>
            <span style='color:{"#ff4444" if tx['is_whale'] else text_main};'>{tx['addr'][:8]}...{tx['addr'][-6:]}</span>
            <span>{time_str}</span>
        </div>
        <div class='radar-bottom'>
            <span class='{tx_color_class}'>[{tx['type']}] {whale_icon}</span>
            <span>Hacim: {tx['bal']:.1f} ETH</span>
        </div>
    </a>
    """
    
    # Sırayla sağ ve sol sütunlara dağıt
    if i % 2 == 0:
        r1.markdown(card_html, unsafe_allow_html=True)
    else:
        r2.markdown(card_html, unsafe_allow_html=True)
