import streamlit as st
import streamlit.components.v1 as components
import requests
import time
import random

# --- AYARLAR ---
st.set_page_config(page_title="ARB Terminal", layout="wide", initial_sidebar_state="collapsed")

# --- ÜST BAR: DİL VE TEMA SEÇİMİ ---
col_title, col_theme, col_lang = st.columns([4, 1, 1])
with col_title:
    st.markdown("<h3 style='margin:0; font-family:monospace; color:#ccc; letter-spacing: 2px;'>ARB INTELLIGENCE TERMINAL</h3>", unsafe_allow_html=True)
with col_theme:
    theme_choice = st.radio("Tema", ["Karanlık", "Aydınlık"], label_visibility="collapsed")
with col_lang:
    lang_choice = st.radio("Dil", ["TR", "EN"], horizontal=True, label_visibility="collapsed")

st.markdown("<hr style='margin-top:5px; margin-bottom:15px; border-color:#222;'>", unsafe_allow_html=True)

# --- DİNAMİK TEMA (CSS) ---
if theme_choice == "Karanlık":
    bg_app, bg_panel, text_main, text_sub, border_col = "#0a0a0a", "#121212", "#d4d4d4", "#777777", "#222222"
else:
    bg_app, bg_panel, text_main, text_sub, border_col = "#f4f4f5", "#ffffff", "#18181b", "#71717a", "#e4e4e7"

st.markdown(f"""
<style>
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} header {{visibility: hidden;}}
    .block-container {{ padding-top: 1rem; padding-bottom: 1rem; max-width: 1400px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
    
    [data-testid="stAppViewContainer"] {{ background-color: {bg_app}; color: {text_main}; }}
    [data-testid="stHeader"] {{ background-color: {bg_app}; }}
    
    .panel-box {{ background-color: {bg_panel}; border: 1px solid {border_col}; padding: 20px; margin-bottom: 20px; border-radius: 6px; }}
    
    .sec-clean {{ border-left: 3px solid #22c55e; padding: 10px 15px; background-color: rgba(34, 197, 94, 0.05); margin-top:5px; }}
    .sec-danger {{ border-left: 3px solid #ef4444; padding: 10px 15px; background-color: rgba(239, 68, 68, 0.05); margin-top:5px; }}
    
    .supply-warn {{ color: #ef4444; font-size: 13px; font-weight: 600; margin-top: 5px; }}
    .supply-safe {{ color: #22c55e; font-size: 13px; font-weight: 600; margin-top: 5px; }}
    
    .metric-val {{ font-size: 20px; font-weight: 600; font-family: monospace; color: {text_main}; }}
    .metric-label {{ color: {text_sub}; font-size: 11px; text-transform: uppercase; font-weight: 600; letter-spacing: 1px; margin-bottom: 4px; }}
    
    .social-container {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px; }}
    a.social-btn {{ color: {text_sub}; font-size: 12px; text-decoration: none; padding: 4px 0; border-bottom: 1px solid transparent; transition: 0.2s; }}
    a.social-btn:hover {{ color: {text_main}; border-bottom: 1px solid {text_main}; }}
    
    .radar-header {{ font-size: 12px; font-weight: 600; color: {text_main}; letter-spacing: 1px; margin-bottom: 10px; border-bottom: 1px solid {border_col}; padding-bottom: 5px; }}
    .radar-row {{ display: flex; justify-content: space-between; align-items: center; padding: 10px; border-bottom: 1px solid {border_col}; font-family: monospace; font-size: 13px; text-decoration: none; color: {text_main}; transition: background 0.2s; background-color: {bg_panel}; }}
    .radar-row:hover {{ background-color: rgba(100,100,100,0.05); }}
    
    .txt-green {{ color: #22c55e; font-weight: bold; }}
    .txt-red {{ color: #ef4444; font-weight: bold; }}
    .txt-muted {{ color: {text_sub}; font-size: 11px; }}
    
    .badge-high {{ background-color: rgba(34, 197, 94, 0.1); color: #22c55e; padding: 3px 8px; border-radius: 4px; border: 1px solid rgba(34, 197, 94, 0.3); font-weight: bold; }}
    .badge-mid {{ background-color: rgba(234, 179, 8, 0.1); color: #eab308; padding: 3px 8px; border-radius: 4px; border: 1px solid rgba(234, 179, 8, 0.3); font-weight: bold; }}
    .badge-low {{ background-color: rgba(239, 68, 68, 0.1); color: #ef4444; padding: 3px 8px; border-radius: 4px; border: 1px solid rgba(239, 68, 68, 0.3); font-weight: bold; }}
</style>
""", unsafe_allow_html=True)

# --- DİL SÖZLÜĞÜ ---
langs = {
    "TR": {
        "search": "Hedef Ara (Token Sembolü veya Adresi):",
        "search_btn": "SORGULA",
        "price": "FİYAT", "liq": "LİKİDİTE", "vol": "24S HACİM", "tax": "VERGİ (AL/SAT)",
        "supply_title": "MAKRO EKONOMİ & ARZ (TOKENOMICS)",
        "mcap": "PİYASA DEĞERİ (MCAP)", "fdv": "TAM SEYRELTİLMİŞ (FDV)", "ratio": "DOLAŞIM ORANI",
        "warn_inf": "⚠️ YÜKSEK ENFLASYON RİSKİ: Tokenların çoğu kilitli, satış baskısı gelebilir.",
        "safe_inf": "✅ SAĞLIKLI DOLAŞIM: Token arzının büyük kısmı piyasada.",
        "sec_title": "SİSTEM GÜVENLİK ANALİZİ", "clean": "TEMİZ KOD", "danger": "YÜKSEK RİSK (HONEYPOT)",
        "creator": "Kurucu Cüzdan", "web": "Web Adresi", "twitter": "X (Twitter)", "tg": "Telegram",
        "radar_flow": "BALİNA RADARI (ALIM / SATIM)", "radar_contracts": "BALİNA RADARI (AKILLI KONTRATLAR)",
        "new_tokens": "AĞDA YENİ ÇIKAN TOKENLAR VE GÜVENLİK ANALİZİ",
        "scan_btn": "Sistemi Güncelle", "no_data": "Geçerli veri bulunamadı."
    },
    "EN": {
        "search": "Search Target (Token Symbol or Address):",
        "search_btn": "SEARCH",
        "price": "PRICE", "liq": "LIQUIDITY", "vol": "24H VOL", "tax": "TAX (B/S)",
        "supply_title": "MACRO ECONOMICS & SUPPLY",
        "mcap": "MARKET CAP", "fdv": "FULLY DILUTED (FDV)", "ratio": "CIRCULATION RATIO",
        "warn_inf": "⚠️ HIGH INFLATION RISK: Majority of tokens are locked. Dump risk is high.",
        "safe_inf": "✅ HEALTHY CIRCULATION: Most of the supply is unlocked.",
        "sec_title": "SYSTEM SECURITY ANALYSIS", "clean": "CLEAN CODE", "danger": "HIGH RISK (HONEYPOT)",
        "creator": "Deployer Wallet", "web": "Website", "twitter": "X (Twitter)", "tg": "Telegram",
        "radar_flow": "WHALE RADAR (BUY / SELL)", "radar_contracts": "WHALE RADAR (SMART CONTRACTS)",
        "new_tokens": "NEWLY DEPLOYED TOKENS & SECURITY ANALYSIS",
        "scan_btn": "Update System", "no_data": "Valid data not found."
    }
}
t = langs[lang_choice]

# --- API FONKSİYONLARI ---
def search_token_dexscreener(query):
    query = query.strip()
    try:
        # Akıllı Yönlendirme: Adres mi İsim mi?
        if query.startswith("0x") and len(query) == 42:
            url = f"https://api.dexscreener.com/latest/dex/tokens/{query}"
        else:
            url = f"https://api.dexscreener.com/latest/dex/search?q={query}"
            
        res = requests.get(url).json()
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
                    "fdv": pair.get("fdv", 0),
                    "marketCap": pair.get("marketCap", 0),
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
            try: b_tax, s_tax = float(data.get("buy_tax", "0")) * 100, float(data.get("sell_tax", "0")) * 100
            except: b_tax, s_tax = 0.0, 0.0
            
            score = 100
            if is_honey: score -= 100
            if not is_open: score -= 20
            if b_tax > 10: score -= 15
            if s_tax > 10: score -= 15
            return {"is_honeypot": is_honey, "score": max(0, score), "buy_tax": b_tax, "sell_tax": s_tax}
    except: pass
    return {"is_honeypot": False, "score": "-", "buy_tax": "-", "sell_tax": "-"}

def format_money(value):
    if value >= 1_000_000_000: return f"${value/1_000_000_000:.2f}B"
    elif value >= 1_000_000: return f"${value/1_000_000:.2f}M"
    elif value >= 1_000: return f"${value/1_000:.2f}K"
    return f"${value:.0f}"

# --- RADAR VERİ SİMÜLASYONU ---
def gen_addr(): return "0x" + "".join(random.choices("0123456789abcdef", k=40))

if "order_flow" not in st.session_state:
    st.session_state.order_flow = [{"addr": gen_addr(), "type": random.choice(["BUY", "SELL"]), "val": random.uniform(20.0, 300.0), "time": time.time() - random.randint(5, 120)} for _ in range(6)]
    st.session_state.order_flow.sort(key=lambda x: x["time"], reverse=True)

if "whale_contracts" not in st.session_state:
    st.session_state.whale_contracts = [{"addr": gen_addr(), "action": random.choice(["Deploy", "Execute", "Approve"]), "val": random.uniform(5.0, 50.0), "time": time.time() - random.randint(5, 120)} for _ in range(6)]
    st.session_state.whale_contracts.sort(key=lambda x: x["time"], reverse=True)

if "new_tokens" not in st.session_state:
    st.session_state.new_tokens = [{"addr": gen_addr(), "score": random.randint(10, 100), "time": time.time() - random.randint(5, 300)} for _ in range(8)]
    st.session_state.new_tokens.sort(key=lambda x: x["time"], reverse=True)

def update_system():
    for _ in range(random.randint(1, 2)): st.session_state.order_flow.insert(0, {"addr": gen_addr(), "type": random.choice(["BUY", "SELL"]), "val": random.uniform(20.0, 400.0), "time": time.time()})
    st.session_state.order_flow = st.session_state.order_flow[:6]
    for _ in range(random.randint(1, 2)): st.session_state.whale_contracts.insert(0, {"addr": gen_addr(), "action": random.choice(["Deploy", "Execute", "Approve"]), "val": random.uniform(5.0, 80.0), "time": time.time()})
    st.session_state.whale_contracts = st.session_state.whale_contracts[:6]
    for _ in range(1): st.session_state.new_tokens.insert(0, {"addr": gen_addr(), "score": random.randint(10, 100), "time": time.time()})
    st.session_state.new_tokens = st.session_state.new_tokens[:8]

# --- 1. ANA EKRAN: ARAMA VE İSTİHBARAT ---
col_input, col_btn = st.columns([4, 1])
with col_input:
    search_query = st.text_input("", placeholder=t['search'], label_visibility="collapsed")
with col_btn:
    search_clicked = st.button("🔎 " + t['search_btn'], use_container_width=True)

# Butona basıldığında veya Enter yapıldığında çalışır
if search_query or search_clicked:
    if search_query: # Boş değilse işlemi başlat
        with st.spinner("Ağ taranıyor..."):
            token = search_token_dexscreener(search_query)
            if token:
                security = check_security_goplus(token['address'])
                st.markdown("<div class='panel-box'>", unsafe_allow_html=True)
                
                # KİMLİK & SOSYAL LİNKLER
                st.markdown(f"<div style='font-size:24px; font-weight:600;'>{token['name']} <span style='color:{text_sub}; font-weight:400;'>{token['symbol']}</span></div>", unsafe_allow_html=True)
                st.markdown(f"<div style='color:{text_sub}; font-family:monospace; font-size:13px; margin-top:2px;'>{token['address']}</div>", unsafe_allow_html=True)
                
                html_links = f"<div class='social-container'><a href='https://arbiscan.io/address/{token['address']}#code' target='_blank' class='social-btn'>[ {t['creator']} ]</a>"
                info = token['info']
                if info:
                    for web in info.get("websites", []): html_links += f"<a href='{web['url']}' target='_blank' class='social-btn'>[ {t['web']} ]</a>"
                    for social in info.get("socials", []):
                        name = t['twitter'] if social['type'] == "twitter" else t['tg'] if social['type'] == "telegram" else "Link"
                        html_links += f"<a href='{social['url']}' target='_blank' class='social-btn'>[ {name} ]</a>"
                html_links += "</div>"
                st.markdown(html_links, unsafe_allow_html=True)
                
                st.markdown(f"<hr style='border-color:{border_col}; margin:20px 0;'>", unsafe_allow_html=True)
                
                # 1. SATIR: PİYASA METRİKLERİ
                c1, c2, c3, c4 = st.columns(4)
                with c1: st.markdown(f"<div class='metric-label'>{t['price']}</div><div class='metric-val'>${float(token['priceUsd']):.6f}</div>", unsafe_allow_html=True)
                with c2: st.markdown(f"<div class='metric-label'>{t['liq']}</div><div class='metric-val'>{format_money(token['liquidity'])}</div>", unsafe_allow_html=True)
                with c3: st.markdown(f"<div class='metric-label'>{t['vol']}</div><div class='metric-val'>{format_money(token['volume24h'])}</div>", unsafe_allow_html=True)
                with c4: st.markdown(f"<div class='metric-label'>{t['tax']}</div><div class='metric-val txt-muted'>%{security['buy_tax']} / %{security['sell_tax']}</div>", unsafe_allow_html=True)

                st.markdown(f"<hr style='border-color:{border_col}; margin:20px 0;'>", unsafe_allow_html=True)
                
                # 2. SATIR: ARZ VE TOKENOMICS
                fdv = float(token.get('fdv', 0))
                mcap = float(token.get('marketCap', 0))
                if mcap == 0 and fdv > 0: mcap = fdv
                
                ratio = (mcap / fdv * 100) if fdv > 0 else 100
                ratio_color = "#ef4444" if ratio < 40 else "#22c55e"
                
                st.markdown(f"<div class='metric-label' style='font-size:13px;'>🏦 {t['supply_title']}</div>", unsafe_allow_html=True)
                s1, s2, s3 = st.columns(3)
                with s1: st.markdown(f"<div class='metric-label'>{t['mcap']}</div><div class='metric-val'>{format_money(mcap)}</div>", unsafe_allow_html=True)
                with s2: st.markdown(f"<div class='metric-label'>{t['fdv']}</div><div class='metric-val'>{format_money(fdv)}</div>", unsafe_allow_html=True)
                with s3: st.markdown(f"<div class='metric-label'>{t['ratio']}</div><div class='metric-val' style='color:{ratio_color};'>%{ratio:.1f}</div>", unsafe_allow_html=True)
                
                if ratio < 40 and fdv > 0:
                    st.markdown(f"<div class='supply-warn'>{t['warn_inf']}</div>", unsafe_allow_html=True)
                elif ratio >= 80 and fdv > 0:
                    st.markdown(f"<div class='supply-safe'>{t['safe_inf']}</div>", unsafe_allow_html=True)

                st.markdown(f"<hr style='border-color:{border_col}; margin:20px 0;'>", unsafe_allow_html=True)
                
                # 3. SATIR: GÜVENLİK ANALİZİ
                st.markdown(f"<div class='metric-label' style='font-size:13px;'>🛡️ {t['sec_title']}</div>", unsafe_allow_html=True)
                if security['is_honeypot']: st.markdown(f"<div class='sec-danger'><span style='color:#ef4444; font-weight:600;'>{t['danger']}</span> | Sistem Skoru: {security['score']}/100</div>", unsafe_allow_html=True)
                else: st.markdown(f"<div class='sec-clean'><span style='color:#22c55e; font-weight:600;'>{t['clean']}</span> | Sistem Skoru: {security['score']}/100</div>", unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # GRAFİK
                chart_theme = "dark" if theme_choice == "Karanlık" else "light"
                components.iframe(f"https://dexscreener.com/arbitrum/{token['pairAddress']}?embed=1&theme={chart_theme}", height=450, scrolling=False)
            else:
                st.error(t['no_data'])

# --- 2. ORTA BÖLÜM: BALİNA RADARI ---
st.markdown(f"<br>", unsafe_allow_html=True)
st.button(t['scan_btn'], on_click=update_system, use_container_width=True)
st.markdown(f"<br>", unsafe_allow_html=True)

curr_time = time.time()
col_flow, col_contracts = st.columns(2)

with col_flow:
    st.markdown(f"<div class='radar-header'>{t['radar_flow']}</div>", unsafe_allow_html=True)
    for flow in st.session_state.order_flow:
        age = int(curr_time - flow['time'])
        time_str = f"{age}s" if age < 60 else f"{age//60}m"
        color_cls = "txt-green" if flow['type'] == "BUY" else "txt-red"
        st.markdown(f"<a href='https://arbiscan.io/address/{flow['addr']}' target='_blank' class='radar-row'><span class='{color_cls}'>[{flow['type']}]</span><span>{flow['val']:.1f} ETH</span><span class='txt-muted'>{time_str}</span></a>", unsafe_allow_html=True)

with col_contracts:
    st.markdown(f"<div class='radar-header'>{t['radar_contracts']}</div>", unsafe_allow_html=True)
    for contract in st.session_state.whale_contracts:
        age = int(curr_time - contract['time'])
        time_str = f"{age}s" if age < 60 else f"{age//60}m"
        st.markdown(f"<a href='https://arbiscan.io/address/{contract['addr']}' target='_blank' class='radar-row'><span>{contract['addr'][:10]}...</span><span style='color:{text_sub};'>[{contract['action']}]</span><span class='txt-muted'>{time_str}</span></a>", unsafe_allow_html=True)

# --- 3. EN ALT BÖLÜM: YENİ TOKENLAR ---
st.markdown(f"<br><br><div class='radar-header'>{t['new_tokens']}</div>", unsafe_allow_html=True)

for token in st.session_state.new_tokens:
    age = int(curr_time - token['time'])
    time_str = f"{age}s" if age < 60 else f"{age//60}m"
    badge_cls = "badge-high" if token['score'] >= 80 else "badge-mid" if token['score'] >= 50 else "badge-low"

    st.markdown(f"<a href='https://arbiscan.io/address/{token['addr']}' target='_blank' class='radar-row' style='margin-bottom: 5px; border-radius: 6px;'><span style='font-family:monospace;'>{token['addr']}</span><span class='{badge_cls}'>Skor: {token['score']}/100</span><span class='txt-muted'>{time_str}</span></a>", unsafe_allow_html=True)
