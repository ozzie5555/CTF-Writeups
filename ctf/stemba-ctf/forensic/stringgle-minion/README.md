# Write-Up: Stringgle Minion (100 Points - Easy)

## Analisis Masalah
Challenge ini memberikan sebuah file gambar bernama `Triplemini.jpg` dengan deskripsi "Haloo Minion, ternyata Minion itu funny ya ...". Judul challenge "Stringgle Minion" terasa seperti permainan kata antara "String" dan "Struggle" (atau Single).

Dari petunjuk judul tersebut, saya menduga challenge ini tidak memerlukan teknik steganografi yang berat, melainkan penyembunyian data tekstual sederhana di dalam raw data gambar yang bisa diakses menggunakan perintah `strings`.

## Langkah Penyelesaian

### 1. Analisis Metadata Gambar

Langkah pertama yang saya lakukan adalah memeriksa metadata file untuk memastikan apakah ada petunjuk yang tertinggal di bagian komentar atau EXIF data lainnya.

Saya menggunakan tool `exiftool`:

```bash
exiftool Triplemini.jpg

```
![Exiftool Output](assets/images/exiftoolfr-file.png)
**Hasil analisis:**
Output menunjukkan format JPEG standar tanpa ada komentar (`Comment`) yang mencurigakan atau data aneh pada metadata. Saya melanjutkan ke analisis konten string.

### 2. Ekstraksi String ASCII

Mengingat judul challenge mengandung kata "String", saya langsung menggunakan perintah `strings` untuk menarik semua karakter yang bisa dibaca (printable characters) dari file binary tersebut.

```bash
strings Triplemini.jpg

```
![strings Output](assets/images/strings-file.png)
**Temuan dari strings:**
Di antara banyaknya karakter sampah, saya menemukan satu baris yang sangat mencolok dan terstruktur di bagian tengah output:
`bendera(65.164.162.61.156.71.65.137.64.154.141.137.64.154.64.137.142.60.171.137.142.60.171)`

Kata "bendera" jelas merujuk pada "Flag", dan angka-angka di dalam kurung kemungkinan besar adalah nilai karakter yang di-encode.

### 3. Decoding Pesan (Octal to Text)

Saya menganalisis deretan angka tersebut (`65.164.162...`). Saya menyadari bahwa tidak ada angka 8 atau 9 dalam deretan tersebut, dan format 3 digit yang dimulai dengan angka kecil mengindikasikan ini adalah bilangan **Oktal (Basis 8)**.

Saya menggunakan Python one-liner untuk mengonversi deretan angka oktal tersebut kembali menjadi teks ASCII:

```bash
python3 -c "print(''.join([chr(int(x, 8)) for x in '65.164.162.61.156.71.65.137.64.154.141.137.64.154.64.137.142.60.171.137.142.60.171'.split('.')]))"

```
![python Output](assets/images/python-file.png)
Script tersebut memisahkan angka berdasarkan titik, mengubahnya dari base-8 ke integer, lalu ke karakter ASCII.

**Hasil Decoding:**
Output yang dihasilkan adalah string unik: `5tr1n95_4la_4l4_b0y_b0y`.

### 4. Penyusunan Flag

Setelah mendapatkan string hasil decode, saya menggabungkannya dengan format standar kompetisi ini.

Flag akhirnya adalah: **`STEMBACTF{5tr1n95_4la_4l4_b0y_b0y}`**

## Tools yang Digunakan

1. **exiftool** - Untuk analisis awal metadata gambar
2. **strings** - Untuk mengekstrak teks ASCII dari dalam file binary gambar
3. **Python 3** - Untuk melakukan decoding (konversi) dari bilangan Oktal ke ASCII text

## Kesimpulan

Challenge "Stringgle Minion" adalah soal forensik dasar yang menguji ketelitian peserta dalam melihat pola data mentah. Penulis soal menyembunyikan flag bukan dengan menyisipkannya ke dalam piksel gambar (steganografi visual), melainkan menyimpannya sebagai teks yang di-encode.

Teknik utama yang digunakan adalah:

* **Obfuscation**: Menyembunyikan teks di dalam file binary.
* **Encoding**: Mengubah teks flag menjadi bilangan Oktal untuk menghindari deteksi langsung (search string "STEMBA").

Flag yang ditemukan adalah **`STEMBACTF{5tr1n95_4la_4l4_b0y_b0y}`**, yang dibaca sebagai "strings ala ala boy boy", sebuah kalimat plesetan/leetspeak.