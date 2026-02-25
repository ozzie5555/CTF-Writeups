#!/usr/bin/env python3
import os
import sys
from pathlib import Path

PLATFORMS = ["picoctf", "ctflearn", "stemba-ctf"]
CATEGORIES = [
    "binary-exploitation", "forensic", "web-exploitation", "cryptography",
    "osint", "miscellaneous", "reverse-engineering", "sandbox"
]

def sanitize(name):
    return name.lower().replace(" ", "-").replace("_", "-").strip("-")

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 new_challenge.py <platform> <category> <challenge_name>")
        print("\nExample:")
        print("  python3 new_challenge.py stemba-ctf forensic 'Stringgle Minion'")
        sys.exit(1)

    platform, category, name = sys.argv[1], sys.argv[2], sys.argv[3]

    if platform not in PLATFORMS:
        print(f"❌ Platform '{platform}' tidak dikenali. Pilih dari: {', '.join(PLATFORMS)}")
        sys.exit(1)
    if category not in CATEGORIES:
        print(f"❌ Kategori '{category}' tidak dikenali. Pilih dari: {', '.join(CATEGORIES)}")
        sys.exit(1)

    clean_name = sanitize(name)
    path = Path("ctf") / platform / category / clean_name
    path.mkdir(parents=True, exist_ok=True)

    # Buat README.md
    readme = path / "README.md"
    if not readme.exists():
        readme.write_text(f"""# Write-Up: {name} (??? Points - ???)

## Analisis Masalah
[Deskripsi challenge dan analisis awal]

## Langkah Penyelesaian
### 1. [Langkah pertama]
[Berikan perintah dan penjelasan]
![Screenshot 1](assets/images/screenshot1.png)

### 2. [Langkah kedua]
[Penjelasan lanjutan]
![Screenshot 2](assets/images/screenshot2.png)

## Tools yang Digunakan
1. **tool1** - [Fungsi]
2. **tool2** - [Fungsi]

## Kesimpulan
[Ringkasan teknik dan flag]
""")

    # Buat folder assets/images secara otomatis
    (path / "assets" / "images").mkdir(parents=True, exist_ok=True)

    print(f"✅ Challenge siap di: {path}")
    print(f"📝 Edit file: {readme}")
    print(f"🖼️  Simpan screenshot di: {path}/assets/images/")

if __name__ == "__main__":
    main()
