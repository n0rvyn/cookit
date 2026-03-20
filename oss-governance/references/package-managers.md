# Package Manager Reference

How to extract dependencies and license information from each supported package manager.

## Overview

| PM | Manifest | Lockfile (preferred) | License Field | Registry API |
|----|----------|---------------------|---------------|-------------|
| npm | package.json | package-lock.json | `.license` | `https://registry.npmjs.org/{pkg}` |
| pip | pyproject.toml / requirements.txt | Pipfile.lock / poetry.lock | `classifiers` / `license` | `https://pypi.org/pypi/{pkg}/json` |
| cargo | Cargo.toml | Cargo.lock | `[package].license` | `https://crates.io/api/v1/crates/{pkg}` |
| go | go.mod | go.sum | — (LICENSE file) | `https://pkg.go.dev/{module}` |
| maven | pom.xml | — | `<licenses>` block | Maven Central search API |
| gradle | build.gradle | — | — (inherits maven) | Maven Central search API |
| swift | Package.swift | Package.resolved | — (LICENSE file) | — |
| cocoapods | Podfile | Podfile.lock | `.license` in podspec | `https://trunk.cocoapods.org/api/v1/pods/{pod}` |
| ruby | Gemfile | Gemfile.lock | `.license` in gemspec | `https://rubygems.org/api/v1/gems/{gem}.json` |
| composer | composer.json | composer.lock | `.license` | `https://repo.packagist.org/p2/{vendor}/{pkg}.json` |

## Per-PM Extraction Details

### npm (Node.js)

**Dependency extraction from package-lock.json (v2/v3)**:
```bash
# Extract all dependencies with versions
cat package-lock.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
pkgs = data.get('packages', {})
for path, info in pkgs.items():
    if path == '': continue  # skip root
    name = path.split('node_modules/')[-1]
    ver = info.get('version', 'unknown')
    lic = info.get('license', 'UNKNOWN')
    print(f'{name}\t{ver}\t{lic}')
"
```

**License from registry (fallback)**:
```bash
curl -s "https://registry.npmjs.org/{pkg}" | python3 -c "
import json, sys
data = json.load(sys.stdin)
latest = data.get('dist-tags', {}).get('latest', '')
ver_info = data.get('versions', {}).get(latest, {})
print(ver_info.get('license', 'UNKNOWN'))
"
```

**Notes**:
- package-lock.json v2/v3 has license info inline for most packages
- `UNLICENSED` in npm means proprietary (NOT public domain)
- Some packages use `licenses` (array) instead of `license` (string) — handle both

### pip (Python)

**Dependency extraction from requirements.txt**:
```bash
# Simple: name==version per line
grep -v '^#' requirements.txt | grep -v '^$' | sed 's/[><=!].*//' | tr -d ' '
```

**Dependency extraction from Pipfile.lock**:
```bash
cat Pipfile.lock | python3 -c "
import json, sys
data = json.load(sys.stdin)
for section in ['default', 'develop']:
    for name, info in data.get(section, {}).items():
        ver = info.get('version', 'unknown').lstrip('=')
        print(f'{name}\t{ver}')
"
```

**Dependency extraction from poetry.lock**:
```bash
# TOML format; each [[package]] block has name, version
grep -A2 '^\[\[package\]\]' poetry.lock | grep -E '^(name|version)' | paste - -
```

**License from registry**:
```bash
curl -s "https://pypi.org/pypi/{pkg}/json" | python3 -c "
import json, sys
data = json.load(sys.stdin)
info = data.get('info', {})
lic = info.get('license', '')
if not lic or lic == 'UNKNOWN':
    classifiers = info.get('classifiers', [])
    for c in classifiers:
        if 'License' in c:
            lic = c.split(' :: ')[-1]
            break
print(lic or 'UNKNOWN')
"
```

**Notes**:
- Python packages often have license in classifiers rather than license field
- Some have license = "UNKNOWN" but valid classifier
- pyproject.toml may have `[project].license` or `[tool.poetry].license`

### cargo (Rust)

**Dependency extraction from Cargo.lock**:
```bash
# TOML format; each [[package]] has name, version
grep -A2 '^\[\[package\]\]' Cargo.lock | grep -E '^(name|version)' | paste - -
```

**License from Cargo.toml** (if available in fetched files):
```bash
grep '^license' Cargo.toml | head -1 | cut -d'"' -f2
```

**License from registry**:
```bash
curl -s "https://crates.io/api/v1/crates/{pkg}" | python3 -c "
import json, sys
data = json.load(sys.stdin)
crate = data.get('crate', {})
print(crate.get('license', 'UNKNOWN') or 'UNKNOWN')
"
```

**Notes**:
- Cargo uses SPDX expressions natively (e.g., "MIT OR Apache-2.0")
- Most Rust crates are dual-licensed MIT/Apache-2.0
- `license-file` field means custom license; treat as unknown

### go (Go)

**Dependency extraction from go.mod**:
```bash
# Lines like: require ( module version )
grep -E '^\t' go.mod | awk '{print $1"\t"$2}' | sed 's|//.*||'
```

**License detection**:
Go has no license field in go.mod. Must check:
1. Vendor directory (if `go mod vendor` was run): `vendor/{module}/LICENSE`
2. Registry: no standard API; use `https://pkg.go.dev/{module}?tab=licenses`
3. GitHub: if module path is `github.com/user/repo`, check repo LICENSE file

**Notes**:
- Go modules often reference GitHub repos directly
- License detection is the hardest for Go; rely on GitHub API as fallback
- `go.sum` contains checksums, not useful for license detection

### maven (Java)

**Dependency extraction from pom.xml**:
```bash
# XML parsing; extract <dependency> blocks
grep -A3 '<dependency>' pom.xml | grep -E '<(groupId|artifactId|version)>' | \
  sed 's/<[^>]*>//g' | tr -d ' ' | paste - - -
```

**License from pom.xml** (project's own license):
```bash
grep -A3 '<license>' pom.xml | grep '<name>' | sed 's/<[^>]*>//g' | tr -d ' '
```

**License from Maven Central**:
```bash
curl -s "https://search.maven.org/solrsearch/select?q=g:{groupId}+AND+a:{artifactId}&rows=1&wt=json"
```

**Notes**:
- Maven dependencies are identified by groupId:artifactId:version
- Transitive dependencies require `mvn dependency:tree` (may not be available remotely)
- Gradle uses same Maven Central repositories

### swift (Swift Package Manager)

**Dependency extraction from Package.resolved (v2)**:
```bash
cat Package.resolved | python3 -c "
import json, sys
data = json.load(sys.stdin)
for pin in data.get('pins', []):
    name = pin.get('identity', 'unknown')
    ver = pin.get('state', {}).get('version', pin.get('state', {}).get('revision', 'unknown'))
    loc = pin.get('location', '')
    print(f'{name}\t{ver}\t{loc}')
"
```

**License detection**:
Swift has no license field in Package.swift or Package.resolved. Must check:
1. If location is GitHub URL: use `gh api repos/{owner}/{repo}/license`
2. Fetch LICENSE file from the repository

**Notes**:
- Package.resolved v1 uses "object.pins[]" with "repositoryURL" and "state.version"
- Package.resolved v2 uses "pins[]" with "location" and "state.version"
- Handle both formats

### cocoapods (Ruby/iOS)

**Dependency extraction from Podfile.lock**:
```bash
# PODS section lists all pods with versions
sed -n '/^PODS:/,/^$/p' Podfile.lock | grep -E '^\s+-\s' | \
  sed 's/.*- //' | sed 's/ (.*//' | while read pod; do
    ver=$(grep -A0 "- $pod (" Podfile.lock | grep -oP '\([\d.]+\)' | tr -d '()')
    echo "$pod\t$ver"
  done
```

**License from trunk API**:
```bash
curl -s "https://trunk.cocoapods.org/api/v1/pods/{pod}" | python3 -c "
import json, sys
data = json.load(sys.stdin)
ver = sorted(data.get('versions', []), key=lambda v: v['name'])[-1]
# License is in the podspec, not in the API response
# Need to fetch the podspec from the Specs repo
print('UNKNOWN')
"
```

**Notes**:
- CocoaPods license info is in individual .podspec files
- Many pods declare license in podspec: `s.license = { :type => 'MIT' }`
- For license detection, best to check the GitHub repo of each pod

### ruby (Bundler)

**Dependency extraction from Gemfile.lock**:
```bash
# GEM section, specs subsection
sed -n '/^  specs:/,/^$/p' Gemfile.lock | grep -E '^\s{4}\S' | \
  awk '{print $1"\t"gsub(/[()]/, "", $2)}'
```

**License from RubyGems API**:
```bash
curl -s "https://rubygems.org/api/v1/gems/{gem}.json" | python3 -c "
import json, sys
data = json.load(sys.stdin)
licenses = data.get('licenses', [])
print(', '.join(licenses) if licenses else 'UNKNOWN')
"
```

### composer (PHP)

**Dependency extraction from composer.lock**:
```bash
cat composer.lock | python3 -c "
import json, sys
data = json.load(sys.stdin)
for pkg in data.get('packages', []) + data.get('packages-dev', []):
    name = pkg.get('name', 'unknown')
    ver = pkg.get('version', 'unknown').lstrip('v')
    lic = ', '.join(pkg.get('license', ['UNKNOWN']))
    print(f'{name}\t{ver}\t{lic}')
"
```

**Notes**:
- composer.lock includes license info inline for most packages
- Similar to npm's package-lock.json in completeness
