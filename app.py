import streamlit as st
import requests

# --- AYARLAR ---
st.set_page_config(page_title="Terminal", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    
    .whale-alert {
        background-color: #2a0404;
        padding: 15px;
        border-radius: 4px;
        border-left: 5px solid #ff0000;
        color: #ff4444;
        margin-bottom: 10px;
        font-family: monospace;
        font-size: 14px;
    }
    .normal-log {
        background-color: #0a0a0a;
        padding: 15px;
        border-radius: 4px;
        border-left: 5px solid #333;
        color: #888;
        margin-bottom: 10px;
        font-family: monospace;
        font-size: 14px;
    }
    .panel-box {
        background-color: #111;
        border: 1px solid #222;
        border-radius: 6px;
        padding: 20px;
        color: #eee;
        min-height: 400px;
    }
    .metric-text { color: #00ff00; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- DOĞRUDAN RPC SIZMASI (WEB3 KÜTÜPHANESİ YOK) ---
ARB_RPC_URL = "https://arb1.arbitrum.io/rpc"

def get_dex_data(token_address):
    """DexScreener üzerinden ücretsiz, anahtarsız likidite ve fiyat çeker."""
    url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
    try:
        res = requests.get(url).json()
        if res.get("pairs") and len(res["pairs"]) > 0:
            pair = res["pairs"][0]
            return {
                "name": pair.get("baseToken", {}).get("name", "Bilinmiyor"),
                "symbol": pair.get("baseToken", {}).get("symbol", "???"),
                "priceUsd": pair.get("priceUsd", "0"),
                "liquidity": pair.get("liquidity", {}).get("usd", 0),
                "volume24h": pair.get("volume", {}).get("h24", 0)
            }
    except:
        pass
    return None

def check_wallet_fast(address):
    """Web3 olmadan, doğrudan JSON-RPC ile ağın kalbinden bakiye çeker."""
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getBalance",
        "params": [address, "latest"],
        "id": 1
    }
    try:
        res = requests.post(ARB_RPC_URL, json=payload).json()
        if "result" in res:
            # Gelen veri hex (örn: 0x1bc16d...) formatındadır. Bunu tam sayıya (10'luk taban) çeviriyoruz.
            balance_wei = int(res["result"], 16)
            balance_eth = balance_wei / (10**18)
            return balance_eth > 50, float(balance_eth) # 50 ETH üstü balina alarmı tetikler
    except:
        pass
    return False, 0.0

# --- ARAYÜZ (GİZLİ TERMINAL) ---
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("<div class='panel-box'>", unsafe_allow_html=True)
    target_address = st.text_input("", placeholder="Hedef Token Adresi (0x...)")
    
    if target_address and len(target_address) == 42:
        with st.spinner("DexScreener ağlarına sızılıyor..."):
            dex_data = get_dex_data(target_address)
            if dex_data:
                st.markdown(f"### [ {dex_data['name']} ({dex_data['symbol']}) ]")
                st.markdown("---")
                st.markdown(f"**Fiyat:** <span class='metric-text'>${dex_data['priceUsd']}</span>", unsafe_allow_html=True)
                st.markdown(f"**Havuz Likiditesi:** <span class='metric-text'>${dex_data['liquidity']:,.2f}</span>", unsafe_allow_html=True)
                st.markdown(f"**24S Hacim:** <span class='metric-text'>${dex_data['volume24h']:,.2f}</span>", unsafe_allow_html=True)
            else:
                st.warning("Bu adresin henüz merkeziyetsiz borsalarda (DEX) bir havuzu yok veya veri alınamıyor.")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='panel-box'>", unsafe_allow_html=True)
    st.markdown("<span style='color:#555; font-family:monospace;'>// ON-CHAIN RADAR (GHOST MODE)</span>", unsafe_allow_html=True)
    
    monitor_wallet = st.text_input("", placeholder="Cüzdan Adresi (0x...)")
    
    if monitor_wallet and len(monitor_wallet) == 42:
        is_whale, balance = check_wallet_fast(monitor_wallet)
        if is_whale:
            st.markdown(f"""
            <div class='whale-alert'>
                [TESPİT] {monitor_wallet[:6]}...{monitor_wallet[-4:]}<br>
                GÜÇ: {balance:.2f} ETH<br>
                DURUM: KIRMIZI ALARM
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='normal-log'>
                [İZLEME] {monitor_wallet[:6]}...{monitor_wallet[-4:]}<br>
                GÜÇ: {balance:.4f} ETH<br>
                DURUM: STANDART
            </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
