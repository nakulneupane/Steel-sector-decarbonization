# H₂ Commitment and Regret Analysis

This study evaluates the cost and stranded investment associated with making
an early hydrogen-dec​arbonization commitment under uncertainty.

The central question is:

> **If steel-sector decarbonization is planned around H₂ arriving by 2030,
> 2035, 2040, or 2045, what happens when reality differs from that commitment,
> and how much investment becomes stranded?**

The study compares four commitment programs against perfect foresight and
evaluates both **no-recourse** and **recourse** strategies.

## Study design

Four commitment programs are created in 2025:

- H₂ commitment by **2030**
- H₂ commitment by **2035**
- H₂ commitment by **2040**
- H₂ commitment by **2045**

Each program is a cost-optimal 2025 plan that assumes H₂ arrives in its
committed year and is fully mature by 2050.

All programs are planned under the same fixed belief backdrop:

| Parameter | Assumption |
|---|---:|
| Technology learning | θ = 0.5 |
| Grid learning | θ = 0.5 |
| CCS learning | θ = 0.5 |
| Scrap growth | 6%/yr |
| Natural-gas price | $10/MMBtu |
| Coking-coal availability | Mid |
| Natural-gas availability | Shock |
| Cumulative emissions target | 1.8 tCO₂/tCS |
| Capacity expansion | Medium ramp |
| Horizon | 2025–2050 |

The commitment programs are subsequently evaluated in **400 sampled worlds**:
the first 100 seeded Monte Carlo draws from each of the four H₂-arrival
clouds. These are the same seeded draws used by the main Monte Carlo study.

## Commitment semantics

Committed investments become **floors** before the relevant review date.
They are therefore treated as sunk commitments and occupy the shared capacity
build ramp, but additional capacity can still be built if required.

The H₂ supply chain is treated as a **financial commitment**:

- Electrolyser capacity
- Renewable-electricity capacity

The realized system follows the realized world's physical deployment
envelope, but the committed H₂ supply capacity must still be financially paid
for if it is not physically built.

## No recourse and recourse

Two execution modes are evaluated.

### No recourse

The committed investment trajectory is frozen for the full 2025–2050 horizon.
Operations can still re-optimize, but committed investment floors cannot be
reversed.

### Recourse

Future investments can be revised after information is revealed.

Two review epochs are used:

- **2035**
- **2045**

Only investments **before** each review remain frozen. Investments after the
review are re-optimized.

At the 2035 review, the planner observes the realized market conditions and
knows whether H₂ has actually arrived. If the original H₂ commitment has been
falsified by then, the H₂ expectation is rolled forward according to the
study's commitment rule.

By 2045, the actual H₂ arrival year is known.

Operations are always re-optimized; recourse applies to future investment
decisions rather than operational decisions.
