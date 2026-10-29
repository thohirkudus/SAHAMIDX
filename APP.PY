import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px

# ==========================================
# 1. KONFIGURASI HALAMAN & CSS RESPONSIVE MOBILE
# ==========================================
st.set_page_config(
    page_title="THOHIR IDX Institutional Screener",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

    /* Global Dark Theme Ala JOSAT */
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
    
    /* Styling Kartu / Metrik yang Responsif di HP */
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

    /* Tabel / DataFrame Agar Tidak Terpotong di Layar Kecil */
    .stDataFrame {
        border-radius: 14px;
        border: 1px solid #1E2D44;
        background-color: #0E1520;
        overflow-x: auto;
    }
    
    /* Tombol & Selectbox */
    .stSelectbox div[data-baseweb="select"] {
        background-color: #0E1520;
        border-color: #1E2D44;
        color: #E2EAF8;
        border-radius: 12px;
    }

    /* Optimasi Tampilan Mobile (Media Query) */
    @media (max-width: 768px) {
        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.2rem !important; }
        h3 { font-size: 1rem !important; }
        .block-container {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

st.title("🏛️ THOHIR - Institutional IDX Screener")
st.markdown("Dashboard analitik tingkat institusi dengan antarmuka responsif (*Mobile & Desktop*) untuk memantau **Arus Uang Sektor** dan **Sinyal Teknikal Beli**.")

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
            df = yf.download(ticker, period="1y", interval="1d", progress=False)
            if df.empty or len(df) < 50:
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
            vol_ma20 = float(volume.rolling(20).mean().iloc[-1])

            if change_pct > 0 and curr_vol > vol_ma20:
                money_flow = "🟢 INFLOW"
            elif change_pct < 0 and curr_vol > vol_ma20:
                money_flow = "🔴 OUTFLOW"
            elif change_pct > 0:
                money_flow = "🟢 INFLOW (Low Vol)"
            else:
                money_flow = "🔴 OUTFLOW (Low Vol)"

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
                "Arus Uang": money_flow,
                "Harga": round(current_price, 2),
                "Change (%)": round(change_pct, 2),
                "Alpha (%)": round(alpha, 2),
                "Beta": round(beta, 2),
                "Sinyal Teknikal": stoch_signal
            })
        except Exception:
            continue
            
    df_result = pd.DataFrame(data_list)
    if not df_result.empty:
        df_result['Is_Golden_Cross'] = df_result['Sinyal Teknikal'].str.contains("Golden Cross").astype(int)
        df_result['Is_Inflow'] = df_result['Arus Uang'].str.contains("🟢 INFLOW").astype(int)
        
        df_result = df_result.sort_values(
            by=["Is_Golden_Cross", "Is_Inflow", "Alpha (%)"], 
            ascending=[False, False, False]
        ).drop(columns=['Is_Golden_Cross', 'Is_Inflow']).reset_index(drop=True)
        
    return df_result

# Load Data Market
with st.spinner("Memuat data pasar real-time..."):
    df_screener = fetch_sector_flow_data(SECTOR_MAPPING)

if df_screener.empty:
    st.warning("Gagal memuat data pasar.")
else:
    # Kartu Ringkasan Atas (Otomatis menyusun ulang menjadi kolom responsif di HP)
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

    # Radar Arus Uang Sektor
    st.subheader("🌍 Radar Arus Uang Sektor IDX")
    sector_flow_summary = []
    for sector_name, group in df_screener.groupby("Sektor"):
        inflow_count = len(group[group['Arus Uang'].str.contains("INFLOW")])
        outflow_count = len(group[group['Arus Uang'].str.contains("OUTFLOW")])
        avg_change = group['Change (%)'].mean()
        status = "🟢 INFLOW" if inflow_count >= outflow_count else "🔴 OUTFLOW"
            
        sector_flow_summary.append({
            "Sektor IDX": sector_name,
            "Status Arus Uang": status,
            "Rata-Rata Perubahan (%)": round(avg_change, 2),
            "Jumlah Emiten": len(group)
        })
        
    df_sector_flow = pd.DataFrame(sector_flow_summary)
    df_sector_flow['Is_Inflow'] = df_sector_flow['Status Arus Uang'].str.contains("🟢 INFLOW").astype(int)
    df_sector_flow = df_sector_flow.sort_values(by=["Is_Inflow", "Rata-Rata Perubahan (%)"], ascending=[False, False]).drop(columns=['Is_Inflow']).reset_index(drop=True)
    
    flow_badges_str = "  |  ".join([f"**{row['Sektor IDX']}** {row['Status Arus Uang']}" for _, row in df_sector_flow.iterrows()])
    st.markdown(f"### `{flow_badges_str}`")
    st.dataframe(df_sector_flow, use_container_width=True)

    st.markdown("---")

    # Tabel Detail Saham & Area Jaring
    st.subheader("📊 Daftar Emiten & Area Masuk (Jaring)")
    filter_sector = st.selectbox("Filter Berdasarkan Sektor IDX:", ["Semua Sektor"] + list(df_screener['Sektor'].unique()))

    df_filtered = df_screener.copy()
    if filter_sector != "Semua Sektor":
        df_filtered = df_filtered[df_filtered['Sektor'] == filter_sector]

    st.dataframe(df_filtered, use_container_width=True, height=400)

    # Tabel Area Jaring Support
    st.markdown("### 🎯 Rekomendasi Area Masuk (Jaring Support)")
    jaring_data = []
    for _, row in df_filtered.head(8).iterrows():
        p = row['Harga']
        jaring_atas = round(p * 0.985, 0)
        jaring_bawah = round(p * 0.965, 0)
        jaring_data.append({
            "Kode Saham": row['Kode Saham'],
            "Sektor": row['Sektor'],
            "Harga Sekarang": p,
            "Area Jaring Support": f"Rp {jaring_bawah:,.0f} – Rp {jaring_atas:,.0f}",
            "Sinyal": row['Sinyal Teknikal']
        })
    st.dataframe(pd.DataFrame(jaring_data), use_container_width=True)

    st.markdown("---")

    # Grafik Sebaran Risiko (Responsif)
    st.subheader("📈 Scatter Plot Analisis Risiko & Imbal Hasil")
    df_screener['Marker_Size'] = df_screener['Change (%)'].abs() + 5

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
