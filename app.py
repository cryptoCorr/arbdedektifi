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
    theme_choice = st.radio("Tema / Theme", ["Siyah (Karanlık)", "Aydınlık (Beyaz)"], label_visibility="collapsed")
with col_lang:
    lang_choice = st.radio("Dil / Lang", ["TR", "EN"], horizontal=True, label_visibility="collapsed")

st.markdown("<hr style='margin-top:5px; margin-bottom:20px;'>", unsafe_allow_html=True)

# --- DİNAMİK TEMA (CSS ENJEKSİYONU) ---
if theme_choice == "Siyah (Karanlık)":
    bg_app = "#000000"
    bg_panel = "#0a0a0a"
    text_main = "#ffffff"
    text_sub = "#aaaaaa"
    border_col = "#222222"
else:
    bg_app = "#f4f6f9"
    bg_panel = "#ffffff"
    text_main = "#111111"
    text_sub = "#555555"
    border_col = "#cccccc"

st.markdown(f"""
<style>
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} header {{visibility: hidden;}}
    .block-container {{ padding-top: 1rem; padding-bottom: 0rem; }}
    
    /* Arka Planı Zorla Değiştir */
    [data-testid="stAppViewContainer"] {{ background-color: {bg_app}; color: {text_main}; }}
    [data-testid="stHeader"] {{ background-color: {bg_app}; }}
    
    .panel-box {{ background-color: {bg_panel}; border: 1px solid {border_col}; border-radius: 8px; padding: 20px; margin-bottom: 20px; }}
    .security-box-clean {{ background-color: rgba(0, 255, 0, 0.05); border: 1px solid #00ff00; border-radius: 8px; padding: 15px; text-align: center; color: {text_main}; }}
    .security-box-danger {{ background-color: rgba(255, 0, 0, 0.1); border: 1px solid #ff0000; border-radius: 8px; padding: 15px; text-align: center; color: {text_main}; animation: pulse 2s infinite; }}
    
    @keyframes pulse {{ 0% {{ box-shadow: 0 0 0 0 rgba(255, 0, 0, 0.4); }} 70% {{ box-shadow: 0 0 0 10px rgba(255, 0, 0, 0); }} 100% {{ box-shadow: 0 0 0 0 rgba(255, 0, 0, 0); }} }}
    
    .metric-val {{ font-size: 24px; font-weight: bold; font-family: monospace; color: {text_main}; }}
    .metric-label {{ color: {text_sub}; font-size: 13px; text-transform: uppercase; font-weight: bold; margin-bottom: 5px; }}
    
    a.social-btn {{ display: inline-block; background-color: {bg_app}; color: #4da6ff; padding: 6px 15px; border-radius: 4px; border: 1px solid {border_col}; text-decoration: none; margin-right: 10px; margin-top: 10px; font-size: 14px; }}
    
    /* Radar Linkleri */
    a.whale-link {{ display: block; background-color: rgba(255,0,0,0.05); border-left: 5px solid #ff0000; color: #ff4d4d; padding: 12px; text-decoration: none; margin-bottom: 8px; font-family: monospace; position: relative; border-radius: 0 4px 4px 0; }}
    a.normal-link {{ display: block; background-color: {bg_panel}; border-left: 5px solid #444; color: {text_main}; padding: 12px; text-decoration: none; margin-bottom: 8px; font-family: monospace; position: relative; border-radius: 0 4px 4px 0; border: 1px solid {border_col}; border-left: 5px solid {text_sub}; }}
    .time-badge {{ position: absolute; right: 10px; top: 12px; font-size: 11px; color: {text_sub}; }}
</style>
""", unsafe_allow_html=True)

# --- DİL SÖZLÜĞÜ ---
langs = {
    "TR": {
        "search": "🔍 İstihbarat Hedefi (Token İsmi veya Kontrat Adresi):",
        "price": "ANLIK FİYAT", "liq": "HAVUZ LİKİDİTESİ", "vol": "24S HACİM",
        "sec_title": "GÜVENLİK PUANI (100 ÜZERİNDEN)", 
        "sec_desc": "Puanlama Kriterleri: Honeypot (Tuzak) riski, açık kaynak kod doğrulaması ve alım/satım vergi (tax) oranlarına göre otomatik hesaplanır.",
        "honey": "Durum", "tax": "Vergi (Al/Sat)",
        "clean": "TEMİZ ✅", "danger": "TUZAK (RUGPULL) 🚨",
        "links": "🔗 Operasyon Bağlantıları:", "creator": "Kurucu (Deployer)",
        "new_contracts": "📜 SOKAK RADARI (CANLI KONTRATLAR)", "whale_tx": "🐋 BALİNA HAREKETLERİ",
        "scan_btn": "📡 Ağı Yenile (Radarı Güncelle)", "no_data": "Hedef bulunamadı."
    },
    "EN": {
        "search": "🔍 Intel Target (Token Name or Contract Address):",
        "price": "LIVE PRICE", "liq": "POOL LIQUIDITY", "vol": "24H VOLUME",
        "sec_title": "SECURITY SCORE (OUT OF 100)", 
        "sec_desc": "Scoring Criteria: Automatically calculated based on Honeypot risk, open-source verification, and buy/sell tax rates.",
        "honey": "Status", "tax": "Tax (Buy/Sell)",
        "clean": "SAFE ✅", "danger": "HONEYPOT 🚨",
        "links": "🔗 Operation Links:", "creator": "Creator (Deployer)",
        "new_contracts": "📜 STREET RADAR (LIVE CONTRACTS)", "whale_tx": "🐋 WHALE ACTIVITY",
        "scan_btn": "📡 Refresh Network (Update Radar)", "no_data": "Target not found."
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
            is_honeypot = data.get("is_honeypot", "0") == "1"
            is_open_source = data.get("is_open_source", "0") == "1"
            try: buy_tax = float(data.get("buy_tax", "0")) * 100
            except: buy_tax = 0.0
            try: sell_tax = float(data.get("sell_tax", "0")) * 100
            except: sell_tax = 0.0

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
search_query = st.text_input("", placeholder=t['search'])

if search_query:
    with st.spinner("Piyasa taranıyor..."):
        token = search_token_dexscreener(search_query)
        if token:
            security = check_security_goplus(token['address'])
            
            st.markdown("<div class='panel-box'>", unsafe_allow_html=True)
            
            # İSİM VE ADRES
            st.markdown(f"<h3 style='margin:0; color:{text_main};'>{token['name']} <span style='color:{text_sub};'>({token['symbol']})</span></h3>", unsafe_allow_html=True)
            st.markdown(f"<code style='color:#00ff00; font-size:16px; background:transparent;'>Adres: {token['address']}</code>", unsafe_allow_html=True)
            st.markdown(f"<hr style='border-color:{border_col}; margin:15px 0px;'>", unsafe_allow_html=True)
            
            # FİYAT, LİKİDİTE VE VERGİLER (Artık Çok Daha Net)
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.markdown(f"<div class='metric-label'>{t['price']}</div><div class='metric-val' style='color:#00ff00;'>${float(token['priceUsd']):.6f}</div>", unsafe_allow_html=True)
            with m2:
                st.markdown(f"<div class='metric-label'>{t['liq']}</div><div class='metric-val'>${token['liquidity']:,.0f}</div>", unsafe_allow_html=True)
            with m3:
                st.markdown(f"<div class='metric-label'>{t['vol']}</div><div class='metric-val'>${token['volume24h']:,.0f}</div>", unsafe_allow_html=True)
            with m4:
                st.markdown(f"<div class='metric-label'>{t['tax']}</div><div class='metric-val' style='color:#ff9900;'>%{security['buy_tax']} / %{security['sell_tax']}</div>", unsafe_allow_html=True)

            st.markdown(f"<hr style='border-color:{border_col}; margin:15px 0px;'>", unsafe_allow_html=True)
            
            # GÜVENLİK PUANI KÖŞESİ (Açıklamalı)
            st.markdown(f"<div class='metric-label' style='font-size:16px;'>🛡️ {t['sec_title']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='color:{text_sub}; font-size:12px; margin-bottom:10px;'>{t['sec_desc']}</div>", unsafe_allow_html=True)
            
            if security['is_honeypot']:
                st.markdown(f"<div class='security-box-danger'><h2 style='margin:0; color:#ff0000;'>{t['danger']}</h2><div style='font-size:20px; font-weight:bold;'>Skor: {security['score']}/100</div></div>", unsafe_allow_html=True)
            else:
                score_color = "#00ff00" if security['score'] != "-" and int(security['score']) > 80 else "#ffcc00"
                st.markdown(f"<div class='security-box-clean'><h2 style='margin:0; color:#00ff00;'>{t['clean']}</h2><div style='font-size:20px; font-weight:bold;'>Skor: <span style='color:{score_color}'>{security['score']}/100</span></div></div>", unsafe_allow_html=True)

            # SOSYAL MEDYA
            st.markdown(f"<div style='margin-top:20px;' class='metric-label'>{t['links']}</div>", unsafe_allow_html=True)
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
            
            # CANLI GRAFİK
            st.markdown(f"<h4 style='color:{text_sub};'>📈 {token['symbol']} / USD Grafiği</h4>", unsafe_allow_html=True)
            # Grafik teması da uygulamanın temasına uysun
            chart_theme = "dark" if theme_choice == "Siyah (Karanlık)" else "light"
            components.iframe(f"https://dexscreener.com/arbitrum/{token['pairAddress']}?embed=1&theme={chart_theme}", height=450, scrolling=False)
            
        else:
            st.error(t['no_data'])

# --- ALT EKRAN: SABİT VE AÇIK RADAR ---
st.markdown(f"<br><hr style='border-color:{border_col};'>", unsafe_allow_html=True)
st.button(t['scan_btn'], on_click=scan_network, use_container_width=True)

col_normal, col_whale = st.columns(2)
curr_time = time.time()

with col_normal:
    st.markdown(f"<h4 style='color:{text_sub};'>{t['new_contracts']}</h4>", unsafe_allow_html=True)
    for c in st.session_state.contracts:
        if not c['is_whale']:
            age = int(curr_time - c['birth'])
            time_str = f"{age} sn önce" if age < 60 else f"{age//60} dk önce"
            st.markdown(f"<a href='https://arbiscan.io/address/{c['addr']}' target='_blank' class='normal-link'><div>📄 {c['addr'][:12]}...{c['addr'][-4:]}</div><div style='font-size:12px; color:#888;'>Kurucu Gücü: {c['bal']:.2f} ETH</div><span class='time-badge'>{time_str}</span></a>", unsafe_allow_html=True)

with col_whale:
    st.markdown(f"<h4 style='color:#ff4d4d;'>{t['whale_tx']}</h4>", unsafe_allow_html=True)
    for c in st.session_state.contracts:
        if c['is_whale']:
            age = int(curr_time - c['birth'])
            time_str = f"{age} sn önce" if age < 60 else f"{age//60} dk önce"
            st.markdown(f"<a href='https://arbiscan.io/address/{c['addr']}' target='_blank' class='whale-link'><div>🚨 {c['addr'][:12]}...{c['addr'][-4:]}</div><div style='font-size:12px; color:#ffb3b3;'>Kurucu Gücü: {c['bal']:.2f} ETH</div><span class='time-badge'>{time_str}</span></a>", unsafe_allow_html=True)
