import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from matplotlib.ticker import MultipleLocator
from supabase import create_client, Client
from datetime import date, datetime
from typing import Dict, Any, Tuple

# ==============================================================================
# KONFIGURASI TERPUSAT UNTUK SEMUA KURVA PERTUMBUHAN
# ==============================================================================

# Konfigurasi ini menggantikan semua fungsi get_settings_* yang berulang.
# Lebih mudah untuk dikelola dan diperbarui di satu tempat.
CONFIG: Dict[str, Dict[str, Any]] = {
    "wfa": {
        "title": "Berat Badan menurut Umur",
        "y_col": "berat_kg",
        "y_label": "Berat Badan (kg)",
        "interpretation_func": lambda berat, z: get_interpretation_wfa(berat, z),
        "ranges": [
            {"max_age": 24, "xlim": (0, 24), "ylim": (0, 18), "x_major": 1, "y_major": 1, "age_range_label": "0-24 Bulan"},
            {"max_age": 60, "xlim": (24, 60), "ylim": (7, 30), "x_major": 1, "y_major": 1, "age_range_label": "24-60 Bulan"},
            {"max_age": 121, "xlim": (60, 120), "ylim": (10, 60), "x_major": 12, "y_major": 5, "age_range_label": "5-10 Tahun"},
        ],
        "file_pattern": "wfa_{gender}_0-to-5-years_zscores.xlsx",
        "x_axis_label": "Umur (Bulan)",
    },
    "wfh": {
        "title": "Berat Badan menurut Tinggi/Panjang Badan",
        "x_col": "tinggi_cm",
        "y_col": "berat_kg",
        "y_label": "Berat Badan (kg)",
        "interpretation_func": lambda berat, z: get_interpretation_wfh(berat, z),
        "ranges": [
            {"max_age": 24, "file_key": "wfl", "x_col_std": "Length", "x_label": "Panjang Badan (cm)", "xlim": (45, 110), "ylim": (1, 25), "x_major": 5, "y_major": 2},
            {"max_age": 61, "file_key": "wfh", "x_col_std": "Height", "x_label": "Tinggi Badan (cm)", "xlim": (65, 120), "ylim": (5, 31), "x_major": 5, "y_major": 2},
        ],
        "file_pattern": "{file_key}_{gender}_{age_group}_zscores.xlsx",
    },
    "bmi": {
        "title": "Indeks Massa Tubuh (IMT) menurut Umur",
        "y_col": "bmi",
        "y_label": "IMT (kg/m²)",
        "interpretation_func": lambda bmi, z: get_interpretation_bmi(bmi, z),
        "ranges": [
            {"max_age": 24, "xlim": (0, 24), "ylim": (9, 23), "x_major": 1, "y_major": 1, "age_range_label": "0-24 Bulan"},
            {"max_age": 61, "xlim": (24, 60), "ylim": (11.6, 21), "x_major": 2, "y_major": 1, "age_range_label": "24-60 Bulan"},
        ],
        "file_pattern": "bmi_{gender}_{age_group}_zscores.xlsx",
        "x_axis_label": "Umur (Bulan)",
    },
    "lhfa": {
        "title": "Panjang/Tinggi Badan menurut Umur",
        "y_col": "tinggi_cm",
        "y_label": "Panjang/Tinggi Badan (cm)",
        "interpretation_func": lambda tinggi, z: get_interpretation_lhfa(tinggi, z),
        "ranges": [
            {"max_age": 24, "xlim": (0, 24), "ylim": (43, 100), "x_major": 1, "y_major": 5, "age_range_label": "0-24 Bulan"},
            {"max_age": 61, "xlim": (24, 60), "ylim": (76, 125), "x_major": 2, "y_major": 5, "age_range_label": "2-5 Tahun"},
        ],
        "file_pattern": "lhfa_{gender}_{age_group}_zscores.xlsx", # Disederhanakan, logika file weekly digabung di dalam fungsi plot
        "x_axis_label": "Umur (Bulan)",
    },
    "hcfa": {
        "title": "Lingkar Kepala menurut Umur",
        "y_col": "lingkar_kepala_cm",
        "y_label": "Lingkar Kepala (cm)",
        "interpretation_func": lambda hc, z: get_interpretation_hcfa(hc, z),
        "ranges": [
            {"max_age": 24, "xlim": (0, 24), "ylim": (32, 52), "x_major": 1, "y_major": 1, "age_range_label": "0-24 Bulan"},
            {"max_age": 61, "xlim": (24, 60), "ylim": (42, 56), "x_major": 2, "y_major": 1, "age_range_label": "2-5 Tahun"},
        ],
        "file_pattern": "hcfa_{gender}_{age_group}_zscores.xlsx",
        "x_axis_label": "Umur (Bulan)",
    },
}

# ==============================================================================
# KONEKSI DATABASE & FUNGSI DATA HELPER
# ==============================================================================

@st.cache_resource
def init_connection() -> Client:
    """Membuat dan mengembalikan koneksi ke database Supabase."""
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

@st.cache_data(ttl=3600)
def load_who_data(file_path: str) -> pd.DataFrame:
    """Memuat dan menyimpan cache data dari file Excel standar WHO."""
    try:
        return pd.read_excel(file_path)
    except FileNotFoundError:
        st.error(f"File standar tidak ditemukan: {file_path}")
        return None

@st.cache_data(ttl=600)
def get_child_list(_supabase: Client) -> pd.DataFrame:
    """Mengambil dan memformat daftar anak yang unik dari database."""
    try:
        response = _supabase.table("data_pengukuran").select("id_anak, nama_anak").execute()
        if not response.data:
            return pd.DataFrame()
        df = pd.DataFrame(response.data).drop_duplicates(subset=['id_anak']).sort_values('nama_anak')
        df['display_name'] = df['nama_anak'] + " (" + df['id_anak'] + ")"
        return df
    except Exception as e:
        st.error(f"Gagal mengambil daftar anak: {e}")
        return pd.DataFrame()

def save_measurement(data: Dict[str, Any]) -> None:
    """Menyimpan satu data pengukuran baru ke Supabase."""
    try:
        supabase.table("data_pengukuran").insert(data).execute()
        st.success(f"Data untuk {data['nama_anak']} berhasil disimpan!")
    except Exception as e:
        st.error(f"Gagal menyimpan data: {e}")

# ==============================================================================
# FUNGSI-FUNGSI LOGIKA DAN PERHITUNGAN
# ==============================================================================

def calculate_age_in_months(birth_date: date, measurement_date: date) -> int:
    """Menghitung usia dalam bulan penuh."""
    return (measurement_date.year - birth_date.year) * 12 + (measurement_date.month - birth_date.month)

def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """Menghitung Indeks Massa Tubuh (IMT)."""
    if height_cm == 0:
        return 0.0
    return weight_kg / ((height_cm / 100) ** 2)

# Fungsi-fungsi interpretasi tetap sama karena logikanya unik untuk setiap kurva.
def get_interpretation_wfa(berat_anak: float, z: Dict) -> Tuple[str, str]:
    if berat_anak > z['SD3']: return "Berat badan sangat lebih", 'red'
    elif berat_anak > z['SD2']: return "Berat badan lebih", 'yellow'
    elif berat_anak >= z['SD2neg']: return "Berat badan normal", 'forestgreen'
    elif berat_anak > z['SD3neg']: return "Berat badan kurang", 'yellow'
    else: return "Berat badan sangat kurang (Underweight)", 'red'

def get_interpretation_wfh(berat_anak: float, z: Dict) -> Tuple[str, str]:
    if berat_anak > z['SD3']: return "Gizi lebih (Obesitas)", 'red'
    elif berat_anak > z['SD2']: return "Berisiko gizi lebih (Overweight)", 'yellow'
    elif berat_anak >= z['SD2neg']: return "Gizi baik (Normal)", 'forestgreen'
    elif berat_anak >= z['SD3neg']: return "Gizi kurang (Wasting)", 'yellow'
    else: return "Gizi buruk (Severe Wasting)", 'red'

def get_interpretation_bmi(bmi_anak: float, z: Dict) -> Tuple[str, str]:
    if bmi_anak > z['SD3']: return "Gizi lebih (Obesitas)", 'red'
    elif bmi_anak > z['SD2']: return "Berisiko gizi lebih (Overweight)", 'yellow'
    elif bmi_anak >= z['SD2neg']: return "Gizi baik (Normal)", 'forestgreen'
    elif bmi_anak >= z['SD3neg']: return "Gizi kurang (Wasting)", 'yellow'
    else: return "Gizi buruk (Severe Wasting)", 'red'

def get_interpretation_lhfa(panjang_anak: float, z: Dict) -> Tuple[str, str]:
    if panjang_anak > z['SD2']: return "Tinggi", 'forestgreen'
    elif panjang_anak >= z['SD2neg']: return "Normal", 'forestgreen'
    elif panjang_anak >= z['SD3neg']: return "Pendek (Stunting)", 'yellow'
    else: return "Sangat Pendek (Severe Stunting)", 'red'

def get_interpretation_hcfa(hc_anak: float, z: Dict) -> Tuple[str, str]:
    if hc_anak > z['SD2']: return "Makrosefali", 'yellow'
    elif hc_anak >= z['SD2neg']: return "Normal", 'forestgreen'
    else: return "Mikrosefali", 'yellow'

# ==============================================================================
# FUNGSI PLOTTING UTAMA (TERABSTRAKSI)
# ==============================================================================

def create_growth_chart(ax: plt.Axes, chart_type: str, history_df: pd.DataFrame, gender: str, latest_data: pd.Series) -> None:
    """
    Fungsi generik untuk membuat dan memformat satu grafik pertumbuhan.
    Mengambil data yang sudah diproses dan menghasilkan plot.
    """
    cfg = CONFIG[chart_type]
    is_age_based = cfg.get("x_axis_label", "").endswith("(Bulan)")
    x_col = cfg.get("x_col", "usia_bulan")
    y_col = cfg["y_col"]
    
    # 1. Dapatkan data dan nilai terakhir
    x_latest = latest_data[x_col]
    y_latest = latest_data[y_col]
    
    # 2. Tentukan range dan file standar berdasarkan data terakhir
    if is_age_based:
        range_cfg = next((r for r in cfg["ranges"] if x_latest < r["max_age"]), cfg["ranges"][-1])
        age_group_map = {24: "0-to-2-years", 60: "2-to-5-years", 61: "2-to-5-years", 121: "5-to-10-years"}
        age_group = next((v for k, v in age_group_map.items() if x_latest < k), "5-to-10-years")
        file_name = cfg["file_pattern"].format(gender="girls" if gender == 'P' else "boys", age_group=age_group)
        x_col_std = "Month"
    else: # Untuk WFH/WFL
        range_cfg = next((r for r in cfg["ranges"] if latest_data['usia_bulan'] < r["max_age"]), cfg["ranges"][-1])
        age_group_map = {24: "0-to-2-years", 61: "2-to-5-years"}
        age_group = next((v for k, v in age_group_map.items() if latest_data['usia_bulan'] < k), "2-to-5-years")
        file_name = cfg["file_pattern"].format(file_key=range_cfg["file_key"], gender="girls" if gender == 'P' else "boys", age_group=age_group)
        x_col_std = range_cfg["x_col_std"]
        
    df_std = load_who_data(file_name)
    if df_std is None: return
    
    # 3. Proses data standar dan hitung Z-scores
    df_std = df_std.rename(columns={x_col_std: 'x_std'}).sort_values('x_std').drop_duplicates('x_std')
    z_cols = ['SD3neg', 'SD2neg', 'SD1neg', 'SD0', 'SD1', 'SD2', 'SD3']
    poly_funcs = {col: np.poly1d(np.polyfit(df_std['x_std'], df_std[col], 5)) for col in z_cols}
    z_scores_at_point = {col: func(x_latest) for col, func in poly_funcs.items()}
    
    # 4. Dapatkan interpretasi
    interpretation, color = cfg["interpretation_func"](y_latest, z_scores_at_point)
    st.info(f"**{cfg['title']}:** {interpretation}")

    # 5. Plotting
    fig = ax.figure
    fig.set_facecolor('hotpink' if gender == 'P' else 'steelblue')
    
    x_smooth = np.linspace(df_std['x_std'].min(), df_std['x_std'].max(), 300)
    smooth_data = {col: func(x_smooth) for col, func in poly_funcs.items()}

    # Area berwarna Z-score
    ax.fill_between(x_smooth, smooth_data['SD3neg'], smooth_data['SD2neg'], color='yellow', alpha=0.5)
    ax.fill_between(x_smooth, smooth_data['SD2neg'], smooth_data['SD2'], color='green', alpha=0.4)
    ax.fill_between(x_smooth, smooth_data['SD2'], smooth_data['SD3'], color='yellow', alpha=0.5)
    
    # Garis Z-score
    for col, data in smooth_data.items():
        ax.plot(x_smooth, data, color='red' if col in ['SD3', 'SD3neg'] else 'black', lw=1, alpha=0.8)

    # Plot riwayat dan titik terakhir
    ax.plot(history_df[x_col].astype(float), history_df[y_col].astype(float), marker='o', linestyle='-', color='darkviolet', label='Riwayat Pertumbuhan')
    ax.scatter(x_latest, y_latest, marker='*', c='cyan', s=300, ec='black', zorder=10, label='Pengukuran Terakhir')

    # Anotasi dan Label
    props = dict(boxstyle='round', facecolor=color, alpha=0.8)
    ax.text(0.03, 0.97, f"Interpretasi: {interpretation}", transform=ax.transAxes, fontsize=12, va='top', bbox=props)
    
    title_text = f"Grafik {cfg['title']} - {'Perempuan' if gender == 'P' else 'Laki-laki'}"
    if 'age_range_label' in range_cfg:
        title_text += f" ({range_cfg['age_range_label']})"
        
    ax.set_title(title_text, pad=20, fontsize=16, color='white', fontweight='bold')
    ax.set_xlabel(cfg.get('x_axis_label') or range_cfg.get('x_label'), fontsize=12, color='white')
    ax.set_ylabel(cfg['y_label'], fontsize=12, color='white')
    
    # Pengaturan Sumbu dan Grid
    ax.set_xlim(range_cfg["xlim"])
    ax.set_ylim(range_cfg["ylim"])
    ax.xaxis.set_major_locator(MultipleLocator(range_cfg["x_major"]))
    ax.yaxis.set_major_locator(MultipleLocator(range_cfg["y_major"]))
    ax.grid(which='major', linestyle='-', linewidth='0.8', color='gray')
    ax.grid(which='minor', axis='y', linestyle=':', linewidth='0.5', color='lightgray')
    
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.legend(loc='lower right')
    fig.tight_layout()

# ==============================================================================
# FUNGSI-FUNGSI PLOT SPESIFIK (SEKARANG JAUH LEBIH RINGKAS)
# ==============================================================================

def plot_all_curves(history_df: pd.DataFrame):
    """Fungsi utama untuk menampilkan semua kurva pertumbuhan."""
    st.header("📈 Hasil Analisis Pertumbuhan")
    if history_df.empty:
        st.warning("Data riwayat tidak tersedia untuk membuat grafik.")
        return

    # Tambah kolom BMI jika belum ada
    if 'bmi' not in history_df.columns:
        history_df['bmi'] = history_df.apply(lambda row: calculate_bmi(row['berat_kg'], row['tinggi_cm']), axis=1)

    latest_data = history_df.iloc[-1]
    gender = latest_data['jenis_kelamin']

    charts_to_plot = ["wfa", "wfh", "bmi", "lhfa", "hcfa"]
    for chart_type in charts_to_plot:
        if latest_data[CONFIG[chart_type]["y_col"]] > 0: # Hanya plot jika ada data
            st.markdown("---")
            st.subheader(f"{charts_to_plot.index(chart_type)+1}. {CONFIG[chart_type]['title']}")
            fig, ax = plt.subplots(figsize=(12, 7))
            try:
                create_growth_chart(ax, chart_type, history_df, gender, latest_data)
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Gagal membuat grafik {chart_type.upper()}: {e}")
            plt.close(fig) # Tutup figure untuk membebaskan memori

# ==============================================================================
# HALAMAN-HALAMAN STREAMLIT (UI)
# ==============================================================================

def page_input_data():
    """Halaman untuk menginput data pengukuran anak."""
    st.header("📝 Input Pengukuran Baru")

    input_type = st.radio("Pilih jenis input:", ('Anak yang Sudah Terdaftar', 'Daftarkan Anak Baru'), horizontal=True)

    if input_type == 'Anak yang Sudah Terdaftar':
        df_anak = get_child_list(supabase)
        if df_anak.empty:
            st.warning("Belum ada anak terdaftar. Silakan pilih 'Daftarkan Anak Baru'.")
            return
        
        option_list = ["-"] + df_anak['display_name'].tolist()
        selected_name = st.selectbox("Pilih Anak:", option_list)

        if selected_name and selected_name != "-":
            child_data = df_anak[df_anak['display_name'] == selected_name].iloc[0]
            with st.form("existing_child_form", clear_on_submit=True):
                st.info(f"Menambahkan pengukuran untuk **{child_data['nama_anak']}**")
                tanggal_pengukuran = st.date_input("Tanggal Pengukuran", max_value=date.today())
                berat_kg = st.number_input("Berat Badan (kg)", min_value=1.0, step=0.1, format="%.2f")
                tinggi_cm = st.number_input("Tinggi/Panjang Badan (cm)", min_value=20.0, step=0.5, format="%.1f")
                lingkar_kepala_cm = st.number_input("Lingkar Kepala (cm)", min_value=10.0, step=0.5, format="%.1f", help="Boleh dikosongkan jika tidak diukur.")

                if st.form_submit_button("Simpan Pengukuran"):
                    # Ambil data anak yg lengkap dari DB untuk submit
                    full_child_data = supabase.table("data_pengukuran").select("*").eq("id_anak", child_data['id_anak']).limit(1).execute().data[0]
                    usia_bulan = calculate_age_in_months(datetime.strptime(full_child_data['tanggal_lahir'], '%Y-%m-%d').date(), tanggal_pengukuran)
                    
                    data_to_insert = {
                        "id_anak": full_child_data['id_anak'], "nama_anak": full_child_data['nama_anak'],
                        "tanggal_lahir": full_child_data['tanggal_lahir'], "jenis_kelamin": full_child_data['jenis_kelamin'],
                        "tanggal_pengukuran": str(tanggal_pengukuran), "usia_bulan": int(usia_bulan),
                        "berat_kg": berat_kg, "tinggi_cm": tinggi_cm, "lingkar_kepala_cm": lingkar_kepala_cm if lingkar_kepala_cm > 0 else None
                    }
                    save_measurement(data_to_insert)

    elif input_type == 'Daftarkan Anak Baru':
        with st.form("new_child_form", clear_on_submit=True):
            st.write("**Data Diri Anak**")
            id_anak = st.text_input("ID Anak (contoh: NIK, No. KMS)", help="ID unik untuk setiap anak.")
            nama_anak = st.text_input("Nama Anak")
            tanggal_lahir = st.date_input("Tanggal Lahir", max_value=date.today(), value=date(2023, 1, 1))
            jenis_kelamin = st.radio("Jenis Kelamin", ('L', 'P'), format_func=lambda x: 'Laki-laki' if x == 'L' else 'Perempuan')
            st.divider()
            st.write("**Data Pengukuran Pertama**")
            tanggal_pengukuran = st.date_input("Tanggal Pengukuran", max_value=date.today())
            berat_kg = st.number_input("Berat Badan (kg)", min_value=1.0, step=0.1, format="%.2f")
            tinggi_cm = st.number_input("Tinggi/Panjang Badan (cm)", min_value=20.0, step=0.5, format="%.1f")
            lingkar_kepala_cm = st.number_input("Lingkar Kepala (cm)", min_value=10.0, step=0.5, format="%.1f", help="Boleh dikosongkan jika tidak diukur.")

            if st.form_submit_button("Daftarkan dan Simpan"):
                if not all([id_anak, nama_anak, berat_kg, tinggi_cm]):
                    st.warning("Harap isi semua field wajib (ID, Nama, Tanggal Lahir, Berat, Tinggi).")
                else:
                    usia_bulan = calculate_age_in_months(tanggal_lahir, tanggal_pengukuran)
                    data_to_insert = {
                        "id_anak": id_anak, "nama_anak": nama_anak, "tanggal_lahir": str(tanggal_lahir), 
                        "jenis_kelamin": jenis_kelamin, "tanggal_pengukuran": str(tanggal_pengukuran), 
                        "usia_bulan": int(usia_bulan), "berat_kg": berat_kg, "tinggi_cm": tinggi_cm, 
                        "lingkar_kepala_cm": lingkar_kepala_cm if lingkar_kepala_cm > 0 else None
                    }
                    save_measurement(data_to_insert)

def page_view_history():
    """Halaman untuk melihat riwayat, mengelola data, dan melihat grafik."""
    st.header("📊 Riwayat & Analisis Pertumbuhan")

    df_anak = get_child_list(supabase)
    if df_anak.empty:
        st.info("Belum ada data tersimpan. Silakan input data baru pada halaman 'Input Pengukuran'.")
        return

    option_list = ["-"] + df_anak['display_name'].tolist()
    selected_name = st.selectbox("Pilih Anak untuk Dilihat Riwayatnya:", option_list)

    if selected_name and selected_name != "-":
        selected_id = df_anak[df_anak['display_name'] == selected_name]['id_anak'].iloc[0]
        
        try:
            response = supabase.table("data_pengukuran").select("*").eq("id_anak", selected_id).order("usia_bulan").execute()
            if not response.data:
                st.warning("Tidak ada riwayat pengukuran untuk anak ini.")
                return

            history_df = pd.DataFrame(response.data)
            history_df.fillna(0, inplace=True) # Ganti NaN/None dengan 0 untuk konsistensi
            
            st.subheader(f"Riwayat untuk: {history_df['nama_anak'].iloc[0]}")
            cols_to_show = ['tanggal_pengukuran', 'usia_bulan', 'berat_kg', 'tinggi_cm', 'lingkar_kepala_cm']
            st.dataframe(history_df[cols_to_show], use_container_width=True)
            
            # Tampilkan semua kurva
            plot_all_curves(history_df)

            # Bagian Kelola Data
            st.divider()
            with st.expander("⚙️ Kelola Data Pengukuran (Revisi/Hapus)"):
                history_df['display_entry'] = pd.to_datetime(history_df['tanggal_pengukuran']).dt.strftime('%d %B %Y') + " (Usia " + history_df['usia_bulan'].astype(str) + " bln)"
                entry_to_manage = st.selectbox("Pilih data yang ingin dikelola:", history_df['display_entry'])
                selected_entry = history_df[history_df['display_entry'] == entry_to_manage].iloc[0]
                
                # Form Edit
                with st.form(f"edit_form_{selected_entry['id']}"):
                    st.write(f"Merevisi data tanggal **{selected_entry['display_entry']}**")
                    edit_berat = st.number_input("Berat (kg)", value=float(selected_entry['berat_kg']))
                    edit_tinggi = st.number_input("Tinggi (cm)", value=float(selected_entry['tinggi_cm']))
                    edit_lk = st.number_input("Lingkar Kepala (cm)", value=float(selected_entry['lingkar_kepala_cm']))
                    if st.form_submit_button("Simpan Perubahan"):
                        try:
                            update_data = {"berat_kg": edit_berat, "tinggi_cm": edit_tinggi, "lingkar_kepala_cm": edit_lk if edit_lk > 0 else None}
                            supabase.table("data_pengukuran").update(update_data).eq("id", int(selected_entry['id'])).execute()
                            st.success("Data berhasil diperbarui! Halaman akan dimuat ulang."); st.rerun()
                        except Exception as e: st.error(f"Gagal memperbarui: {e}")

                # Tombol Hapus
                if st.checkbox(f"Saya yakin ingin menghapus data **{selected_entry['display_entry']}**"):
                    if st.button("🗑️ Hapus Data Ini Secara Permanen", type="primary"):
                        try:
                            supabase.table("data_pengukuran").delete().eq("id", int(selected_entry['id'])).execute()
                            st.success("Data berhasil dihapus! Halaman akan dimuat ulang."); st.rerun()
                        except Exception as e: st.error(f"Gagal menghapus: {e}")

        except Exception as e:
            st.error(f"Gagal mengambil riwayat data: {e}")

# ==============================================================================
# STRUKTUR UTAMA APLIKASI STREAMLIT
# ==============================================================================

def main():
    st.set_page_config(page_title="Growth Monitor", layout="centered")
    st.title("👶 Aplikasi Monitor Pertumbuhan Anak")
    st.write("Berdasarkan Standar Antropometri WHO 2005")

    global supabase
    supabase = init_connection()

    if not supabase:
        st.error("Koneksi ke database gagal. Aplikasi tidak dapat berjalan.")
        st.info("Pastikan Anda sudah mengatur SUPABASE_URL dan SUPABASE_KEY di Streamlit Secrets.")
        return
    
    pages = {
        "Input Pengukuran": page_input_data,
        "Lihat Riwayat & Analisis": page_view_history
    }
    
    st.sidebar.title("Navigasi")
    selection = st.sidebar.radio("Pilih Halaman", list(pages.keys()))
    
    # Jalankan fungsi halaman yang dipilih
    page_function = pages[selection]
    page_function()
    
    st.sidebar.info("Dibuat dengan Streamlit & Supabase")

if __name__ == "__main__":
    main()