import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from matplotlib.ticker import MultipleLocator
from supabase import create_client, Client
from datetime import date, datetime

# ==============================================================================
# KONEKSI KE DATABASE SUPABASE
# ==============================================================================

@st.cache_resource
def init_connection():
    """Membuat dan mengembalikan koneksi ke database Supabase."""
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Gagal terhubung ke Supabase: {e}")
        st.info("Pastikan Anda sudah mengatur SUPABASE_URL dan SUPABASE_KEY di Streamlit Secrets.")
        return None

supabase = init_connection()

# ==============================================================================
# FUNGSI-FUNGSI LOGIKA DAN PENGATURAN (ASLI DARI ANDA)
# ==============================================================================

def get_settings_wfa(age_in_months):
    if age_in_months <= 24: return {"xlim": (0, 24), "ylim": (0, 18), "xticks": range(0, 25, 1), "yticks": range(0, 19, 1), "x_major": 1, "x_minor": 0.2, "y_major": 1, "y_minor": 0.1, "age_range": "0-24 Bulan"}
    if age_in_months <= 60: return {"xlim": (24, 60), "ylim": (7, 30), "xticks": range(24, 61, 1), "yticks": range(7, 31, 1), "x_major": 1, "x_minor": 1, "y_major": 1, "y_minor": 0.1, "age_range": "24-60 Bulan"}
    else: return {"xlim": (60, 120), "ylim": (10, 60), "xticks": range(60, 121, 12), "yticks": range(10, 61, 5), "x_major": 12, "x_minor": 1, "y_major": 5, "y_minor": 1, "age_range": "5-10 Tahun"}

def get_interpretation_wfa(berat_anak, z_scores_at_age):
    if berat_anak > z_scores_at_age['SD3']: return "Berat badan sangat lebih", 'red'
    elif berat_anak > z_scores_at_age['SD2']: return "Berat badan lebih", 'yellow'
    elif berat_anak >= z_scores_at_age['SD1']: return "Berat cukup normal", 'lightgreen'
    elif berat_anak >= z_scores_at_age['SD1neg']: return "Berat badan normal", 'darkgreen'
    elif berat_anak > z_scores_at_age['SD2neg']: return "Berat cukup normal", 'lightgreen'
    elif berat_anak > z_scores_at_age['SD3neg']: return "Berat badan kurang", 'yellow'
    else: return "Berat badan kurang (Underweight)", 'red'

def get_settings_wfh(age_in_months):
    if age_in_months <= 24: return {"xlim": (45, 110), "ylim": (1, 25), "xticks": range(45, 111, 5), "yticks": range(1, 26, 2), "x_major": 5, "x_minor": 1, "y_major": 2, "y_minor": 0.5, "age_range": "0-24 Bulan"}
    else: return {"xlim": (65, 120), "ylim": (5, 31), "xticks": range(65, 121, 5), "yticks": range(5, 32, 2), "x_major": 5, "x_minor": 1, "y_major": 2, "y_minor": 0.5, "age_range": "24-60 Bulan"}

def get_interpretation_wfh(berat_anak, z_scores_at_length):
    if berat_anak > z_scores_at_length['SD3']: return "Gizi lebih (Obesitas)", 'red'
    elif berat_anak > z_scores_at_length['SD2']: return "Berisiko gizi lebih (Overweight)", 'yellow'
    elif berat_anak >= z_scores_at_length['SD2neg']: return "Gizi baik (Normal)", 'forestgreen'
    elif berat_anak >= z_scores_at_length['SD3neg']: return "Gizi kurang (Wasting)", 'yellow'
    else: return "Gizi buruk (Severe Wasting)", 'red'

def get_settings_bmi(age_in_months):
    if age_in_months <= 24: return {"xlim": (0, 24), "ylim": (9, 23), "xticks": range(0, 25, 1), "yticks": range(9, 24, 1), "x_major": 1, "x_minor": 1, "y_major": 1, "y_minor": 0.2, "age_range": "0-24 Bulan"}
    else: return {"xlim": (24, 60), "ylim": (11.6, 21), "xticks": np.arange(24, 61, 2), "yticks": range(12, 22, 1), "x_major": 2, "x_minor": 2, "y_major": 1, "y_minor": 0.1, "age_range": "24-60 Bulan"}

def get_interpretation_bmi(bmi_anak, z_scores_at_age):
    if bmi_anak > z_scores_at_age['SD3']: return "Gizi lebih (Obesitas)", 'red'
    elif bmi_anak > z_scores_at_age['SD2']: return "Berisiko gizi lebih (Overweight)", 'yellow'
    elif bmi_anak >= z_scores_at_age['SD2neg']: return "Gizi baik (Normal)", 'forestgreen'
    elif bmi_anak >= z_scores_at_age['SD3neg']: return "Gizi kurang (Wasting)", 'yellow'
    else: return "Gizi buruk (Severe Wasting)", 'red'

def get_settings_lhfa(age_in_months):
    if age_in_months <= 6: return {"xlim": (0, 6), "ylim": (43, 75), "xticks": range(0, 7, 1), "yticks": range(43, 76, 5), "x_major": 1, "x_minor": 1, "y_major": 5, "y_minor": 1, "age_range_title": "0-6 Bulan"}
    elif 6 < age_in_months <= 24: return {"xlim": (6, 24), "ylim": (60, 100), "xticks": range(6, 25, 1), "yticks": range(60, 101, 5), "x_major": 1, "x_minor": 1, "y_major": 5, "y_minor": 1, "age_range_title": "6-24 Bulan"}
    else: return {"xlim": (24, 60), "ylim": (76, 125), "xticks": range(24, 61, 2), "yticks": range(76, 126, 5), "x_major": 2, "x_minor": 1, "y_major": 5, "y_minor": 1, "age_range_title": "2-5 Tahun"}

def get_interpretation_lhfa(panjang_anak, z_scores_at_age):
    if 'SD2' not in z_scores_at_age or 'SD2neg' not in z_scores_at_age or 'SD3neg' not in z_scores_at_age: return "Data tidak lengkap untuk interpretasi", "gray"
    if panjang_anak > z_scores_at_age['SD2']: return "Tinggi", 'forestgreen'
    elif panjang_anak >= z_scores_at_age['SD2neg']: return "Normal", 'forestgreen'
    elif panjang_anak >= z_scores_at_age['SD3neg']: return "Pendek (Stunting)", 'yellow'
    else: return "Sangat Pendek (Severe Stunting)", 'red'

def get_settings_hcfa(age_in_months):
    if age_in_months <= 24: return {"xlim": (0, 24), "ylim": (32, 52), "age_range_title": "0-24 Bulan"}
    else: return {"xlim": (24, 60), "ylim": (42, 56), "age_range_title": "2-5 Tahun"}

def get_interpretation_hcfa(hc_anak, z_scores_at_age):
    if hc_anak > z_scores_at_age['SD2']: return "Makrosefali (Perlu evaluasi medis)", 'yellow'
    elif hc_anak >= z_scores_at_age['SD2neg']: return "Normal", 'forestgreen'
    else: return "Mikrosefali (Perlu evaluasi medis)", 'yellow'

# ==============================================================================
# HALAMAN-HALAMAN APLIKASI
# ==============================================================================

def page_input_data():
    st.header("📝 Input Pengukuran Baru")
    if not supabase: return

    # --- PERUBAHAN UTAMA: Menambahkan pilihan jenis input ---
    input_type = st.radio(
        "Pilih jenis input:",
        ('Anak yang Sudah Terdaftar', 'Daftarkan Anak Baru'),
        horizontal=True,
        label_visibility="collapsed"
    )

    # --- ALUR KERJA BARU UNTUK ANAK TERDAFTAR ---
    if input_type == 'Anak yang Sudah Terdaftar':
        try:
            response = supabase.table("data_pengukuran").select("id_anak, nama_anak, tanggal_lahir, jenis_kelamin").execute()
            if not response.data:
                st.warning("Belum ada data anak yang terdaftar. Silakan daftarkan anak baru terlebih dahulu.")
                return

            df_anak = pd.DataFrame(response.data).drop_duplicates(subset=['id_anak'])
            df_anak['display_name'] = df_anak['nama_anak'] + " (" + df_anak['id_anak'] + ")"
            
            option_list = ["-"] + sorted(df_anak['display_name'].tolist())
            selected_display_name = st.selectbox("Pilih Anak:", option_list)

            if selected_display_name and selected_display_name != "-":
                selected_child_data = df_anak[df_anak['display_name'] == selected_display_name].iloc[0]
                
                with st.form("existing_child_form", clear_on_submit=True):
                    st.write("Data Anak (tidak bisa diubah):")
                    st.text_input("ID Anak", value=selected_child_data['id_anak'], disabled=True)
                    st.text_input("Nama Anak", value=selected_child_data['nama_anak'], disabled=True)
                    
                    st.divider()
                    st.write("Masukkan data pengukuran baru:")
                    tanggal_pengukuran = st.date_input("Tanggal Pengukuran", max_value=date.today())
                    berat_kg = st.number_input("Berat Badan (kg)", min_value=0.0, step=0.1, format="%.2f")
                    tinggi_cm = st.number_input("Tinggi/Panjang Badan (cm)", min_value=0.0, step=0.5, format="%.1f")
                    lingkar_kepala_cm = st.number_input("Lingkar Kepala (cm)", min_value=0.0, step=0.5, format="%.1f")

                    submitted = st.form_submit_button("Simpan Pengukuran")
                    if submitted:
                        if not all([berat_kg > 0, tinggi_cm > 0]):
                            st.warning("Harap isi data pengukuran (Berat dan Tinggi).")
                        else:
                            try:
                                tanggal_lahir_dt = datetime.strptime(selected_child_data['tanggal_lahir'], '%Y-%m-%d').date()
                                usia_bulan = (tanggal_pengukuran.year - tanggal_lahir_dt.year) * 12 + (tanggal_pengukuran.month - tanggal_lahir_dt.month)
                                data_to_insert = {
                                    "id_anak": selected_child_data['id_anak'], "nama_anak": selected_child_data['nama_anak'],
                                    "tanggal_lahir": str(tanggal_lahir_dt), "jenis_kelamin": selected_child_data['jenis_kelamin'],
                                    "tanggal_pengukuran": str(tanggal_pengukuran), "usia_bulan": int(usia_bulan), 
                                    "berat_kg": berat_kg, "tinggi_cm": tinggi_cm, "lingkar_kepala_cm": lingkar_kepala_cm
                                }
                                supabase.table("data_pengukuran").insert(data_to_insert).execute()
                                st.success(f"Data pengukuran baru untuk {selected_child_data['nama_anak']} berhasil disimpan!")
                            except Exception as e:
                                st.error(f"Gagal menyimpan data: {e}")
        except Exception as e:
            st.error(f"Gagal mengambil daftar anak: {e}")

    # --- ALUR KERJA UNTUK ANAK BARU (SEPERTI SEBELUMNYA) ---
    elif input_type == 'Daftarkan Anak Baru':
        with st.form("new_child_form", clear_on_submit=True):
            st.write("Masukkan data anak dan hasil pengukuran pertama:")
            id_anak = st.text_input("ID Anak (contoh: NIK, No. KMS)", help="ID unik untuk setiap anak.")
            nama_anak = st.text_input("Nama Anak")
            tanggal_lahir = st.date_input("Tanggal Lahir", max_value=date.today(), value=date(2023, 1, 1))
            jenis_kelamin = st.radio("Jenis Kelamin", ('L', 'P'), format_func=lambda x: 'Laki-laki' if x == 'L' else 'Perempuan')
            
            st.divider()
            
            tanggal_pengukuran = st.date_input("Tanggal Pengukuran", max_value=date.today())
            berat_kg = st.number_input("Berat Badan (kg)", min_value=0.0, step=0.1, format="%.2f")
            tinggi_cm = st.number_input("Tinggi/Panjang Badan (cm)", min_value=0.0, step=0.5, format="%.1f")
            lingkar_kepala_cm = st.number_input("Lingkar Kepala (cm)", min_value=0.0, step=0.5, format="%.1f")
            
            submitted = st.form_submit_button("Daftarkan dan Simpan Pengukuran")
            if submitted:
                if not all([id_anak, nama_anak, berat_kg > 0, tinggi_cm > 0]):
                    st.warning("Harap isi semua field yang wajib (ID, Nama, Tanggal Lahir, Berat, Tinggi).")
                else:
                    try:
                        usia_bulan = (tanggal_pengukuran.year - tanggal_lahir.year) * 12 + (tanggal_pengukuran.month - tanggal_lahir.month)
                        data_to_insert = {"id_anak": id_anak, "nama_anak": nama_anak, "tanggal_lahir": str(tanggal_lahir), "jenis_kelamin": jenis_kelamin, "tanggal_pengukuran": str(tanggal_pengukuran), "usia_bulan": int(usia_bulan), "berat_kg": berat_kg, "tinggi_cm": tinggi_cm, "lingkar_kepala_cm": lingkar_kepala_cm}
                        supabase.table("data_pengukuran").insert(data_to_insert).execute()
                        st.success(f"Anak baru bernama {nama_anak} berhasil didaftarkan dan data pengukurannya disimpan!")
                    except Exception as e:
                        st.error(f"Gagal menyimpan data: {e}")

def page_view_history():
    st.header("📊 Lihat Riwayat & Kelola Data")
    if not supabase: return

    try:
        response = supabase.table("data_pengukuran").select("id_anak, nama_anak").execute()
        if not response.data:
            st.info("Belum ada data yang tersimpan. Silakan input data baru terlebih dahulu.")
            return

        df_anak = pd.DataFrame(response.data).drop_duplicates(subset=['id_anak'])
        df_anak['display_name'] = df_anak['nama_anak'] + " (" + df_anak['id_anak'] + ")"
        option_list = ["-"] + sorted(df_anak['display_name'].tolist())
        selected_display_name = st.selectbox("Pilih Anak:", option_list)

        if selected_display_name and selected_display_name != "-":
            selected_id = df_anak[df_anak['display_name'] == selected_display_name]['id_anak'].iloc[0]
            history_response = supabase.table("data_pengukuran").select("*").eq("id_anak", selected_id).order("usia_bulan").execute()
            
            if not history_response.data:
                st.warning("Tidak ada riwayat pengukuran untuk anak ini.")
                return

            history_df = pd.DataFrame(history_response.data)
            st.subheader(f"Riwayat Pengukuran untuk: {history_df['nama_anak'].iloc[0]}")
            st.dataframe(history_df[['tanggal_pengukuran', 'usia_bulan', 'berat_kg', 'tinggi_cm', 'lingkar_kepala_cm', 'lingkar_lengan_cm']])
            
            plot_all_curves(history_df)
            
            st.divider()
            st.subheader("⚙️ Kelola Data Pengukuran")
            
            history_df['display_entry'] = "Data tanggal " + pd.to_datetime(history_df['created_at']).dt.strftime('%Y-%m-%d %H:%M') + " (Usia: " + history_df['usia_bulan'].astype(str) + " bln)"
            entry_to_manage = st.selectbox("Pilih data yang ingin dikelola:", history_df['display_entry'])
            selected_entry = history_df[history_df['display_entry'] == entry_to_manage].iloc[0]
            
            with st.expander("Revisi Data Terpilih"):
                with st.form("edit_form"):
                    st.write(f"Mengubah data untuk pengukuran tanggal **{pd.to_datetime(selected_entry['created_at']).strftime('%Y-%m-%d')}**")
                    edit_berat = st.number_input("Berat (kg)", value=float(selected_entry['berat_kg']))
                    edit_tinggi = st.number_input("Tinggi (cm)", value=float(selected_entry['tinggi_cm']))
                    edit_lingkar_kepala = st.number_input("Lingkar Kepala (cm)", value=float(selected_entry['lingkar_kepala_cm']))
                    
                    if st.form_submit_button("Simpan Perubahan"):
                        try:
                            update_data = {"berat_kg": edit_berat, "tinggi_cm": edit_tinggi, "lingkar_kepala_cm": edit_lingkar_kepala}
                            supabase.table("data_pengukuran").update(update_data).eq("id", int(selected_entry['id'])).execute()
                            st.success("Data berhasil diperbarui! Memuat ulang halaman..."); st.rerun()
                        except Exception as e: st.error(f"Gagal memperbarui data: {e}")

            with st.expander("Hapus Data Terpilih"):
                st.warning("PERHATIAN: Tindakan ini tidak dapat diurungkan.")
                if st.checkbox(f"Saya yakin ingin menghapus data pengukuran tanggal {pd.to_datetime(selected_entry['created_at']).strftime('%Y-%m-%d')}."):
                    if st.button("Hapus Permanen"):
                        try:
                            supabase.table("data_pengukuran").delete().eq("id", int(selected_entry['id'])).execute()
                            st.success("Data berhasil dihapus! Memuat ulang halaman..."); st.rerun()
                        except Exception as e: st.error(f"Gagal menghapus data: {e}")
    except Exception as e:
        st.error(f"Gagal mengambil data dari Supabase: {e}")

# ==============================================================================
# FUNGSI PLOTTING UTAMA (LENGKAP)
# ==============================================================================

def plot_all_curves(history_df):
    st.header("Hasil Analisis Pertumbuhan")
    plot_wfa(history_df)
    st.markdown("---")
    plot_wfh(history_df)
    st.markdown("---")
    plot_bmi(history_df)
    st.markdown("---")
    plot_lhfa(history_df)
    st.markdown("---")
    plot_hcfa(history_df)

def plot_wfa(history_df):
    st.subheader("1. Berat Badan menurut Umur")
    try:
        latest_data = history_df.iloc[-1]
        kelamin, umur_terakhir, berat_terakhir = latest_data['jenis_kelamin'], float(latest_data['usia_bulan']), float(latest_data['berat_kg'])
        settings = get_settings_wfa(umur_terakhir)
        gender_text = "Perempuan" if kelamin == 'P' else "Laki-laki"
        
        if umur_terakhir <= 60: nama_file = f"wfa_{'girls' if kelamin == 'P' else 'boys'}_0-to-5-years_zscores.xlsx"
        else: nama_file = f"wfa_{'girls' if kelamin == 'P' else 'boys'}_5-to-10-years_zscores.xlsx"
        
        judul = f'Grafik Berat Badan vs Umur - Anak {gender_text} ({settings["age_range"]})'
        df_std = pd.read_excel(nama_file)
        
        x_original, z_cols = df_std['Month'], ['SD3neg', 'SD2neg', 'SD1neg', 'SD0', 'SD1', 'SD2', 'SD3']
        poly_funcs = {col: np.poly1d(np.polyfit(x_original, df_std[col], 5)) for col in z_cols}
        z_scores_at_age = {col: func(umur_terakhir) for col, func in poly_funcs.items()}
        interpretasi, warna = get_interpretation_wfa(berat_terakhir, z_scores_at_age)
        st.info(f"Berat Badan: {interpretasi}")
        
        x_smooth = np.linspace(df_std['Month'].min(), df_std['Month'].max(), 500)
        smooth_data = {col: func(x_smooth) for col, func in poly_funcs.items()}
        
        fig, ax = plt.subplots(figsize=(12, 7))
        # --- KODE FORMATTING ASLI ANDA ---
        fig.set_facecolor('steelblue' if kelamin == 'L' else 'hotpink')
        ax.fill_between(x_smooth, smooth_data['SD3neg'], smooth_data['SD2neg'], color='yellow', alpha=0.5)
        ax.fill_between(x_smooth, smooth_data['SD2neg'], smooth_data['SD1neg'], color='lightgreen', alpha=0.4)
        ax.fill_between(x_smooth, smooth_data['SD1neg'], smooth_data['SD1'], color='darkgreen', alpha=0.4)
        ax.fill_between(x_smooth, smooth_data['SD1'], smooth_data['SD2'], color='lightgreen', alpha=0.5)
        ax.fill_between(x_smooth, smooth_data['SD2'], smooth_data['SD3'], color='yellow', alpha=0.5)
        for col, data in smooth_data.items(): ax.plot(x_smooth, data, color='black' if col not in ['SD3neg', 'SD3'] else 'red', lw=1)
        ax.plot(history_df['usia_bulan'].astype(float), history_df['berat_kg'].astype(float), marker='o', linestyle='-', color='darkviolet', label='Riwayat Pertumbuhan')
        ax.scatter(umur_terakhir, berat_terakhir, marker='*', c='cyan', s=300, ec='black', zorder=10, label='Pengukuran Terakhir')
        props = dict(boxstyle='round', facecolor=warna, alpha=0.8)
        ax.text(0.03, 0.97, f"Interpretasi: {interpretasi}", transform=ax.transAxes, fontsize=12, va='top', bbox=props)
        ax.set_title(judul, pad=20, fontsize=16, color='white', fontweight='bold')
        if umur_terakhir > 60: ax.set_xlabel('Umur', fontsize=12, color='white', labelpad=26)
        else: ax.set_xlabel('Umur (Bulan)', fontsize=12, color='white')
        ax.set_ylabel('Berat Badan (kg)', fontsize=12, color='white')
        ax.set_xlim(settings["xlim"]); ax.set_ylim(settings["ylim"]); ax.set_xticks(settings["xticks"]); ax.set_yticks(settings["yticks"])
        ax.grid(which='major', axis='y', linestyle='-', linewidth='0.8', color='gray'); ax.grid(which='minor', axis='y', linestyle=':', linewidth='0.5', color='lightgray')
        ax2 = ax.twinx(); ax2.set_ylim(ax.get_ylim())
        ax.xaxis.set_major_locator(MultipleLocator(settings["x_major"])); ax.xaxis.set_minor_locator(MultipleLocator(settings["x_minor"]))
        ax.yaxis.set_major_locator(MultipleLocator(settings["y_major"])); ax2.yaxis.set_major_locator(MultipleLocator(settings["y_major"]))
        ax.yaxis.set_minor_locator(MultipleLocator(settings["y_minor"])); ax2.yaxis.set_minor_locator(MultipleLocator(settings["y_minor"]))
        for spine_position in ['top', 'bottom', 'left', 'right']: ax.spines[spine_position].set_visible(False); ax2.spines[spine_position].set_visible(False)
        ax.tick_params(which='minor', axis='x', length=0); ax.tick_params(which='minor', axis='y', length=0)
        ax.tick_params(which='major', axis='x', labelcolor='white', length=0); ax.tick_params(which='major', axis='y', labelcolor='white', length=0)
        ax2.tick_params(which='both', axis='y', labelcolor='white', length=0)
        ax.grid(which='major', linestyle='-', linewidth='0.8', color='gray'); ax.grid(which='minor', axis='y', linestyle=':', linewidth='0.7', color='gray')
        if umur_terakhir > 60:
            major_x_ticks = [60, 72, 84, 96, 108, 120]; ax.set_xticks(major_x_ticks); ax.grid(which='major', axis='x', linestyle='-', linewidth='0.8', color='gray'); ax.tick_params(axis='x', labelbottom=False)
            month_to_year = {60: '5', 72: '6', 84: '7', 96: '8', 108: '9', 120: '10'}; posisi_y_tahun = settings["ylim"][0] - 1.5
            for bulan, tahun in month_to_year.items():
                ax.text(bulan, posisi_y_tahun, tahun, ha='center', va='top', fontsize=12, color='white', fontweight='bold')
                ax.text(bulan, posisi_y_tahun - 1.2, 'Tahun', ha='center', va='top', fontsize=8, color='white')
            posisi_y_bulan, posisi_y_teks = settings["ylim"][0] - 0.8, settings["ylim"][0] - 1.4
            for awal_tahun_bulan in range(60, 120, 12):
                for tambahan_bulan in [3, 6, 9]:
                    posisi_x = awal_tahun_bulan + tambahan_bulan
                    ax.axvline(x=posisi_x, color='gray', linestyle=':', linewidth=0.7, zorder=0)
                    ax.text(posisi_x, posisi_y_bulan, str(tambahan_bulan), ha='center', va='top', fontsize=8, color='white')
                    ax.text(posisi_x, posisi_y_teks, "Bulan", ha='center', va='top', fontsize=6, color='white')
        ax.legend(loc='lower right'); fig.tight_layout()
        st.pyplot(fig)
    except Exception as e: st.error(f"Gagal membuat plot WfA: {e}")

def plot_wfh(history_df):
    st.subheader("2. Berat Badan menurut Tinggi/Panjang")
    try:
        latest_data = history_df.iloc[-1]
        kelamin, umur_terakhir, tinggi_terakhir, berat_terakhir = latest_data['jenis_kelamin'], float(latest_data['usia_bulan']), float(latest_data['tinggi_cm']), float(latest_data['berat_kg'])
        settings = get_settings_wfh(umur_terakhir)
        gender_text = "Perempuan" if kelamin == 'P' else "Laki-laki"
        if umur_terakhir <= 24: nama_file, x_axis_label, judul, x_col_name = f"wfl_{'girls' if kelamin == 'P' else 'boys'}_0-to-2-years_zscores.xlsx", "Panjang Badan (cm)", f'Grafik Berat Badan vs Panjang Badan - {gender_text}', 'Length'
        else: nama_file, x_axis_label, judul, x_col_name = f"wfh_{'girls' if kelamin == 'P' else 'boys'}_2-to-5-years_zscores.xlsx", "Tinggi Badan (cm)", f'Grafik Berat Badan vs Tinggi Badan - {gender_text}', 'Height'
        
        df_std = pd.read_excel(nama_file)
        df_std = df_std.rename(columns={x_col_name: 'PanjangTinggi'}).sort_values(by='PanjangTinggi').drop_duplicates(subset='PanjangTinggi')
        x_original, z_cols = df_std['PanjangTinggi'], ['SD3neg', 'SD2neg', 'SD1neg', 'SD0', 'SD1', 'SD2', 'SD3']
        poly_funcs = {col: np.poly1d(np.polyfit(x_original, df_std[col], 5)) for col in z_cols}
        z_scores_at_length = {col: poly_funcs[col](tinggi_terakhir) for col in z_cols}
        interpretasi, warna = get_interpretation_wfh(berat_terakhir, z_scores_at_length)
        st.info(f"Status Gizi: {interpretasi}")
        
        x_smooth = np.linspace(x_original.min(), x_original.max(), 500)
        smooth_data = {col: func(x_smooth) for col, func in poly_funcs.items()}
        fig, ax = plt.subplots(figsize=(12, 7))
        # --- KODE FORMATTING ASLI ANDA ---
        fig.set_facecolor('steelblue' if kelamin == 'L' else 'hotpink')
        ax.fill_between(x_smooth, smooth_data['SD3neg'], smooth_data['SD2neg'], color='yellow', alpha=0.5)
        ax.fill_between(x_smooth, smooth_data['SD2neg'], smooth_data['SD2'], color='green', alpha=0.4)
        ax.fill_between(x_smooth, smooth_data['SD2'], smooth_data['SD3'], color='yellow', alpha=0.5)
        for col, data in smooth_data.items(): ax.plot(x_smooth, data, color='black' if col not in ['SD3neg', 'SD3'] else 'red', lw=1)
        ax.plot(history_df['tinggi_cm'].astype(float), history_df['berat_kg'].astype(float), marker='o', linestyle='-', color='darkviolet', label='Riwayat Pertumbuhan')
        ax.scatter(tinggi_terakhir, berat_terakhir, marker='*', c='cyan', s=300, ec='black', zorder=10, label='Pengukuran Terakhir')
        props = dict(boxstyle='round', facecolor=warna, alpha=0.8)
        ax.text(0.03, 0.97, f"Status Gizi: {interpretasi}", transform=ax.transAxes, fontsize=12, va='top', bbox=props)
        ax.set_title(judul, pad=20, fontsize=16, color='white', fontweight='bold')
        ax.set_xlabel(x_axis_label, fontsize=12, color='white')
        ax.set_ylabel('Berat Badan (kg)', fontsize=12, color='white')
        ax.set_xlim(settings["xlim"]); ax.set_ylim(settings["ylim"]); ax.set_xticks(settings["xticks"]); ax.set_yticks(settings["yticks"])
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.legend(loc='lower right'); fig.tight_layout()
        st.pyplot(fig)
    except Exception as e: st.error(f"Gagal membuat plot WfH: {e}")

def plot_bmi(history_df):
    st.subheader("3. Indeks Massa Tubuh (IMT) Menurut Umur")
    try:
        latest_data = history_df.iloc[-1]
        kelamin, umur_terakhir, tinggi_terakhir, berat_terakhir = latest_data['jenis_kelamin'], float(latest_data['usia_bulan']), float(latest_data['tinggi_cm']), float(latest_data['berat_kg'])
        if tinggi_terakhir == 0: st.error("Tinggi badan nol, IMT tidak dapat dihitung."); return
        
        bmi_terakhir = berat_terakhir / ((tinggi_terakhir / 100) ** 2)
        #t.info(f"IMT: {bmi_terakhir:.2f} kg/m²")

        history_df['bmi'] = history_df['berat_kg'].astype(float) / ((history_df['tinggi_cm'].astype(float) / 100) ** 2)
        
        settings = get_settings_bmi(umur_terakhir)
        gender_text = "Perempuan" if kelamin == 'P' else "Laki-laki"
        if umur_terakhir <= 24: nama_file = f"bmi_{'girls' if kelamin == 'P' else 'boys'}_0-to-2-years_zscores.xlsx"
        else: nama_file = f"bmi_{'girls' if kelamin == 'P' else 'boys'}_2-to-5-years_zscores.xlsx"
        
        judul = f'Grafik IMT vs Umur - Anak {gender_text} ({settings["age_range"]})'
        df_std = pd.read_excel(nama_file)
        df_std = df_std.sort_values(by='Month').drop_duplicates(subset='Month')
        x_original, z_cols = df_std['Month'], ['SD3neg', 'SD2neg', 'SD1neg', 'SD0', 'SD1', 'SD2', 'SD3']
        poly_funcs = {col: np.poly1d(np.polyfit(x_original, df_std[col], 5)) for col in z_cols}
        z_scores_at_age = {col: func(umur_terakhir) for col, func in poly_funcs.items()}
        interpretasi, warna = get_interpretation_bmi(bmi_terakhir, z_scores_at_age)

        st.info(f"IMT: {bmi_terakhir:.2f} kg/m² ({interpretasi})")
        #st.info(f"Berat Badan: {interpretasi}")
        
        x_smooth = np.linspace(0, 60, 500)
        smooth_data = {col: func(x_smooth) for col, func in poly_funcs.items()}
        fig, ax = plt.subplots(figsize=(12, 7))
        # --- KODE FORMATTING ASLI ANDA ---
        fig.set_facecolor('steelblue' if kelamin == 'L' else 'hotpink')
        ax.fill_between(x_smooth, smooth_data['SD3neg'], smooth_data['SD2neg'], color='yellow', alpha=0.5)
        ax.fill_between(x_smooth, smooth_data['SD2neg'], smooth_data['SD2'], color='green', alpha=0.4)
        ax.fill_between(x_smooth, smooth_data['SD2'], smooth_data['SD3'], color='yellow', alpha=0.5)
        for col, data in smooth_data.items(): ax.plot(x_smooth, data, color='black' if col not in ['SD3neg', 'SD3'] else 'red', lw=1)
        ax.plot(history_df['usia_bulan'].astype(float), history_df['bmi'].astype(float), marker='o', linestyle='-', color='darkviolet', label='Riwayat IMT')
        ax.scatter(umur_terakhir, bmi_terakhir, marker='*', c='cyan', s=300, ec='black', zorder=10, label=f'IMT Terakhir')
        ax.text(umur_terakhir + 0.3, bmi_terakhir, f'{bmi_terakhir:.2f}', fontsize=11, color='darkviolet', va='center')
        props = dict(boxstyle='round', facecolor=warna, alpha=0.8)
        ax.text(0.03, 0.97, f"Status Gizi: {interpretasi}", transform=ax.transAxes, fontsize=12, va='top', bbox=props)
        ax.set_title(judul, pad=20, fontsize=16, color='white', fontweight='bold')
        ax.set_xlabel('Umur (Bulan)', fontsize=12, color='white'); ax.set_ylabel('IMT (kg/m²)', fontsize=12, color='white')
        ax.set_xlim(settings["xlim"]); ax.set_ylim(settings["ylim"]); ax.set_xticks(settings["xticks"]); ax.set_yticks(settings["yticks"])
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.legend(loc='lower right'); fig.tight_layout()
        st.pyplot(fig)
    except Exception as e: st.error(f"Gagal membuat plot BMI: {e}")

def plot_lhfa(history_df):
    st.subheader("4. Panjang/Tinggi Badan Menurut Umur")
    try:
        latest_data = history_df.iloc[-1]
        kelamin, umur_terakhir, panjang_terakhir = latest_data['jenis_kelamin'], float(latest_data['usia_bulan']), float(latest_data['tinggi_cm'])
        settings = get_settings_lhfa(umur_terakhir)
        gender_text = "Perempuan" if kelamin == 'P' else "Laki-laki"
        gender_file_key = 'girls' if kelamin == 'P' else 'boys'
        if umur_terakhir <= 24:
            df_mingguan = pd.read_excel(f"lhfa_{gender_file_key}_0-to-13-weeks_zscores.xlsx")
            df_bulanan = pd.read_excel(f"lhfa_{gender_file_key}_0-to-2-years_zscores.xlsx")
            df_mingguan['Month'] = df_mingguan['Week'] / 4.345
            df_to_process = pd.concat([df_mingguan, df_bulanan], ignore_index=True).sort_values(by='Month').drop_duplicates(subset='Month', keep='first')
        else:
            df_to_process = pd.read_excel(f"lhfa_{gender_file_key}_2-to-5-years_zscores.xlsx")
        
        judul = f'Grafik Panjang/Tinggi Badan vs Umur - {gender_text} ({settings["age_range_title"]})'
        x_original = df_to_process['Month']
        df_to_process = df_to_process.rename(columns={'SD-3': 'SD3neg', 'SD-2': 'SD2neg', 'SD-1': 'SD1neg'})
        z_cols = ['SD3neg', 'SD2neg', 'SD1neg', 'SD0', 'SD1', 'SD2', 'SD3']
        poly_funcs = {col: np.poly1d(np.polyfit(x_original, df_to_process[col], 3)) for col in z_cols}
        z_scores_at_age = {col: func(umur_terakhir) for col, func in poly_funcs.items()}
        z_scores_at_age['SD_2'] = z_scores_at_age.get('SD2neg'); z_scores_at_age['SD_3'] = z_scores_at_age.get('SD3neg')
        interpretasi, warna = get_interpretation_lhfa(panjang_terakhir, z_scores_at_age)
        st.info(f"Panjang/Tinggi Badan: {interpretasi}")
        
        x_smooth = np.linspace(x_original.min(), x_original.max(), 500)
        smooth_data = {col: func(x_smooth) for col, func in poly_funcs.items()}
        fig, ax = plt.subplots(figsize=(12, 7))
        # --- KODE FORMATTING ASLI ANDA ---
        fig.set_facecolor('steelblue' if kelamin == 'L' else 'hotpink')
        line_colors = {'SD3': 'black', 'SD2': 'red', 'SD1':'black', 'SD0': 'green', 'SD1neg':'black', 'SD2neg': 'red', 'SD3neg': 'black'}
        for col, data in smooth_data.items():
            if col in line_colors: ax.plot(x_smooth, data, color=line_colors[col], lw=1.5)
        ax.plot(history_df['usia_bulan'].astype(float), history_df['tinggi_cm'].astype(float), marker='o', linestyle='-', color='darkviolet', label='Riwayat Pertumbuhan')
        ax.scatter(umur_terakhir, panjang_terakhir, marker='*', c='cyan', s=300, ec='black', zorder=10, label='Pengukuran Terakhir')
        props = dict(boxstyle='round', facecolor=warna, alpha=0.8)
        ax.text(0.03, 0.97, f"Interpretasi: {interpretasi}", transform=ax.transAxes, fontsize=12, va='top', bbox=props)
        ax.set_title(judul, pad=20, fontsize=16, color='white', fontweight='bold')
        ax.set_xlabel("Umur (Bulan)", fontsize=12, color='white'); ax.set_ylabel('Panjang/Tinggi Badan (cm)', fontsize=12, color='white')
        ax.set_xlim(settings["xlim"]); ax.set_ylim(settings["ylim"]); ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.legend(loc='lower right'); fig.tight_layout()
        st.pyplot(fig)
    except Exception as e: st.error(f"Gagal membuat plot L/H-f-A: {e}")

def plot_hcfa(history_df):
    st.subheader("5. Lingkar Kepala Menurut Umur")
    try:
        latest_data = history_df.iloc[-1]
        kelamin, umur_terakhir, hc_terakhir = latest_data['jenis_kelamin'], float(latest_data['usia_bulan']), float(latest_data['lingkar_kepala_cm'])
        settings = get_settings_hcfa(umur_terakhir)
        gender_text = "Perempuan" if kelamin == 'P' else "Laki-laki"
        gender_file_key = 'girls' if kelamin == 'P' else 'boys'
        judul = f'Grafik Lingkar Kepala vs Umur - {gender_text} ({settings["age_range_title"]})'
        
        df_mingguan = pd.read_excel(f"hcfa_{gender_file_key}_0-13-zscores.xlsx")
        df_bulanan = pd.read_excel(f"hcfa_{gender_file_key}_0-5-zscores.xlsx")
        df_mingguan['Month'] = df_mingguan['Week'] / 4.345
        df_to_process = pd.concat([df_mingguan, df_bulanan], ignore_index=True).sort_values(by='Month').drop_duplicates(subset='Month', keep='first')
        df_to_process = df_to_process.rename(columns={'SD-3': 'SD3neg', 'SD-2': 'SD2neg', 'SD-1': 'SD1neg'})
        
        x_original, z_cols = df_to_process['Month'], ['SD3neg', 'SD2neg', 'SD1neg', 'SD0', 'SD1', 'SD2', 'SD3']
        poly_funcs = {col: np.poly1d(np.polyfit(x_original, df_to_process[col], 5)) for col in z_cols}
        z_scores_at_age = {col: func(umur_terakhir) for col, func in poly_funcs.items()}
        interpretasi, warna = get_interpretation_hcfa(hc_terakhir, z_scores_at_age)
        st.info(f"Lingkar Kepala: {interpretasi}")
        
        x_smooth = np.linspace(0, 60, 500)
        smooth_data = {col: func(x_smooth) for col, func in poly_funcs.items()}
        fig, ax = plt.subplots(figsize=(12, 7))
        # --- KODE FORMATTING ASLI ANDA ---
        fig.set_facecolor('steelblue' if kelamin == 'L' else 'hotpink')
        line_colors = {'SD3': 'black', 'SD2': 'red', 'SD1': 'orange', 'SD0': 'green', 'SD1neg': 'orange', 'SD2neg': 'red', 'SD3neg': 'black'}
        for col, data in smooth_data.items():
            if col in line_colors: ax.plot(x_smooth, data, color=line_colors[col], lw=1.5)
        for col, data in smooth_data.items():
            if col in ['SD3', 'SD2', 'SD0', 'SD2neg', 'SD3neg']:
                label_text = col.replace('neg', '-').replace('SD', '')
                ax.text(x_smooth[-1] + (settings['xlim'][1] * 0.01), data[-1], label_text, color=line_colors[col], va='center', ha='left', fontweight='bold')
        ax.plot(history_df['usia_bulan'].astype(float), history_df['lingkar_kepala_cm'].astype(float), marker='o', linestyle='-', color='darkviolet', label='Riwayat Pertumbuhan')
        ax.scatter(umur_terakhir, hc_terakhir, marker='*', c='cyan', s=300, ec='black', zorder=10, label='Pengukuran Terakhir')
        props = dict(boxstyle='round', facecolor=warna, alpha=0.8)
        ax.text(0.03, 0.97, f"Interpretasi: {interpretasi}", transform=ax.transAxes, fontsize=12, va='top', bbox=props)
        ax.set_title(judul, pad=20, fontsize=16, color='white', fontweight='bold')
        ax.set_xlabel("Umur (Bulan)", fontsize=12); ax.set_ylabel('Lingkar Kepala (cm)', fontsize=12)
        ax.set_xlim(settings["xlim"]); ax.set_ylim(settings["ylim"]); ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.legend(loc='lower right'); fig.tight_layout()
        st.pyplot(fig)
    except Exception as e: st.error(f"Gagal membuat plot HCFA: {e}")

# ==============================================================================
# BAGIAN UTAMA APLIKASI (MAIN)
# ==============================================================================

st.set_page_config(page_title="Aplikasi KMS Posyandu", layout="wide")
st.title("👶 Aplikasi KMS Posyandu Mawar - KBU")

st.sidebar.title("Menu Navigasi")
page_options = ["📝 Input Pengukuran Baru", "📊 Lihat Riwayat & Kelola Data"]
selected_page = st.sidebar.radio("Pilih Halaman:", page_options)

if selected_page == "📝 Input Pengukuran Baru":
    page_input_data()
elif selected_page == "📊 Lihat Riwayat & Kelola Data":
    page_view_history()
