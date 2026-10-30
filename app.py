import streamlit as st
import pandas as pd
from datetime import date
import gspread
from google.oauth2.service_account import Credentials

# Konfigurasi Halaman
st.set_page_config(page_title="Generator Laporan SPBU", page_icon="⛽", layout="centered")

st.title("⛽ Generator Laporan & Histori SPBU")
st.markdown("Sistem terintegrasi dengan Google Sheets untuk keamanan data stok dan histori keuangan.")

# --- KONEKSI GOOGLE SHEETS ---
# Menggunakan st.secrets untuk keamanan data kredensial di Streamlit Cloud
@st.cache_resource
def init_connection():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    # Mengambil kredensial dari secrets.toml di Streamlit Cloud
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    return client

try:
    client = init_connection()
    # Buka Spreadsheet berdasarkan nama file di Google Drive Anda
    spreadsheet = client.open("Database SPBU Berkah Cahaya Gag")
    sheet_stok = spreadsheet.worksheet("Stok_BBM")
    sheet_riwayat = spreadsheet.worksheet("Riwayat_Laporan")
except Exception as e:
    st.error(f"Gagal terhubung ke Google Sheets. Periksa konfigurasi secrets. Error: {e}")
    st.stop()

# --- FUNGSI AMBIL STOK TERAKHIR ---
def load_last_stock():
    try:
        data = sheet_stok.get_all_records()
        if data:
            last_row = data[-1]
            return {
                "ptl": float(last_row.get("Sisa_Ptl", 0.0)),
                "pmx": float(last_row.get("Sisa_Pmx", 0.0)),
                "sol": float(last_row.get("Sisa_Sol", 0.0)),
                "dex": float(last_row.get("Sisa_Dex", 0.0)),
            }
    except Exception:
        pass
    return {"ptl": 0.0, "pmx": 0.0, "sol": 0.0, "dex": 0.0}

last_stock = load_last_stock()

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
    
    # Produk 1: Pertalite
    st.markdown("#### **• Pertalite**")
    c1, c2, c3, c4 = st.columns(4)
    with c1: stok_awal_ptl = st.number_input("Stok Awal Ptl", min_value=0.0, value=last_stock["ptl"], step=10.0, key="sa_ptl")
    with c2: stok_masuk_ptl = st.number_input("Stok Masuk Ptl", min_value=0.0, step=10.0, key="sm_ptl")
    with c3: terjual_ptl = st.number_input("Terjual Ptl", min_value=0.0, step=10.0, key="tj_ptl")
    with c4: harga_ptl = st.number_input("Harga/Liter Ptl", value=10000.0, step=100.0, key="h_ptl")

    # Produk 2: Pertamax
    st.markdown("#### **• Pertamax**")
    d1, d2, d3, d4 = st.columns(4)
    with d1: stok_awal_pmx = st.number_input("Stok Awal Pmx", min_value=0.0, value=last_stock["pmx"], step=10.0, key="sa_pmx")
    with d2: stok_masuk_pmx = st.number_input("Stok Masuk Pmx", min_value=0.0, step=10.0, key="sm_pmx")
    with d3: terjual_pmx = st.number_input("Terjual Pmx", min_value=0.0, step=10.0, key="tj_pmx")
    with d4: harga_pmx = st.number_input("Harga/Liter Pmx", value=13000.0, step=100.0, key="h_pmx")

    # Produk 3: Biosolar
    st.markdown("#### **• Biosolar**")
    e1, e2, e3, e4 = st.columns(4)
    with e1: stok_awal_sol = st.number_input("Stok Awal Solar", min_value=0.0, value=last_stock["sol"], step=10.0, key="sa_sol")
    with e2: stok_masuk_sol = st.number_input("Stok Masuk Solar", min_value=0.0, step=10.0, key="sm_sol")
    with e3: terjual_sol = st.number_input("Terjual Solar", min_value=0.0, step=10.0, key="tj_sol")
    with e4: harga_sol = st.number_input("Harga/Liter Solar", value=6800.0, step=100.0, key="h_sol")

    # Produk 4: Dexlite
    st.markdown("#### **• Dexlite**")
    f1, f2, f3, f4 = st.columns(4)
    with f1: stok_awal_dex = st.number_input("Stok Awal Dex", min_value=0.0, value=last_stock["dex"], step=10.0, key="sa_dex")
    with f2: stok_masuk_dex = st.number_input("Stok Masuk Dex", min_value=0.0, step=10.0, key="sm_dex")
    with f3: terjual_dex = st.number_input("Terjual Dex", min_value=0.0, step=10.0, key="tj_dex")
    with f4: harga_dex = st.number_input("Harga/Liter Dex", value=14500.0, step=100.0, key="h_dex")

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
    
    catatan = st.text_area("Catatan / Kendala Hari Ini (Opsional)", placeholder="Contoh: Stok aman, pengiriman lancar.")

    # Tombol Generate
    submitted = st.form_submit_button("Generate Laporan & Simpan ke Google Sheets")

if submitted:
    # Hitung Stok Akhir
    stok_akhir_ptl = stok_awal_ptl + stok_masuk_ptl - terjual_ptl
    stok_akhir_pmx = stok_awal_pmx + stok_masuk_pmx - terjual_pmx
    stok_akhir_sol = stok_awal_sol + stok_masuk_sol - terjual_sol
    stok_akhir_dex = stok_awal_dex + stok_masuk_dex - terjual_dex

    # Hitung Rupiah
    rp_ptl = terjual_ptl * harga_ptl
    rp_pmx = terjual_pmx * harga_pmx
    rp_sol = terjual_sol * harga_sol
    rp_dex = terjual_dex * harga_dex
    
    total_penjualan_bbm = rp_ptl + rp_pmx + rp_sol + rp_dex
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

    # Simpan ke Google Sheets (Tab Stok_BBM)
    sheet_stok.append_row([str(tanggal), stok_akhir_ptl, stok_akhir_pmx, stok_akhir_sol, stok_akhir_dex])
    
    # Simpan ke Google Sheets (Tab Riwayat_Laporan)
    sheet_riwayat.append_row([
        str(tanggal), shift, pelapor, 
        total_penjualan_bbm, total_penjualan_oli, total_omzet_keseluruhan,
        setor_tunai, transfer_qris, piutang_bon, biaya_operasional, status_kas
    ])

    # Format Teks WhatsApp
    wa_output = f"""📊 *LAPORAN HARIAN OPERASIONAL & KEUANGAN SPBU*
📍 *Unit / Lokasi:* {lokasi}
📅 *Tanggal:* {tanggal.strftime('%d/%m/%Y')}
🕒 *Shift Operasional:* {shift}

--------------------------------------------------

⛽ *1. REKAP PENJUALAN & STOK BBM*
• *Pertalite:*
  - Terjual: {terjual_ptl:,.0f} L (Rp {rp_ptl:,.0f})
  - Stok (Awal {stok_awal_ptl:,.0f} | Masuk {stok_masuk_ptl:,.0f} | Sisa {stok_akhir_ptl:,.0f})
• *Pertamax:*
  - Terjual: {terjual_pmx:,.0f} L (Rp {rp_pmx:,.0f})
  - Stok (Awal {stok_awal_pmx:,.0f} | Masuk {stok_masuk_pmx:,.0f} | Sisa {stok_akhir_pmx:,.0f})
• *Biosolar:*
  - Terjual: {terjual_sol:,.0f} L (Rp {rp_sol:,.0f})
  - Stok (Awal {stok_awal_sol:,.0f} | Masuk {stok_masuk_sol:,.0f} | Sisa {stok_akhir_sol:,.0f})
• *Dexlite:*
  - Terjual: {terjual_dex:,.0f} L (Rp {rp_dex:,.0f})
  - Stok (Awal {stok_awal_dex:,.0f} | Masuk {stok_masuk_dex:,.0f} | Sisa {stok_akhir_dex:,.0f})

🔹 *Total Penjualan BBM:* *Rp {total_penjualan_bbm:,.0f}*

--------------------------------------------------

🛢️ *2. PENJUALAN OLI / PELUMAS*
• Oli Botol Kecil: {terjual_oli_kecil} Pcs (Rp {omzet_oli_kecil:,.0f})
• Oli Dirigen/Besar: {terjual_oli_besar} Pcs (Rp {omzet_oli_besar:,.0f})
🔹 *Total Penjualan Oli:* *Rp {total_penjualan_oli:,.0f}*

💰 *Total Omzet Keseluruhan:* *Rp {total_omzet_keseluruhan:,.0f}*

--------------------------------------------------

💳 *3. REKONSILIASI PEMBAYARAN*
• *Setoran Tunai (Cash):* Rp {setor_tunai:,.0f}
• *Transfer / EDC / QRIS:* Rp {transfer_qris:,.0f}
• *Piutang / DO Korporat:* Rp {piutang_bon:,.0f}
🔸 *Total Penerimaan:* *Rp {total_penerimaan:,.0f}*

--------------------------------------------------

📉 *4. PENGELUARAN & OPERASIONAL*
• Biaya Operasional Harian: Rp {biaya_operasional:,.0f}
🔹 *Total Pengeluaran:* *Rp {biaya_operasional:,.0f}*

--------------------------------------------------

🔍 *5. REKAP & STATUS KAS*
• Status Kas: *{status_kas}*

📝 *Catatan / Kendala:*
- {catatan if catatan else "Nihil"}

--------------------------------------------------
*Dilaporkan oleh:* {pelapor}"""

    st.success("Laporan berhasil dibuat dan otomatis tersimpan ke Google Sheets!")
    st.code(wa_output, language="text")
