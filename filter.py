import tkinter as tk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import mysql.connector

# Inisialisasi dan latih model Naive Bayes
vektorizer_tfidf = TfidfVectorizer()
model_klasifikasi = MultinomialNB()

# Terhubung ke server MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="data_email"
)

# Memeriksa apakah koneksi berhasil
if db.is_connected():
    print("Berhasil terhubung ke database")

    # Membuat kursor untuk berinteraksi dengan database
    kursor = db.cursor()

    # Menjalankan query SELECT untuk mengambil data dari kolom 'email' dan 'label'
    query = "SELECT email, label FROM email"  
    kursor.execute(query)

    # Mengambil semua baris
    hasil_query = kursor.fetchall()

    # Menutup kursor
    kursor.close()

    # Memisahkan hasil query menjadi teks_email dan label_spam
    teks_email_from_database = [row[0] for row in hasil_query]
    label_spam_from_database = [row[1] for row in hasil_query]

    # Update data email dan label dengan data dari database
    teks_email = teks_email_from_database
    label_spam = label_spam_from_database

    # Vektorisasi teks menggunakan TF-IDF
    matriks_fitur_tfidf = vektorizer_tfidf.fit_transform(teks_email)

    # Latih model
    model_klasifikasi.fit(matriks_fitur_tfidf, label_spam)

    # Fungsi untuk memfilter email
    def filter_email():
        isi_email = kotak_isi_email.get("1.0", "end-1c")

        # Vektorisasi teks menggunakan model TF-IDF yang sudah dilatih
        vektor_email = vektorizer_tfidf.transform([isi_email])

        # Prediksi menggunakan model Naive Bayes
        prediksi = model_klasifikasi.predict(vektor_email)

        label_hasil.config(text=f"Hasil: {prediksi[0]}")

    # Membuat jendela utama
    utama = tk.Tk()
    utama.title("Aplikasi Filter Email Spam(ERIC_18120062)")

    # Membuat label dan area teks untuk input email
    label_isi_email = tk.Label(utama, text="Masukkan Teks Email:")
    label_isi_email.pack(pady=10)

    kotak_isi_email = tk.Text(utama, width=50, height=5)
    kotak_isi_email.pack(pady=10, padx=10)

    # Membuat tombol dan menetapkannya ke fungsi filter_email
    tombol_filter = tk.Button(utama, text="Filter Email", command=filter_email)
    tombol_filter.pack(pady=10)

    # Membuat label untuk menampilkan hasil
    label_hasil = tk.Label(utama, text="Hasil: ")
    label_hasil.pack(pady=10)

    # Menjalankan jendela
    utama.mainloop()

    # Menutup koneksi setelah aplikasi ditutup
    db.close()

else:
    print("Gagal terhubung ke database")
