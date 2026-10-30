import streamlit as st
import pandas as pd
from datetime import date, datetime
import gspread
from google.oauth2.service_account import Credentials

# Konfigurasi Halaman
st.set_page_config(page_title="Dashboard & Laporan SPBU", page_icon="⛽", layout="wide")

# --- KONEKSI GOOGLE SHEETS ---
@st.cache_resource
def init_connection():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    return client

try:
    client = init_connection()
    spreadsheet = client.open("Database SPBU Berkah Cahaya Gag")
    sheet_stok = spreadsheet.worksheet("Stok_BBM")
    sheet_riwayat = spreadsheet.worksheet("Riwayat_Laporan")
except Exception as e:
    st.error(f"Gagal terhubung ke Google Sheets. Periksa konfigurasi secrets atau nama file. Error: {e}")
    st.stop()

# --- MENU NAVIGASI ---
menu = st.sidebar.selectbox("Pilih Menu", ["📝 Input Laporan Harian", "📊 Dashboard & Histori"])

# FUNGSI AMBIL STOK TERAKHIR
def load_last_stock():
    try:
        data = sheet_stok.get_all_records()
        if data:
            last_row = data[-1]
            return {
                "ptl": float(last_row.get("Sisa_Ptl", 0.0)),
                "sol": float(last_row.get("Sisa_Sol", 0.0)),
                "mtn": float(last_row.get("Sisa_Mtn", 0.0)),
            }
    except Exception:
        pass
    return {"ptl": 0.0, "sol": 0.0, "mtn": 0.0}

last_stock = load_last_stock()

if menu == "📝 Input Laporan Harian":
    st.title("⛽ Generator Laporan & Histori SPBU")
    st.markdown("Isi form di bawah ini untuk menghasilkan format WhatsApp dan menyimpan data ke Google Sheets.")

    with st.form("form_laporan_lengkap"):
        st.subheader("📌 1. Informasi Umum")
        col1, col2 = st.columns(2)
        with col1:
            lokasi = st.text_input("Lokasi / Unit SPBU", value="Pulau Gag, Raja Ampat")
            tanggal = st.date_input("Tanggal Laporan", value=date.today())
        with col2:
            shift = st.selectbox("Shift Operasional", ["Shift 1 (Pagi - Sore)", "Shift 2 (Sore - Malam)", "Full Day (1 Hari)"])
            pelapor = st.text_input("Nama Pelapor / Admin", value="Admin SPBU")

        st.markdown("---")
        st.subheader("⛽ 2. Rekonsiliasi Stok BBM (Liter)")
        st.info("💡 *Stok Awal otomatis terambil dari sisa stok akhir hari sebelumnya di Google Sheets.*")
        
        # Pertalite
        c1, c2, c3, c4 = st.columns(4)
        with c1: stok_awal_ptl = st.number_input("Stok Awal Ptl", min_value=0.0, value=last_stock["ptl"], step=10.0)
        with c2: stok_masuk_ptl = st.number_input("Stok Masuk Ptl", min_value=0.0, step=10.0)
        with c3: terjual_ptl = st.number_input("Terjual Ptl", min_value=0.0, step=10.0)
        with c4: harga_ptl = st.number_input("Harga/Liter Ptl", value=10000.0, step=100.0)

        # Biosolar
        e1, e2, e3, e4 = st.columns(4)
        with e1: stok_awal_sol = st.number_input("Stok Awal Solar", min_value=0.0, value=last_stock["sol"], step=10.0)
        with e2: stok_masuk_sol = st.number_input("Stok Masuk Solar", min_value=0.0, step=10.0)
        with e3: terjual_sol = st.number_input("Terjual Solar", min_value=0.0, step=10.0)
        with e4: harga_sol = st.number_input("Harga/Liter Solar", value=6800.0, step=100.0)

        # Minyak Tanah
        m1, m2, m3, m4 = st.columns(4)
        with m1: stok_awal_mtn = st.number_input("Stok Awal M. Tanah", min_value=0.0, value=last_stock["mtn"], step=10.0)
        with m2: stok_masuk_mtn = st.number_input("Stok Masuk M. Tanah", min_value=0.0, step=10.0)
        with m3: terjual_mtn = st.number_input("Terjual M. Tanah", min_value=0.0, step=10.0)
        with m4: harga_mtn = st.number_input("Harga/Liter M. Tanah", value=15000.0, step=100.0)

        st.markdown("---")
        st.subheader("🛢️ 3. Penjualan Oli / Pelumas")
        col_o1, col_o2 = st.columns(2)
        with col_o1:
            terjual_oli_kecil = st.number_input("Oli Botol Kecil (Botol)", min_value=0, step=1)
            omzet_oli_kecil = st.number_input("Total Pendapatan Oli Kecil (Rp)", min_value=0.0, step=1000.0)
        with col_o2:
            terjual_oli_besar = st.number_input("Oli Dirigen/Besar (Pcs)", min_value=0, step=1)
            omzet_oli_besar = st.number_input("Total Pendapatan Oli Besar (Rp)", min_value=0.0, step=1000.0)

        st.markdown("---")
        st.subheader("💰 4. Keuangan, Pembayaran & Operasional")
        setor_tunai = st.number_input("Setoran Tunai (Cash) di Brankas/Kasir", min_value=0.0, step=1000.0)
        transfer_qris = st.number_input("Total Transfer / EDC / QRIS", min_value=0.0, step=1000.0)
        piutang_bon = st.number_input("Total Piutang / DO Korporat", min_value=0.0, step=1000.0)
        biaya_operasional = st.number_input("Pengeluaran Operasional Harian", min_value=0.0, step=1000.0)
        catatan = st.text_area("Catatan / Kendala Hari Ini (Opsional)")

        submitted = st.form_submit_button("Generate Laporan & Simpan ke Google Sheets")

    if submitted:
        stok_akhir_ptl = stok_awal_ptl + stok_masuk_ptl - terjual_ptl
        stok_akhir_sol = stok_awal_sol + stok_masuk_sol - terjual_sol
        stok_akhir_mtn = stok_awal_mtn + stok_masuk_mtn - terjual_mtn

        rp_ptl = terjual_ptl * harga_ptl
        rp_sol = terjual_sol * harga_sol
        rp_mtn = terjual_mtn * harga_mtn
        
        total_penjualan_bbm = rp_ptl + rp_sol + rp_mtn
        total_penjualan_oli = omzet_oli_kecil + omzet_oli_besar
        total_omzet_keseluruhan = total_penjualan_bbm + total_penjualan_oli

        total_penerimaan = setor_tunai + transfer_qris + piutang_bon
        selisih = total_penerimaan - total_omzet_keseluruhan
        
        if abs(selisih) < 1000:
            status_kas = "Aman (Nihil Selisih)"
        elif selisih > 0:
            status_kas = f"Surplus Rp {selisih:,.0f}"
        else:
            status_kas = f"Minus Rp {abs(selisih):,.0f}"

        sheet_stok.append_row([str(tanggal), stok_akhir_ptl, stok_akhir_sol, stok_akhir_mtn])
        sheet_riwayat.append_row([
            str(tanggal), shift, pelapor, 
            total_penjualan_bbm, total_penjualan_oli, total_omzet_keseluruhan,
            setor_tunai, transfer_qris, piutang_bon, biaya_operasional, status_kas
        ])

        wa_output = f"""📊 *LAPORAN HARIAN OPERASIONAL & KEUANGAN SPBU*
📍 *Unit / Lokasi:* {lokasi}
📅 *Tanggal:* {tanggal.strftime('%d/%m/%Y')}
🕒 *Shift Operasional:* {shift}

--------------------------------------------------
⛽ *1. REKAP PENJUALAN & STOK BBM*
• *Pertalite:* Terjual {terjual_ptl:,.0f} L (Sisa {stok_akhir_ptl:,.0f} L)
• *Biosolar:* Terjual {terjual_sol:,.0f} L (Sisa {stok_akhir_sol:,.0f} L)
• *Minyak Tanah:* Terjual {terjual_mtn:,.0f} L (Sisa {stok_akhir_mtn:,.0f} L)
🔹 *Total Penjualan BBM:* *Rp {total_penjualan_bbm:,.0f}*

🛢️ *2. PENJUALAN OLI & OMZET*
🔹 *Total Penjualan Oli:* *Rp {total_penjualan_oli:,.0f}*
💰 *Total Omzet Keseluruhan:* *Rp {total_omzet_keseluruhan:,.0f}*

💳 *3. REKONSILIASI PEMBAYARAN*
• Tunai: Rp {setor_tunai:,.0f} | Transfer/QRIS: Rp {transfer_qris:,.0f} | Piutang: Rp {piutang_bon:,.0f}
🔸 *Total Penerimaan:* *Rp {total_penerimaan:,.0f}*

🔍 *4. STATUS KAS:* *{status_kas}*
📝 *Catatan:* {catatan if catatan else "Nihil"}
*Dilaporkan oleh:* {pelapor}"""

        st.success("Laporan berhasil dibuat dan tersimpan ke Google Sheets!")
        st.code(wa_output, language="text")

elif menu == "📊 Dashboard & Histori":
    st.title("📊 Dashboard & Riwayat Operasional SPBU")
    st.markdown("Filter data berdasarkan rentang tanggal. Secara *default* menampilkan data bulan berjalan.")

    try:
        data_riwayat = sheet_riwayat.get_all_records()
        if data_riwayat:
            df = pd.DataFrame(data_riwayat)
            
            # Konversi kolom Tanggal ke format datetime
            df["Tanggal_DT"] = pd.to_datetime(df["Tanggal"], errors="coerce")
            
            # Tentukan default rentang tanggal (Awal bulan ini sampai hari ini)
            today = date.today()
            first_day_of_month = today.replace(day=1)
            
            st.markdown("---")
            st.subheader("📅 Filter Periode Tanggal")
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                start_date = st.date_input("Dari Tanggal", value=first_day_of_month)
            with col_f2:
                end_date = st.date_input("Sampai Tanggal", value=today)

            # Filter dataframe berdasarkan tanggal
            mask = (df["Tanggal_DT"].dt.date >= start_date) & (df["Tanggal_DT"].dt.date <= end_date)
            df_filtered = df.loc[mask]

            st.markdown("---")
            st.subheader(f"📌 Ringkasan Performa ({start_date.strftime('%d/%m/%Y')} s.d {end_date.strftime('%d/%m/%Y')})")
            
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                total_akumulasi_omzet = df_filtered["Total_Omzet"].sum() if "Total_Omzet" in df_filtered.columns else 0
                st.metric("Total Omzet Periode Ini", f"Rp {total_akumulasi_omzet:,.0f}")
            with col_m2:
                total_laporan = len(df_filtered)
                st.metric("Jumlah Shift / Laporan", f"{total_laporan} Laporan")
            with col_m3:
                total_bbm_all = df_filtered["Total_BBM"].sum() if "Total_BBM" in df_filtered.columns else 0
                st.metric("Penjualan BBM Periode Ini", f"Rp {total_bbm_all:,.0f}")

            st.markdown("---")
            st.subheader("📈 Grafik Tren Omzet Harian")
            if not df_filtered.empty and "Tanggal" in df_filtered.columns and "Total_Omzet" in df_filtered.columns:
                chart_data = df_filtered.set_index("Tanggal")[["Total_Omzet"]]
                st.line_chart(chart_data)
            else:
                st.info("Tidak ada data omzet pada rentang tanggal yang dipilih.")
            
            st.markdown("---")
            st.subheader("📋 Tabel Riwayat Laporan Terfilter")
            # Tampilkan dataframe tanpa kolom bantuan datetime sementara
            display_df = df_filtered.drop(columns=["Tanggal_DT"], errors="ignore")
            st.dataframe(display_df, use_container_width=True)
        else:
            st.info("Belum ada data histori laporan yang tersimpan.")
    except Exception as e:
        st.error(f"Gagal memuat dashboard: {e}")
