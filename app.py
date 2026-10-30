import streamlit as st
import pandas as pd
from datetime import date
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
    sheet_bank = spreadsheet.worksheet("Setoran_Bank")
except Exception as e:
    st.error(f"Gagal terhubung ke Google Sheets. Periksa nama tab (Stok_BBM, Riwayat_Laporan, Setoran_Bank). Error: {e}")
    st.stop()

# --- MENU NAVIGASI ---
menu = st.sidebar.selectbox("Pilih Menu", ["📝 Input Laporan Harian", "🏦 Catat Setoran Bank", "📊 Dashboard & Histori"])

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

# --- MENU 1: INPUT LAPORAN HARIAN ---
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
        
        c1, c2, c3, c4 = st.columns(4)
        with c1: stok_awal_ptl = st.number_input("Stok Awal Ptl", min_value=0.0, value=last_stock["ptl"], step=10.0)
        with c2: stok_masuk_ptl = st.number_input("Stok Masuk Ptl", min_value=0.0, step=10.0)
        with c3: terjual_ptl = st.number_input("Terjual Ptl", min_value=0.0, step=10.0)
        with c4: harga_ptl = st.number_input("Harga/Liter Ptl", value=10000.0, step=100.0)

        e1, e2, e3, e4 = st.columns(4)
        with e1: stok_awal_sol = st.number_input("Stok Awal Solar", min_value=0.0, value=last_stock["sol"], step=10.0)
        with e2: stok_masuk_sol = st.number_input("Stok Masuk Solar", min_value=0.0, step=10.0)
        with e3: terjual_sol = st.number_input("Terjual Solar", min_value=0.0, step=10.0)
        with e4: harga_sol = st.number_input("Harga/Liter Solar", value=6800.0, step=100.0)

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
        setor_tunai = st.number_input("Setoran Tunai (Cash) Masuk", min_value=0.0, step=1000.0)
        transfer_qris = st.number_input("Total Transfer / EDC /
