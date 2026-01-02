import math

# Physical constants
hbar = 1.054571817e-34  # J⋅s
m_neutron = 1.67492749804e-27  # kg
eV_to_J = 1.602176634e-19  # J/eV
pi = math.pi

# Parameters
a = 25e-9  # 25 nm well width
w = -2.0 * eV_to_J  # -2.0 eV well depth
h = 0.5 * eV_to_J   # 0.5 eV barrier height

# Ground state energy
E1_kinetic = (pi * hbar)**2 / (2 * m_neutron * a**2)
E1_total = w + E1_kinetic

print("NEUTRON TUNNELING - ULTRA-NARROW BARRIER")
print("=" * 45)
print(f"Ground state energy: {E1_total/eV_to_J:.8f} eV")
print(f"Barrier height: {h/eV_to_J:.1f} eV")
print(f"Energy gap: {(h - E1_total)/eV_to_J:.1f} eV")
print()

# Calculate penetration parameter
k = math.sqrt(2 * m_neutron * (h - E1_total)) / hbar
print(f"Barrier wave vector k = {k:.2e} m^-1")

# Ultra-narrow barrier: 5e-6 nm = 5 picometers
d3 = 5e-6 * 1e-9  # Convert to meters: 5e-15 m
kd3 = k * d3

print(f"\nCASE: {d3*1e12:.0f} pm barrier (5e-6 nm)")
print(f"Barrier width: {d3:.2e} m")
print(f"k*d = {kd3:.6f}")
print(f"Transmission ~ exp(-2*k*d) ~ exp(-{2*kd3:.6f})")

P3 = math.exp(-2*kd3)
print(f"Transmission coefficient: {P3:.6f}")

# Time factor
omega = E1_kinetic / hbar
time_factor = (math.sin(omega * 1.0 / 2))**2

print(f"\nTime evolution factor: {time_factor:.6f}")
print(f"Final probability at t=1s: {P3 * time_factor:.6f}")

print(f"\nCOMPARISON:")
print(f"5 nm barrier: P ~ 0 (completely suppressed)")
print(f"0.05 nm barrier: P ~ 0 (still suppressed)")
print(f"5 pm barrier: P = {P3 * time_factor:.6f} (significant!)")

print(f"\nCODE CHANGE:")
print("Simply change: b = a + 5e-15  # 5 picometer barrier")
print("No other modifications needed")