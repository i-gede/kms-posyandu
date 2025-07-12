import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from matplotlib.ticker import MultipleLocator

# ==============================================================================
# FUNGSI-FUNGSI PENGATURAN DAN INTERPRETASI (TIDAK DIUBAH)
# ==============================================================================

def get_settings_wfa(age_in_months):
    """Menentukan pengaturan plot untuk WfA berdasarkan usia."""
    if age_in_months <= 24:
        return {
            "xlim": (0, 24), "ylim": (0, 18),
            "xticks": range(0, 25, 1), "yticks": range(0, 19, 1),
            "x_major": 1, "x_minor": 0.2,
            "y_major": 1, "y_minor": 0.1,
            "age_range": "0-24 Bulan"
            }
    if age_in_months <= 60:
        return {
            "xlim": (24, 60), "ylim": (7, 30),
            "xticks": range(24, 61, 1), "yticks": range(7, 31, 1),
            "x_major": 1, "x_minor": 1,
            "y_major": 1, "y_minor": 0.1,
            "age_range": "24-60 Bulan"
            }
    else:
        return {
            "xlim": (60, 120), "ylim": (10, 60),
            "xticks": range(60, 121, 12), "yticks": range(10, 61, 5),
            "x_major": 12, "x_minor": 1,
            "y_major": 5, "y_minor": 1,
            "age_range": "5-10 Tahun"
            }

def get_interpretation_wfa(berat_anak, z_scores_at_age):
    """Menentukan interpretasi untuk WfA."""
    if berat_anak > z_scores_at_age['SD3']: return "Berat badan sangat lebih", 'red'
    elif berat_anak > z_scores_at_age['SD2']: return "Berat badan lebih", 'yellow'
    elif berat_anak >= z_scores_at_age['SD1neg']: return "Berat badan normal", 'darkgreen'
    elif berat_anak > z_scores_at_age['SD2neg']: return "Berat badan kurang", 'yellow'
    elif berat_anak > z_scores_at_age['SD3neg']: return "Berat badan sangat kurang", 'red'
    else: return "Berat badan sangat kurang (Underweight)", 'red'

def get_settings_wfh(age_in_months):
    """Menentukan pengaturan plot untuk WfH berdasarkan usia."""
    if age_in_months <= 24:
        return {
            "xlim": (45, 110), "ylim": (1, 25),
            "xticks": range(45, 111, 5), "yticks": range(1, 26, 2),
            "x_major": 5, "x_minor": 1,
            "y_major": 2, "y_minor": 0.5,
            "age_range": "0-24 Bulan"
            }
    else:
        return {
            "xlim": (65, 120), "ylim": (5, 31),
            "xticks": range(65, 121, 5), "yticks": range(5, 32, 2),
            "x_major": 5, "x_minor": 1,
            "y_major": 2, "y_minor": 0.5,
            "age_range": "24-60 Bulan"
            }

def get_interpretation_wfh(berat_anak, z_scores_at_length):
    """Menentukan interpretasi untuk WfH/WfL."""
    if berat_anak > z_scores_at_length['SD3']: return "Gizi lebih (Obesitas)", 'red'
    elif berat_anak > z_scores_at_length['SD2']: return "Berisiko gizi lebih (Overweight)", 'yellow'
    elif berat_anak >= z_scores_at_length['SD2neg']: return "Gizi baik (Normal)", 'forestgreen'
    elif berat_anak >= z_scores_at_length['SD3neg']: return "Gizi kurang (Wasting)", 'yellow'
    else: return "Gizi buruk (Severe Wasting)", 'red'

def get_settings_bmi(age_in_months):
    """Menentukan pengaturan plot untuk IMT vs Umur."""
    if age_in_months <= 24:
        return {
            "xlim": (0, 24), "ylim": (9, 23),
            "xticks": range(0, 25, 1), "yticks": range(9, 24, 1),
            "x_major": 1, "x_minor": 1,
            "y_major": 1, "y_minor": 0.2,
            "age_range": "0-24 Bulan"
            }
    else:
        return {
            "xlim": (24, 60), "ylim": (11.6, 21),
            "xticks": np.arange(24, 61, 2), "yticks": range(12, 22, 1),
            "x_major": 2, "x_minor": 2,
            "y_major": 1, "y_minor": 0.1,
            "age_range": "24-60 Bulan"
            }

def get_interpretation_bmi(bmi_anak, z_scores_at_age):
    """Menentukan interpretasi untuk IMT. Logikanya sama dengan WfH."""
    if bmi_anak > z_scores_at_age['SD3']: return "Gizi lebih (Obesitas)", 'red'
    elif bmi_anak > z_scores_at_age['SD2']: return "Berisiko gizi lebih (Overweight)", 'yellow'
    elif bmi_anak >= z_scores_at_age['SD2neg']: return "Gizi baik (Normal)", 'forestgreen'
    elif bmi_anak >= z_scores_at_age['SD3neg']: return "Gizi kurang (Wasting)", 'yellow'
    else: return "Gizi buruk (Severe Wasting)", 'red'

def get_settings_lhfa(age_in_months):
    """Menentukan pengaturan plot untuk L/H-f-A berdasarkan usia."""
    if age_in_months <= 6:
        return {
            "xlim": (0, 6), "ylim": (43, 75),
            "xticks": range(0, 7, 1), "yticks": range(43, 76, 5),
            "x_major": 1, "y_major": 5, "y_minor": 1,
            "age_range_title": "0-6 Bulan"
            }
    elif 6 < age_in_months <= 24:
        return {
            "xlim": (6, 24), "ylim": (60, 100),
            "xticks": range(6, 25, 1), "yticks": range(60, 101, 5),
            "x_major": 1, "y_major": 5, "y_minor": 1,
            "age_range_title": "6-24 Bulan"
            }
    else:
        return {
            "xlim": (24, 60), "ylim": (76, 125),
            "xticks": range(24, 61, 2), "yticks": range(76, 126, 5),
            "x_major": 2, "y_major": 5, "y_minor": 1,
            "age_range_title": "2-5 Tahun"
            }

def get_interpretation_lhfa(panjang_anak, z_scores_at_age):
    """Menentukan interpretasi untuk stunting."""
    if 'SD2' not in z_scores_at_age or 'SD2neg' not in z_scores_at_age or 'SD3neg' not in z_scores_at_age:
        return "Data tidak lengkap untuk interpretasi", "gray"
    if panjang_anak > z_scores_at_age['SD2']: return "Tinggi", 'forestgreen'
    elif panjang_anak >= z_scores_at_age['SD2neg']: return "Normal", 'forestgreen'
    elif panjang_anak >= z_scores_at_age['SD3neg']: return "Pendek (Stunting)", 'yellow'
    else: return "Sangat Pendek (Severe Stunting)", 'red'

def get_settings_hcfa(age_in_months):
    """Menentukan pengaturan plot untuk HCFA berdasarkan usia."""
    if age_in_months <= 24:
        return {"xlim": (0, 24), "ylim": (32, 52), "age_range_title": "0-24 Bulan"}
    else:
        return {"xlim": (24, 60), "ylim": (42, 56), "age_range_title": "2-5 Tahun"}

def get_interpretation_hcfa(hc_anak, z_scores_at_age):
    """Menentukan interpretasi untuk Lingkar Kepala."""
    if hc_anak > z_scores_at_age['SD2']: return "Makrosefali (Perlu evaluasi medis)", 'yellow'
    elif hc_anak >= z_scores_at_age['SD2neg']: return "Normal", 'forestgreen'
    else: return "Mikrosefali (Perlu evaluasi medis)", 'yellow'


# ==============================================================================
# FUNGSI-FUNGSI UTAMA (HANDLE) YANG TELAH DIPERBAIKI
# ==============================================================================

def handle_weight_for_age():
    st.header("Grafik Berat Badan menurut Umur (WfA)")
    
    kelamin = st.radio("Pilih Jenis Kelamin:", ('L', 'P'), format_func=lambda x: 'Laki-laki' if x == 'L' else 'Perempuan', key="wfa_gender")
    umur_anak = st.number_input("Umur anak (bulan):", min_value=0.0, max_value=120.0, value=12.0, step=0.5, key="wfa_age")
    berat_anak = st.number_input("Berat badan anak (kg):", min_value=0.0, value=7.0, step=0.1, key="wfa_weight")

    if st.button("Buat Grafik WfA", key="wfa_button"):
        try:
            settings = get_settings_wfa(umur_anak)
            gender_text = "Perempuan" if kelamin == 'P' else "Laki-laki"
            
            if umur_anak <= 60:
                nama_file = f"wfa_{'girls' if kelamin == 'P' else 'boys'}_0-to-5-years_zscores.xlsx"
            else:
                nama_file = f"wfa_{'girls' if kelamin == 'P' else 'boys'}_5-to-10-years_zscores.xlsx"
            
            judul = f'Grafik Berat Badan vs Umur - Anak {gender_text} ({settings["age_range"]})'
            df = pd.read_excel(nama_file)
            
            x_original = df['Month']
            z_cols = ['SD3neg', 'SD2neg', 'SD1neg', 'SD0', 'SD1', 'SD2', 'SD3']
            poly_funcs = {col: np.poly1d(np.polyfit(x_original, df[col], 5)) for col in z_cols}
            x_smooth = np.linspace(x_original.min(), x_original.max(), 500)
            smooth_data = {col: func(x_smooth) for col, func in poly_funcs.items()}
            
            fig, ax = plt.subplots(figsize=(12, 7))
            fig.set_facecolor('steelblue' if kelamin == 'L' else 'hotpink')
            
            ax.fill_between(x_smooth, smooth_data['SD3neg'], smooth_data['SD2neg'], color='yellow', alpha=0.5)
            ax.fill_between(x_smooth, smooth_data['SD2neg'], smooth_data['SD1neg'], color='lightgreen', alpha=0.4)
            ax.fill_between(x_smooth, smooth_data['SD1neg'], smooth_data['SD1'], color='darkgreen', alpha=0.4)
            ax.fill_between(x_smooth, smooth_data['SD1'], smooth_data['SD2'], color='lightgreen', alpha=0.5)
            ax.fill_between(x_smooth, smooth_data['SD2'], smooth_data['SD3'], color='yellow', alpha=0.5)
            
            for col, data in smooth_data.items():
                ax.plot(x_smooth, data, color='black' if col not in ['SD3neg', 'SD3'] else 'red', lw=1)
            
            ax.scatter(umur_anak, berat_anak, marker='*', c='darkviolet', s=250, ec='black', zorder=10, label='Data Anak')
            
            z_scores_at_age = {col: func(umur_anak) for col, func in poly_funcs.items()}
            interpretasi, warna = get_interpretation_wfa(berat_anak, z_scores_at_age)
            props = dict(boxstyle='round', facecolor=warna, alpha=0.8)
            ax.text(0.03, 0.97, f"Interpretasi: {interpretasi}", transform=ax.transAxes, fontsize=12, va='top', bbox=props)
            
            ax.set_title(judul, pad=20, fontsize=16, color='white', fontweight='bold')
            ax.set_xlabel('Umur (Bulan)' if umur_anak <= 60 else 'Umur (Tahun)', fontsize=12, color='white')
            ax.set_ylabel('Berat Badan (kg)', fontsize=12, color='white')
            ax.set_xlim(settings["xlim"])
            ax.set_ylim(settings["ylim"])
            
            st.pyplot(fig)

        except FileNotFoundError:
            st.error(f"File data tidak ditemukan: {nama_file}. Pastikan file ada di repositori Anda.")
        except Exception as e:
            st.error(f"Terjadi error saat membuat grafik: {e}")


def handle_weight_for_height():
    st.header("Grafik Berat Badan menurut Tinggi/Panjang Badan (WfH/L)")

    kelamin = st.radio("Pilih Jenis Kelamin:", ('L', 'P'), format_func=lambda x: 'Laki-laki' if x == 'L' else 'Perempuan', key="wfh_gender")
    umur_anak = st.number_input("Umur anak (bulan):", min_value=0.0, max_value=60.0, value=18.0, step=1.0, key="wfh_age")
    prompt_panjang = "Panjang" if umur_anak <= 24 else "Tinggi"
    panjang_anak = st.number_input(f"{prompt_panjang} badan anak (cm):", min_value=45.0, max_value=120.0, value=80.0, step=0.5, key="wfh_height")
    berat_anak = st.number_input("Berat badan anak (kg):", min_value=0.0, value=10.0, step=0.1, key="wfh_weight")

    if st.button("Buat Grafik WfH/L", key="wfh_button"):
        try:
            settings = get_settings_wfh(umur_anak)
            gender_text = "Perempuan" if kelamin == 'P' else "Laki-laki"

            if umur_anak <= 24:
                nama_file = f"wfl_{'girls' if kelamin == 'P' else 'boys'}_0-to-2-years_zscores.xlsx"
                x_axis_label = "Panjang Badan (cm)"
                judul = f'Grafik Berat Badan vs Panjang Badan - Anak {gender_text} (0-2 Tahun)'
                x_col_name = 'Length'
            else:
                nama_file = f"wfh_{'girls' if kelamin == 'P' else 'boys'}_2-to-5-years_zscores.xlsx"
                x_axis_label = "Tinggi Badan (cm)"
                judul = f'Grafik Berat Badan vs Tinggi Badan - Anak {gender_text} (2-5 Tahun)'
                x_col_name = 'Height'

            df = pd.read_excel(nama_file)
            df = df.rename(columns={x_col_name: 'PanjangTinggi'}).sort_values(by='PanjangTinggi').drop_duplicates(subset='PanjangTinggi')
            
            x_original = df['PanjangTinggi']
            z_cols = ['SD3neg', 'SD2neg', 'SD1neg', 'SD0', 'SD1', 'SD2', 'SD3']
            poly_funcs = {col: np.poly1d(np.polyfit(x_original, df[col], 5)) for col in z_cols}
            x_smooth = np.linspace(x_original.min(), x_original.max(), 500)
            smooth_data = {col: func(x_smooth) for col, func in poly_funcs.items()}
            
            fig, ax = plt.subplots(figsize=(12, 7))
            fig.set_facecolor('steelblue' if kelamin == 'L' else 'hotpink')
            
            ax.fill_between(x_smooth, smooth_data['SD3neg'], smooth_data['SD2neg'], color='yellow', alpha=0.5)
            ax.fill_between(x_smooth, smooth_data['SD2neg'], smooth_data['SD2'], color='green', alpha=0.4)
            ax.fill_between(x_smooth, smooth_data['SD2'], smooth_data['SD3'], color='yellow', alpha=0.5)
            
            for col, data in smooth_data.items():
                ax.plot(x_smooth, data, color='black' if col not in ['SD3neg', 'SD3'] else 'red', lw=1)
            
            ax.scatter(panjang_anak, berat_anak, marker='*', c='darkviolet', s=250, ec='black', zorder=10, label='Data Anak')
            
            z_scores_at_length = {col: func(panjang_anak) for col, func in poly_funcs.items()}
            interpretasi, warna = get_interpretation_wfh(berat_anak, z_scores_at_length)
            props = dict(boxstyle='round', facecolor=warna, alpha=0.8)
            ax.text(0.03, 0.97, f"Status Gizi: {interpretasi}", transform=ax.transAxes, fontsize=12, va='top', bbox=props)
            
            ax.set_title(judul, pad=20, fontsize=16, color='white', fontweight='bold')
            ax.set_xlabel(x_axis_label, fontsize=12, color='white')
            ax.set_ylabel('Berat Badan (kg)', fontsize=12, color='white')
            ax.set_xlim(settings["xlim"])
            ax.set_ylim(settings["ylim"])
            
            st.pyplot(fig)

        except FileNotFoundError:
            st.error(f"File data tidak ditemukan: {nama_file}. Pastikan file ada di repositori Anda.")
        except Exception as e:
            st.error(f"Terjadi error saat membuat grafik: {e}")


def handle_bmi_for_age():
    st.header("Grafik IMT menurut Umur (BMI-for-Age)")

    kelamin = st.radio("Pilih Jenis Kelamin:", ('L', 'P'), format_func=lambda x: 'Laki-laki' if x == 'L' else 'Perempuan', key="bmi_gender")
    umur_anak = st.number_input("Umur anak (bulan):", min_value=0.0, max_value=60.0, value=24.0, step=1.0, key="bmi_age")
    tinggi_cm = st.number_input("Tinggi/Panjang badan anak (cm):", min_value=0.0, value=85.0, step=0.5, key="bmi_height")
    berat_kg = st.number_input("Berat badan anak (kg):", min_value=0.0, value=12.0, step=0.1, key="bmi_weight")

    if st.button("Buat Grafik IMT", key="bmi_button"):
        try:
            if tinggi_cm == 0:
                st.error("Tinggi badan tidak boleh nol.")
                return

            tinggi_m = tinggi_cm / 100
            bmi_anak = berat_kg / (tinggi_m ** 2)
            st.info(f"IMT anak yang dihitung: {bmi_anak:.2f} kg/m²")

            settings = get_settings_bmi(umur_anak)
            gender_text = "Perempuan" if kelamin == 'P' else "Laki-laki"
            
            if umur_anak <= 24:
                nama_file = f"bmi_{'girls' if kelamin == 'P' else 'boys'}_0-to-2-years_zscores.xlsx"
            else:
                nama_file = f"bmi_{'girls' if kelamin == 'P' else 'boys'}_2-to-5-years_zscores.xlsx"
            
            judul = f'Grafik IMT vs Umur - Anak {gender_text} ({settings["age_range"]})'
            df = pd.read_excel(nama_file)
            df = df.sort_values(by='Month').drop_duplicates(subset='Month')

            x_original = df['Month']
            z_cols = ['SD3neg', 'SD2neg', 'SD1neg', 'SD0', 'SD1', 'SD2', 'SD3']
            poly_funcs = {col: np.poly1d(np.polyfit(x_original, df[col], 5)) for col in z_cols}
            x_smooth = np.linspace(x_original.min(), x_original.max(), 500)
            smooth_data = {col: func(x_smooth) for col, func in poly_funcs.items()}
            
            fig, ax = plt.subplots(figsize=(12, 7))
            fig.set_facecolor('steelblue' if kelamin == 'L' else 'hotpink')
            
            ax.fill_between(x_smooth, smooth_data['SD3neg'], smooth_data['SD2neg'], color='yellow', alpha=0.5)
            ax.fill_between(x_smooth, smooth_data['SD2neg'], smooth_data['SD2'], color='green', alpha=0.4)
            ax.fill_between(x_smooth, smooth_data['SD2'], smooth_data['SD3'], color='yellow', alpha=0.5)
            
            for col, data in smooth_data.items():
                ax.plot(x_smooth, data, color='black' if col not in ['SD3neg', 'SD3'] else 'red', lw=1)
            
            ax.scatter(umur_anak, bmi_anak, marker='*', c='darkviolet', s=250, ec='black', zorder=10, label=f'Data Anak ({bmi_anak:.2f} IMT)')
            
            z_scores_at_age = {col: func(umur_anak) for col, func in poly_funcs.items()}
            interpretasi, warna = get_interpretation_bmi(bmi_anak, z_scores_at_age)
            props = dict(boxstyle='round', facecolor=warna, alpha=0.8)
            ax.text(0.03, 0.97, f"Status Gizi: {interpretasi}", transform=ax.transAxes, fontsize=12, va='top', bbox=props)
            
            ax.set_title(judul, pad=20, fontsize=16, color='white', fontweight='bold')
            ax.set_xlabel('Umur (Bulan)', fontsize=12, color='white')
            ax.set_ylabel('IMT (kg/m²)', fontsize=12, color='white')
            ax.set_xlim(settings["xlim"])
            ax.set_ylim(settings["ylim"])
            
            st.pyplot(fig)

        except FileNotFoundError:
            st.error(f"File data tidak ditemukan: {nama_file}. Pastikan file ada di repositori Anda.")
        except Exception as e:
            st.error(f"Terjadi error saat membuat grafik: {e}")


def handle_length_for_age():
    st.header("Grafik Panjang/Tinggi Badan menurut Umur (L/H-f-A)")

    kelamin = st.radio("Pilih Jenis Kelamin:", ('L', 'P'), format_func=lambda x: 'Laki-laki' if x == 'L' else 'Perempuan', key="lhfa_gender")
    umur_anak = st.number_input("Umur anak (bulan):", min_value=0.0, max_value=60.0, value=12.0, step=1.0, key="lhfa_age")
    panjang_anak = st.number_input("Panjang/Tinggi badan anak (cm):", min_value=0.0, value=75.0, step=0.5, key="lhfa_height")

    if st.button("Buat Grafik L/H-f-A", key="lhfa_button"):
        try:
            settings = get_settings_lhfa(umur_anak)
            gender_text = "Perempuan" if kelamin == 'P' else "Laki-laki"
            gender_file_key = 'girls' if kelamin == 'P' else 'boys'

            if umur_anak <= 24:
                file_mingguan = f"lhfa_{gender_file_key}_0-to-13-weeks_zscores.xlsx"
                file_bulanan = f"lhfa_{gender_file_key}_0-to-2-years_zscores.xlsx"
                df_mingguan = pd.read_excel(file_mingguan)
                df_bulanan = pd.read_excel(file_bulanan)
                df_mingguan['Month'] = df_mingguan['Week'] / 4.345
                combined_df = pd.concat([df_mingguan, df_bulanan], ignore_index=True)
                combined_df = combined_df.sort_values(by='Month').drop_duplicates(subset='Month', keep='first')
                df_to_process = combined_df
            else:
                nama_file = f"lhfa_{gender_file_key}_2-to-5-years_zscores.xlsx"
                df_to_process = pd.read_excel(nama_file)

            judul = f'Grafik Panjang/Tinggi Badan vs Umur - Anak {gender_text} ({settings["age_range_title"]})'
            x_original = df_to_process['Month']
            rename_dict = {'SD-3': 'SD3neg', 'SD-2': 'SD2neg', 'SD-1': 'SD1neg'}
            df_to_process = df_to_process.rename(columns=rename_dict)
            
            z_cols = ['SD3neg', 'SD2neg', 'SD1neg', 'SD0', 'SD1', 'SD2', 'SD3']
            poly_funcs = {col: np.poly1d(np.polyfit(x_original, df_to_process[col], 3)) for col in z_cols}
            x_smooth = np.linspace(x_original.min(), x_original.max(), 500)
            smooth_data = {col: func(x_smooth) for col, func in poly_funcs.items()}
            
            fig, ax = plt.subplots(figsize=(12, 7))
            fig.set_facecolor('steelblue' if kelamin == 'L' else 'hotpink')
            
            line_colors = {'SD3': 'black', 'SD2': 'red', 'SD1':'black', 'SD0': 'green', 'SD1neg':'black', 'SD2neg': 'red', 'SD3neg': 'black'}
            for col, data in smooth_data.items():
                if col in line_colors:
                    ax.plot(x_smooth, data, color=line_colors[col], lw=1.5)
            
            ax.scatter(umur_anak, panjang_anak, marker='*', c='darkviolet', s=250, ec='black', zorder=10, label='Data Anak')
            
            z_scores_at_age = {col: func(umur_anak) for col, func in poly_funcs.items()}
            z_scores_at_age['SD_2'] = z_scores_at_age.get('SD2neg')
            z_scores_at_age['SD_3'] = z_scores_at_age.get('SD3neg')
            interpretasi, warna = get_interpretation_lhfa(panjang_anak, z_scores_at_age)
            
            props = dict(boxstyle='round', facecolor=warna, alpha=0.8)
            ax.text(0.03, 0.97, f"Interpretasi: {interpretasi}", transform=ax.transAxes, fontsize=12, va='top', bbox=props)
            
            ax.set_title(judul, pad=20, fontsize=16, color='white', fontweight='bold')
            ax.set_xlabel("Umur (Bulan)", fontsize=12, color='white')
            ax.set_ylabel('Panjang/Tinggi Badan (cm)', fontsize=12, color='white')
            ax.set_xlim(settings["xlim"])
            ax.set_ylim(settings["ylim"])
            
            st.pyplot(fig)

        except FileNotFoundError:
            st.error(f"Salah satu file data tidak ditemukan. Pastikan file lhfa_*_zscores.xlsx ada di repositori.")
        except Exception as e:
            st.error(f"Terjadi error saat membuat grafik: {e}")


def handle_head_circumference_for_age():
    st.header("Grafik Lingkar Kepala menurut Umur (HCFA)")

    kelamin = st.radio("Pilih Jenis Kelamin:", ('L', 'P'), format_func=lambda x: 'Laki-laki' if x == 'L' else 'Perempuan', key="hcfa_gender")
    umur_anak_bulan = st.number_input("Umur anak (bulan):", min_value=0.0, max_value=60.0, value=12.0, step=1.0, key="hcfa_age")
    hc_anak = st.number_input("Lingkar kepala anak (cm):", min_value=0.0, value=45.0, step=0.5, key="hcfa_hc")

    if st.button("Buat Grafik HCFA", key="hcfa_button"):
        try:
            settings = get_settings_hcfa(umur_anak_bulan)
            gender_text = "Perempuan" if kelamin == 'P' else "Laki-laki"
            gender_file_key = 'girls' if kelamin == 'P' else 'boys'
            
            judul = f'Grafik Lingkar Kepala vs Umur - Anak {gender_text} ({settings["age_range_title"]})'

            file_mingguan = f"hcfa_{gender_file_key}_0-13-zscores.xlsx"
            file_bulanan = f"hcfa_{gender_file_key}_0-5-zscores.xlsx"
            df_mingguan = pd.read_excel(file_mingguan)
            df_bulanan = pd.read_excel(file_bulanan)
            df_mingguan['Month'] = df_mingguan['Week'] / 4.345
            combined_df = pd.concat([df_mingguan, df_bulanan], ignore_index=True)
            combined_df = combined_df.sort_values(by='Month').drop_duplicates(subset='Month', keep='first')
            df_to_process = combined_df

            rename_dict = {'SD-3': 'SD3neg', 'SD-2': 'SD2neg', 'SD-1': 'SD1neg'}
            df_to_process = df_to_process.rename(columns=rename_dict)
            
            x_original = df_to_process['Month']
            z_cols = ['SD3neg', 'SD2neg', 'SD1neg', 'SD0', 'SD1', 'SD2', 'SD3']
            poly_funcs = {col: np.poly1d(np.polyfit(x_original, df_to_process[col], 5)) for col in z_cols}
            x_smooth = np.linspace(0, 60, 500)
            smooth_data = {col: func(x_smooth) for col, func in poly_funcs.items()}
            
            fig, ax = plt.subplots(figsize=(12, 7))
            fig.set_facecolor('steelblue' if kelamin == 'L' else 'hotpink')
            
            line_colors = {'SD3': 'black', 'SD2': 'red', 'SD1': 'orange', 'SD0': 'green', 'SD1neg': 'orange', 'SD2neg': 'red', 'SD3neg': 'black'}
            for col, data in smooth_data.items():
                if col in line_colors:
                    ax.plot(x_smooth, data, color=line_colors[col], lw=1.5)
            
            ax.scatter(umur_anak_bulan, hc_anak, marker='*', c='darkviolet', s=250, ec='black', zorder=10, label='Data Anak')
            
            z_scores_at_age = {col: func(umur_anak_bulan) for col, func in poly_funcs.items()}
            interpretasi, warna = get_interpretation_hcfa(hc_anak, z_scores_at_age)
            props = dict(boxstyle='round', facecolor=warna, alpha=0.8)
            ax.text(0.03, 0.97, f"Interpretasi: {interpretasi}", transform=ax.transAxes, fontsize=12, va='top', bbox=props)
            
            ax.set_title(judul, pad=20, fontsize=16, color='white', fontweight='bold')
            ax.set_xlabel("Umur (Bulan)", fontsize=12)
            ax.set_ylabel('Lingkar Kepala (cm)', fontsize=12)
            ax.set_xlim(settings["xlim"])
            ax.set_ylim(settings["ylim"])
            
            st.pyplot(fig)

        except FileNotFoundError:
            st.error(f"Salah satu file data tidak ditemukan. Pastikan file hcfa_*_zscores.xlsx ada di repositori.")
        except Exception as e:
            st.error(f"Terjadi error saat membuat grafik: {e}")


# ==============================================================================
# BAGIAN UTAMA APLIKASI WEB STREAMLIT
# ==============================================================================

st.title("📈 Program Kurva Pertumbuhan Anak WHO")
st.write("Aplikasi untuk memvisualisasikan pertumbuhan anak berdasarkan standar WHO.")

menu_pilihan = st.sidebar.selectbox(
    "Pilih Jenis Kurva:",
    (
        "Berat Badan menurut UMUR (WfA)",
        "Berat Badan menurut TINGGI/PANJANG (WfH/L)",
        "IMT menurut UMUR (BMI-for-Age)",
        "Panjang/Tinggi Badan menurut UMUR (L/H-f-A)",
        "Lingkar Kepala menurut UMUR (HCFA)"
    )
)

if menu_pilihan == "Berat Badan menurut UMUR (WfA)":
    handle_weight_for_age()
elif menu_pilihan == "Berat Badan menurut TINGGI/PANJANG (WfH/L)":
    handle_weight_for_height()
elif menu_pilihan == "IMT menurut UMUR (BMI-for-Age)":
    handle_bmi_for_age()
elif menu_pilihan == "Panjang/Tinggi Badan menurut UMUR (L/H-f-A)":
    handle_length_for_age()
elif menu_pilihan == "Lingkar Kepala menurut UMUR (HCFA)":
    handle_head_circumference_for_age()
