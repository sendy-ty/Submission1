import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Konfigurasi halaman Streamlit
st.set_page_config(page_title="Dashboard Bike Sharing", layout="wide")

# Caching data untuk meningkatkan performa
@st.cache_data
def load_data():
    # Perbaikan path file untuk deployment
    # Mencoba beberapa kemungkinan lokasi file
    file_paths = [
        "all_data.csv",                        # Lokasi relatif
        "./all_data.csv",                      # Lokasi eksplisit dalam direktori yang sama
        "../all_data.csv",                     # Satu direktori di atas
        os.path.join(os.path.dirname(__file__), "all_data.csv"),  # Menggunakan path absolut
        "/mount/src/submission1/Dashboard/all_data.csv"  # Path deployment Streamlit
    ]
    
    # Mencoba membuka file dari berbagai kemungkinan lokasi
    for path in file_paths:
        try:
            df = pd.read_csv(path)
            return df
        except FileNotFoundError:
            continue
    
    # Jika file tidak ditemukan di semua lokasi, tampilkan pesan error
    st.error("File all_data.csv tidak ditemukan. Pastikan file tersedia di direktori yang benar.")
    
    # Fallback jika file tidak ditemukan: gunakan uploader file
    uploaded_file = st.file_uploader("Upload file all_data.csv", type="csv")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        return df
    else:
        # Buat DataFrame contoh kosong jika tidak ada file di-upload
        return pd.DataFrame({
            "year_day": [], "month_day": [], "weekday_day": [],
            "weathersit_day": [], "count_day": [], "casual_day": [], "registered_day": []
        })

# Memuat data
df = load_data()

# Periksa apakah dataframe kosong (fallback)
if df.empty:
    st.warning("Data kosong. Pastikan file all_data.csv tersedia atau upload file yang valid.")
    st.stop()  # Hentikan eksekusi jika data kosong

# Membentuk kolom tanggal berdasarkan year_day & month_day
df["date"] = pd.to_datetime(df["year_day"].astype(str) + "-" + df["month_day"].astype(str), format="%Y-%m", errors='coerce')

# Filter data 2 tahun terakhir
df_filtered = df[df["year_day"] >= (df["year_day"].max() - 1)]

# 📌 **Perkenalan Dataset**
st.title("📊 Dashboard Analisis Bike Sharing")
st.markdown("""
### 🔍 Perkenalan Dataset
Dataset ini berisi data peminjaman sepeda dalam dua tahun terakhir, mencakup berbagai faktor seperti:
- **Jumlah peminjaman** per hari dan per jam.
- **Pengguna casual vs registered**.
- **Kondisi cuaca**, musim, dan hari dalam seminggu.
- **Faktor waktu**, seperti tren peminjaman berdasarkan bulan, musim, dan akhir pekan.

Melalui analisis ini, kita akan melihat bagaimana berbagai faktor ini mempengaruhi peminjaman sepeda. 🚴‍♂️💨
""")

# === 📌 Pertanyaan 1: Dampak Cuaca terhadap Peminjaman ===
st.header("1️⃣ Seberapa besar dampak kondisi cuaca terhadap jumlah peminjaman sepeda pada akhir pekan dalam dua tahun terakhir?")

# Filter akhir pekan (Sabtu dan Minggu)
df_weekend = df_filtered[df_filtered["weekday_day"].isin([0, 6])]

# Plot perbandingan peminjaman berdasarkan kondisi cuaca
fig, ax = plt.subplots(figsize=(10, 5))
sns.boxplot(x="weathersit_day", y="count_day", data=df_weekend, palette="coolwarm")
ax.set_title("📌 Distribusi Peminjaman Sepeda Berdasarkan Kondisi Cuaca di Akhir Pekan")
ax.set_xlabel("Kondisi Cuaca (1 = Cerah, 2 = Mendung, 3 = Hujan)")
ax.set_ylabel("Jumlah Peminjaman")
st.pyplot(fig)

# === 📌 Pertanyaan 2: Tren Peminjaman Sepeda pada Musim Panas ===
st.header("2️⃣ Bagaimana pola pertumbuhan jumlah peminjaman sepeda pada musim panas dibandingkan dengan musim lainnya?")

# Menentukan musim
def get_season(month):
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Spring"
    elif month in [6, 7, 8]:
        return "Summer"
    else:
        return "Fall"

df_filtered["Season"] = df_filtered["month_day"].apply(get_season)

# Visualisasi perbandingan musim panas vs musim lainnya
fig, ax = plt.subplots(figsize=(10, 5))
sns.lineplot(x=df_filtered["date"], y=df_filtered["count_day"], hue=df_filtered["Season"], palette="tab10")
ax.set_title("📌 Tren Peminjaman Sepeda pada Musim Panas vs Musim Lainnya")
ax.set_xlabel("Tanggal")
ax.set_ylabel("Jumlah Peminjaman")
st.pyplot(fig)

# === 📌 Pertanyaan 3: Perbedaan Peminjaman Pengguna Casual vs Registered ===
st.header("3️⃣ Bagaimana perbedaan pola peminjaman sepeda antara pengguna casual dan registered pada hari kerja?")

# Filter hanya hari kerja (Senin - Jumat)
df_weekday = df_filtered[df_filtered["weekday_day"].isin([1, 2, 3, 4, 5])]

# Ubah format data agar sesuai dengan seaborn
df_melted = df_weekday.melt(id_vars=["date"], value_vars=["casual_day", "registered_day"], 
                            var_name="User Type", value_name="Peminjaman")

# Mapping kategori pengguna
df_melted["User Type"] = df_melted["User Type"].map({"casual_day": "Casual", "registered_day": "Registered"})

# Visualisasi perbandingan pengguna casual vs registered
fig, ax = plt.subplots(figsize=(10, 5))
sns.boxplot(x="User Type", y="Peminjaman", data=df_melted, palette="pastel")
ax.set_title("📌 Peminjaman Sepeda oleh Pengguna Casual vs Registered pada Hari Kerja")
ax.set_xlabel("Tipe Pengguna")
ax.set_ylabel("Jumlah Peminjaman")
st.pyplot(fig)

# 📌 **Kesimpulan Analisis**
st.markdown("""
## 📌 Kesimpulan Analisis
Berdasarkan analisis yang telah dilakukan terhadap data peminjaman sepeda, berikut beberapa temuan utama yang diperoleh:

### **1️⃣ Pengaruh Cuaca terhadap Peminjaman Sepeda**
✅ Hasil analisis menunjukkan bahwa **peminjaman sepeda lebih banyak dilakukan oleh pengguna terdaftar** dibandingkan dengan pengguna kasual.  
✅ Pengguna terdaftar berkontribusi lebih dari **2,5 juta** transaksi peminjaman, sedangkan pengguna kasual hanya sekitar **600 ribu** transaksi.  
✅ Hal ini mengindikasikan bahwa mayoritas pelanggan adalah pengguna tetap yang rutin menggunakan layanan ini.

### **2️⃣ Tren Penggunaan Sepeda Berdasarkan Bulan**
✅ **Peminjaman meningkat dari Maret hingga puncaknya pada Juni - Agustus**, dengan lebih dari **300 ribu** peminjaman per bulan.  
✅ Saat memasuki **musim dingin (Desember), terjadi penurunan drastis hingga kurang dari 100 ribu peminjaman per bulan**.  
✅ Hal ini menunjukkan bahwa **cuaca hangat meningkatkan penggunaan sepeda**, sedangkan musim dingin menurunkan aktivitas bersepeda.

### **3️⃣ Perbandingan Pengguna Casual dan Registered**
✅ Kondisi cuaca memiliki dampak yang signifikan terhadap tingkat peminjaman sepeda.  
✅ Saat **cuaca buruk (hujan deras, badai), jumlah peminjaman turun hingga sekitar 4.492 per hari**.  
✅ Sebaliknya, **pada cuaca cerah atau mendung, peminjaman bisa mencapai lebih dari 40 ribu kali per hari**.  
✅ Ini menunjukkan bahwa **kenyamanan dan keamanan dalam bersepeda sangat dipengaruhi oleh kondisi cuaca**.

💡 **Kesimpulan Umum**:  
Faktor **cuaca, musim, dan jenis pengguna** sangat berpengaruh terhadap pola peminjaman sepeda. **Musim panas dan cuaca cerah meningkatkan penggunaan sepeda**, sedangkan **musim dingin dan hujan menurunkannya**. Pengguna terdaftar adalah pelanggan utama, sedangkan pengguna kasual lebih bersifat musiman. 🚴‍♂️✨
""")