import imaplib
import email
from email.header import decode_header
import pymysql
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import pas

# Ganti dengan informasi akun email Anda
alamat_email = pas.akun
kata_sandi = pas.passw

print(f"Email: {alamat_email}")

# Membuat koneksi IMAP
email_server = imaplib.IMAP4_SSL("imap.gmail.com")

# Masuk ke akun email
try:
    email_server.login(alamat_email, kata_sandi)
except imaplib.IMAP4.error as e:
    print(f"Login failed: {e}")
    exit()

# Pilih folder email (misalnya, "inbox")
email_server.select("inbox")

# Cari email yang belum dibaca
status, pesan = email_server.search(None, "UNSEEN")

# Ambil subjek dari 10 email terbaru yang belum dibaca
teks_email = []
for id_email in pesan[0].split()[-10:]:  # Ambil 10 email terbaru
    _, data_pesan = email_server.fetch(id_email, "(RFC822)")
    _, pesan_email = data_pesan[0]
    pesan_email = email.message_from_bytes(pesan_email)

    subjek = decode_header(pesan_email["Subject"])[0][0]
    pengirim = pesan_email.get("From")

    # Tampilkan informasi email di konsol
    print(f"Subjek: {subjek}")
    print(f"Dari: {pengirim}")
    print("-" * 40)

    teks_email.append(str(subjek))

# Vektorisasi teks menggunakan TF-IDF
vektorizer_tfidf = TfidfVectorizer()
matriks_fitur_tfidf = vektorizer_tfidf.fit_transform(teks_email)

# Load your pre-existing dataset from the database
host = 'localhost'
user = 'root'
password = ''
database = 'data_email'

koneksi_db = pymysql.connect(host=host, user=user, password=password, database=database)
kursor_db = koneksi_db.cursor()

# Assuming you have a 'label' column in your 'email' table
try:
    # Select the existing data from the 'email' table
    kursor_db.execute("SELECT id, email, label FROM email")
    hasil_query = kursor_db.fetchall()
    teks_email_database = [row[1] for row in hasil_query]
    label_spam_database = [row[2] for row in hasil_query]

    # Check if there is data in the existing dataset
    if label_spam_database:
        # Train the model Naive Bayes
        model_klasifikasi = MultinomialNB()
        model_klasifikasi.fit(matriks_fitur_tfidf, label_spam_database)

        # Predict labels for the new data
        label_spam_prediksi = model_klasifikasi.predict(matriks_fitur_tfidf)

        # Get the maximum existing ID
        kursor_db.execute("SELECT MAX(id) FROM email")
        max_id = kursor_db.fetchone()[0]
        if max_id is None:
            max_id = 0

        # Insert the new data into the 'email' table
        for idx, subjek_email in enumerate(teks_email):
            email_id = max_id + idx + 1
            label = 'spam' if label_spam_prediksi[idx] == 1 else 'non-spam'

            kursor_db.execute('''
                INSERT INTO email (id, email, label)
                VALUES (%s, %s, %s)
            ''', (email_id, subjek_email, label))

        koneksi_db.commit()
        print("Data inserted successfully.")
    else:
        print("No existing data in the dataset. Skipping training.")

except pymysql.Error as e:
    print(f"MySQL error: {e}")

finally:
    # Tutup koneksi
    email_server.close()
    email_server.logout()

    # Tutup koneksi database
    koneksi_db.close()
