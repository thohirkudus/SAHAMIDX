import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px

# ==========================================
# 1. KONFIGURASI HALAMAN & CSS RESPONSIVE MOBILE
# ==========================================
st.set_page_config(
    page_title="thohir saham - Institutional Screener",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

    .stApp {
        background-color: #080C14;
        font-family: 'Inter', sans-serif;
        color: #E2EAF8;
    }
    
    header {visibility: hidden;}
    .block-container {
        padding-top: 1rem;
        padding-bottom: 3rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    h1, h2, h3 {
        font-family: 'Space Grotesk', sans-serif !important;
        color: #E2EAF8 !important;
    }
    
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #0F1D38 0%, #0A1526 100%);
        border: 1px solid #1E2D44;
        padding: 12px 16px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        margin-bottom: 10px;
    }
    div[data-testid="stMetric"] label {
        color: #8A9BBF !important;
        font-size: 10px !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-family: 'Space Grotesk', sans-serif !important;
        color: #3D8EF8 !important;
        font-size: 20px !important;
    }

    .stDataFrame {
        border-radius: 14px;
        border: 1px solid #1E2D44;
        background-color: #0E1520;
        overflow-x: auto;
    }
    
    .stSelectbox div[data-baseweb="select"] {
        background-color: #0E1520;
        border-color: #1E2D44;
        color: #E2EAF8;
        border-radius: 12px;
    }

    @media (max-width: 768px) {
        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.2rem !important; }
        h3 { font-size: 1.0rem !important; }
        .block-container {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 📊 📊 [thohir saham](https://gemini.google.com/notebook/48f4b0c5-0333-4d6b-8d57-dce2d75bdadb)")
st.markdown("Dashboard analitik institusi dengan **On-Balance Volume (OBV)**, **Klasifikasi Bandar**, dan filter anti-terjebak.")

# ==========================================
# 2. PEMETAAN SEKTOR & DATA PASAR
# ==========================================
SECTOR_MAPPING = {
    "BBCA.JK": "IDXFINANCE", "BBRI.JK": "IDXFINANCE", "BMRI.JK": "IDXFINANCE", "BBNI.JK": "IDXFINANCE", "BRIS.JK": "IDXFINANCE",
    "CTRA.JK": "IDXPROPERT", "BSDE.JK": "IDXPROPERT", "PWON.JK": "IDXPROPERT", "SMRA.JK": "IDXPROPERT",
    "ICBP.JK": "IDXNONCYC", "INDF.JK": "IDXNONCYC", "AMRT.JK": "IDXNONCYC", "UNVR.JK": "IDXNONCYC", "JPFA.JK": "IDXNONCYC",
    "KLBF.JK": "IDXHEALTH",
    "ASII.JK": "IDXCYCLIC", "ACES.JK": "IDXCYCLIC", "ERAA.JK": "IDXCYCLIC", "MAPI.JK": "IDXCYCLIC", "SCMA.JK": "IDXCYCLIC",
    "ANTM.JK": "IDXBASIC", "INCO.JK": "IDXBASIC", "NCKL.JK": "IDXBASIC", "MBMA.JK": "IDXBASIC", "AMMN.JK": "IDXBASIC", "ESSA.JK": "IDXBASIC",
    "ASSA.JK": "IDXTRANS", "BIRD.JK": "IDXTRANS", "TMAS.JK": "IDXTRANS",
    "PTBA.JK": "IDXINDUST",
    "ARTO.JK": "IDXTECHNO", "EMTK.JK": "IDXTECHNO",
    "ADRO.JK": "IDXENERGY", "ITMG.JK": "IDXENERGY", "MEDC.JK": "IDXENERGY", "PGAS.JK": "IDXENERGY", "BUMI.JK": "IDXENERGY", "DEWA.JK": "IDXENERGY", "INDY.JK": "IDXENERGY", "ADMR.JK": "IDXENERGY", "AADI.JK": "IDXENERGY",
    "TLKM.JK": "IDXINFRA", "ISAT.JK": "IDXINFRA", "EXCL.JK": "IDXINFRA", "MTEL.JK": "IDXINFRA", "TBIG.JK": "IDXINFRA", "TOWR.JK": "IDXINFRA", "CMNP.JK": "IDXINFRA", "AKRA.JK": "IDXINFRA"
}

@st.cache_data(ttl=3600)
def fetch_sector_flow_data(sector_map):
    data_list = []
    try:
        benchmark = yf.download("^JKSE", period="1y", interval="1d", progress=False)['Close']
        if isinstance(benchmark, pd.DataFrame):
            benchmark = benchmark.iloc[:, 0]
        bm_returns = benchmark.pct_change().dropna()
    except Exception:
        bm_returns = pd.Series()

    for ticker, sector in sector_map.items():
        try:
            df = yf.download(ticker, period="3mo", interval="1d", progress=False)
            if df.empty or len(df) < 22:
                continue
                
            if isinstance(df.columns, pd.MultiIndex):
                close = df['Close'].iloc[:, 0]
                high = df['High'].iloc[:, 0]
                low = df['Low'].iloc[:, 0]
                volume = df['Volume'].iloc[:, 0]
            else:
                close = df['Close']
                high = df['High']
                low = df['Low']
                volume = df['Volume']
                
            current_price = float(close.iloc[-1])
            prev_price = float(close.iloc[-2])
            change_pct = ((current_price - prev_price) / prev_price) * 100
            
            curr_vol = float(volume.iloc[-1])
            vol_rata2 = float(volume.mean())
            if vol_rata2 == 0:
                vol_rata2 = 1.0

            # Logika Rasio Volume & Kelas Bandar
            rasio_vol = curr_vol / vol_rata2
            if rasio_vol >= 5:
                kelas_bandar = "🐳 PAUS (>5x)"
            elif rasio_vol >= 3:
                kelas_bandar = "🦈 HIU (>3x)"
            elif rasio_vol >= 1.5:
                kelas_bandar = "🐟 LOKAL (>1.5x)"
            else:
                kelas_bandar = "⏳ NORMAL"

            # Perhitungan OBV (On-Balance Volume) ala Formula Google Sheets Anda
            close_diff = close.diff().fillna(0)
            obv_series = np.where(close_diff > 0, volume, np.where(close_diff < 0, -volume, 0))
            total_obv = float(np.sum(obv_series))
            avg_obv_ratio = total_obv / len(close)

            # Deteksi Akumulasi vs Distribusi OBV (Termasuk deteksi volume naik harga turun)
            if change_pct < 0 and curr_vol > (vol_rata2 * 1.5):
                obv_status = "🔴 DISTRIBUSI (Volume Naik, Harga Turun)"
            elif total_obv > avg_obv_ratio:
                obv_status = "🟢 AKUMULASI (BUY)"
            else:
                obv_status = "🔴 DISTRIBUSI (SELL)"

            # Estimasi Nilai Rupiah Dana Paus / Volume Harian
            estimated_paus_value_idr = (curr_vol * current_price)
            if estimated_paus_value_idr >= 1e9:
                val_str = f"Rp {estimated_paus_value_idr / 1e9:,.1f} M"
            else:
                val_str = f"Rp {estimated_paus_value_idr / 1e6:,.1f} Jt"

            ma20 = close.rolling(window=20).mean()
            paus_min = round(float(ma20.iloc[-1]) * 0.97, 0)
            paus_max = round(float(ma20.iloc[-1]) * 1.005, 0)
            paus_zone = f"Rp {paus_min:,.0f} – Rp {paus_max:,.0f} ({val_str})"

            # Stochastic
            low_14 = low.rolling(window=14).min()
            high_14 = high.rolling(window=14).max()
            stoch_k = 100 * ((close - low_14) / (high_14 - low_14))
            stoch_d = stoch_k.rolling(window=3).mean()
            curr_k = float(stoch_k.iloc[-1])
            curr_d = float(stoch_d.iloc[-1])
            prev_k = float(stoch_k.iloc[-2])
            prev_d = float(stoch_d.iloc[-2])
            
            stoch_signal = "Normal"
            if prev_k < prev_d and curr_k >= curr_d and curr_k < 40:
                stoch_signal = "🎯 Stoch Golden Cross"
            elif curr_k < 20:
                stoch_signal = "📉 Oversold Zone"

            # Bollinger Bands
            std20 = close.rolling(window=20).std()
            lower_band = ma20 - (2 * std20)
            upper_band = ma20 + (2 * std20)
            curr_lower = float(lower_band.iloc[-1])
            curr_upper = float(upper_band.iloc[-1])

            if current_price <= curr_lower * 1.01:
                bb_status = "🎯 Support Bollinger (Aman Masuk)"
            elif current_price >= curr_upper * 0.99:
                bb_status = "⚠️ Rawan Pucuk (Bollinger Atas)"
            else:
                bb_status = "⚖️ Zona Normal"

            # Alpha & Beta
            stock_returns = close.pct_change().dropna()
            if not bm_returns.empty:
                combined = pd.concat([stock_returns, bm_returns], axis=1).dropna()
                combined.columns = ['Stock', 'Market']
                if len(combined) > 30:
                    covariance = np.cov(combined['Stock'], combined['Market'])[0][1]
                    market_variance = np.var(combined['Market'])
                    beta = covariance / market_variance if market_variance != 0 else 1.0
                    rf = 0.06 / 252
                    alpha = (combined['Stock'].mean() - (rf + beta * (combined['Market'].mean() - rf))) * 252 * 100
                else:
                    beta, alpha = 1.0, 0.0
            else:
                beta, alpha = 1.0, 0.0

            data_list.append({
                "Kode Saham": ticker.replace(".JK", ""),
                "Sektor": sector,
                "Status OBV": obv_status,
                "Harga": round(current_price, 2),
                "Kelas Bandar": kelas_bandar,
                "Kolom Paus (Akumulasi & Nilai)": paus_zone,
                "Alpha (%)": round(alpha, 2),
                "Beta": round(beta, 2),
                "Sinyal Teknikal": stoch_signal,
                "Status Bollinger": bb_status
            })
        except Exception:
            continue
            
    df_result = pd.DataFrame(data_list)
    if not df_result.empty:
        df_result['Is_Golden_Cross'] = df_result['Sinyal Teknikal'].str.contains("Golden Cross").astype(int)
        df_result['Is_Akumulasi'] = df_result['Status OBV'].str.contains("AKUMULASI").astype(int)
        
        df_result = df_result.sort_values(
            by=["Is_Golden_Cross", "Is_Akumulasi", "Alpha (%)"], 
            ascending=[False, False, False]
        ).drop(columns=['Is_Golden_Cross', 'Is_Akumulasi']).reset_index(drop=True)
        
    return df_result

# Load Data Market
with st.spinner("Memuat data pasar real-time..."):
    df_screener = fetch_sector_flow_data(SECTOR_MAPPING)

if df_screener.empty:
    st.warning("Gagal memuat data pasar.")
else:
    # Kartu Ringkasan Atas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Emiten", f"{len(df_screener)} Saham")
    with col2:
        top_sector = df_screener.groupby("Sektor")['Alpha (%)'].mean().idxmax()
        st.metric("Sektor Alpha Tertinggi", top_sector)
    with col3:
        gc_count = len(df_screener[df_screener['Sinyal Teknikal'].str.contains("Golden Cross")])
        st.metric("Peluang Golden Cross", f"{gc_count} Emiten")
    with col4:
        top_alpha = df_screener.iloc[0]
        st.metric("Top Alpha", f"{top_alpha['Kode Saham']} (+{top_alpha['Alpha (%)']}%)")

    st.markdown("---")

    # Tabel Detail Saham dengan Pembekuan Kolom (Pinned)
    st.subheader("📊 Daftar Emiten & Analisis OBV Institusi")
    filter_sector = st.selectbox("Filter Berdasarkan Sektor IDX:", ["Semua Sektor"] + list(df_screener['Sektor'].unique()))

    df_filtered = df_screener.copy()
    if filter_sector != "Semua Sektor":
        df_filtered = df_filtered[df_filtered['Sektor'] == filter_sector]

    st.dataframe(
        df_filtered, 
        use_container_width=True, 
        height=400, 
        hide_index=True,
        column_config={
            "Kode Saham": st.column_config.TextColumn(
                "Kode Saham",
                pinned=True
            )
        }
    )

    # Tabel Area Jaring Support
    st.markdown("### 🎯 Rekomendasi Area Masuk (Jaring Support)")
    jaring_data = []
    for _, row in df_filtered.head(8).iterrows():
        jaring_data.append({
            "Kode Saham": row['Kode Saham'],
            "Sektor": row['Sektor'],
            "Harga Sekarang": row['Harga'],
            "Status OBV": row['Status OBV'],
            "Kelas Bandar": row['Kelas Bandar'],
            "Kolom Paus (Akumulasi & Nilai)": row['Kolom Paus (Akumulasi & Nilai)'],
            "Sinyal": row['Sinyal Teknikal'],
            "Filter Bollinger": row['Status Bollinger']
        })
    st.dataframe(
        pd.DataFrame(jaring_data), 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Kode Saham": st.column_config.TextColumn(
                "Kode Saham",
                pinned=True
            )
        }
    )

    st.markdown("---")

    # Grafik Sebaran Risiko
    st.subheader("📈 Scatter Plot Analisis Risiko & Imbal Hasil")
    df_screener['Marker_Size'] = 10

    fig = px.scatter(
        df_screener,
        x="Beta",
        y="Alpha (%)",
        text="Kode Saham",
        color="Sektor",
        size="Marker_Size",
        title="Peta Sebaran Beta vs Alpha per Sektor IDX",
        labels={"Beta": "Beta (Sensitivitas Pasar)", "Alpha (%)": "Alpha Tahunan (%)"}
    )
    fig.update_traces(textposition='top center')
    fig.update_layout(height=450, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)
