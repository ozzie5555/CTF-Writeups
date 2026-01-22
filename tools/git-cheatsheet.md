# ───────────────────────────────
# 1. CEK PERUBAHAN SAAT INI
# ───────────────────────────────
git status

# ───────────────────────────────
# 2. TAMBAHKAN SEMUA PERUBAHAN
# ───────────────────────────────
git add .

# ───────────────────────────────
# 3. COMMIT DENGAN PESAN JELAS
# ───────────────────────────────
# → Jika TAMBAH challenge baru:
git commit -m "feat(<platform>): add <Challenge Name> write-up"

# → Jika PERBAIKI/UPDATE challenge:
git commit -m "fix(<platform>): update <Challenge Name> write-up"

# Contoh:
git commit -m "feat(stemba-ctf): add Pijipi write-up"
git commit -m "fix(picoctf): update Login Bypass with better screenshots"

# ───────────────────────────────
# 4. PUSH KE GITHUB
# ───────────────────────────────
git push

# ───────────────────────────────
# 5. (Opsional) CEK RIWAYAT TERAKHIR
# ───────────────────────────────
git log --oneline -3