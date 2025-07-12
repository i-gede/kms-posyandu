# Menggunakan image dasar Python
FROM python:3.9-slim

# Menetapkan direktori kerja di dalam container
WORKDIR /app

# Salin file requirements dan instal library terlebih dahulu
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Salin sisa file aplikasi
COPY . .

# Beritahu container untuk membuka port 7860
EXPOSE 7860

# Perintah untuk menjalankan aplikasi Streamlit dengan statistik dinonaktifkan
CMD ["streamlit", "run", "kms_wfa_lhfa_bfa_hcfa_acfa_wflh-st-0_1.py", "--server.port=7860", "--server.headless=true", "--browser.gatherUsageStats=false"]