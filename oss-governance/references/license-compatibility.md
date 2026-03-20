# License Compatibility Matrix

Core reference for license compliance judgments. Used by the dependency-analyzer agent.

## License Categories

### Permissive (Green) — Low risk, broad compatibility

| SPDX ID | Name | Key Obligations |
|---------|------|----------------|
| MIT | MIT License | Include copyright + license text in distributions |
| Apache-2.0 | Apache License 2.0 | Include copyright + license + NOTICE file + state changes |
| BSD-2-Clause | BSD 2-Clause "Simplified" | Include copyright + license text |
| BSD-3-Clause | BSD 3-Clause "New" | Include copyright + license text + no endorsement clause |
| ISC | ISC License | Include copyright + license text |
| Unlicense | The Unlicense | No obligations |
| 0BSD | Zero-Clause BSD | No obligations |
| CC0-1.0 | CC0 1.0 Universal | No obligations (public domain dedication) |
| Zlib | zlib License | Include copyright in source; no misrepresentation |
| BSL-1.0 | Boost Software License 1.0 | Include license in source distributions |
| WTFPL | Do What The F*ck You Want To | No obligations |
| PostgreSQL | PostgreSQL License | Include copyright + license text |
| X11 | X11 License | Include copyright + license text (MIT variant) |
| curl | curl License | Include copyright + license text (MIT variant) |

### Weak Copyleft (Yellow) — Moderate risk, file-level or module-level sharing

| SPDX ID | Name | Copyleft Scope | Key Detail |
|---------|------|---------------|-----------|
| LGPL-2.1-only | GNU LGPL 2.1 | Modified LGPL files | Linking from proprietary code OK; modified LGPL source must be shared |
| LGPL-2.1-or-later | GNU LGPL 2.1+ | Modified LGPL files | Same as above; can upgrade to LGPL-3.0 |
| LGPL-3.0-only | GNU LGPL 3.0 | Modified LGPL files | Linking OK; must allow re-linking; anti-tivoization |
| LGPL-3.0-or-later | GNU LGPL 3.0+ | Modified LGPL files | Same as above |
| MPL-2.0 | Mozilla Public License 2.0 | Modified MPL files | File-level copyleft; can combine with proprietary in larger work |
| EPL-2.0 | Eclipse Public License 2.0 | Modified EPL modules | Module-level copyleft; secondary license option for GPL compatibility |
| CDDL-1.0 | Common Development and Distribution License 1.0 | Modified CDDL files | File-level copyleft; GPL-incompatible |
| CPL-1.0 | Common Public License 1.0 | Modified CPL modules | Module-level copyleft; predecessor of EPL |
| OSL-3.0 | Open Software License 3.0 | Modified files | Network use clause; similar to AGPL for copyleft scope |
| EUPL-1.2 | European Union Public License 1.2 | Modified files | Compatible with GPL/LGPL/MPL/AGPL via compatibility list |

### Strong Copyleft (Red) — High risk, project-wide sharing requirement

| SPDX ID | Name | Copyleft Scope | Key Detail |
|---------|------|---------------|-----------|
| GPL-2.0-only | GNU GPL 2.0 | Entire derivative work | All linked code must be GPL-2.0; no "or later" escape |
| GPL-2.0-or-later | GNU GPL 2.0+ | Entire derivative work | Can satisfy with GPL-2.0 or GPL-3.0 |
| GPL-3.0-only | GNU GPL 3.0 | Entire derivative work | Anti-tivoization; patent retaliation clause |
| GPL-3.0-or-later | GNU GPL 3.0+ | Entire derivative work | Same as above |
| AGPL-3.0-only | GNU Affero GPL 3.0 | Entire work + network use | Network interaction = distribution; strongest OSI copyleft |
| AGPL-3.0-or-later | GNU Affero GPL 3.0+ | Entire work + network use | Same as above |

### Non-OSI / Commercial Risk (Orange) — Requires legal review

| SPDX ID / Name | Type | Key Restriction |
|----------------|------|----------------|
| SSPL-1.0 (Server Side Public License) | Source-available | Providing as a service requires sharing entire stack source |
| BSL-1.1 (Business Source License) | Source-available | Time-delayed open source; check "Change Date" and "Change License" |
| BUSL-1.1 | Source-available | Same as BSL-1.1 |
| Elastic-2.0 (Elastic License 2.0) | Source-available | Cannot provide as managed service competing with Elastic |
| Commons-Clause | License rider | Cannot sell the software "as is"; attaches to host license |
| CC-BY-NC-4.0 | Creative Commons | Non-commercial use only; not for code typically |
| CC-BY-NC-SA-4.0 | Creative Commons | Non-commercial + share-alike |
| Prosperity | Ethical source | Non-commercial use only |
| PolyForm-Noncommercial | Source-available | Non-commercial use only |
| PolyForm-Small-Business | Source-available | Free for small businesses; revenue cap |

## Compatibility Matrix

How to read: "Can project under License A use a dependency under License B?"

### Permissive Project (MIT, Apache-2.0, BSD)

| Dependency License | Compatible? | Notes |
|-------------------|-------------|-------|
| MIT, BSD, ISC, Unlicense | YES | No conflict |
| Apache-2.0 | YES | Must include NOTICE file |
| LGPL-2.1/3.0 | CAUTION | OK if dynamically linked; static linking may trigger copyleft |
| MPL-2.0 | CAUTION | OK if MPL files kept separate; modifications to MPL files must be shared |
| GPL-2.0 | CONFLICT | Project must become GPL-2.0 to comply |
| GPL-3.0 | CONFLICT | Project must become GPL-3.0 to comply |
| AGPL-3.0 | CONFLICT | Project must become AGPL-3.0 to comply |
| SSPL-1.0 | CONFLICT | Requires sharing entire service stack |

### GPL-2.0 Project

| Dependency License | Compatible? | Notes |
|-------------------|-------------|-------|
| MIT, BSD, ISC | YES | Permissive deps OK under GPL |
| Apache-2.0 | CONFLICT (GPL-2.0 only) | Patent clause incompatibility with GPL-2.0-only |
| Apache-2.0 | YES (GPL-2.0-or-later) | Via upgrade to GPL-3.0 |
| LGPL-2.1/3.0 | YES | LGPL is GPL-compatible |
| MPL-2.0 | YES | MPL 2.0 has explicit GPL compatibility clause |
| GPL-3.0 | CONFLICT (GPL-2.0-only) | GPL-3.0 adds restrictions not in 2.0 |
| GPL-3.0 | YES (GPL-2.0-or-later) | Via upgrade to GPL-3.0 |
| AGPL-3.0 | CONFLICT | AGPL adds network-use clause |

### GPL-3.0 Project

| Dependency License | Compatible? | Notes |
|-------------------|-------------|-------|
| MIT, BSD, ISC | YES | Permissive deps OK under GPL |
| Apache-2.0 | YES | Apache-2.0 is one-way compatible with GPL-3.0 |
| LGPL-2.1/3.0 | YES | LGPL is GPL-compatible |
| MPL-2.0 | YES | MPL 2.0 has explicit GPL compatibility clause |
| GPL-2.0 | YES (GPL-2.0-or-later) | Via upgrade |
| GPL-2.0 | CONFLICT (GPL-2.0-only) | Cannot upgrade; version mismatch |
| AGPL-3.0 | YES | GPL-3.0 project can incorporate AGPL-3.0 code |

### Apache-2.0 Project

| Dependency License | Compatible? | Notes |
|-------------------|-------------|-------|
| MIT, BSD, ISC | YES | No conflict |
| Apache-2.0 | YES | Same license |
| LGPL-2.1/3.0 | CAUTION | Same dynamic linking consideration |
| MPL-2.0 | CAUTION | File-level copyleft applies |
| GPL-2.0-only | CONFLICT | Patent clause incompatibility |
| GPL-2.0-or-later / GPL-3.0 | CONFLICT | Apache project cannot become GPL |
| AGPL-3.0 | CONFLICT | Apache project cannot become AGPL |

## SPDX Expression Parsing

Dependencies may declare compound licenses using SPDX expressions:

### OR Expressions (choose one)
- `(MIT OR Apache-2.0)` — user can choose either; pick the more compatible one
- `(MIT OR GPL-2.0-only)` — choose MIT for permissive projects
- `(Apache-2.0 OR GPL-2.0-or-later)` — choose Apache for non-GPL projects

**Rule**: For OR expressions, evaluate each option against the project license and pick the most favorable.

### AND Expressions (both apply)
- `(MIT AND BSD-3-Clause)` — both obligations apply simultaneously
- `(Apache-2.0 AND MIT)` — must satisfy both sets of obligations

**Rule**: For AND expressions, check compatibility of EACH license. If any is incompatible, the combination is incompatible.

### WITH Expressions (license + exception)
- `Apache-2.0 WITH LLVM-exception` — Apache-2.0 with LLVM linking exception
- `GPL-2.0-only WITH Classpath-exception-2.0` — GPL with classpath exception (allows linking without GPL propagation)
- `GPL-2.0-only WITH GCC-exception-3.1` — GPL with GCC runtime exception

**Rule**: Exceptions generally RELAX the base license. Treat as the base license but note the exception reduces copyleft scope.

## Common License String Normalization

Lockfiles and registries often use non-SPDX strings. Normalize before lookup:

| Raw String | SPDX ID |
|-----------|---------|
| "MIT" | MIT |
| "ISC" | ISC |
| "Apache 2.0", "Apache-2", "Apache License 2.0" | Apache-2.0 |
| "BSD", "BSD-2", "FreeBSD" | BSD-2-Clause |
| "BSD-3", "New BSD" | BSD-3-Clause |
| "GPL", "GPL-2", "GNU GPL v2" | GPL-2.0-only |
| "GPLv3", "GPL-3", "GNU GPL v3" | GPL-3.0-only |
| "LGPL", "LGPL-2.1" | LGPL-2.1-only |
| "LGPLv3", "LGPL-3" | LGPL-3.0-only |
| "MPL", "MPL 2.0", "Mozilla" | MPL-2.0 |
| "AGPL", "AGPLv3" | AGPL-3.0-only |
| "Unlicense", "UNLICENSED" (npm) | Check context: Unlicense = public domain; UNLICENSED = proprietary |
| "UNKNOWN", "", null, undefined | UNKNOWN — requires manual review |
| "SEE LICENSE IN <file>" | UNKNOWN — read the referenced file |
| "Commercial", "Proprietary" | NON-OSS — flag for legal review |
