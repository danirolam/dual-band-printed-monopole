"""Starting dimensions for a dual-band printed monopole with a parasitic inverted-L.

These are hand-calculation starting points for the HFSS sweeps, not final values.
Run:  python hand_calcs.py
"""
import math

C0 = 299_792_458.0  # speed of light, m/s

# Board, from the project brief
ER = 4.4      # FR-4 relative permittivity
H = 1.6e-3    # substrate thickness, m
Z0 = 50.0     # target feed-line impedance, ohms

F1 = 2.4e9    # band 1, set by the monopole
F2 = 5.8e9    # band 2, set by the parasitic element


def microstrip_width(z0, er, h):
    """Strip width for a given impedance (Hammerstad synthesis, Pozar Sec. 3.8)."""
    a = z0 / 60 * math.sqrt((er + 1) / 2) + (er - 1) / (er + 1) * (0.23 + 0.11 / er)
    w_over_h = 8 * math.exp(a) / (math.exp(2 * a) - 2)
    if w_over_h > 2:  # wide-strip branch
        b = 377 * math.pi / (2 * z0 * math.sqrt(er))
        w_over_h = 2 / math.pi * (b - 1 - math.log(2 * b - 1)
                                  + (er - 1) / (2 * er) * (math.log(b - 1) + 0.39 - 0.61 / er))
    return w_over_h * h


def microstrip_eeff(w, er, h):
    """Effective permittivity of a microstrip line (Pozar Sec. 3.8)."""
    return (er + 1) / 2 + (er - 1) / 2 / math.sqrt(1 + 12 * h / w)


def microstrip_z0(w, er, h):
    """Impedance of a strip of width w, used to check the synthesis."""
    ee = microstrip_eeff(w, er, h)
    u = w / h
    if u <= 1:
        return 60 / math.sqrt(ee) * math.log(8 / u + u / 4)
    return 120 * math.pi / (math.sqrt(ee) * (u + 1.393 + 0.667 * math.log(u + 1.444)))


def mm(x):
    return f"{x * 1e3:.2f} mm"


# 1. 50-ohm feed line
w = microstrip_width(Z0, ER, H)
ee_line = microstrip_eeff(w, ER, H)
print("1. 50-ohm microstrip feed line")
print(f"   width W              = {mm(w)}   (W/h = {w / H:.3f})")
print(f"   check: Z0 of that W  = {microstrip_z0(w, ER, H):.2f} ohm")
print(f"   eps_eff              = {ee_line:.3f}")
for f in (F1, F2):
    lam0 = C0 / f
    print(f"   at {f / 1e9:.1f} GHz: lambda0 = {mm(lam0)}, lambda_g = {mm(lam0 / math.sqrt(ee_line))}")

# 2. Monopole: resonates when about a quarter wavelength long.
#    The strip has FR-4 on one side and air on the other, so assume
#    eps_eff ~ (er + 1) / 2, the average of the two.
ee_strip = (ER + 1) / 2
print()
print(f"2. Monopole length Lm for {F1 / 1e9:.1f} GHz (quarter wave), eps_eff = (er+1)/2 = {ee_strip:.2f}")
lm = C0 / F1 / 4 / math.sqrt(ee_strip)
print(f"   Lm = lambda0 / (4 sqrt(eps_eff)) = {mm(lm)}")
print("   sensitivity to the eps_eff assumption:")
for e in (1.0, 2.0, ee_strip, ee_line):
    print(f"     eps_eff = {e:.2f}  ->  Lm = {mm(C0 / F1 / 4 / math.sqrt(e))}")

# 3. Parasitic inverted-L: floating (touches neither the monopole nor the ground),
#    so both ends are open and it resonates near half a wavelength, measured
#    along both arms of the L.
lp = C0 / F2 / 2 / math.sqrt(ee_strip)
print()
print(f"3. Parasitic element total length (both arms) for {F2 / 1e9:.1f} GHz (half wave), eps_eff = {ee_strip:.2f}")
print(f"   Lp = lambda0 / (2 sqrt(eps_eff)) = {mm(lp)}")
print(f"   (a grounded L would resonate near a quarter wave instead: {mm(lp / 2)})")

# Why a parasitic is needed: a quarter-wave monopole's next resonance is
# near 3/4 wavelength, i.e. about 3x the first frequency, not 5.8 GHz.
print()
print(f"Monopole's next resonance on its own: ~3 x {F1 / 1e9:.1f} GHz = {3 * F1 / 1e9:.1f} GHz, not {F2 / 1e9:.1f} GHz")
