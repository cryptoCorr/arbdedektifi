import streamlit as st
import streamlit.components.v1 as components
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
    a.whale-link, a.normal-link {
        display: block; padding: 12px; text-decoration: none; margin-bottom: 8px;
        font-family: monospace; border-radius: 0 4px 4px 0; transition: 0.3s; position: relative;
    }
    a.whale-link { background-color: #1f0303; border-left: 5px solid #ff0000; color: #ff4d4d; }
    a.whale-link:hover { background-color: #3b0707; color: #ff8080; }
    
    a.normal-link { background-color: #121212; border-left: 5px solid #444; color: #aaa; }
    a.normal-link:hover { background-color: #1e1e1e; color: #fff; }
    
    .time-badge { position: absolute; right: 10px; top: 12px; font-size: 11px; color: #777; }
    
    /* Sosyal Medya Butonları */
    a.social-btn {
        display: inline-block; background-color: #1a1a1a; color: #4da6ff;
        padding: 6px 15px; border-radius: 4px; border: 1px solid #333;
        text-decoration: none; margin-right: 10px; margin-top: 10px; font-size: 14px;
    }
    a.social-btn:hover { background-color: #2a2a2a; color: #fff; }
</style>
""", unsafe_allow_html=True)

# --- DİLLER ---
langs = {
    "TR": {
        "menu": "KOMUTA MERKEZİ", "search_label": "Hedef Token veya Adres:",
        "price": "Anlık Fiyat", "liq": "Havuz Derinliği", "vol": "24S Hacim",
        "latest_whale": "🚨 EN SON BALİNA TESPİTİ", "new_contracts": "📜 SOKAK RADARI",
        "whale_tx": "🐋 BALİNA HAREKETLERİ", "scan_btn": "📡 Sokağı Dinle (Ağı Yenile)",
        "links": "İstihbarat Bağlantıları:", "creator": "Kurucu (Deployer) Cüzdanı",
        "no_data": "İstihbarat bulunamadı.", "sec": "sn önce", "min": "dk önce"
    },
    "EN": {
        "menu": "COMMAND CENTER", "search_label": "Target Token or Address:",
        "price": "Live Price", "liq": "Pool Depth", "vol": "24H Volume",
        "latest_whale": "🚨 LATEST WHALE DETECTED", "new_contracts": "📜 STREET RADAR",
        "whale_tx": "🐋 WHALE ACTIVITY", "scan_btn": "📡 Listen to Streets",
        "links": "Intel Links:", "creator": "Creator (Deployer) Wallet",
        "no_data": "No intel found.", "sec": "sec ago", "min": "min ago"
    }
}

with st.sidebar:
    st.markdown("### 🌐 Dil / Language")
    selected_lang = st.radio("", ["TR", "EN"], horizontal=True, label_visibility="collapsed")
    t = langs[selected_lang]
    st.markdown("---")
    st.markdown(f"### 🎛️ {t['menu']}")
    st.markdown("- 🔍 Hedef Analizi\n- 📈 Canlı Grafik\n- 📜 Sokak Radarı\n- 🐋 Balina Takibi")

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
                    "pairAddress": pair.get("pairAddress", ""), # Grafik için havuz adresi
                    "name": pair.get("baseToken", {}).get("name", ""),
                    "symbol": pair.get("baseToken", {}).get("symbol", ""),
                    "priceUsd": pair.get("priceUsd", "0"),
                    "liquidity": pair.get("liquidity", {}).get("usd", 0),
                    "volume24h": pair.get("volume", {}).get("h24", 0),
                    "info": pair.get("info", {}) # Sosyal medya linkleri
                }
    except: pass
    return None

def format_time(seconds_ago, lang_dict):
    if seconds_ago < 60: return f"{int(seconds_ago)} {lang_dict['sec']}"
    else: return f"{int(seconds_ago // 60)} {lang_dict['min']}"

def generate_random_address(): return "0x" + "".join(random.choices("0123456789abcdef", k=40))

# --- HAFIZA VE SİMÜLASYON ---
if "contracts" not in st.session_state:
    st.session_state.contracts = []
    current_time = time.time()
    for i in range(15):
        is_whale = random.choice([True, False, False, False])
        bal = random.uniform(55.0, 300.0) if is_whale else random.uniform(0.1, 15.0)
        st.session_state.contracts.append({
            "addr": generate_random_address(), "is_whale": is_whale, 
            "bal": bal, "birth": current_time - random.randint(5, 600)
        })
    st.session_state.contracts.sort(key=lambda x: x["birth"], reverse=True)

def scan_network_for_contracts():
    new_count = random.randint(1, 3)
    for _ in range(new_count):
        is_whale = random.choice([True, False, False, False, False])
        bal = random.uniform(51.0, 500.0) if is_whale else random.uniform(0.01, 8.0)
        st.session_state.contracts.insert(0, {
            "addr": generate_random_address(), "is_whale": is_whale, 
            "bal": bal, "birth": time.time()
        })
    st.session_state.contracts = st.session_state.contracts[:25]

latest_whale = next((c for c in st.session_state.contracts if c["is_whale"]), None)

# --- 1. ANA EKRAN: TOKEN ARAMA VE GRAFİK ---
st.markdown(f"<h2>{t['search_label']}</h2>", unsafe_allow_html=True)
search_query = st.text_input("", placeholder="Örn: ARB, PENDLE, 0x...", label_visibility="collapsed")

if search_query:
    with st.spinner("İstihbarat toplanıyor..."):
        token_data = search_token_dexscreener(search_query)
        if token_data:
            st.markdown("<div class='panel-box'>", unsafe_allow_html=True)
            st.markdown(f"<h3>{token_data['name']} <span style='color:#555;'>({token_data['symbol']})</span></h3>", unsafe_allow_html=True)
            st.markdown(f"<code style='color:#888;'>{token_data['address']}</code>", unsafe_allow_html=True)
            
            # İstihbarat Bağlantıları (Sosyal Medya ve Kurucu)
            info = token_data['info']
            st.markdown(f"<div style='margin-top:15px; color:#888;'>{t['links']}</div>", unsafe_allow_html=True)
            html_links = f"<a href='https://arbiscan.io/token/{token_data['address']}' target='_blank' class='social-btn'>🕵️‍♂️ {t['creator']}</a>"
            
            if info:
                for web in info.get("websites", []):
                    html_links += f"<a href='{web['url']}' target='_blank' class='social-btn'>🌐 Web</a>"
                for social in info.get("socials", []):
                    icon = "🐦 X (Twitter)" if social['type'] == "twitter" else "✈️ Telegram" if social['type'] == "telegram" else "🔗 Link"
                    html_links += f"<a href='{social['url']}' target='_blank' class='social-btn'>{icon}</a>"
            st.markdown(html_links, unsafe_allow_html=True)
            
            st.markdown("<hr style='border-color:#333; margin:20px 0px;'>", unsafe_allow_html=True)
            
            # Metrikler
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
            
            # Canlı Grafik Entegrasyonu (DexScreener iframe)
            st.markdown(f"<h4 style='color:#aaa; margin-top:20px;'>📈 {token_data['symbol']} / USD Grafiği</h4>", unsafe_allow_html=True)
            chart_url = f"https://dexscreener.com/arbitrum/{token_data['pairAddress']}?embed=1&theme=dark"
            components.iframe(chart_url, height=500, scrolling=False)
            
        else:
            st.error(t['no_data'])

# --- 2. EN SON BALİNA ALARMI ---
st.markdown("<br>", unsafe_allow_html=True)
if latest_whale:
    st.markdown(f"""
    <div class='whale-box'>
        <h4 style='color:#ff4d4d; margin-top:0;'>{t['latest_whale']}</h4>
        <a href="https://arbiscan.io/address/{latest_whale['addr']}" target="_blank" style="color:#fff; text-decoration:underline; font-family:monospace; font-size:18px;">
            {latest_whale['addr']}
        </a>
        <div style="color:#aaa; margin-top:10px;">Güç: <span style="color:#ff4d4d; font-weight:bold;">{latest_whale['bal']:.2f} ETH</span></div>
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
            time_str = format_time(current_time - c['birth'], t)
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
            time_str = format_time(current_time - c['birth'], t)
            st.markdown(f"""
            <a href="https://arbiscan.io/address/{c['addr']}" target="_blank" class="whale-link">
                <div>🚨 {c['addr'][:12]}...{c['addr'][-4:]}</div>
                <div style="font-size:12px; color:#ffb3b3; margin-top:4px;">Güç: {c['bal']:.2f} ETH</div>
                <span class="time-badge">{time_str}</span>
            </a>
            """, unsafe_allow_html=True)
