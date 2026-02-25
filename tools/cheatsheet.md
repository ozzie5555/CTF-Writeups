# 1. Buat struktur challenge baru
python3 tools/new_challenge.py stemba-ctf miscellaneous "Pijipi"

# 2. Edit write-up
code ctf/stemba-ctf/miscellaneous/pijipi/README.md

# 3. Masukkan screenshot ke folder images
mkdir -p ctf/stemba-ctf/miscellaneous/pijipi/assets/images
cp ~/Downloads/*.png ctf/stemba-ctf/miscellaneous/pijipi/assets/images/

# 4. Pastikan path gambar di README.md menggunakan:
#    assets/images/nama-file.png

# 5. Tambahkan ke Git
git add ctf/stemba-ctf/miscellaneous/pijipi/

# 6. Commit dengan pesan standar
git commit -m "feat(stemba-ctf): add Pijipi write-up"

# 7. Push ke GitHub
git push origin main