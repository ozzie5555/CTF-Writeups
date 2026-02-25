# Write-Up: Crack the Power (Unknown Points - Medium)

## Analisis Masalah

Challenge ini menyajikan masalah enkripsi RSA. Berdasarkan deskripsi, modulus $n$ dibangun dari bilangan prima yang sangat besar sehingga serangan faktorisasi tidak memungkinkan dilakukan. Namun, terdapat anomali pada nilai eksponen publiknya, yaitu $e = 20$.

Dalam kriptografi RSA, nilai $e$ yang sangat kecil sangat rentan terhadap serangan **Low Exponent Attack**. Karena $e$ kecil, ada kemungkinan nilai $m^e$ tidak melampaui $n$ sama sekali. Jika $m^e < n$, maka operasi modulo $n$ tidak berpengaruh, dan kita dapat mencari pesan asli $m$ hanya dengan menarik akar pangkat $e$ dari *ciphertext* $c$.

## Langkah Penyelesaian

### 1. Ekstraksi Parameter RSA

Saya mulai dengan membaca file `message.txt` untuk mendapatkan nilai $n, e,$ dan $c$. Saya mencatat bahwa $e$ bernilai 20, yang sangat tidak lazim dan lemah untuk standar RSA.

```bash
cat message.txt

```
**![cat Output](assets/images/cat.png)**
*(Di sini saya mengambil screenshot isi file message.txt yang menampilkan angka-angka masif)*

### 2. Implementasi Serangan Low Exponent

Saya membuat *script* Python menggunakan *library* `gmpy2` untuk menarik akar pangkat 20 dari nilai $c$. Saya juga menyiapkan fungsi iterasi $k$ untuk berjaga-jaga jika terjadi *wrap around* pada modulus, namun ternyata pada $k = 0$ akar yang sempurna sudah ditemukan.

```python
import gmpy2
from Crypto.Util.number import long_to_bytes

# Masukkan variabel dari soal
n = 718204453817916632384745594761900464412144284705396459555716996319312571515592763943145934923673551915339141531553031134429114773058956306106500001671368432519272757858096014834936872615193112144319812943678891456959272220636119264415015020165074274832579509242714109956298048230049758440586171674963729188716723456458194433701171028919206866609943434282369373218290465626780729902496421904457237378457686822786940281510025847164910694926099274321807566281149684545815957271404104980501231385991832997218932135792206480920142153806391334667546347189708934360039169929965734295156106305678346864431229099615153956114170652898295616739821955186487137045546621669382973480089056994971406148317223631282502904301425947334399040747850663426551256165462834602070932340607757069029118774249462088639270711074523814833419696917336313799548073671226933918006077312555298632074087709581083779195319039463651500670736660295741275474430597627373785401275311478205671039709699621181040880979445780924799766714591377541657440239272356215994618125022760557081950055215576564046389950059970629607602280976406520427594530200241437828616607992940055164106571484256063707809883156987595015277831171345781117218314358633769560567681431683061714668293787
e = 20
c = 640637430810406857500566702096274079953234675442588712312106071904739499753398196527344640811211863722507254239415694819658045618138336642576884391879473392890230707971098037832398086644737027052626228736785956882223200606159684451634377610328546762858522141975597851840146359987859722345000991878661453671323412360968895582061494778497806380915142184196289535350393166627827071039949914412770114974582515640305291773127777421254039786025154606968666635013785457491982265342058032520153813453599143627413759182717345225168698308519659443942778949086394257710245780304341349878498988215036368938776796574378330306231657048595127991471711596098783374857393044282771517132891710342477350547018519353178402258910615154338704720057384458777553456467427729268841634142520031345815584869228128878199550466142543457854980045969943593285011027905364799360858411442027387934350028982173477202918407132277424424215253794395022342744476629669368449521238198744274650910502291336750941085240886812450891840935584954453053914568767631706062136137642013113245272610139383169120735490321663686852628008988984881307500426298651960109438706600837190105373313866086801

print("[*] Memulai serangan Brute-force pada eksponen kecil...")

# Mencoba brute-force k dari 0 hingga 10000
for k in range(10000):
    target = c + (k * n)
    
    # Menarik akar pangkat 'e' (20) dari target
    root, is_exact = gmpy2.iroot(target, e)
    
    # Jika hasilnya bulat sempurna (is_exact == True)
    if is_exact:
        print(f"\n[+] Sukses! Ditemukan pada k = {k}")
        
        # Ubah angka int tersebut menjadi teks byte
        flag = long_to_bytes(root)
        print(f"[+] Flag: {flag.decode('utf-8', errors='ignore')}")
        break
else:
    print("\n[-] Gagal menemukan akar yang tepat. Coba perbesar range k.")

```
**![script Output](assets/images/script.png)**
*(Di sini saya mengambil screenshot terminal saat menjalankan solve.py dan menemukan hasil pada k = 0)*

### 3. Dekripsi Flag

Setelah menemukan akar pangkat yang sempurna, saya mengonversi nilai integer tersebut menjadi *bytes* untuk mendapatkan teks flag-nya.

```bash
python3 solve.py

```
**![flag Output](assets/images/flag.png)**

*(Di sini saya mengambil screenshot terminal yang menampilkan output flag: picoCTF{t1ny_e_46e014ec})*

## Tools yang Digunakan

1. **Python 3** - Untuk eksekusi script otomasi dekripsi.
2. **gmpy2** - Library untuk operasi akar pangkat tinggi presisi tinggi (`iroot`).
3. **pycryptodome** - Untuk fungsi utilitas `long_to_bytes`.

## Kesimpulan

Challenge "Crack the Power" membuktikan bahwa modulus yang sangat besar sekalipun tidak berguna jika eksponen publik $e$ terlalu kecil. Karena $e=20$, nilai pesan yang dipangkatkan ternyata tidak cukup besar untuk melewati nilai modulus ($m^e < n$), sehingga enkripsi ini kehilangan sifat "modulo"-nya dan hanya menjadi operasi pemangkatan biasa yang sangat mudah dipatahkan.

Flag yang ditemukan adalah: **`picoCTF{t1ny_e_46e014ec}`**. Makna dari flag ini merujuk pada "Tiny E" atau eksponen yang sangat kecil, yang merupakan akar masalah dari kerentanan enkripsi ini.

---