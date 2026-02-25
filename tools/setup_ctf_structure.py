import os
from pathlib import Path

# Konfigurasi
PLATFORMS = ["picoctf", "ctflearn", "stemba-ctf"]
CATEGORIES = [
    "binary-exploitation",
    "forensic",
    "web-exploitation",
    "cryptography",
    "osint",
    "miscellaneous",
    "reverse-engineering",
    "sandbox"
]

def create_ctf_structure():
    base_dir = Path("ctf")
    base_dir.mkdir(exist_ok=True)
    
    for platform in PLATFORMS:
        platform_dir = base_dir / platform
        platform_dir.mkdir(parents=True, exist_ok=True)
        
        for category in CATEGORIES:
            category_dir = platform_dir / category
            category_dir.mkdir(exist_ok=True)
            # Buat placeholder agar Git bisa track folder kosong
            (category_dir / ".gitkeep").touch()
    
    print("✅ Struktur CTF Writeups berhasil dibuat!")
    print(f"📁 Total platform: {len(PLATFORMS)}")
    print(f"📁 Total kategori per platform: {len(CATEGORIES)}")
    print("\nContoh penggunaan:")
    print("  ctf/picoctf/web-exploitation/nama-challenge/")

if __name__ == "__main__":
    create_ctf_structure()
