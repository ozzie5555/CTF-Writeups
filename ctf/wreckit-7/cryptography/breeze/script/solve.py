import ast, random
from hashlib import sha256, blake2s, sha3_256
from math import isqrt
from collections import Counter
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

print("[*] Loading data from out.txt...")
with open("out.txt") as f:
    data = f.read()
ns = {}
for line in data.strip().split("\n"):
    k, v = line.split("=", 1)
    ns[k.strip()] = v.strip()

P0 = ast.literal_eval(ns['o'])
p  = int(ns['n'])
g  = int(ns['r'])
le = ast.literal_eval(ns['le'])
sc = ast.literal_eval(ns['sc'])
ct = bytes.fromhex(ns['ct'].strip("'"))
print(f"  p={p}, g={g}, len(le)={len(le)}, len(sc)={len(sc)}, len(ct)={len(ct)}")

print("[*] Cloning MT19937 state from P0...")
def untemper(y):
    def undo_right(y, s):
        x = y
        for _ in range(32): x = y ^ (x >> s)
        return x
    def undo_left(y, s, mask):
        x = y
        for _ in range(32): x = y ^ ((x << s) & mask)
        return x
    y = undo_right(y, 18)
    y = undo_left(y, 15, 0xefc60000)
    y = undo_left(y, 7,  0x9d2c5680)
    y = undo_right(y, 11)
    return y & 0xffffffff

mt = [untemper(v) for v in P0]
R = random.Random()
R.setstate((3, tuple(mt + [624]), None))

print("[*] Replaying parameter generation...")
def A(): return R.getrandbits(32)
def B(n):
    x = 0
    while n:
        k = min(n, A().bit_length() or 1)
        if k > 32: k = 32
        x = (x << k) | (A() >> (32 - k))
        n -= k
    return x
def C(n):
    k = n.bit_length()
    while 1:
        x = B(k)
        if x < n: return x
def D(v):
    v = list(v)
    for i in range(len(v) - 1, 0, -1):
        j = C(i + 1)
        v[i], v[j] = v[j], v[i]
    return v
def U(): return (A() << 32) ^ A()
def V(n): return (1 << n) - 1

w0 = A().bit_length() + A().bit_length()
while w0 < 48 or w0 > 80:
    w0 = A().bit_length() + A().bit_length()
m0 = 1 << w0; z0 = m0 - 1

def X(t): return (U() ^ (t * 0x9e3779b97f4a7c15)) & z0
def G(t, o=0, u=1):
    x = X(t)
    y = (U() ^ ((x << 9) & z0) ^ (x >> 13) ^ (t << 17)) & z0
    pv = 2 + (x & 31); qv = 4 + ((y >> 7) & 31)
    v = []
    for i in range(qv):
        r = pv + i + ((x >> (i & 31)) & 1) + ((y >> ((i + 5) & 31)) & 1)
        if o: r = (r << 1) | 1
        v.append(r * u)
    return D(v)
def H(t, o=0, u=1):
    v = G(t, o, u)
    return v[C(len(v))]

a0 = H(A()); a1 = H(A())
while not 20 <= a0 + a1 <= 38:
    a0 = H(A()); a1 = H(A())
a2 = a0 + a1
a3 = H(A()) + H(A())
a4 = H(A(), 1)
while 1:
    a5 = B(a3) | 1
    a6 = pow(a5, a4, m0)
    if a5 > 3 and a6 not in (1, z0): break
a7 = H(A(), 0, 4)
while not 104 <= a7 <= 184: a7 = H(A(), 0, 4)
a8 = H(A()); a9 = H(A())
aa = [1 + C(H(A())) for _ in range(a7)]
ab = C(4); ac = C(4); ad = C(4); ae = C(3)
af = B(a2); ag = B(a2) | 1; ah = B(a2)
ai = C(a2); aj = C(a2); ak = B(a2); al = B(a2)
am = H(A())
while not 30 <= am <= 40: am = H(A())
an = p.bit_length()
ao = C(an); ap = B(an); aq = B(an) | 1; ar = B(an)

print(f"  w0={w0} a2={a2} a4={a4} a5={a5}")
print(f"  a7={a7} (len(aa)={len(aa)})  a8={a8} a9={a9}")
print(f"  ab={ab} ac={ac} ad={ad} ae={ae}")
print(f"  am={am} an={an} ao={ao}")
assert a7 == len(le), f"a7={a7} != len(le)={len(le)} — clone RNG salah!"
print(f"  [OK] a7 == len(le) == {len(le)}")

def L(x, s, w): return x if s == 0 else ((x << s) | (x >> (w - s))) & V(w)
def O(x, s, w): return x if s == 0 else ((x >> s) | (x << (w - s))) & V(w)
def L_inv(x, s, w): return x if s == 0 else ((x >> s) | (x << (w - s))) & V(w)
def O_inv(x, s, w): return x if s == 0 else ((x << s) | (x >> (w - s))) & V(w)

def CUT(x, i):
    y = x
    if ab & 1: y ^= af
    if ab & 2: y = L(y, ai, an)
    if ac & 1: y ^= (ag * i + ah) & V(an)
    if ac & 2: y = O(y, aj, an)
    if ad & 1: y ^= ak
    if ad & 2: y ^= al
    return L(y, ao, an)

def inverse_CUT(y, i):
    y = L_inv(y, ao, an)
    if ad & 2: y ^= al
    if ad & 1: y ^= ak
    if ac & 2: y = O_inv(y, aj, an)
    if ac & 1: y ^= (ag * i + ah) & V(an)
    if ab & 2: y = L_inv(y, ai, an)
    if ab & 1: y ^= af
    return y

for _ in range(2000):
    x = random.randrange(1, p); i = random.randrange(200)
    assert inverse_CUT(CUT(x, i), i) == x
print("  [OK] CUT inverse validated")

print("[*] Building BSGS table...")
em = V(am); M = 1 << am
m = isqrt(em + 1) + 1
baby = {}
pw = 1
for j in range(m):
    baby[pw] = j
    pw = (pw * g) % p
g_inv_m = pow(g, -m, p)
print(f"  m={m} table={len(baby)}")

def bsgs(h):
    if h == 1: return 0
    gamma = h % p
    for i in range(m):
        if gamma in baby:
            a = i * m + baby[gamma]
            if a <= em: return a
        gamma = (gamma * g_inv_m) % p
    return None

print("[*] Computing dlogs...")
dlogs = [None] * len(le)
valid = []
for i, val in enumerate(le):
    h = inverse_CUT(val, i)
    if h == 0 or h >= p: continue
    x = bsgs(h)
    if x is not None:
        dlogs[i] = x
        valid.append(i)
print(f"  Valid: {len(valid)}/{len(le)} ({100*len(valid)/len(le):.1f}%)")

A5 = pow(a5, a4, M)
assert A5 % 2 == 1
A5_inv = pow(A5, -1, M)
print(f"  A5 = {A5}")

cumsum_aa = []
s = 0
for x in aa:
    s += x
    cumsum_aa.append(s)

base_idx = a8 + 1 + a9 + 1

K_counter = Counter()
for i in valid:
    n = base_idx + cumsum_aa[i]
    if n < 2: continue
    K_cand = (dlogs[i] * pow(A5_inv, n - 1, M)) % M
    K_counter[K_cand] += 1

K, K_count = K_counter.most_common(1)[0]
print(f"[+] K = {K} (muncul {K_count}x dari {len(valid)} sampel)")

n_k0 = a8 + 1
n_k1 = a8 + 1 + a9 + 1
lo0 = (K * pow(A5, n_k0 - 1, M)) % M
lo1 = (K * pow(A5, n_k1 - 1, M)) % M
print(f"[+] lo0 = {lo0}")
print(f"[+] lo1 = {lo1}")

def HW(x): return x.bit_count()

print("\n[*] Brute ml...")
ml_cands = []
for ml_try in range(1 << 16):
    ok = True
    for i in range(16):
        x = (ml_try >> i) & 1
        y = HW(((ml_try * (i + 1) + lo0 + (lo1 << (i & 7))) & 0xffff))
        if not (0 <= sc[i] - (y << 1) - x <= 2):
            ok = False; break
    if ok: ml_cands.append(ml_try)
print(f"  ml candidates: {len(ml_cands)}")
ml = ml_cands[0]

print("[*] Brute mr...")
mr_cands = []
for mr_try in range(1 << 16):
    ok = True
    for j in range(16):
        i = 16 + j
        x = (mr_try >> j) & 1
        y = HW(((ml * (i + 1) + lo0 + (lo1 << (i & 7))) & 0xffff))
        if not (0 <= sc[i] - (y << 1) - x <= 2):
            ok = False; break
    if ok: mr_cands.append(mr_try)
print(f"  mr candidates: {len(mr_cands)}")

print("\n[*] Brute AES...")
def printability(b):
    if not b: return 0
    return sum(1 for c in b if 32 <= c < 127 or c in (9,10,13)) / len(b)

results = []
for mr_try in mr_cands:
    a_bytes = (lo0 ^ ml).to_bytes(8, "big")
    b_bytes = (lo1 ^ mr_try).to_bytes(8, "big")
    for salt in range(11):
        s0 = a_bytes + b_bytes + bytes([salt])
        for ae_try, hfn in [(0,sha256),(1,blake2s),(2,sha3_256)]:
            if ae_try != ae: continue   
            key = hfn(s0).digest()[:16]
            try:
                pt = AES.new(key, AES.MODE_ECB).decrypt(ct)
                flag = unpad(pt, 16)
                results.append((printability(flag), mr_try, salt, ae_try, flag))
            except Exception:
                pass

if not results:
    print("  [!] ae replay gagal, coba semua ae...")
    for mr_try in mr_cands:
        a_bytes = (lo0 ^ ml).to_bytes(8, "big")
        b_bytes = (lo1 ^ mr_try).to_bytes(8, "big")
        for salt in range(11):
            s0 = a_bytes + b_bytes + bytes([salt])
            for ae_try, hfn in [(0,sha256),(1,blake2s),(2,sha3_256)]:
                key = hfn(s0).digest()[:16]
                try:
                    pt = AES.new(key, AES.MODE_ECB).decrypt(ct)
                    flag = unpad(pt, 16)
                    results.append((printability(flag), mr_try, salt, ae_try, flag))
                except Exception:
                    pass

if not results:
    print("[-] Gagal decrypt.")
    exit(1)

results.sort(reverse=True)
print(f"\n  Total lolos PKCS7: {len(results)}")
for sc_, mr_try, salt, ae_try, flag in results[:5]:
    print(f"    score={sc_:.3f} mr={mr_try} salt={salt} ae={ae_try} {flag[:60]!r}")

score, mr_, salt_, ae_, flag = results[0]
print(f"\n{'='*60}")
print(f"[+] FLAG = {flag.decode(errors='replace')}")
print(f"    mr={mr_} salt={salt_} ae={ae_} score={score:.3f}")
print(f"{'='*60}")
