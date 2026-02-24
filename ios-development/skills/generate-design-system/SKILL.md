---
name: generate-design-system
description: Generate Apple HIG-compliant SwiftUI Design System code from token specifications
---

# Generate Design System Skill

Generate complete Design System code based on Apple HIG token standards and OKLCH color generation.
Colors are derived from the primary color established in prior design discussion — not from preset category names.

## Input Parameters

From calling command or user:
- `primaryColor`: hex value (e.g. `#3A73B5`) or hue angle (e.g. `210°`) — from prior design discussion
- `colorRelationship`: `complementary` (default) / `analogous` / `triadic`
- `proportionRule`: `60-30-10` (default) / `80-15-5`
- `platform`: iOS / macOS / both
- `projectPath`: Path to Xcode project root
- `generateComponents`: true / false (optional)

## Process

### 1. Read Token Specification (section-targeted)

Grep for section markers:

```
Grep("<!-- section:", "references/apple-hig-design-tokens.md")
```

Read the following sections by their marker line offsets:

- Spacing system: section "Part 2: Apple HIG reference values" — contains 8pt grid, corner radius, shadow, typography
- OKLCH color generation: section "Part 4: Parameterizable color generation with OKLCH"

Read each section individually with offset and limit derived from the Grep output.

### 2. Derive Color Palette from Primary Color

**Step 2a: Extract primary hue H₀**
- If `primaryColor` is a hex value: convert to OKLCH using the standard formula (hex → linear sRGB → OKLab → OKLCH), extract H₀
- If `primaryColor` is already a hue angle: use directly as H₀

**Step 2b: Derive accent hue from `colorRelationship`**
```
complementary: H_accent = (H₀ + 180) % 360
analogous:     H_secondary = (H₀ + 30) % 360, H_accent = (H₀ - 30 + 360) % 360
triadic:       H_secondary = (H₀ + 120) % 360, H_accent = (H₀ + 240) % 360
```

**Step 2c: Assign semantic roles via `proportionRule`**

| Role | proportionRule | Hue | chromaPeak | chromaBase |
|------|---------------|-----|-----------|-----------|
| Background/neutral (60% or 80%) | both | H₀ | 0.06 | 0.01 |
| Primary brand (30% or 15%) | both | H₀ | 0.25 | 0.06 |
| Accent/CTA (10% or 5%) | both | H_accent | 0.28 | 0.07 |

**Step 2d: Generate OKLCH step parameters for each palette**

For each palette (neutral / primary / accent), compute 11 steps i=0..10:
```
L = 0.97 - (i / 10) * (0.97 - 0.15)
C = chromaBase + sin(i/10 * π) * chromaPeak
H = hue for this palette
```

**Step 2e: Apply tone-swapping for light/dark mode** (per Part 4 Light/dark mode table)
- Primary brand: light → step 500 (L≈0.55), dark → step 300 (L≈0.77)
- Background: light → step 50 (L≈0.97), dark → step 950 (L≈0.15)
- Surface: light → step 100 (L≈0.93), dark → step 900 (L≈0.21)
- Text: light → step 900 (L≈0.21), dark → step 100 (L≈0.93)
- Accent: light → step 500 (L≈0.55), dark → step 300 (L≈0.77)

### 3. Generate DesignSystem.swift

Create file with:

```swift
import SwiftUI

// MARK: - Spacing

enum AppSpacing {
    static let _4xs: CGFloat = 2
    static let _3xs: CGFloat = 4
    static let _2xs: CGFloat = 8
    static let xs: CGFloat = 12
    static let sm: CGFloat = 16
    static let md: CGFloat = 24
    static let lg: CGFloat = 32
    static let xl: CGFloat = 48
    static let _2xl: CGFloat = 64
}

// MARK: - Corner Radius

enum AppCornerRadius {
    static let small: CGFloat = 8
    static let medium: CGFloat = 12
    static let large: CGFloat = 16
}

// MARK: - Shadow

enum AppShadow {
    static let subtle = ShadowStyle(color: .black.opacity(0.04), radius: 2, y: 1)
    static let medium = ShadowStyle(color: .black.opacity(0.08), radius: 4, y: 2)
}

struct ShadowStyle {
    let color: Color
    let radius: CGFloat
    let y: CGFloat
}

extension View {
    func appShadow(_ style: ShadowStyle) -> some View {
        self.shadow(color: style.color, radius: style.radius, y: style.y)
    }
}
```

### 4. Generate OKLCHConverter.swift

Output this file verbatim — it contains the verified OKLCH → UIColor conversion formula.
The LLM does not need to compute any color math; all sRGB conversion is handled by this file at runtime.

```swift
// OKLCHConverter.swift
// OKLCH → OKLab → linear sRGB → gamma sRGB → UIColor
// Formula source: https://www.w3.org/TR/css-color-4/#color-conversion-code

import SwiftUI

struct OKLCHColor {
    let l: Double  // Lightness 0–1
    let c: Double  // Chroma ≥ 0
    let h: Double  // Hue in degrees

    /// Returns an adaptive Color using UIColor's trait-based initializer.
    /// - Parameters:
    ///   - darkL: Lightness value for the dark mode variant (tone-swapped step)
    func adaptive(darkL: Double) -> Color {
        Color(uiColor: UIColor { traits in
            let lightness = traits.userInterfaceStyle == .dark ? darkL : l
            return Self.toUIColor(l: lightness, c: c, h: h)
        })
    }

    static func toUIColor(l: Double, c: Double, h: Double) -> UIColor {
        let hRad = h * .pi / 180
        // OKLCH → OKLab
        let a = c * cos(hRad)
        let b = c * sin(hRad)
        // OKLab → linear sRGB (via LMS)
        let l_ = l + 0.3963377774 * a + 0.2158037573 * b
        let m_ = l - 0.1055613458 * a - 0.0638541728 * b
        let s_ = l - 0.0894841775 * a - 1.2914855480 * b
        let lc = l_ * l_ * l_
        let mc = m_ * m_ * m_
        let sc = s_ * s_ * s_
        var r = +4.0767416621 * lc - 3.3077115913 * mc + 0.2309699292 * sc
        var g = -1.2684380046 * lc + 2.6097574011 * mc - 0.3413193965 * sc
        var bv = -0.0041960863 * lc - 0.7034186147 * mc + 1.7076147010 * sc
        // Gamma correction (linear → sRGB)
        func gamma(_ x: Double) -> Double {
            x >= 0.0031308 ? 1.055 * pow(x, 1/2.4) - 0.055 : 12.92 * x
        }
        r = max(0, min(1, gamma(r)))
        g = max(0, min(1, gamma(g)))
        bv = max(0, min(1, gamma(bv)))
        return UIColor(red: r, green: g, blue: bv, alpha: 1)
    }
}
```

### 5. Generate Colors+Tokens.swift

Using the OKLCH step parameters from Step 2d/2e, output `OKLCHColor(l:c:h:).adaptive(darkL:)` calls.
The LLM only provides the L/C/H numbers (simple arithmetic from Step 2) — no sRGB conversion needed.

```swift
// Colors+Tokens.swift
// Generated from primaryColor: {primaryColor}, relationship: {colorRelationship}, proportion: {proportionRule}
import SwiftUI

extension Color {
    // MARK: - Primary Brand Colors (30% of visual weight)

    static let appPrimary = OKLCHColor(l: {L_500}, c: {C_500}, h: {H₀}).adaptive(darkL: {L_300})
    static let appPrimaryLight = OKLCHColor(l: {L_300}, c: {C_300}, h: {H₀}).adaptive(darkL: {L_200})
    static let appPrimaryDark = OKLCHColor(l: {L_700}, c: {C_700}, h: {H₀}).adaptive(darkL: {L_500})

    // MARK: - Accent / CTA Colors (10% or 5% of visual weight)

    static let appAccent = OKLCHColor(l: {L_500_accent}, c: {C_500_accent}, h: {H_accent}).adaptive(darkL: {L_300_accent})
    static let appAccentLight = OKLCHColor(l: {L_300_accent}, c: {C_300_accent}, h: {H_accent}).adaptive(darkL: {L_200_accent})

    // MARK: - Background / Neutral Colors (60% or 80% of visual weight)

    static let appBackground = OKLCHColor(l: {L_50_neutral}, c: {C_50_neutral}, h: {H₀}).adaptive(darkL: {L_950_neutral})
    static let appSurface = OKLCHColor(l: {L_100_neutral}, c: {C_100_neutral}, h: {H₀}).adaptive(darkL: {L_900_neutral})
    static let appText = OKLCHColor(l: {L_900_neutral}, c: {C_900_neutral}, h: {H₀}).adaptive(darkL: {L_100_neutral})
    static let appTextSecondary = OKLCHColor(l: {L_600_neutral}, c: {C_600_neutral}, h: {H₀}).adaptive(darkL: {L_400_neutral})

    // MARK: - Status Colors (system semantic — not theme-derived)

    static let appSuccess = OKLCHColor(l: 0.55, c: 0.18, h: 145).adaptive(darkL: 0.72)
    static let appWarning = OKLCHColor(l: 0.72, c: 0.18, h: 85).adaptive(darkL: 0.82)
    static let appError = OKLCHColor(l: 0.52, c: 0.22, h: 25).adaptive(darkL: 0.70)
}
```

Replace all `{placeholder}` values with the computed L/C/H numbers from Step 2d/2e before writing the file.

### 6. Generate Typography+Tokens.swift

Based on platform selection:

**iOS**:
```swift
// No custom code needed, use system text styles:
// .font(.largeTitle)  // 34pt
// .font(.title)       // 28pt
// .font(.body)        // 17pt
```

**macOS**:
```swift
// macOS — use semantic text styles, same as iOS
// No custom Font extension needed
// .font(.largeTitle), .font(.title), .font(.body), .font(.caption)
// SwiftUI on macOS 13+ maps these to system-appropriate point sizes with Dynamic Type support
```

### 7. (Optional) Generate Components

If `generateComponents == true`, create:
- `Components/DSButton.swift`
- `Components/DSCard.swift`
- `Components/DSTextField.swift`

Each component uses Design Token constants.

### 8. Output File List

Return:
```
✅ Generated:
- [ProjectName]/DesignSystem/DesignSystem.swift
- [ProjectName]/DesignSystem/OKLCHConverter.swift
- [ProjectName]/DesignSystem/Colors+Tokens.swift
- [ProjectName]/DesignSystem/Typography+Tokens.swift
- [ProjectName]/DesignSystem/Components/ (if requested)
```

## Success Criteria

- All spacing values are from 8pt grid
- Colors derived from `primaryColor` + color relationship — no preset category names
- `Colors+Tokens.swift` uses `OKLCHColor(l:c:h:).adaptive(darkL:)` — no raw `UIColor(red:green:blue:)` calls
- `OKLCHConverter.swift` is present (handles all OKLCH → sRGB math at runtime)
- Accent color is derived from the correct hue offset for the chosen `colorRelationship`
- Typography uses Dynamic Type text styles
- Platform-specific values when platform=both
