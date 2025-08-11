import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from matplotlib.ticker import MultipleLocator

# ==============================================================================
# FUNGSI-FUNGSI UNTUK KURVA BERAT BADAN vs UMUR (WfA)
# ==============================================================================

# def get_input_wfa():
#     while True:
#         kelamin = input("Masukkan jenis kelamin anak (L/P): ").upper()
#         if kelamin in ['L', 'P']: break
#         print("Input tidak valid. Harap masukkan 'L' atau 'P'.")
    
#     umur_str = input(f"Umur anak {'laki-laki' if kelamin == 'L' else 'perempuan'} (bulan): ")
#     berat_str = input("Berat badan anak (kg): ")
    
#     umur = float(umur_str)
#     if not (0 <= umur <= 120):
#         raise ValueError("Usia harus berada dalam rentang 0 hingga 120 bulan atau 10 tahun.")
        
#     return kelamin, umur, float(berat_str)

def get_settings_wfa(age_in_months):
    """Menentukan pengaturan plot untuk WfA berdasarkan usia."""
    if age_in_months <= 24:
        return {
            "xlim": (0, 24), "ylim": (0, 18), 
            "xticks": range(0, 24, 1), "yticks": range(0, 18, 1), 
            "x_major": 1, "x_minor": 0.2, # Minor grid setiap 0.2 bln (5 bagian)
            "y_major": 1, "y_minor": 0.1,
            "age_range": "0-24 Bulan"
            }
    if age_in_months <= 60:
        return {
            "xlim": (24, 60), "ylim": (7, 30), 
            "xticks": range(24, 60, 1), "yticks": range(7, 30, 1), 
            "x_major": 1, "x_minor": 1, # Minor grid setiap 1 bulan
            "y_major": 1, "y_minor": 0.1,
            "age_range": "24-60 Bulan"
            }
    else:
        return {
            "xlim": (60, 120), "ylim": (10, 60), 
            "xticks": range(60, 120, 12), "yticks": range(10, 60, 5), 
            "x_major": 12, "x_minor": 1, # Minor grid setiap 1 bulan
            "y_major": 5, "y_minor": 1,
            "age_range": "5-10 Tahun"
            }

def get_interpretation_wfa(berat_anak, z_scores_at_age):
    """Menentukan interpretasi untuk WfA."""
    if berat_anak > z_scores_at_age['SD3']: return "Berat badan sangat lebih", 'red'
    elif berat_anak > z_scores_at_age['SD2']: return "Berat badan lebih", 'yellow'
    elif berat_anak >= z_scores_at_age['SD1']: return "Berat cukup normal", 'lightgreen'
    elif berat_anak >= z_scores_at_age['SD1neg']: return "Berat badan normal", 'darkgreen'
    elif berat_anak > z_scores_at_age['SD2neg']: return "Berat cukup normal", 'lightgreen'
    elif berat_anak > z_scores_at_age['SD3neg']: return "Berat badan kurang", 'yellow'
    else: return "Berat badan kurang (Underweight)", 'red'

def handle_weight_for_age():
    st.header("Grafik Berat Badan menurut Umur (WfA)") # Judul di web

    # Ganti input() dengan komponen UI Streamlit
    kelamin = st.radio("Pilih Jenis Kelamin:", ('L', 'P'), format_func=lambda x: 'Laki-laki' if x == 'L' else 'Perempuan')
    umur_anak = st.number_input("Umur anak (bulan):", min_value=0.0, max_value=120.0, step=0.5)
    berat_anak = st.number_input("Berat badan anak (kg):", min_value=0.0, step=0.1)

    # Tambahkan tombol untuk memproses
    if st.button("Buat Grafik WfA"):
        # Masukkan semua logika Anda yang sudah ada di sini...
        try:
            #kelamin, umur_anak, berat_anak = get_input_wfa()
            settings = get_settings_wfa(umur_anak)
            
            gender_text = "Perempuan" if kelamin == 'P' else "Laki-laki"
            nama_file = f"wfa_{'girls' if kelamin == 'P' else 'boys'}_0-to-5-years_zscores.xlsx"
            judul = f'Grafik Berat Badan vs Umur - Anak {gender_text} ({settings["age_range"]})'


            # Logika untuk memilih file dan pengaturan berdasarkan USIA
            if umur_anak <= 60:
                nama_file = f"wfa_{'girls' if kelamin == 'P' else 'boys'}_0-to-5-years_zscores.xlsx"
                judul = f'Grafik Berat Badan vs Umur - Anak {gender_text} ({settings["age_range"]})'
            else: # Usia > 24 bulan
                nama_file = f"wfa_{'girls' if kelamin == 'P' else 'boys'}_5-to-10-years_zscores.xlsx"
                judul = f'Grafik Berat Badan vs Umur - Anak {gender_text} ({settings["age_range"]})'

            df = pd.read_excel(nama_file)
            #df = df.rename(columns={'SD-2': 'SD_2', 'SD-3': 'SD_3'}).sort_values(by='Month').drop_duplicates(subset='Month')

            x_original = df['Month']
            z_cols = ['SD3neg', 'SD2neg', 'SD1neg', 'SD0', 'SD1', 'SD2', 'SD3']
            poly_funcs = {col: np.poly1d(np.polyfit(x_original, df[col], 5)) for col in z_cols}

            x_smooth = np.linspace(x_original.min(), x_original.max(), 500)
            smooth_data = {col: func(x_smooth) for col, func in poly_funcs.items()}
            
            fig, ax = plt.subplots(figsize=(12, 7))

            # --- TAMBAHKAN BARIS INI ---
            # Mengatur warna latar belakang Figure menjadi biru muda
            if kelamin == 'L':
                fig.set_facecolor('steelblue')#fig.set_facecolor('darkturquoise') deepskyblue dodgerblue
            else:
                fig.set_facecolor('hotpink')
            # ---------------------------
            
            ax.fill_between(x_smooth, smooth_data['SD3neg'], smooth_data['SD2neg'], color='yellow', alpha=0.5)
            ax.fill_between(x_smooth, smooth_data['SD2neg'], smooth_data['SD1neg'], color='lightgreen', alpha=0.4)
            ax.fill_between(x_smooth, smooth_data['SD1neg'], smooth_data['SD1'], color='darkgreen', alpha=0.4)
            ax.fill_between(x_smooth, smooth_data['SD1'], smooth_data['SD2'], color='lightgreen', alpha=0.5)
            ax.fill_between(x_smooth, smooth_data['SD2'], smooth_data['SD3'], color='yellow', alpha=0.5)
            
            for col, data in smooth_data.items():
                ax.plot(x_smooth, data, color='black' if col not in ['SD3neg', 'SD3'] else 'red', lw=1)
            
            ax.scatter(umur_anak, berat_anak, marker='*', c='darkviolet', s=250, ec='black', zorder=10, label=f'Data Anak')
            
            z_scores_at_age = {col: func(umur_anak) for col, func in poly_funcs.items()}
            interpretasi, warna = get_interpretation_wfa(berat_anak, z_scores_at_age)
            props = dict(boxstyle='round', facecolor=warna, alpha=0.8)
            ax.text(0.03, 0.97, f"Interpretasi: {interpretasi}", transform=ax.transAxes, fontsize=12, va='top', bbox=props)
            
            ax.set_title(judul, pad=20, fontsize=16, color='white', fontweight='bold')
            if umur_anak > 60:
                ax.set_xlabel('Umur', fontsize=12, color='white', labelpad=26)
            else:
                ax.set_xlabel('Umur (Bulan)', fontsize=12, color='white')
            ax.set_ylabel('Berat Badan (kg)', fontsize=12, color='white')
            ax.set_xlim(settings["xlim"]); ax.set_ylim(settings["ylim"])
            ax.set_xticks(settings["xticks"]); ax.set_yticks(settings["yticks"])
            #ax.grid(True, which='both', linestyle='--', linewidth=0.5)
            # Gambar grid Y
            ax.grid(which='major', axis='y', linestyle='-', linewidth='0.8', color='gray')
            ax.grid(which='minor', axis='y', linestyle=':', linewidth='0.5', color='lightgray')

            # 1. Buat sumbu Y kedua
            ax2 = ax.twinx()
            ax2.set_ylim(ax.get_ylim())
            
            ax.xaxis.set_major_locator(MultipleLocator(settings["x_major"]))
            ax.xaxis.set_minor_locator(MultipleLocator(settings["x_minor"]))
            ax.yaxis.set_major_locator(MultipleLocator(settings["y_major"]))
            ax2.yaxis.set_major_locator(MultipleLocator(settings["y_major"]))
            ax.yaxis.set_minor_locator(MultipleLocator(settings["y_minor"]))
            ax2.yaxis.set_minor_locator(MultipleLocator(settings["y_minor"]))
            
            # 1. Nonaktifkan Spines (Frame) untuk KEDUA sumbu
            for spine_position in ['top', 'bottom', 'left', 'right']:
                ax.spines[spine_position].set_visible(False)
                ax2.spines[spine_position].set_visible(False)
            
            ax.tick_params(which='minor', axis='x', length=0)
            ax.tick_params(which='minor', axis='y', length=0)
            ax.tick_params(which='major', axis='x', labelcolor='white', length=0)
            ax.tick_params(which='major', axis='y', labelcolor='white', length=0)
            ax2.tick_params(which='both', axis='y', labelcolor='white', length=0)#sumbu y ke-dua (sebelah kanan)

            ax.grid(which='major', linestyle='-', linewidth='0.8', color='gray')
            ax.grid(which='minor', axis='y', linestyle=':', linewidth='0.7', color='gray')

            
            # --- LOGIKA KONDISIONAL UNTUK SUMBU X ---
            if umur_anak > 60:
                # === Pengaturan Manual untuk 5-10 Tahun ===
                
                # 1. Tentukan posisi Major Tick untuk penempatan grid utama (di setiap tahun)
                major_x_ticks = [60, 72, 84, 96, 108, 120]
                ax.set_xticks(major_x_ticks)
                ax.grid(which='major', axis='x', linestyle='-', linewidth='0.8', color='gray')

                # 2. Sembunyikan label default agar kita bisa gambar manual
                ax.tick_params(axis='x', labelbottom=False)

                # 3. Gambar label TAHUN secara manual
                month_to_year = {60: '5', 72: '6', 84: '7', 96: '8', 108: '9', 120: '10'}
                posisi_y_tahun = settings["ylim"][0] - 1.5  # Posisi Y untuk label tahun
                
                for bulan, tahun in month_to_year.items():
                    ax.text(bulan, posisi_y_tahun, tahun, ha='center', va='top', fontsize=12, color='white', fontweight='bold')
                    # Tambahkan teks "Tahun" di bawah angka
                    ax.text(bulan, posisi_y_tahun - 1.2, 'Tahun', ha='center', va='top', fontsize=8, color='white')

                # 4. Gambar grid dan label BULAN minor (3, 6, 9)
                posisi_y_bulan = settings["ylim"][0] - 0.8 # Posisi Y untuk label bulan
                posisi_y_teks  = settings["ylim"][0] - 1.4 # Posisi Y untuk teks "Bulan"
                for awal_tahun_bulan in range(60, 120, 12): # Loop per tahun (60, 72, 84, 96, 108)
                    for tambahan_bulan in [3, 6, 9]:
                        posisi_x = awal_tahun_bulan + tambahan_bulan
                        # Gambar garis grid minor vertikal
                        ax.axvline(x=posisi_x, color='gray', linestyle=':', linewidth=0.7, zorder=0)
                        # Gambar label bulan
                        ax.text(posisi_x, posisi_y_bulan, str(tambahan_bulan), ha='center', va='top', fontsize=8, color='white')
                        ax.text(posisi_x, posisi_y_teks, "Bulan", ha='center', va='top', fontsize=6, color='white')

            
            ax.legend(loc='lower right')
            fig.tight_layout()
            #plt.show()
            st.pyplot(fig)

        except Exception as e:
            print(f"\nError pada proses WfA: {e}")

# ==============================================================================
# FUNGSI-FUNGSI UNTUK KURVA BERAT BADAN vs TINGGI/PANJANG (WfH/WfL)
# ==============================================================================

def get_input_wfh():
    """Meminta input untuk kurva Berat Badan vs Tinggi/Panjang."""
    while True:
        kelamin = input("Masukkan jenis kelamin anak (L/P): ").upper()
        if kelamin in ['L', 'P']: break
        print("Input tidak valid. Harap masukkan 'L' atau 'P'.")

    umur_str = input(f"Umur anak {'laki-laki' if kelamin == 'L' else 'perempuan'} (bulan): ")
    umur = float(umur_str)
    
    prompt_panjang = "Panjang" if umur <= 24 else "Tinggi"
    panjang_str = input(f"{prompt_panjang} badan anak (cm): ")
    berat_str = input("Berat badan anak (kg): ")

    panjang = float(panjang_str)
    
    if not (45 <= panjang <= 120): # Rentang diperluas hingga 120 cm untuk anak 5 tahun
        raise ValueError("Panjang/Tinggi badan harus berada dalam rentang 45 hingga 120 cm.")
        
    return kelamin, umur, panjang, float(berat_str)

def get_settings_wfh(age_in_months):
    """Menentukan pengaturan plot untuk WfH berdasarkan usia."""
    if age_in_months <= 24:
        return {
            "xlim": (45, 110), "ylim": (1, 25), 
            "xticks": range(45, 110, 5), "yticks": range(1, 25, 2), 
            "x_major": 5, "x_minor": 1, # Minor grid setiap 1 cm (5 bagian)
            "y_major": 2, "y_minor": 0.5,
            "age_range": "0-24 Bulan"
            }
    else:
        return {
            "xlim": (65, 120), "ylim": (5, 31), 
            "xticks": range(65, 120, 5), "yticks": range(5, 31, 2), 
            "x_major": 5, "x_minor": 1, # Minor grid setiap 1 cm
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

def handle_weight_for_height():
    """Fungsi utama untuk menangani semua logika kurva Berat Badan vs Tinggi/Panjang."""
    try:
        kelamin, umur_anak, panjang_anak, berat_anak = get_input_wfh()
        #tambahan
        settings = get_settings_wfh(umur_anak)
        
        gender_text = "Perempuan" if kelamin == 'P' else "Laki-laki"
        
        # Logika untuk memilih file dan pengaturan berdasarkan USIA
        if umur_anak <= 24:
            nama_file = f"wfl_{'girls' if kelamin == 'P' else 'boys'}_0-to-2-years_zscores.xlsx"
            x_axis_label = "Panjang Badan (cm)"
            judul = f'Grafik Berat Badan vs Panjang Badan - Anak {gender_text} (0-2 Tahun)'
            x_col_name = 'Length'
        else: # Usia > 24 bulan
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

        # --- TAMBAHKAN BARIS INI ---
        # Mengatur warna latar belakang Figure menjadi biru muda
        if kelamin == 'L':
            fig.set_facecolor('steelblue')#fig.set_facecolor('darkturquoise') deepskyblue dodgerblue
        else:
            fig.set_facecolor('hotpink')
        # ---------------------------
        
        ax.fill_between(x_smooth, smooth_data['SD3neg'], smooth_data['SD2neg'], color='yellow', alpha=0.5)
        ax.fill_between(x_smooth, smooth_data['SD2neg'], smooth_data['SD2'], color='green', alpha=0.4)
        ax.fill_between(x_smooth, smooth_data['SD2'], smooth_data['SD3'], color='yellow', alpha=0.5)
        
        for col, data in smooth_data.items():
            ax.plot(x_smooth, data, color='black' if col not in ['SD3neg', 'SD3'] else 'red', lw=1)
        
        ax.scatter(panjang_anak, berat_anak, marker='*', c='darkviolet', s=250, ec='black', zorder=10, label=f'Data Anak')
        
        z_scores_at_length = {col: func(panjang_anak) for col, func in poly_funcs.items()}
        interpretasi, warna = get_interpretation_wfh(berat_anak, z_scores_at_length)
        props = dict(boxstyle='round', facecolor=warna, alpha=0.8)
        ax.text(0.03, 0.97, f"Status Gizi: {interpretasi}", transform=ax.transAxes, fontsize=12, va='top', bbox=props)
        
        ax.set_title(judul, pad=20, fontsize=16, color='white', fontweight='bold')
        ax.set_xlabel(x_axis_label, fontsize=12, color='white')
        ax.set_ylabel('Berat Badan (kg)', fontsize=12, color='white')
        ax.set_xlim(settings["xlim"]); ax.set_ylim(settings["ylim"])
        ax.set_xticks(settings["xticks"]); ax.set_yticks(settings["yticks"])
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)

        # 1. Buat sumbu Y kedua
        ax2 = ax.twinx()
        ax2.set_ylim(ax.get_ylim())

        ax.xaxis.set_major_locator(MultipleLocator(settings["x_major"]))
        ax.xaxis.set_minor_locator(MultipleLocator(settings["x_minor"]))
        ax.yaxis.set_major_locator(MultipleLocator(settings["y_major"]))
        ax2.yaxis.set_major_locator(MultipleLocator(settings["y_major"]))
        ax.yaxis.set_minor_locator(MultipleLocator(settings["y_minor"]))
        ax2.yaxis.set_minor_locator(MultipleLocator(settings["y_minor"]))
        
        # 1. Nonaktifkan Spines (Frame) untuk KEDUA sumbu
        for spine_position in ['top', 'bottom', 'left', 'right']:
            ax.spines[spine_position].set_visible(False)
            ax2.spines[spine_position].set_visible(False)
        
        # Mengatur Ticks (tanda) berdasarkan interval yang sudah ditentukan
        ax.tick_params(which='minor', axis='x', length=0)
        ax.tick_params(which='minor', axis='y', length=0)
        ax.tick_params(which='major', axis='x', labelcolor='white', length=0)
        ax.tick_params(which='major', axis='y', labelcolor='white', length=0)
        ax2.tick_params(which='both', axis='y', labelcolor='white', length=0)#sumbu y ke-dua (sebelah kanan)

        ax.grid(which='major', linestyle='-', linewidth='0.8', color='gray')
        ax.grid(which='minor', axis='y', linestyle='-', linewidth='0.7', color='gray')

        #ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.legend(loc='lower right')
        fig.tight_layout()
        plt.show()

    except Exception as e:
        print(f"\nError pada proses WfH/WfL: {e}")


# ==============================================================================
# FUNGSI-FUNGSI BARU UNTUK KURVA IMT vs UMUR (BMI-for-Age)
# ==============================================================================

def get_input_bmi():
    """Meminta input untuk kurva IMT vs Umur dan menghitung IMT."""
    while True:
        kelamin = input("Masukkan jenis kelamin anak (L/P): ").upper()
        if kelamin in ['L', 'P']: break
        print("Input tidak valid. Harap masukkan 'L' atau 'P'.")

    umur_str = input(f"Umur anak {'laki-laki' if kelamin == 'L' else 'perempuan'} (bulan): ")
    tinggi_str = input("Tinggi/Panjang badan anak (cm): ")
    berat_str = input("Berat badan anak (kg): ")
    
    umur = float(umur_str)
    tinggi_cm = float(tinggi_str)
    berat_kg = float(berat_str)

    if not (0 <= umur <= 60):
        raise ValueError("Usia harus berada dalam rentang 0 hingga 60 bulan.")
    
    # Hitung IMT: berat(kg) / (tinggi(m))^2
    tinggi_m = tinggi_cm / 100
    if tinggi_m == 0:
        raise ValueError("Tinggi badan tidak boleh nol.")
    bmi_anak = berat_kg / (tinggi_m ** 2)
    print(f"IMT anak yang dihitung: {bmi_anak:.2f} kg/m²")

    return kelamin, umur, bmi_anak

def get_settings_bmi(age_in_months):
    """Menentukan pengaturan plot untuk IMT vs Umur."""
    if age_in_months <= 24:
        return {
            "xlim": (0, 24), "ylim": (9, 23), 
            "xticks": range(0, 24, 1), "yticks": range(9, 23, 1), 
            "x_major": 1, "x_minor": 1, # Minor grid setiap 1 cm (5 bagian)
            "y_major": 1, "y_minor": 0.2,
            "age_range": "0-24 Bulan"
            }
    else:
        return {
            "xlim": (24, 60), "ylim": (11.6, 21), 
            "xticks": np.arange(24, 60, 2), "yticks": range(12, 21, 1), 
            "x_major": 2, "x_minor": 2, # Minor grid setiap 1 cm (5 bagian)
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

def handle_bmi_for_age():
    """Fungsi utama untuk menangani semua logika kurva IMT vs Umur."""
    try:
        kelamin, umur_anak, bmi_anak = get_input_bmi()
        settings = get_settings_bmi(umur_anak)
        
        gender_text = "Perempuan" if kelamin == 'P' else "Laki-laki"
        
        # Memilih file berdasarkan usia
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
        
        # Sumbu X untuk plot adalah seluruh rentang 0-60 bulan
        x_smooth = np.linspace(0, 60, 500)
        smooth_data = {col: func(x_smooth) for col, func in poly_funcs.items()}
        
        fig, ax = plt.subplots(figsize=(12, 7))

        # --- TAMBAHKAN BARIS INI ---
        # Mengatur warna latar belakang Figure menjadi biru muda
        if kelamin == 'L':
            fig.set_facecolor('steelblue')#fig.set_facecolor('darkturquoise') deepskyblue dodgerblue
        else:
            fig.set_facecolor('hotpink')
        # ---------------------------
        
        # Mengisi area dan menggambar garis (sama seperti WfH)
        ax.fill_between(x_smooth, smooth_data['SD3neg'], smooth_data['SD2neg'], color='yellow', alpha=0.5)
        ax.fill_between(x_smooth, smooth_data['SD2neg'], smooth_data['SD2'], color='green', alpha=0.4)
        ax.fill_between(x_smooth, smooth_data['SD2'], smooth_data['SD3'], color='yellow', alpha=0.5)
        for col, data in smooth_data.items():
            ax.plot(x_smooth, data, color='black' if col not in ['SD3neg', 'SD3'] else 'red', lw=1)

        # Plot titik IMT anak
        ax.scatter(umur_anak, bmi_anak, marker='*', c='darkviolet', s=250, ec='black', zorder=10, 
                   label=f'Data Anak ({umur_anak} bln, {bmi_anak:.2f} IMT)')

        # --- TAMBAHKAN BARIS INI ---
        # Menambahkan label nilai IMT di samping titik
        ax.text(umur_anak + 0.3,  # Posisi X: sedikit ke kanan dari titik
                bmi_anak,         # Posisi Y: sejajar dengan titik
                f'{bmi_anak:.2f} kg/m²', # Teks yang ditampilkan (IMT dengan 1 desimal)
                fontsize=11,         # Ukuran font
                color='darkviolet',   # Warna teks disamakan dengan warna titik
                va='center')        # Vertical Alignment: center
        # ---------------------------
        
        # Menambahkan interpretasi
        z_scores_at_age = {col: func(umur_anak) for col, func in poly_funcs.items()}
        interpretasi, warna = get_interpretation_bmi(bmi_anak, z_scores_at_age)
        props = dict(boxstyle='round', facecolor=warna, alpha=0.8)
        ax.text(0.03, 0.97, f"Status Gizi: {interpretasi}", transform=ax.transAxes, fontsize=12, va='top', bbox=props)
        
        # Kustomisasi Sumbu dan Grid
        ax.set_title(judul, pad=20, fontsize=16, color='white', fontweight='bold')
        ax.set_xlabel('Umur (Bulan)', fontsize=12, color='white')
        ax.set_ylabel('IMT (kg/m²)', fontsize=12, color='white') # Label Y diubah menjadi IMT
        ax.set_xlim(settings["xlim"]); ax.set_ylim(settings["ylim"])
        ax.set_xticks(settings["xticks"]); ax.set_yticks(settings["yticks"])
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        
        # 1. Buat sumbu Y kedua
        ax2 = ax.twinx()
        ax2.set_ylim(ax.get_ylim())

        ax.xaxis.set_major_locator(MultipleLocator(settings["x_major"]))
        ax.xaxis.set_minor_locator(MultipleLocator(settings["x_minor"]))
        ax.yaxis.set_major_locator(MultipleLocator(settings["y_major"]))
        ax2.yaxis.set_major_locator(MultipleLocator(settings["y_major"]))
        ax.yaxis.set_minor_locator(MultipleLocator(settings["y_minor"]))
        ax2.yaxis.set_minor_locator(MultipleLocator(settings["y_minor"]))
        
        # 1. Nonaktifkan Spines (Frame) untuk KEDUA sumbu
        for spine_position in ['top', 'bottom', 'left', 'right']:
            ax.spines[spine_position].set_visible(False)
            ax2.spines[spine_position].set_visible(False)
        
        # Mengatur Ticks (tanda) berdasarkan interval yang sudah ditentukan
        ax.tick_params(which='minor', axis='x', length=0)
        ax.tick_params(which='minor', axis='y', length=0)
        ax.tick_params(which='major', axis='x', labelcolor='white', length=0)
        ax.tick_params(which='major', axis='y', labelcolor='white', length=0)
        ax2.tick_params(which='both', axis='y', labelcolor='white', length=0)#sumbu y ke-dua (sebelah kanan)

        ax.grid(which='major', linestyle='-', linewidth='0.8', color='gray')
        ax.grid(which='minor', axis='y', linestyle=':', linewidth='0.7', color='gray')

        #ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        
        ax.legend(loc='lower right')
        fig.tight_layout()
        plt.show()

    except Exception as e:
        print(f"\nError pada proses IMT vs Umur: {e}")


# ==============================================================================
# FUNGSI-FUNGSI UNTUK KURVA PANJANG/TINGGI BADAN vs UMUR (L/H-f-A) - BARU
# ==============================================================================

def get_input_lhfa():
    """Meminta input usia (minggu/bulan), jenis kelamin, dan panjang badan."""
    while True:
        kelamin = input("Masukkan jenis kelamin anak (L/P): ").upper()
        if kelamin in ['L', 'P']: break
        print("Input tidak valid. Harap masukkan 'L' atau 'P'.")

    # Meminta pengguna memilih satuan usia
    while True:
        unit_pilihan = input("Pilih satuan usia (1: Minggu, 2: Bulan): ")
        if unit_pilihan in ['1', '2']: break
        print("Pilihan tidak valid. Harap masukkan '1' atau '2'.")

    umur_str = input("Masukkan usia anak (dalam satuan yang dipilih): ")
    panjang_str = input("Panjang/Tinggi badan anak (cm): ")

    umur_input = float(umur_str)
    panjang_anak = float(panjang_str)

    # Konversi semua input usia ke satuan BULAN untuk diproses
    if unit_pilihan == '1': # Jika input dalam minggu
        umur_bulan = umur_input / 4.345
        if umur_input > 60 * 4.345: # Validasi setara 60 bulan
             raise ValueError("Usia dalam minggu melebihi rentang 5 tahun.")
    else: # Jika input sudah dalam bulan
        umur_bulan = umur_input

    if not (0 <= umur_bulan <= 60):
        raise ValueError("Usia harus berada dalam rentang 0 hingga 60 bulan.")

    return kelamin, umur_bulan, panjang_anak

def get_settings_lhfa(age_in_months):
    """Menentukan pengaturan plot, file, dan unit untuk L/H-f-A berdasarkan usia."""
    # Rentang 1: Usia 0-6 bulan (menggunakan data mingguan, ditampilkan per bulan)
    if age_in_months <= 6:
        return {
            "file_key": "0-to-13-weeks", "x_col_name": "Week", "is_weekly": True,
            "xlim": (0, 6), "ylim": (43, 75), 
            "xticks": range(0, 6, 1), "yticks": range(43, 75, 5),
            "x_major": 1, "x_minor": 1, # Minor grid setiap 1 cm (5 bagian)
            "y_major": 5, "y_minor": 1,
            "x_axis_label": "Umur (Bulan)", 
            "age_range_title": "0-6 Bulan"
        }
    # Rentang 2: Usia 6-24 Bulan
    elif 6 < age_in_months <= 24:
        return {
            "file_key": "0-to-2-years", "x_col_name": "Month", "is_weekly": False,
            "xlim": (6, 24), "ylim": (60, 100), 
            "xticks": range(6, 24, 1), "yticks": range(60, 100, 5),
            "x_axis_label": "Umur (Bulan)", 
            "x_major": 1, "x_minor": 1, # Minor grid setiap 1 cm (5 bagian)
            "y_major": 5, "y_minor": 1,
            "age_range_title": "6-24 Bulan"
        }
    # Rentang 3: Usia 24-60 Bulan
    else:
        return {
            "file_key": "2-to-5-years", "x_col_name": "Month", "is_weekly": False,
            "xlim": (24, 60), "ylim": (76, 125), 
            "xticks": range(24, 60, 2), "yticks": range(76, 125, 5),
            "x_axis_label": "Umur (Bulan)", 
            "x_major": 2, "x_minor": 1, # Minor grid setiap 1 cm (5 bagian)
            "y_major": 5, "y_minor": 1,
            "age_range_title": "2-5 Tahun"
        }

def get_interpretation_lhfa(panjang_anak, z_scores_at_age):
    """Menentukan interpretasi untuk stunting."""
    # Pastikan kunci ada sebelum diakses
    if 'SD2' not in z_scores_at_age or 'SD_2' not in z_scores_at_age or 'SD_3' not in z_scores_at_age:
        return "Data tidak lengkap untuk interpretasi", "gray"
    if panjang_anak > z_scores_at_age['SD2']: return "Tinggi", 'forestgreen'
    elif panjang_anak >= z_scores_at_age['SD_2']: return "Normal", 'forestgreen'
    elif panjang_anak >= z_scores_at_age['SD_3']: return "Pendek (Stunting)", 'yellow'
    else: return "Sangat Pendek (Severe Stunting)", 'red'

def handle_length_for_age():
    """
    Fungsi utama yang menggabungkan data mingguan dan bulanan untuk kurva L/H-f-A.
    """
    try:
        kelamin, umur_anak, panjang_anak = get_input_lhfa()
        settings = get_settings_lhfa(umur_anak)

        gender_text = "Perempuan" if kelamin == 'P' else "Laki-laki"
        gender_file_key = 'girls' if kelamin == 'P' else 'boys'

        # Logika untuk memilih dan menggabungkan data
        if umur_anak <= 24:
            # === PROSES KONSOLIDASI DATA UNTUK 0-24 BULAN ===
            # 1. Baca kedua file data
            file_mingguan = f"lhfa_{gender_file_key}_0-to-13-weeks_zscores.xlsx"
            file_bulanan = f"lhfa_{gender_file_key}_0-to-2-years_zscores.xlsx"
            df_mingguan = pd.read_excel(file_mingguan)
            df_bulanan = pd.read_excel(file_bulanan)

            # 2. Standarisasi Sumbu X: konversi minggu ke bulan
            df_mingguan['Month'] = df_mingguan['Week'] / 4.345

            # 3. Gabungkan kedua DataFrame
            combined_df = pd.concat([df_mingguan, df_bulanan], ignore_index=True)

            # 4. Bersihkan data: prioritaskan data mingguan (yang ada di urutan pertama)
            combined_df = combined_df.sort_values(by='Month').drop_duplicates(subset='Month', keep='first')
            
            x_original = combined_df['Month']
            df_to_process = combined_df
            #settings = {"xlim": (0, 24), "ylim": (45, 95), "age_range_title": "0-24 Bulan"}
            judul = f'Grafik Panjang Badan vs Umur - Anak {gender_text} ({settings["age_range_title"]})'
        
        else: # Usia > 24 bulan
            # === PROSES UNTUK 2-5 TAHUN (TIDAK PERLU GABUNG DATA) ===
            nama_file = f"lhfa_{gender_file_key}_2-to-5-years_zscores.xlsx"
            df_tahunan = pd.read_excel(nama_file)
            
            x_original = df_tahunan['Month']
            df_to_process = df_tahunan
            #settings = {"xlim": (24, 60), "ylim": (80, 120), "age_range_title": "2-5 Tahun"}
            judul = f'Grafik Tinggi Badan vs Umur - Anak {gender_text} ({settings["age_range_title"]})'

        # --- Proses Pembuatan Model & Plotting (Berlaku untuk kedua kondisi) ---
        rename_dict = {'SD-3': 'SD3neg', 'SD-2': 'SD2neg', 'SD-1': 'SD1neg'}
        df_to_process = df_to_process.rename(columns=rename_dict)
        
        z_cols = ['SD3neg', 'SD2neg', 'SD1neg', 'SD0', 'SD1', 'SD2', 'SD3']
        poly_funcs = {col: np.poly1d(np.polyfit(x_original, df_to_process[col], 3)) for col in z_cols}

        x_smooth = np.linspace(x_original.min(), x_original.max(), 500)
        smooth_data = {col: func(x_smooth) for col, func in poly_funcs.items()}
        
        fig, ax = plt.subplots(figsize=(12, 7))

        # --- TAMBAHKAN BARIS INI ---
        # Mengatur warna latar belakang Figure menjadi biru muda
        if kelamin == 'L':
            fig.set_facecolor('steelblue')#fig.set_facecolor('darkturquoise') deepskyblue dodgerblue
        else:
            fig.set_facecolor('hotpink')
        # ---------------------------
        
        line_colors = {'SD3': 'black', 'SD2': 'red', 'SD1':'black', 'SD0': 'green', 'SD1neg':'black', 'SD2neg': 'red', 'SD3neg': 'black'}
        for col, data in smooth_data.items():
            if col in line_colors:
                ax.plot(x_smooth, data, color=line_colors[col], lw=1.5)
        
        ax.scatter(umur_anak, panjang_anak, marker='*', c='darkviolet', s=250, ec='black', zorder=10, label=f'Data Anak')
        
        z_scores_at_age = {col: func(umur_anak) for col, func in poly_funcs.items()}
        # Ganti nama kolom sementara untuk fungsi interpretasi
        z_scores_at_age['SD_2'] = z_scores_at_age.get('SD2neg', None)
        z_scores_at_age['SD_3'] = z_scores_at_age.get('SD3neg', None)
        interpretasi, warna = get_interpretation_lhfa(panjang_anak, z_scores_at_age)
        
        props = dict(boxstyle='round', facecolor=warna, alpha=0.8)
        ax.text(0.03, 0.97, f"Interpretasi: {interpretasi}", transform=ax.transAxes, fontsize=12, va='top', bbox=props)
        
        ax.set_title(judul, pad=20, fontsize=16, color='white', fontweight='bold')
        if umur_anak <= 6:
            ax.set_xlabel("Umur (Minggu atau Bulan)", fontsize=12, color='white', labelpad=22)
        else:
            ax.set_xlabel("Umur (Bulan)", fontsize=12, color='white')

        if umur_anak >= 24:
            ax.set_ylabel('Tinggi Badan (cm)', fontsize=12, color='white')
        else:
            ax.set_ylabel('Panjang Badan (cm)', fontsize=12, color='white')
        ax.set_xlim(settings["xlim"]); ax.set_ylim(settings["ylim"])
        ax.set_xticks(settings["xticks"]); ax.set_yticks(settings["yticks"])
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)

         # 1. Buat sumbu Y kedua
        ax2 = ax.twinx()
        ax2.set_ylim(ax.get_ylim())

        #ax.xaxis.set_major_locator(MultipleLocator(settings["x_major"]))
        #ax.xaxis.set_minor_locator(MultipleLocator(settings["x_minor"]))
        ax.yaxis.set_major_locator(MultipleLocator(settings["y_major"]))
        ax2.yaxis.set_major_locator(MultipleLocator(settings["y_major"]))
        ax.yaxis.set_minor_locator(MultipleLocator(settings["y_minor"]))
        ax2.yaxis.set_minor_locator(MultipleLocator(settings["y_minor"]))

        # 1. Nonaktifkan Spines (Frame) untuk KEDUA sumbu
        for spine_position in ['top', 'bottom', 'left', 'right']:
            ax.spines[spine_position].set_visible(False)
            ax2.spines[spine_position].set_visible(False)
        
        # Mengatur Ticks (tanda) berdasarkan interval yang sudah ditentukan
        ax.tick_params(which='minor', axis='x', length=0)
        ax.tick_params(which='minor', axis='y', length=0)
        ax.tick_params(which='major', axis='x', labelcolor='white', length=0)
        ax.tick_params(which='major', axis='y', labelcolor='white', length=0)
        ax2.tick_params(which='both', axis='y', labelcolor='white', length=0)#sumbu y ke-dua (sebelah kanan)

        ax.grid(which='major', linestyle='-', linewidth='0.9', color='gray')
        ax.grid(which='minor', axis='y', linestyle=':', linewidth='0.8', color='gray')
        
        
        # 2. Atur Ticks dan Grid Sumbu X (kondisional)
        if umur_anak <= 24:
            # Untuk 0-6 bulan, kita atur tick manual dan grid spesial
            major_x_ticks = [0, 3, 4, 5, 6]
            ax.set_xticks(major_x_ticks)
            ax.grid(which='major', axis='x', linestyle='-', linewidth='0.9', color='gray') # Grid utama
            
            # Nonaktifkan label bawaan agar kita bisa menggambar manual
            ax.tick_params(axis='x', labelbottom=False)

            # --- KODE BARU: Menggambar label X secara manual ---
            y_pos_normal = settings["ylim"][0] - 0.8  # Posisi Y untuk label '0'
            y_pos_lower  = settings["ylim"][0] - 0.9  # Posisi Y lebih rendah untuk 3,4,5,6
            
            for tick in major_x_ticks:
                y_pos = y_pos_lower if tick in [3, 4, 5, 6] else y_pos_normal
                ax.text(tick, y_pos, str(tick), ha='center', va='top', fontsize=12, color='white')

            # Gambar 12 garis vertikal untuk 13 bagian antara 0-3 bulan
            interval = 3.0 / 13.0
            for i in range(1, 13):
                ax.axvline(x=i * interval, color='lightgray', linestyle='-', linewidth=0.8, zorder=0)
            
            # Loop untuk menempatkan setiap angka
            y_min_limit = settings["ylim"][0]
            for i in range(1, 14): # Loop dari 1 sampai 13
                posisi_x = i * interval
                label_text = str(i)
                # Tempatkan teks sedikit di bawah garis sumbu x
                ax.text(posisi_x, y_min_limit - 0.2, label_text, 
                        ha='center', va='top', fontsize=8, color='white')
            # -----------------------------------------------
        
        
        ax.legend(loc='lower right')
        fig.tight_layout()
        plt.show()

    except Exception as e:
        print(f"\nError pada proses L/H-f-A: {e}")


# ==============================================================================
# FUNGSI-FUNGSI BARU UNTUK KURVA LINGKAR KEPALA vs UMUR (HCFA)
# ==============================================================================

def get_input_hcfa():
    """Meminta input untuk kurva Lingkar Kepala vs Umur."""
    while True:
        kelamin = input("Masukkan jenis kelamin anak (L/P): ").upper()
        if kelamin in ['L', 'P']: break
        print("Input tidak valid. Harap masukkan 'L' atau 'P'.")

    while True:
        unit_pilihan = input("Pilih satuan usia (1: Minggu, 2: Bulan): ")
        if unit_pilihan in ['1', '2']: break
        print("Pilihan tidak valid. Harap masukkan '1' atau '2'.")

    umur_str = input("Masukkan usia anak (dalam satuan yang dipilih): ")
    lingkar_kepala_str = input("Lingkar kepala anak (cm): ")

    umur_input = float(umur_str)
    lingkar_kepala = float(lingkar_kepala_str)

    # Konversi semua input usia ke satuan BULAN untuk diproses
    if unit_pilihan == '1': # Jika input dalam minggu
        umur_bulan = umur_input / 4.345
        if umur_input > 60 * 4.345:
             raise ValueError("Usia dalam minggu melebihi rentang 5 tahun.")
    else: # Jika input sudah dalam bulan
        umur_bulan = umur_input

    if not (0 <= umur_bulan <= 60):
        raise ValueError("Usia harus berada dalam rentang 0 hingga 60 bulan.")

    return kelamin, umur_bulan, lingkar_kepala

def get_settings_hcfa(age_in_months):
    """Menentukan pengaturan plot untuk HCFA berdasarkan usia."""
    if age_in_months <= 24:
        return {
            "xlim": (0, 24), "ylim": (32, 52),
            "age_range_title": "0-24 Bulan"
        }
    else:
        return {
            "xlim": (24, 60), "ylim": (42, 56),
            "age_range_title": "2-5 Tahun"
        }

def get_interpretation_hcfa(hc_anak, z_scores_at_age):
    """Menentukan interpretasi untuk Lingkar Kepala."""
    if hc_anak > z_scores_at_age['SD2']:
        return "Makrosefali (Perlu evaluasi medis)", 'yellow'
    elif hc_anak >= z_scores_at_age['SD2neg']:
        return "Normal", 'forestgreen'
    else: # hc_anak < z_scores_at_age['SD2neg']
        return "Mikrosefali (Perlu evaluasi medis)", 'yellow'

def handle_head_circumference_for_age():
    """Fungsi utama yang menangani kurva Lingkar Kepala vs Umur."""
    try:
        kelamin, umur_anak_bulan, hc_anak = get_input_hcfa()
        settings = get_settings_hcfa(umur_anak_bulan)
        
        gender_text = "Perempuan" if kelamin == 'P' else "Laki-laki"
        gender_file_key = 'girls' if kelamin == 'P' else 'boys'
        
        judul = f'Grafik Lingkar Kepala vs Umur - Anak {gender_text} ({settings["age_range_title"]})'

        # === PROSES KONSOLIDASI DATA ===
        file_mingguan = f"hcfa_{gender_file_key}_0-13-zscores.xlsx"
        file_bulanan = f"hcfa_{gender_file_key}_0-5-zscores.xlsx"
        df_mingguan = pd.read_excel(file_mingguan)
        df_bulanan = pd.read_excel(file_bulanan)
        df_mingguan['Month'] = df_mingguan['Week'] / 4.345
        combined_df = pd.concat([df_mingguan, df_bulanan], ignore_index=True)
        combined_df = combined_df.sort_values(by='Month').drop_duplicates(subset='Month', keep='first')
        
        x_original = combined_df['Month']
        df_to_process = combined_df

        rename_dict = {'SD-3': 'SD3neg', 'SD-2': 'SD2neg', 'SD-1': 'SD1neg'}
        df_to_process = df_to_process.rename(columns=rename_dict)
        
        z_cols = ['SD3neg', 'SD2neg', 'SD1neg', 'SD0', 'SD1', 'SD2', 'SD3']
        poly_funcs = {col: np.poly1d(np.polyfit(x_original, df_to_process[col], 5)) for col in z_cols}

        x_smooth = np.linspace(0, 60, 500) # Buat kurva untuk seluruh rentang
        smooth_data = {col: func(x_smooth) for col, func in poly_funcs.items()}
        
        fig, ax = plt.subplots(figsize=(12, 7))

        # --- TAMBAHKAN BARIS INI ---
        # Mengatur warna latar belakang Figure menjadi biru muda
        if kelamin == 'L':
            fig.set_facecolor('steelblue')#fig.set_facecolor('darkturquoise') deepskyblue dodgerblue
        else:
            fig.set_facecolor('hotpink')
        # ---------------------------
        
        # --- PLOTTING GAYA GARIS WHO ---
        line_colors = {'SD3': 'black', 'SD2': 'red', 'SD1': 'orange', 'SD0': 'green', 'SD1neg': 'orange', 'SD2neg': 'red', 'SD3neg': 'black'}
        for col, data in smooth_data.items():
            if col in line_colors:
                ax.plot(x_smooth, data, color=line_colors[col], lw=1.5)
        
        # Menambahkan label angka Z-score di ujung kanan garis
        for col, data in smooth_data.items():
            if col in ['SD3', 'SD2', 'SD0', 'SD2neg', 'SD3neg']:
                label_text = col.replace('neg', '-').replace('SD', '')
                ax.text(x_smooth[-1] + (settings['xlim'][1] * 0.01), data[-1], label_text, 
                        color=line_colors[col], va='center', ha='left', fontweight='bold')
        # --------------------------------

        ax.scatter(umur_anak_bulan, hc_anak, marker='*', c='darkviolet', s=250, ec='black', zorder=10, label=f'Data Anak')
        
        z_scores_at_age = {col: func(umur_anak_bulan) for col, func in poly_funcs.items()}
        interpretasi, warna = get_interpretation_hcfa(hc_anak, z_scores_at_age)
        props = dict(boxstyle='round', facecolor=warna, alpha=0.8)
        ax.text(0.03, 0.97, f"Interpretasi: {interpretasi}", transform=ax.transAxes, fontsize=12, va='top', bbox=props)
        
        # Kustomisasi Sumbu dan Grid
        ax.set_title(judul, pad=20, fontsize=16, color='white', fontweight='bold')
        ax.set_xlabel("Umur (Bulan)", fontsize=12)
        ax.set_ylabel('Lingkar Kepala (cm)', fontsize=12)
        ax.set_xlim(settings["xlim"]); ax.set_ylim(settings["ylim"])
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        
        ax.legend(loc='lower right')
        fig.tight_layout()
        plt.show()

    except Exception as e:
        print(f"\nError pada proses HCFA: {e}")

# ==============================================================================
# BAGIAN UTAMA APLIKASI WEB STREAMLIT
# ==============================================================================

# Judul utama aplikasi yang akan tampil di bagian atas halaman web
st.title("📈 Program Kurva Pertumbuhan Anak WHO")
st.write("Aplikasi untuk memvisualisasikan pertumbuhan anak berdasarkan standar WHO.")

# Buat menu pilihan di sidebar (bilah sisi) kiri
# st.sidebar.selectbox akan membuat dropdown menu yang rapi
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

# === Logika untuk menampilkan konten berdasarkan pilihan menu ===
# Alih-alih memeriksa input '1', '2', dst., kita memeriksa teks
# dari opsi yang dipilih di sidebar.

if menu_pilihan == "Berat Badan menurut UMUR (WfA)":
    # Panggil fungsi yang sudah Anda modifikasi untuk WfA
    handle_weight_for_age()

elif menu_pilihan == "Berat Badan menurut TINGGI/PANJANG (WfH/L)":
    # Panggil fungsi yang sudah Anda modifikasi untuk WfH/L
    handle_weight_for_height()

elif menu_pilihan == "IMT menurut UMUR (BMI-for-Age)":
    # Panggil fungsi yang sudah Anda modifikasi untuk BMI
    handle_bmi_for_age()

elif menu_pilihan == "Panjang/Tinggi Badan menurut UMUR (L/H-f-A)":
    # Panggil fungsi yang sudah Anda modifikasi untuk L/H-f-A
    handle_length_for_age()

elif menu_pilihan == "Lingkar Kepala menurut UMUR (HCFA)":
    # Panggil fungsi yang sudah Anda modifikasi untuk HCFA
    handle_head_circumference_for_age()