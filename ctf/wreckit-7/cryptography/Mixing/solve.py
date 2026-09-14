#!/usr/bin/env python3
"""
Solver for "Mixing" (crypto, 337 pts)

--------------------------------------------------------------------------
IDEA
--------------------------------------------------------------------------
chall.py generates a 512-bit prime P (P % 4 == 3), a random curve
parameter A, and a point (X1, Y1) where Y1 = flag (padded to 64 bytes).
B is derived so that the point lies on the Weierstrass curve:

        y^2 = x^3 + A*x + B   (mod P)

It then repeatedly applies:

    num = (x^2 - A)^2 - 8*B*x
    den = 4*(x^3 + A*x + B)
    x'  = num * den^-1  (mod P)

This is *exactly* the standard elliptic-curve point-DOUBLING formula for
the x-coordinate only (derived from the slope lambda = (3x^2+A)/(2y),
x' = lambda^2 - 2x). So the output list

    X = [X1, X2, X3, X4, X5, X6]   (X2 = 2*P1, X3 = 4*P1, ... as x-coords)

are x-coordinates of a doubling chain of the secret point P1 = (X1, Y1).

The challenge never prints P, A or B - we must recover all three purely
from the 6 leaked x-coordinates.

--------------------------------------------------------------------------
STEP 1 - Recover P
--------------------------------------------------------------------------
For each consecutive pair (X_i, X_{i+1}) the doubling relation, cleared
of the modular inverse, gives an *integer* polynomial identity that is
only guaranteed to vanish modulo P (not over the integers):

    e_i(A, B) = (X_i^2 - A)^2 - 8*B*X_i - 4*X_{i+1}*(X_i^3 + A*X_i + B) ≡ 0 (mod P)

e_i is quadratic in A and linear in B. Taking two such equations e_i, e_j
we eliminate B (linear combination using each equation's B-coefficient),
producing a polynomial g_ij(A) (quadratic in A) that is also ≡ 0 mod P.

Taking two different g's (which share the unknown root A mod P) and
computing their algebraic RESULTANT with respect to A eliminates A too,
producing a plain integer that must be a multiple of P (since both
polynomials in F_P[A] share a common root there, their resultant is
0 mod P).

Doing this for a few independent pairs and taking the GCD of the
resulting integers isolates P (after stripping any small common
cofactors picked up incidentally). We verify with isprime() and P%4==3.

--------------------------------------------------------------------------
STEP 2 - Recover A and B
--------------------------------------------------------------------------
Once P is known, take e_i mod P for two indices i, j. Each is linear in
B, so B = -(A^2*a2 + A*a1 + a0) * inverse(b1) mod P. Setting the two
expressions for B equal removes B and leaves one quadratic equation in
A mod P, solved directly with the square-root formula valid because
P ≡ 3 (mod 4):

    sqrt(a) = a^((P+1)/4) mod P

This gives (at most) two candidate A values; each yields a candidate B.
We keep the (A, B) pair that satisfies ALL FIVE original equations e_i
(mod P) - the other root is an artifact of the elimination process.

--------------------------------------------------------------------------
STEP 3 - Recover the flag
--------------------------------------------------------------------------
With the true (A, B) and X1 = X[0], compute

    rhs = X1^3 + A*X1 + B (mod P)


which is Y1^2 mod P. Because P ≡ 3 (mod 4), take the square root the
same way. There are two roots {y, P-y}; convert each to 64 bytes
(big-endian) and check which one starts with printable flag text
(the challenge right-pads the flag with 0x00 bytes before turning it
into an integer, so the correct root's byte string ends in \x00 bytes).
"""

from sympy import symbols, Poly, resultant, isprime
import math


# ---------------------------------------------------------------------
# 0. Leaked data from out.txt
# ---------------------------------------------------------------------
X = [1310728018303650763936027566726118990540730463418184722626247766533259897833339472201369793020753036897354956372655805443666265539520643579468280542790912,
     1948567695288789033882726566040664624967196105123510164670807174337853448573304124592834588010330665765241266759938926247542041919802062304813097620037961,
     3770888144390194259291756870781587478561974187172600114039080697232166318179389261967556513452232735112227886010717711511566088733244254977109884050750521,
     6685219650661520592837452091527901959121163338051479114854456479415168009003692128002422024872994156351020672099581144020816412383886103779026501845968524,
     3445973769773227766423737354206143846342976057594988433631816479986063937687945211927469517217182447001986012000990667311685794996130773953481639400178746,
     341460821872650281559806202378121714041594962254191119981490154027800966470418186955386638018116210324473072042502834593429857879741880406950528171126212]

A_s, B_s = symbols('A B')


def make_e(xi, xj):
    """Integer polynomial that must vanish mod P for consecutive x-coords."""
    return (xi**2 - A_s)**2 - 8 * B_s * xi - 4 * xj * (xi**3 + A_s * xi + B_s)


def get_coeffs(e):
    """e = a2*A^2 + a1*A + a0 + b1*B  ->  return (a2, a1, a0, b1)."""
    p = Poly(e, A_s, B_s)
    a2 = p.coeff_monomial(A_s**2)
    a1 = p.coeff_monomial(A_s)
    a0 = p.coeff_monomial(1)
    b1 = p.coeff_monomial(B_s)
    return a2, a1, a0, b1


def modsqrt(a, P):
    """Square root mod P, valid because P % 4 == 3."""
    a %= P
    if a == 0:
        return 0
    r = pow(a, (P + 1) // 4, P)
    return r if (r * r) % P == a else None


# ---------------------------------------------------------------------
# 1. Recover P via resultant elimination
# ---------------------------------------------------------------------
def recover_P():
    es = [make_e(X[i], X[i + 1]) for i in range(5)]

    # eliminate B between consecutive e_i -> quadratics in A only
    gs = []
    for i in range(4):
        p1, p2 = Poly(es[i], B_s), Poly(es[i + 1], B_s)
        b1 = p1.coeff_monomial(B_s)
        b2 = p2.coeff_monomial(B_s)
        g = b2 * es[i] - b1 * es[i + 1]        # B eliminated
        gs.append(Poly(g, A_s))

    # eliminate A via resultant between several independent pairs of g's
    pairs = [(0, 1), (1, 2), (2, 3), (0, 2), (1, 3)]
    rs = [int(resultant(gs[i].as_expr(), gs[j].as_expr(), A_s)) for i, j in pairs]

    g = rs[0]
    for r in rs[1:]:
        g = math.gcd(g, r)

    # strip small cofactors that got dragged along in the gcd
    for sp in range(2, 100000):
        while g % sp == 0:
            g //= sp

    assert isprime(g) and g % 4 == 3, "failed to recover P cleanly"
    return g


# ---------------------------------------------------------------------
# 2. Recover A, B  (mod P)
# ---------------------------------------------------------------------
def recover_A_B(P):
    es = [make_e(X[i], X[i + 1]) for i in range(5)]
    coeffs = [tuple(int(c) % P for c in get_coeffs(e)) for e in es]

    def solve_pair(i, j):
        a2i, a1i, a0i, b1i = coeffs[i]
        a2j, a1j, a0j, b1j = coeffs[j]
        inv_bi, inv_bj = pow(b1i, -1, P), pow(b1j, -1, P)

        # B = -(a2*A^2 + a1*A + a0) * inv_b   (from e_i = 0)
        # equate B from i and j  ->  quadratic in A
        c2 = (a2i * inv_bi - a2j * inv_bj) % P
        c1 = (a1i * inv_bi - a1j * inv_bj) % P
        c0 = (a0i * inv_bi - a0j * inv_bj) % P
        if c2 == 0:
            return []

        inv_c2 = pow(c2, -1, P)
        b, c = (c1 * inv_c2) % P, (c0 * inv_c2) % P
        disc = (b * b - 4 * c) % P
        sq = modsqrt(disc, P)
        if sq is None:
            return []

        inv2 = pow(2, -1, P)
        out = []
        for Acand in [(-b + sq) * inv2 % P, (-b - sq) * inv2 % P]:
            Bcand = (-(a2i * Acand * Acand + a1i * Acand + a0i) * inv_bi) % P
            out.append((Acand, Bcand))
        return out

    def check(Acand, Bcand):
        for xi, xj in zip(X, X[1:]):
            e = (xi**2 - Acand)**2 - 8 * Bcand * xi - 4 * xj * (xi**3 + Acand * xi + Bcand)
            if e % P != 0:
                return False
        return True

    for Acand, Bcand in solve_pair(0, 1):
        if check(Acand, Bcand):
            return Acand, Bcand

    raise RuntimeError("no valid (A, B) found")


# ---------------------------------------------------------------------
# 3. Recover the flag
# ---------------------------------------------------------------------
def recover_flag(P, A, B):
    X1 = X[0]
    rhs = (X1**3 + A * X1 + B) % P
    y = modsqrt(rhs, P)
    if y is None:
        raise RuntimeError("X1 not on the recovered curve")

    for cand in (y, P - y):
        raw = cand.to_bytes(64, 'big')
        if raw[:1].isascii() and raw[0:1] != b'\x00':
            return raw.rstrip(b'\x00')
    return None


if __name__ == "__main__":
    P = recover_P()
    print("[+] Recovered P:", P)

    A, B = recover_A_B(P)
    print("[+] Recovered A:", A)
    print("[+] Recovered B:", B)

    flag = recover_flag(P, A, B)
    print("[+] FLAG:", flag.decode())