# Dual-band printed monopole (2.4 and 5.8 GHz)

A printed monopole antenna on FR-4 that covers the 2.4 GHz and 5.8 GHz ISM
bands. A parasitic inverted-L element adds the second band. Designed and
simulated in Ansys HFSS for the project in ECSE 593 (Antennas and Propagation,
a graduate course at McGill University), Fall 2026.

It was a team project of two. This repository holds my own design and
calculations. My teammate built a second candidate, which is not here.

## The design

| | |
| --- | --- |
| Substrate | FR-4, relative permittivity 4.4, loss tangent 0.02, 1.6 mm thick |
| Board | 30 mm by 50 mm |
| Feed | 50 ohm microstrip, 3.06 mm wide, over a partial ground 20 mm long |
| Monopole | 24 mm |
| Parasitic L | On the bottom side, connected to the ground. Arms of 5.2 mm and 5 mm, 1.8 mm wide. |

## Simulated results

| Band | Target | Where S11 is below -10 dB | Worst S11 inside the target |
| --- | --- | --- | --- |
| Low | 2.400 to 2.4835 GHz | 2.243 to 2.762 GHz (20.7%) | -22.6 dB |
| High | 5.725 to 5.875 GHz | 5.106 to 6.699 GHz (27.0%) | -16.7 dB |

The mesh was adapted at both 2.4 and 5.8 GHz and the solve converged at pass 11.

The same monopole without the L sits at -4.6 dB at 5.8 GHz. An L that floats,
on either side of the board, did not create the second band. Connecting it to
the ground did.

## Files

- `hfss/monopole.aedt`: the HFSS project. `HFSSDesign4` is the design above
  and `HFSSDesign3` is the same monopole without the L. The other designs are
  earlier attempts.
- `calculations/hand_calcs.py`: starting dimensions by hand. Feed line width
  for 50 ohm, effective permittivity, and the quarter-wave lengths.
- `figures/s11_figure.py`: draws the S11 plot from an HFSS report exported as
  CSV and prints the -10 dB bands.
