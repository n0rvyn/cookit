# License Categories Quick Lookup

Fast lookup table for the dependency-analyzer agent. Given a license string, return the risk category.

For full compatibility analysis and SPDX expression parsing, see `license-compatibility.md`.

## Category Definitions

| Category | Color | Risk Level | Meaning |
|----------|-------|-----------|---------|
| permissive | Green | Low | Free to use in any project; minimal obligations |
| weak-copyleft | Yellow | Medium | File/module-level sharing required; linking from proprietary OK |
| strong-copyleft | Red | High | Entire derivative work must be shared under same license |
| non-osi | Orange | Review | Not OSI-approved; may have commercial restrictions; needs legal review |
| unknown | White | Review | License not detected or not recognized; manual review required |

## Lookup Table

### Permissive (Green)

```
MIT
ISC
BSD-2-Clause
BSD-3-Clause
0BSD
Apache-2.0
Unlicense
CC0-1.0
Zlib
BSL-1.0
WTFPL
PostgreSQL
X11
curl
Artistic-2.0
Python-2.0
PSF-2.0
BlueOak-1.0.0
UPL-1.0
```

### Weak Copyleft (Yellow)

```
LGPL-2.0-only
LGPL-2.0-or-later
LGPL-2.1-only
LGPL-2.1-or-later
LGPL-3.0-only
LGPL-3.0-or-later
MPL-2.0
EPL-1.0
EPL-2.0
CDDL-1.0
CDDL-1.1
CPL-1.0
OSL-3.0
EUPL-1.1
EUPL-1.2
MS-RL
Artistic-1.0
```

### Strong Copyleft (Red)

```
GPL-2.0-only
GPL-2.0-or-later
GPL-3.0-only
GPL-3.0-or-later
AGPL-1.0-only
AGPL-3.0-only
AGPL-3.0-or-later
```

### Non-OSI / Commercial Risk (Orange)

```
SSPL-1.0
BSL-1.1
BUSL-1.1
Elastic-2.0
Commons-Clause
CC-BY-NC-4.0
CC-BY-NC-SA-4.0
CC-BY-NC-ND-4.0
Prosperity-3.0.0
PolyForm-Noncommercial-1.0.0
PolyForm-Small-Business-1.0.0
```

## Normalization Rules

Before lookup, normalize the raw license string:

1. Trim whitespace
2. Case-insensitive match against known aliases (see `license-compatibility.md` normalization table)
3. Handle SPDX expressions:
   - `(A OR B)` → evaluate each; report the more favorable category
   - `(A AND B)` → report the more restrictive category
   - `A WITH exception` → report base license category with exception note
4. If no match after normalization → category = `unknown`

## Special Cases

| Input | Category | Notes |
|-------|----------|-------|
| `UNLICENSED` (npm) | unknown | Typically means proprietary; NOT the same as Unlicense |
| `SEE LICENSE IN <file>` | unknown | Must read the referenced file |
| `""` / `null` / missing | unknown | No license declared |
| `Commercial` / `Proprietary` | non-osi | Flag for legal review |
| `Custom` / `Custom: ...` | unknown | Custom license text needs human review |
