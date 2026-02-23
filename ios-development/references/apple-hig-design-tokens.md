# A 100-score parameterizable iOS + macOS design token system
<!-- SECTION MARKERS: Each "section" comment line immediately precedes the ##
     heading it labels. Use Grep("<!-- section:", file) to find sections, then
     Read(file, offset, limit) to fetch only the relevant lines. -->

**A fully parameterizable design token architecture that generates complete, Apple HIG-compliant token sets for iOS and macOS from a single style configuration.** This system uses the W3C DTCG specification, a three-tier token hierarchy (primitive → semantic → component), and OKLCH-based color generation to produce theme variants — sporty, diet, minimalist, or any custom mood — while maintaining WCAG AA accessibility and pixel-perfect platform fidelity. It integrates with Style Dictionary for cross-platform output and ships with phased prompts for Claude Code and Figma AI to turn tokens into production SwiftUI code and design files.

---

<!-- section: Part 1: Token architecture keywords: token architecture, design tokens, primitive, semantic, component, DTCG, W3C -->
## Part 1: Token architecture and the three-tier hierarchy

The system follows the industry-standard **primitive → semantic → component** token pattern used by GitHub Primer, Shopify Polaris, IBM Carbon, and Salesforce Lightning, aligned to the **W3C Design Tokens Community Group (DTCG) specification v2025.10**.

**Tier 1 — Primitive tokens** are raw, context-free values: the complete color palette (50–950 per hue), the spacing scale, every font size, border radii, and opacity steps. They are never referenced directly by components. **Tier 2 — Semantic tokens** assign meaning to primitives: `color.bg.surface` references `color.gray.50` in light mode and `color.gray.900` in dark mode. Theme switching happens entirely at this tier — only semantic mappings change. **Tier 3 — Component tokens** bind semantic tokens to specific UI elements: `button.primary.bg` references `color.bg.brand`.

The parameterization layer sits *before* Tier 1. A `ThemeConfig` object specifies a primary hue, chroma curve, harmony strategy, and mood parameters. A generator function produces the full primitive palette, and semantic + component tokens inherit automatically through alias chains.

```
ThemeConfig → Generator → Primitive Tokens → Semantic Tokens → Component Tokens
                              ↑                    ↑
                        OKLCH algorithm      Light/Dark mode swap
```

### File structure

```
tokens/
├── config/
│   ├── sporty.json            # ThemeConfig for sporty mood
│   ├── diet.json              # ThemeConfig for diet mood
│   └── minimalist.json        # ThemeConfig for minimalist mood
├── generated/
│   ├── primitives/
│   │   ├── colors.tokens.json
│   │   ├── typography.tokens.json
│   │   ├── spacing.tokens.json
│   │   └── motion.tokens.json
│   ├── semantic/
│   │   ├── colors-light.tokens.json
│   │   ├── colors-dark.tokens.json
│   │   ├── typography.tokens.json
│   │   └── spacing.tokens.json
│   └── component/
│       ├── button.tokens.json
│       ├── card.tokens.json
│       ├── textfield.tokens.json
│       └── navigation.tokens.json
└── style-dictionary.config.json
```

### Naming convention

All tokens follow the **category-property-variant-state** pattern with kebab-case in JSON, transformed to camelCase for Swift output via Style Dictionary:

| Layer | Pattern | Example |
|-------|---------|---------|
| Primitive | `{category}.{hue}.{step}` | `color.blue.500` |
| Semantic | `{category}.{purpose}.{variant}` | `color.bg.brand` |
| Component | `{component}.{variant}.{property}.{state}` | `button.primary.bg.pressed` |

---

<!-- section: Part 2: Apple HIG reference values keywords: HIG values, spacing, corner radius, shadow, typography, Apple spec -->
## Part 2: Apple HIG reference values — the complete specification

### iOS typography scale (default "Large" Dynamic Type)

Every value below is the system default at the standard content size. The font family is **SF Pro** — Text variant for ≤19pt, Display variant for ≥20pt. Tracking is handled automatically by the variable font's optical sizing axis.

| Text Style | Size (pt) | Weight | Line Height (pt) | Tracking |
|-----------|----------|--------|-----------------|----------|
| extraLargeTitle (iOS 17+) | **36** | Bold | ~43 | — |
| extraLargeTitle2 (iOS 17+) | **28** | Bold | ~34 | — |
| largeTitle | **34** | Regular | **41** | 0.37 |
| title1 | **28** | Regular | **34** | 0.36 |
| title2 | **22** | Regular | **28** | 0.35 |
| title3 | **20** | Regular | **25** | 0.38 |
| headline | **17** | Semibold | **22** | −0.41 |
| body | **17** | Regular | **22** | −0.41 |
| callout | **16** | Regular | **21** | −0.32 |
| subheadline | **15** | Regular | **20** | −0.24 |
| footnote | **13** | Regular | **18** | −0.08 |
| caption1 | **12** | Regular | **16** | 0.00 |
| caption2 | **11** | Regular | **13** | 0.07 |

### macOS typography scale — all sizes are smaller

macOS uses **13pt** as the base body size versus iOS's 17pt. macOS does **not** support Dynamic Type — sizes are fixed.

| Text Style | macOS Size | macOS Weight | iOS Size | Ratio |
|-----------|-----------|-------------|---------|-------|
| largeTitle | **26** | Regular | 34 | 76% |
| title1 | **22** | Regular | 28 | 79% |
| title2 | **17** | Regular | 22 | 77% |
| title3 | **15** | Regular | 20 | 75% |
| headline | **13** | **Bold** | 17 | 76% |
| body | **13** | Regular | 17 | 76% |
| callout | **12** | Regular | 16 | 75% |
| subheadline | **11** | Regular | 15 | 73% |
| footnote | **10** | Regular | 13 | 77% |
| caption1 | **10** | Regular | 12 | 83% |
| caption2 | **10** | **Medium** | 11 | 91% |

The ~77% ratio matches the Mac Catalyst scaling factor exactly. Headline uses Bold on macOS (vs. Semibold on iOS) and caption2 uses Medium weight (vs. Regular).

### Dynamic Type complete scaling table (iOS)

The body style scales from **14pt** at xSmall to **53pt** at AX5 — a **3.12× range**. Title styles scale less aggressively; headline caps at **23pt** across all accessibility sizes.

| Style | xS | S | M | **L (default)** | xL | xxL | xxxL | AX1 | AX2 | AX3 | AX4 | AX5 |
|-------|---|---|---|---|---|---|---|---|---|---|---|---|
| largeTitle | 31 | 32 | 33 | **34** | 36 | 38 | 40 | 44 | 48 | 52 | 56 | 76 |
| title1 | 25 | 26 | 27 | **28** | 30 | 32 | 34 | 38 | 43 | 48 | 53 | 60 |
| title2 | 19 | 20 | 21 | **22** | 24 | 26 | 28 | 34 | 38 | 43 | 48 | 53 |
| title3 | 17 | 18 | 19 | **20** | 22 | 24 | 26 | 31 | 36 | 41 | 46 | 51 |
| headline | 14 | 15 | 16 | **17** | 19 | 21 | 23 | 23 | 23 | 23 | 23 | 23 |
| body | 14 | 15 | 16 | **17** | 19 | 21 | 23 | 28 | 33 | 40 | 47 | 53 |
| callout | 13 | 14 | 15 | **16** | 18 | 20 | 22 | 26 | 32 | 38 | 44 | 51 |
| subheadline | 12 | 13 | 14 | **15** | 17 | 19 | 21 | 25 | 30 | 36 | 42 | 49 |
| footnote | 12 | 12 | 12 | **13** | 15 | 17 | 19 | 23 | 27 | 33 | 38 | 44 |
| caption1 | 11 | 11 | 11 | **12** | 14 | 16 | 18 | 22 | 26 | 32 | 37 | 38 |
| caption2 | 11 | 11 | 11 | **11** | 13 | 15 | 17 | 20 | 24 | 29 | 34 | 38 |

### Spacing system

Apple does not publish a formal grid. The observed system uses **multiples of 4pt** as the de facto base unit.

| Token Name | Value | Usage |
|-----------|-------|-------|
| space.xxs | **2pt** | Tight icon-to-text gap |
| space.xs | **4pt** | Minimum element spacing |
| space.sm | **8pt** | Default VStack/HStack spacing, view margins |
| space.md | **16pt** | Standard content padding, cell horizontal margins |
| space.lg | **20pt** | Content margins on larger iPhones (414pt+ width) |
| space.xl | **24pt** | Section spacing |
| space.2xl | **32pt** | Large section gaps |
| space.3xl | **48pt** | Major layout divisions |

### Safe area insets (current devices, portrait)

| Device | Top | Bottom | Left | Right |
|--------|-----|--------|------|-------|
| iPhone 15/16 (Dynamic Island) | **59** | **34** | 0 | 0 |
| iPhone X–14 (notch) | **47–50** | **34** | 0 | 0 |
| iPhone SE (no notch) | **20** | **0** | 0 | 0 |

### Component dimensions (iOS)

| Component | Dimension | Value (pt) |
|-----------|-----------|-----------|
| Navigation bar (standard) | height | **44** |
| Navigation bar (large title) | height | **96** (44 + 52) |
| Tab bar | height | **49** (83 total with home indicator) |
| Toolbar | height | **44** |
| Search bar | height | **44** |
| UISwitch (Toggle) | width × height | **51 × 31** |
| Slider thumb | diameter | **28** |
| Slider track | height | **2** |
| Standard list row | height | **44** |
| Subtitle list row | height | **~58** |
| Alert | width | **270** |
| Alert corner radius | radius | **14** |
| Action sheet row | height | **~57** |
| Segmented control | height | **32** |
| Badge (min) | diameter | **18** |
| Minimum touch target | size | **44 × 44** |

### macOS component dimensions

| Component | Value | Notes |
|-----------|-------|-------|
| Menu bar height | **24pt** (37pt with notch) | `NSMenu.menuBarHeight` |
| Title bar | **22pt** | Without toolbar |
| Toolbar (unified) | **~52pt** total | Title + toolbar |
| Toolbar (unified compact) | **~38pt** total | — |
| Sidebar (default width) | **200pt** | Min 180, max ~300 |
| Inspector panel | **200–260pt** | Trailing sidebar |
| Table row (small) | **~17pt** | — |
| Table row (medium) | **~24pt** | Default |
| Table row (large) | **~28pt** | — |
| Button (mini) | **~15pt** | 9pt font |
| Button (small) | **~19pt** | 11pt font |
| Button (regular) | **~22pt** | 13pt font |
| Button (large) | **~30pt** | ~15pt font |

### Apple semantic color system (exact hex values)

**Label colors:**

| Token | Light Mode | Dark Mode |
|-------|-----------|----------|
| label | `#000000` (1.0 alpha) | `#FFFFFF` (1.0 alpha) |
| secondaryLabel | `#3C3C43` (0.60 alpha) | `#EBEBF5` (0.60 alpha) |
| tertiaryLabel | `#3C3C43` (0.30 alpha) | `#EBEBF5` (0.30 alpha) |
| quaternaryLabel | `#3C3C43` (0.18 alpha) | `#EBEBF5` (0.18 alpha) |

**Background colors:**

| Token | Light Mode | Dark Mode |
|-------|-----------|----------|
| systemBackground | `#FFFFFF` | `#000000` |
| secondarySystemBackground | `#F2F2F7` | `#1C1C1E` |
| tertiarySystemBackground | `#FFFFFF` | `#2C2C2E` |
| systemGroupedBackground | `#F2F2F7` | `#000000` |
| secondarySystemGroupedBackground | `#FFFFFF` | `#1C1C1E` |
| tertiarySystemGroupedBackground | `#F2F2F7` | `#2C2C2E` |

**Fill colors:**

| Token | Light Mode | Dark Mode |
|-------|-----------|----------|
| systemFill | `#787880` (0.20 alpha) | `#787880` (0.36 alpha) |
| secondarySystemFill | `#787880` (0.16 alpha) | `#787880` (0.32 alpha) |
| tertiarySystemFill | `#767680` (0.12 alpha) | `#767680` (0.24 alpha) |
| quaternarySystemFill | `#747480` (0.08 alpha) | `#767680` (0.18 alpha) |

**Separator colors:**

| Token | Light | Dark |
|-------|-------|------|
| separator | `#3C3C43` (0.29 alpha) | `#545458` (0.60 alpha) |
| opaqueSeparator | `#C6C6C8` | `#38383A` |

**System tint colors (all 12):**

| Color | Light Hex | Dark Hex |
|-------|----------|---------|
| systemRed | `#FF3B30` | `#FF453A` |
| systemOrange | `#FF9500` | `#FF9F0A` |
| systemYellow | `#FFCC00` | `#FFD60A` |
| systemGreen | `#34C759` | `#30D158` |
| systemMint | `#00C7BE` | `#63E6E2` |
| systemTeal | `#30B0C7` | `#40C8E0` |
| systemCyan | `#32ADE6` | `#64D2FF` |
| systemBlue | `#007AFF` | `#0A84FF` |
| systemIndigo | `#5856D6` | `#5E5CE6` |
| systemPurple | `#AF52DE` | `#BF5AF2` |
| systemPink | `#FF2D55` | `#FF375F` |
| systemBrown | `#A2845E` | `#AC8E68` |

**System gray scale:**

| Token | Light | Dark |
|-------|-------|------|
| systemGray | `#8E8E93` | `#8E8E93` |
| systemGray2 | `#AEAEB2` | `#636366` |
| systemGray3 | `#C7C7CC` | `#48484A` |
| systemGray4 | `#D1D1D6` | `#3A3A3C` |
| systemGray5 | `#E5E5EA` | `#2C2C2E` |
| systemGray6 | `#F2F2F7` | `#1C1C1E` |

### Corner radius conventions

| Component | Radius | Notes |
|-----------|--------|-------|
| Buttons (medium) | **8pt** | System default |
| Buttons (small) | **6pt** | — |
| Buttons (large) | **12pt** | — |
| Buttons (capsule) | **height/2** | Fully rounded |
| Cards / grouped sections | **10pt** | — |
| Sheets / modals | **10–12pt** | Top corners only |
| Alerts | **14pt** | Continuous curve |
| Search bar | **10pt** | — |
| Badges | **full** | Capsule shape |

All system corners use `CALayerCornerCurve.continuous` (superellipse) — in SwiftUI: `RoundedRectangle(cornerRadius: x, style: .continuous)`.

### Animation and motion tokens

| Token | Value | Context |
|-------|-------|---------|
| duration.instant | **0s** | Immediate feedback |
| duration.fast | **0.2s** | Quick transitions, keyboard |
| duration.default | **0.35s** | System standard (UIKit default) |
| duration.slow | **0.5s** | Modal presentations |
| spring.default | response: **0.55**, damping: **0.825** | SwiftUI `.spring()` |
| spring.bouncy | bounce: **~0.15** | Brisk, slight bounce |
| spring.snappy | bounce: **~0.0** | No overshoot, responsive |
| spring.smooth | bounce: **0.0** | Critically damped |
| easing.easeInOut | **0.42, 0, 0.58, 1** | Standard UIKit curve |

### SF Symbols sizing

Symbols scale with the paired text style — a body-sized symbol renders at **17pt**. Weight matching is automatic in SwiftUI when using `.font()`. Tab bar icons use the **fill** variant at **~25pt**; navigation bar icons use **outline** at **~22pt**.

---

<!-- section: Part 3: iOS 26 Liquid Glass keywords: Liquid Glass, iOS 26, materials, blur, specular -->
## Part 3: iOS 26 — Liquid Glass and the new design language

iOS 26 shipped September 2025 with **Liquid Glass**, Apple's largest visual overhaul since iOS 7. This translucent material uses real-time refraction, specular highlights that respond to device motion, and adaptive shadows — creating UI elements that behave like real glass. The design unifies across all Apple platforms simultaneously.

### New design tokens required for iOS 26

The Liquid Glass system introduces several token-relevant changes that must be captured:

- **Glass material variants**: `.regular`, `.clear`, `.tint(Color)`, applied via `glassEffect(_:in:)` modifier
- **Tab bars float** above content on glass surfaces with collapse-on-scroll behavior. New API: `tabViewBottomAccessory` for persistent floating content (mini-players). The search tab now transforms into a search field with `.search` role
- **Scroll edge effects** replace hard dividers — **soft** (default, iOS) uses subtle blur; **hard** (macOS) uses stronger opacity
- **Concentric shape system**: three shape types — fixed radius, capsule (height/2), and concentric (outer radius − padding). New `ContainerRelativeShape` adapts child corner radii to parent containers
- **ToolbarSpacer** for visual grouping; `toolbarGlassBackgroundVisibility` controls glass rendering
- **Search bar relocated** to screen bottom for ergonomics
- **macOS X-Large control size** added with Liquid Glass emphasis
- **Typography is bolder and left-aligned** in system UI (alerts, onboarding)
- **New button styles**: `.buttonStyle(.glass)` and `.buttonStyle(.glassProminent)` for tinted glass

### Key SwiftUI APIs

```swift
// Glass effect on any view
.glassEffect(.regular, in: .rect(cornerRadius: 20))

// Glass button
Button("Action") { }.buttonStyle(.glass)
Button("Primary") { }.buttonStyle(.glassProminent)

// Tab bar with bottom accessory
TabView {
    Tab("Home", systemImage: "house") { HomeView() }
    Tab("Search", systemImage: "magnifyingglass", role: .search) { SearchView() }
}
.tabViewBottomAccessory { MiniPlayerView() }

// Concentric shapes
RoundedRectangle(cornerRadius: outerRadius - padding, style: .continuous)
```

### Token implications

The glass material renders dynamically — there is no static hex value. Token the *intent* (glass vs. opaque) and *variant* (regular, clear, prominent), not the rendered pixel color. For non-Liquid-Glass fallback on older devices, semantic surface color tokens provide the opaque alternative.

---

<!-- section: Part 4: OKLCH color generation keywords: OKLCH, color generation, hue, chroma, lightness, palette -->
## Part 4: Parameterizable color generation with OKLCH

The color system uses **OKLCH** (Lightness-Chroma-Hue) because it is perceptually uniform: equal numeric changes produce equal perceived changes, unlike HSL where blue and yellow at 50% lightness look vastly different.

### ThemeConfig specification

```json
{
  "$schema": "theme-config-v1",
  "name": "sporty",
  "color": {
    "primaryHue": 210,
    "chromaPeak": 0.30,
    "chromaBase": 0.08,
    "lightnessRange": { "min": 0.15, "max": 0.97 },
    "saturationCurve": "sine",
    "warmthBias": 0,
    "secondaryHueOffset": 180,
    "tertiaryHueOffset": 60,
    "neutralChroma": 0.02
  },
  "typography": {
    "fontFamily": "SF Pro",
    "basePlatform": "iOS",
    "typeScale": 1.0
  },
  "shape": {
    "baseRadius": 8,
    "radiusScale": "proportional",
    "cornerStyle": "continuous"
  },
  "motion": {
    "style": "spring",
    "responsiveness": "default"
  }
}
```

### Generation algorithm (sine-curve chroma easing)

The recommended approach uses `sin()` to create a chroma curve that peaks at mid-tones and falls off at extremes, producing rich mid-range colors with muted light and dark endpoints:

```
For each step i from 0 to 10 (mapped to lightness values):
  L = lightnessRange.max - (i / 10) * (lightnessRange.max - lightnessRange.min)
  C = chromaBase + sin(i/10 * π) * chromaPeak
  H = primaryHue + (warmthBias * (1 - L))  // warm shift in darks
```

This produces scales like Tailwind CSS v4's OKLCH colors, where chroma peaks at steps 400–600 and hue may drift slightly across the scale for organic warmth.

### Three theme configurations

| Parameter | 🏃 Sporty | 🥗 Diet | ✨ Minimalist |
|-----------|----------|---------|--------------|
| primaryHue | 210 (electric blue) | 145 (forest green) | 260 (muted indigo) |
| chromaPeak | **0.30** | **0.18** | **0.10** |
| chromaBase | 0.08 | 0.03 | 0.01 |
| Harmony | Complementary (180°) | Analogous (±30°) | Close analogous (±15°) |
| neutralChroma | 0.02 (tinted) | 0.015 (warm) | 0.008 (near-pure gray) |
| Lightness range | 0.15–0.97 (wide) | 0.18–0.96 (medium) | 0.20–0.95 (narrow) |
| warmthBias | 0° | +10° | 0° |
| Mood | High energy, bold contrast | Organic, warm, earthy | Quiet, restrained, neutral |

**Sporty primary scale example (H=210):**
```
50:  oklch(0.97  0.08  210)    ← near-white with blue tint
300: oklch(0.77  0.27  210)    ← vivid mid-light
500: oklch(0.55  0.30  210)    ← brand color (peak chroma)
700: oklch(0.37  0.22  210)    ← deep blue
950: oklch(0.15  0.08  210)    ← near-black with blue tint
```

### Light/dark mode generation

Dark mode uses **tone swapping**, not simple lightness inversion. Following the Material Design 3 pattern:

| Role | Light Mode Step | Dark Mode Step |
|------|----------------|---------------|
| primary (accent) | 500 (L≈0.55) | 300 (L≈0.77) |
| primaryContainer | 100 (L≈0.93) | 800 (L≈0.28) |
| surface | 50 (L≈0.97) | 950 (L≈0.15) |
| onSurface (text) | 900 (L≈0.21) | 100 (L≈0.93) |
| outline | 500 (L≈0.55) | 400 (L≈0.65) |

In dark mode, backgrounds go dark while accent colors get *lighter* to maintain visibility. Surface hierarchy uses lightness instead of shadows (you can't see shadows in the dark).

### Accessibility enforcement

Every generated color pair is validated against WCAG AA: **4.5:1** for normal text, **3:1** for large text and UI components. Apple's "Increase Contrast" mode requires a fourth color variant per token (light, dark, light-high-contrast, dark-high-contrast). The OKLCH lightness channel directly correlates to perceived brightness, making contrast predictions more reliable than HSL-based approaches.

---

<!-- section: Part 5: Semantic and component tokens keywords: semantic tokens, component tokens, button, card, textfield -->
## Part 5: Complete semantic and component token specification

### Semantic color tokens (JSON, DTCG format)

```json
{
  "$schema": "https://www.designtokens.org/schemas/2025.10/format.json",
  "color": {
    "bg": {
      "$type": "color",
      "primary":   { "$value": "{color.neutral.50}",  "$description": "Default page background" },
      "secondary": { "$value": "{color.neutral.100}", "$description": "Grouped/card background" },
      "tertiary":  { "$value": "{color.neutral.50}",  "$description": "Nested surface" },
      "brand":     { "$value": "{color.primary.500}", "$description": "Brand-colored surfaces" },
      "success":   { "$value": "{color.green.100}",   "$description": "Success state background" },
      "warning":   { "$value": "{color.yellow.100}",  "$description": "Warning state background" },
      "error":     { "$value": "{color.red.100}",     "$description": "Error state background" },
      "info":      { "$value": "{color.blue.100}",    "$description": "Info state background" }
    },
    "text": {
      "$type": "color",
      "primary":   { "$value": "{color.neutral.900}", "$description": "High-emphasis body text" },
      "secondary": { "$value": "{color.neutral.500}", "$description": "Supporting text, 60% emphasis" },
      "tertiary":  { "$value": "{color.neutral.400}", "$description": "Placeholders, 30% emphasis" },
      "onBrand":   { "$value": "{color.neutral.50}",  "$description": "Text on brand-colored surfaces" },
      "link":      { "$value": "{color.primary.500}", "$description": "Interactive text links" },
      "error":     { "$value": "{color.red.600}",     "$description": "Error messages" },
      "success":   { "$value": "{color.green.600}",   "$description": "Success messages" }
    },
    "border": {
      "$type": "color",
      "default":   { "$value": "{color.neutral.200}", "$description": "Standard borders" },
      "strong":    { "$value": "{color.neutral.400}", "$description": "High-emphasis borders" },
      "brand":     { "$value": "{color.primary.500}", "$description": "Focus rings, active borders" },
      "error":     { "$value": "{color.red.500}",     "$description": "Error state borders" }
    },
    "fill": {
      "$type": "color",
      "primary":   { "$value": "{color.neutral.100}", "$description": "Default fill (toggles, sliders)" },
      "secondary": { "$value": "{color.neutral.200}", "$description": "Secondary fill" }
    },
    "interactive": {
      "$type": "color",
      "primary":      { "$value": "{color.primary.500}", "$description": "Primary action color" },
      "primaryHover":  { "$value": "{color.primary.600}", "$description": "Primary hover/pressed" },
      "secondary":     { "$value": "{color.primary.100}", "$description": "Secondary action bg" },
      "destructive":   { "$value": "{color.red.500}",     "$description": "Destructive actions" }
    }
  }
}
```

### Component token specifications

Every interactive component needs tokens for **background, text, border, cornerRadius, padding, height, font, shadow, opacity** across **default, pressed, disabled, focused** states.

**Button tokens (all variants):**

```json
{
  "button": {
    "primary": {
      "bg":            { "$value": "{color.interactive.primary}" },
      "bgPressed":     { "$value": "{color.interactive.primaryHover}" },
      "bgDisabled":    { "$value": "{color.fill.secondary}" },
      "text":          { "$value": "{color.text.onBrand}" },
      "textDisabled":  { "$value": "{color.text.tertiary}" },
      "cornerRadius":  { "$value": "{radius.md}" },
      "paddingX":      { "$value": "{space.md}" },
      "paddingY":      { "$value": "{space.sm}" },
      "minHeight":     { "$value": "{ size.touch-target }" },
      "font":          { "$value": "{typography.body}" },
      "fontWeight":    { "$value": "semibold" },
      "disabledOpacity": { "$value": "0.4" }
    },
    "secondary": {
      "bg":            { "$value": "transparent" },
      "bgPressed":     { "$value": "{color.fill.primary}" },
      "text":          { "$value": "{color.interactive.primary}" },
      "border":        { "$value": "{color.interactive.primary}" },
      "borderWidth":   { "$value": "{border.width.thin}" }
    },
    "tertiary": {
      "bg":            { "$value": "transparent" },
      "bgPressed":     { "$value": "{color.fill.primary}" },
      "text":          { "$value": "{color.interactive.primary}" }
    },
    "destructive": {
      "bg":            { "$value": "{color.interactive.destructive}" },
      "text":          { "$value": "{color.text.onBrand}" }
    },
    "glass": {
      "material":      { "$value": "glass.regular" },
      "materialProminent": { "$value": "glass.tinted" }
    },
    "sizing": {
      "small":  { "minHeight": { "$value": "34" }, "paddingX": { "$value": "12" }, "fontSize": { "$value": "15" } },
      "medium": { "minHeight": { "$value": "44" }, "paddingX": { "$value": "16" }, "fontSize": { "$value": "17" } },
      "large":  { "minHeight": { "$value": "50" }, "paddingX": { "$value": "20" }, "fontSize": { "$value": "17" } }
    }
  }
}
```

**TextField tokens:**

```json
{
  "textField": {
    "bg":              { "$value": "{color.fill.primary}" },
    "bgFocused":       { "$value": "{color.bg.primary}" },
    "text":            { "$value": "{color.text.primary}" },
    "placeholder":     { "$value": "{color.text.tertiary}" },
    "border":          { "$value": "{color.border.default}" },
    "borderFocused":   { "$value": "{color.border.brand}" },
    "borderError":     { "$value": "{color.border.error}" },
    "borderWidth":     { "$value": "{border.width.thin}" },
    "cornerRadius":    { "$value": "{radius.sm}" },
    "height":          { "$value": "44" },
    "paddingX":        { "$value": "{space.sm}" },
    "fontSize":        { "$value": "17" },
    "labelFont":       { "$value": "{typography.subheadline}" },
    "helperFont":      { "$value": "{typography.caption1}" },
    "helperColor":     { "$value": "{color.text.secondary}" },
    "errorColor":      { "$value": "{color.text.error}" }
  }
}
```

**Card tokens:**

```json
{
  "card": {
    "bg":              { "$value": "{color.bg.secondary}" },
    "border":          { "$value": "{color.border.default}" },
    "borderWidth":     { "$value": "0" },
    "cornerRadius":    { "$value": "{radius.lg}" },
    "padding":         { "$value": "{space.md}" },
    "shadow": {
      "$type": "shadow",
      "$value": { "offsetX": "0", "offsetY": "2", "blur": "8", "spread": "0", "color": "#00000014" }
    }
  }
}
```

**Navigation, tab bar, and list tokens:**

```json
{
  "navigationBar": {
    "height":        { "$value": "44", "$description": "Standard; 96 with large title" },
    "bg":            { "$value": "{color.bg.primary}" },
    "titleColor":    { "$value": "{color.text.primary}" },
    "titleFont":     { "$value": "{typography.headline}" },
    "largeTitleFont": { "$value": "{typography.largeTitle}" },
    "tintColor":     { "$value": "{color.interactive.primary}" }
  },
  "tabBar": {
    "height":        { "$value": "49" },
    "bg":            { "$value": "{color.bg.primary}" },
    "selectedColor": { "$value": "{color.interactive.primary}" },
    "unselectedColor": { "$value": "{color.text.secondary}" },
    "iconSize":      { "$value": "25" },
    "labelFont":     { "$value": "10", "weight": "medium" },
    "badgeBg":       { "$value": "{color.interactive.destructive}" },
    "badgeText":     { "$value": "{color.text.onBrand}" },
    "badgeSize":     { "$value": "18" }
  },
  "list": {
    "rowHeight":     { "$value": "44" },
    "rowBg":         { "$value": "{color.bg.primary}" },
    "separator":     { "$value": "{color.border.default}" },
    "separatorInset": { "$value": "16" },
    "cellPadding":   { "$value": "{space.md}" },
    "primaryText":   { "$value": "{typography.body}" },
    "secondaryText": { "$value": "{typography.subheadline}" },
    "secondaryColor": { "$value": "{color.text.secondary}" }
  }
}
```

### State modification rules

Rather than defining every state explicitly, the system uses modification rules:

| State | Modification | Opacity |
|-------|-------------|---------|
| Default | Base value | 1.0 |
| Pressed/Highlighted | Darken 10% (light mode) or lighten 10% (dark mode) | 1.0 |
| Disabled | Base value | **0.4** |
| Focused | Add `color.border.brand` ring, **2pt** width, **2pt** offset | 1.0 |
| Loading | Replace content with skeleton shimmer | 0.7 for placeholder |

### Elevation / shadow scale

```json
{
  "shadow": {
    "none": { "$type": "shadow", "$value": { "offsetX": "0", "offsetY": "0", "blur": "0", "spread": "0", "color": "#00000000" } },
    "xs":   { "$type": "shadow", "$value": { "offsetX": "0", "offsetY": "1", "blur": "2", "spread": "0", "color": "#0000000D" } },
    "sm":   { "$type": "shadow", "$value": { "offsetX": "0", "offsetY": "2", "blur": "4", "spread": "0", "color": "#0000001A" } },
    "md":   { "$type": "shadow", "$value": { "offsetX": "0", "offsetY": "4", "blur": "8", "spread": "-1", "color": "#00000014" } },
    "lg":   { "$type": "shadow", "$value": { "offsetX": "0", "offsetY": "8", "blur": "16", "spread": "-2", "color": "#00000014" } },
    "xl":   { "$type": "shadow", "$value": { "offsetX": "0", "offsetY": "16", "blur": "32", "spread": "-4", "color": "#0000001A" } }
  }
}
```

---

## Part 6: Responsive and adaptive token strategies

### Size class token overrides

Tokens adapt between compact and regular width size classes. The system uses platform-level overrides rather than duplicating token sets:

| Token | Compact (iPhone) | Regular (iPad/Mac) |
|-------|-----------------|-------------------|
| layout.margin | **16pt** | **20pt** |
| layout.maxContentWidth | **100%** | **672pt** (readable width) |
| nav.style | Stack | Split (sidebar) |
| list.rowHeight | **44pt** | **44pt** (or denser on Mac) |
| typography.scale | 1.0× | 1.0× (same text styles) |

### Platform override pattern (iOS → macOS)

Rather than duplicating every token, the system applies a platform multiplier at the semantic layer:

```json
{
  "platform": {
    "iOS": {
      "typography.body.size": 17,
      "component.minTouchTarget": 44,
      "layout.defaultMargin": 16,
      "list.rowHeight": 44,
      "controlSize": "regular"
    },
    "macOS": {
      "typography.body.size": 13,
      "component.minTouchTarget": 22,
      "layout.defaultMargin": 20,
      "list.rowHeight": 24,
      "controlSize": "regular"
    }
  }
}
```

SwiftUI components render differently per platform automatically (Toggle → Switch on iOS, Checkbox on macOS; Picker → wheel on iOS, popup on macOS), so component tokens must account for these platform behaviors.

### Dynamic Type adaptation

Font tokens use Apple's `UIFont.TextStyle` rather than hardcoded sizes, allowing automatic scaling. Component tokens define minimum heights that grow with text:

```swift
// Token-driven component that respects Dynamic Type
@ScaledMetric(relativeTo: .body) var bodyPadding: CGFloat = 16
@ScaledMetric(relativeTo: .body) var minRowHeight: CGFloat = 44
```

Spacing tokens can optionally scale with Dynamic Type using `@ScaledMetric`, but this should be limited to padding directly surrounding text — structural spacing (section gaps, margins) should remain fixed to prevent layout distortion at AX5 sizes.

---

## Part 7: Complete primitive token set (JSON)

This is the full primitive layer generated from the sporty ThemeConfig:

```json
{
  "$schema": "https://www.designtokens.org/schemas/2025.10/format.json",

  "color": {
    "primary": {
      "$type": "color",
      "50":  { "$value": "oklch(0.97 0.08 210)" },
      "100": { "$value": "oklch(0.93 0.12 210)" },
      "200": { "$value": "oklch(0.85 0.20 210)" },
      "300": { "$value": "oklch(0.77 0.27 210)" },
      "400": { "$value": "oklch(0.65 0.30 210)" },
      "500": { "$value": "oklch(0.55 0.30 210)" },
      "600": { "$value": "oklch(0.45 0.27 210)" },
      "700": { "$value": "oklch(0.37 0.22 210)" },
      "800": { "$value": "oklch(0.28 0.16 210)" },
      "900": { "$value": "oklch(0.21 0.10 210)" },
      "950": { "$value": "oklch(0.15 0.08 210)" }
    },
    "secondary": {
      "$type": "color",
      "50":  { "$value": "oklch(0.97 0.08 30)" },
      "500": { "$value": "oklch(0.55 0.30 30)" },
      "900": { "$value": "oklch(0.21 0.10 30)" }
    },
    "neutral": {
      "$type": "color",
      "50":  { "$value": "oklch(0.97 0.02 210)" },
      "100": { "$value": "oklch(0.93 0.02 210)" },
      "200": { "$value": "oklch(0.87 0.02 210)" },
      "300": { "$value": "oklch(0.80 0.02 210)" },
      "400": { "$value": "oklch(0.68 0.02 210)" },
      "500": { "$value": "oklch(0.55 0.02 210)" },
      "600": { "$value": "oklch(0.45 0.02 210)" },
      "700": { "$value": "oklch(0.37 0.02 210)" },
      "800": { "$value": "oklch(0.28 0.02 210)" },
      "900": { "$value": "oklch(0.21 0.02 210)" },
      "950": { "$value": "oklch(0.15 0.02 210)" }
    },
    "red":    { "$type": "color", "500": { "$value": "oklch(0.55 0.24 25)" } },
    "green":  { "$type": "color", "500": { "$value": "oklch(0.55 0.18 145)" } },
    "yellow": { "$type": "color", "500": { "$value": "oklch(0.75 0.18 85)" } },
    "blue":   { "$type": "color", "500": { "$value": "oklch(0.55 0.24 250)" } }
  },

  "spacing": {
    "$type": "dimension",
    "0":   { "$value": "0pt" },
    "1":   { "$value": "4pt" },
    "2":   { "$value": "8pt" },
    "3":   { "$value": "12pt" },
    "4":   { "$value": "16pt" },
    "5":   { "$value": "20pt" },
    "6":   { "$value": "24pt" },
    "8":   { "$value": "32pt" },
    "10":  { "$value": "40pt" },
    "12":  { "$value": "48pt" },
    "16":  { "$value": "64pt" }
  },

  "radius": {
    "$type": "dimension",
    "none": { "$value": "0pt" },
    "xs":   { "$value": "4pt" },
    "sm":   { "$value": "6pt" },
    "md":   { "$value": "8pt" },
    "lg":   { "$value": "10pt" },
    "xl":   { "$value": "14pt" },
    "full": { "$value": "9999pt" }
  },

  "borderWidth": {
    "$type": "dimension",
    "none":   { "$value": "0pt" },
    "thin":   { "$value": "1pt" },
    "medium": { "$value": "2pt" },
    "thick":  { "$value": "3pt" }
  },

  "opacity": {
    "$type": "number",
    "disabled":     { "$value": 0.4 },
    "hoverOverlay": { "$value": 0.08 },
    "pressOverlay": { "$value": 0.12 },
    "overlay":      { "$value": 0.5 }
  },

  "typography": {
    "iOS": {
      "largeTitle":  { "$type": "typography", "$value": { "fontFamily": "SF Pro Display", "fontSize": "34pt", "fontWeight": 400, "lineHeight": "41pt", "letterSpacing": "0.37pt" } },
      "title1":      { "$type": "typography", "$value": { "fontFamily": "SF Pro Display", "fontSize": "28pt", "fontWeight": 400, "lineHeight": "34pt", "letterSpacing": "0.36pt" } },
      "title2":      { "$type": "typography", "$value": { "fontFamily": "SF Pro Display", "fontSize": "22pt", "fontWeight": 400, "lineHeight": "28pt", "letterSpacing": "0.35pt" } },
      "title3":      { "$type": "typography", "$value": { "fontFamily": "SF Pro Display", "fontSize": "20pt", "fontWeight": 400, "lineHeight": "25pt", "letterSpacing": "0.38pt" } },
      "headline":    { "$type": "typography", "$value": { "fontFamily": "SF Pro Text", "fontSize": "17pt", "fontWeight": 600, "lineHeight": "22pt", "letterSpacing": "-0.41pt" } },
      "body":        { "$type": "typography", "$value": { "fontFamily": "SF Pro Text", "fontSize": "17pt", "fontWeight": 400, "lineHeight": "22pt", "letterSpacing": "-0.41pt" } },
      "callout":     { "$type": "typography", "$value": { "fontFamily": "SF Pro Text", "fontSize": "16pt", "fontWeight": 400, "lineHeight": "21pt", "letterSpacing": "-0.32pt" } },
      "subheadline": { "$type": "typography", "$value": { "fontFamily": "SF Pro Text", "fontSize": "15pt", "fontWeight": 400, "lineHeight": "20pt", "letterSpacing": "-0.24pt" } },
      "footnote":    { "$type": "typography", "$value": { "fontFamily": "SF Pro Text", "fontSize": "13pt", "fontWeight": 400, "lineHeight": "18pt", "letterSpacing": "-0.08pt" } },
      "caption1":    { "$type": "typography", "$value": { "fontFamily": "SF Pro Text", "fontSize": "12pt", "fontWeight": 400, "lineHeight": "16pt", "letterSpacing": "0pt" } },
      "caption2":    { "$type": "typography", "$value": { "fontFamily": "SF Pro Text", "fontSize": "11pt", "fontWeight": 400, "lineHeight": "13pt", "letterSpacing": "0.07pt" } }
    },
    "macOS": {
      "largeTitle":  { "$type": "typography", "$value": { "fontFamily": "SF Pro Display", "fontSize": "26pt", "fontWeight": 400, "lineHeight": "32pt" } },
      "title1":      { "$type": "typography", "$value": { "fontFamily": "SF Pro Display", "fontSize": "22pt", "fontWeight": 400, "lineHeight": "28pt" } },
      "title2":      { "$type": "typography", "$value": { "fontFamily": "SF Pro Text", "fontSize": "17pt", "fontWeight": 400, "lineHeight": "22pt" } },
      "title3":      { "$type": "typography", "$value": { "fontFamily": "SF Pro Text", "fontSize": "15pt", "fontWeight": 400, "lineHeight": "20pt" } },
      "headline":    { "$type": "typography", "$value": { "fontFamily": "SF Pro Text", "fontSize": "13pt", "fontWeight": 700, "lineHeight": "18pt" } },
      "body":        { "$type": "typography", "$value": { "fontFamily": "SF Pro Text", "fontSize": "13pt", "fontWeight": 400, "lineHeight": "18pt" } },
      "callout":     { "$type": "typography", "$value": { "fontFamily": "SF Pro Text", "fontSize": "12pt", "fontWeight": 400, "lineHeight": "16pt" } },
      "subheadline": { "$type": "typography", "$value": { "fontFamily": "SF Pro Text", "fontSize": "11pt", "fontWeight": 400, "lineHeight": "14pt" } },
      "footnote":    { "$type": "typography", "$value": { "fontFamily": "SF Pro Text", "fontSize": "10pt", "fontWeight": 400, "lineHeight": "13pt" } },
      "caption1":    { "$type": "typography", "$value": { "fontFamily": "SF Pro Text", "fontSize": "10pt", "fontWeight": 400, "lineHeight": "13pt" } },
      "caption2":    { "$type": "typography", "$value": { "fontFamily": "SF Pro Text", "fontSize": "10pt", "fontWeight": 500, "lineHeight": "13pt" } }
    }
  },

  "motion": {
    "duration": {
      "$type": "duration",
      "instant":  { "$value": "0ms" },
      "fast":     { "$value": "200ms" },
      "default":  { "$value": "350ms" },
      "slow":     { "$value": "500ms" }
    },
    "easing": {
      "$type": "cubicBezier",
      "easeInOut": { "$value": [0.42, 0, 0.58, 1] },
      "easeOut":   { "$value": [0, 0, 0.58, 1] },
      "easeIn":    { "$value": [0.42, 0, 1, 1] }
    }
  },

  "zIndex": {
    "$type": "number",
    "base":    { "$value": 0 },
    "raised":  { "$value": 1 },
    "overlay": { "$value": 100 },
    "modal":   { "$value": 200 },
    "toast":   { "$value": 300 }
  }
}
```

---

## Part 8: Style Dictionary pipeline for cross-platform output

### Configuration

```json
{
  "source": ["tokens/generated/**/*.tokens.json"],
  "platforms": {
    "ios-swift": {
      "transformGroup": "ios-swift",
      "buildPath": "build/ios/",
      "files": [
        { "destination": "DesignTokenColors.swift", "format": "ios-swift/class.swift", "filter": { "$type": "color" }, "className": "TokenColors" },
        { "destination": "DesignTokenTypography.swift", "format": "ios-swift/class.swift", "filter": { "$type": "typography" }, "className": "TokenTypography" },
        { "destination": "DesignTokenSpacing.swift", "format": "ios-swift/class.swift", "filter": { "$type": "dimension" }, "className": "TokenSpacing" }
      ]
    },
    "ios-colorsets": {
      "buildPath": "build/ios-colorsets/",
      "transforms": ["attribute/cti", "name/cti/pascal", "attribute/color"],
      "actions": ["colorsets"]
    },
    "figma": {
      "transformGroup": "css",
      "buildPath": "build/figma/",
      "files": [
        { "destination": "tokens-for-figma.json", "format": "json/nested" }
      ]
    }
  }
}
```

Style Dictionary transforms the DTCG JSON source into: Swift extensions with `UIColor`/`Color` initializers, Asset Catalog `.colorset` files with automatic light/dark variants, and Figma-compatible JSON for import via Tokens Studio.

---

<!-- section: Part 9: Phased prompts keywords: Claude Code prompts, Figma AI, generation, workflow -->
## Part 9: Phased prompts for Claude Code and Figma AI

### CLAUDE.md system context file

Place this at the project root. Claude Code reads it automatically:

```markdown
# Design System Rules

## Token Sources
- All tokens: `DesignSystem/Tokens/`
- Colors: `TokenColors.swift` — use `Color.tokenName`, never raw hex
- Typography: Use SwiftUI `.font(.textStyle)` mapped to Apple text styles
- Spacing: `TokenSpacing.swift` — use `Spacing.md` etc., never magic numbers
- Radii: `TokenRadius.swift` — use `Radius.md` etc.

## Rules
1. NEVER use hardcoded colors, spacing, or font sizes
2. ALL interactive elements must be at least 44×44pt
3. Support light AND dark mode via semantic color tokens
4. Use SF Symbols for icons; match symbol weight to adjacent text weight
5. Use `.continuous` corner style on all rounded rectangles
6. Use SwiftUI native components; avoid UIKit wrapping unless necessary
7. Support Dynamic Type — use text styles, not fixed font sizes
8. Apply `.accessibilityLabel` to all interactive elements
9. For iOS 26: prefer `.buttonStyle(.glass)` for secondary actions
10. Test at AX5 Dynamic Type to verify layout doesn't break
```

### Phase 1 — Foundation prompt

```
Read DesignSystem/Tokens/ to understand our complete token system. Then create:

1. Color+Tokens.swift — All semantic colors as static Color properties with
   light/dark mode support using UIColor { traits in ... } pattern
2. Typography+Tokens.swift — Font extension mapping token names to Font values
3. Spacing.swift — Spacing enum with all values from the spacing scale
4. Radius.swift — Corner radius constants
5. Shadow.swift — Shadow token modifiers as ViewModifier

Generate a PreviewProvider gallery that shows every token visually.
Use @Environment(\.colorScheme) for mode switching. No hardcoded values.
```

### Phase 2 — Component library prompt

```
Using the foundation tokens from Phase 1, build these SwiftUI components:

1. DSButton — Variants: primary, secondary, tertiary, destructive, glass
   - Sizes: small (34pt), medium (44pt), large (50pt)
   - States: default, pressed (0.9 scale + pressed color), disabled (0.4 opacity), loading (ProgressView)
   - Use semantic color tokens only

2. DSTextField — With label, placeholder, helper text, error state
   - Focus ring using color.border.brand at 2pt
   - Shake animation on error

3. DSCard — Surface container with shadow.md, radius.lg, padding.md

4. DSBadge — Pill shape, destructive color, caption2 white text

5. DSToggle, DSSlider, DSSegmentedControl — Styled with tokens

Each component: PreviewProvider with all variants, .accessibilityLabel, no magic numbers.
```

### Phase 3 — Screen composition prompt

```
Using DSButton, DSTextField, DSCard from Phase 2, compose:

1. OnboardingScreen — Hero image area, title (largeTitle), subtitle (body),
   primary CTA button, secondary text button. Spacing.xl between sections.

2. SettingsScreen — List with grouped sections, toggles, navigation links,
   destructive "Sign Out" button. Use list tokens for row height and separators.

3. DashboardScreen — Cards grid (LazyVGrid), each card with DSCard tokens,
   tab bar at bottom with 4 tabs using tabBar tokens.

All screens: NavigationStack, support both size classes, respect safe areas.
```

### Phase 4 — Polish and animation prompt

```
Add to existing screens:
1. Staggered fade-in entry animation (0.05s delay per element, spring.smooth)
2. Button press scale: .scaleEffect(isPressed ? 0.96 : 1.0) with spring.snappy
3. Card hover effect (macOS): shadow.lg on hover, shadow.md default
4. Skeleton loading states using shimmer gradient animation
5. Pull-to-refresh with spring.bouncy
6. Haptic feedback: .light on button press, .success on completion
7. iOS 26: Apply .glassEffect to navigation bar background
8. Keyboard avoidance with ScrollView + .scrollDismissesKeyboard(.interactively)
```

### Figma AI / Figma Make prompts

**Library setup prompt:**
```
Create a component library using these design tokens as Figma Variables:
- Primitives collection (hidden from publishing): color scales, spacing scale, radii
- Semantic collection: surface colors, text colors, border colors, interactive colors
- Map light and dark mode as Variable modes

Build atomic components: Button/primary, Button/secondary, TextField, Card, Badge
Each component should use only semantic variables, never raw values.
Apply Auto Layout with spacing tokens. Use continuous corner radius.
```

**Screen generation prompt:**
```
Using the component library with design tokens, generate a [screen name] screen:
- Follow iOS 26 Liquid Glass conventions for navigation and tab bar
- Use spacing tokens for all gaps and padding
- Apply the semantic color system for light mode
- Ensure all text uses the typography token scale
- Minimum 44pt touch targets for all interactive elements
- Add a dark mode variant using the same semantic tokens with mode switching
```

---

## Part 10: Consistency rules and what components should share

Components should share token values through semantic aliases rather than coincidentally identical numbers. This enforces intentional consistency — when a shared value changes, all consumers update together.

**Shared token bindings:**

- **All interactive elements** share `color.interactive.primary` for their active/accent color, `radius.md` (8pt) for standard corner radius, and `size.touchTarget` (44pt) as minimum height
- **All text inputs** (TextField, TextEditor, SearchBar) share `textField.bg`, `textField.border`, `textField.borderFocused`, and `textField.height` tokens
- **All container surfaces** (Card, Sheet, Alert, ActionSheet) share the `color.bg.secondary` background and a corner radius of `radius.lg` (10pt) or larger
- **All navigation chrome** (NavigationBar, TabBar, Toolbar) share `color.bg.primary` background with glass material overlay on iOS 26
- **All destructive actions** use `color.interactive.destructive` regardless of component type
- **Disabled state** universally applies `opacity.disabled` (0.4) — never varies by component

The separation of these shared semantics from component-specific overrides is what makes the system maintainable at scale while remaining fully themeable from a single configuration file.

## Conclusion

This token system achieves completeness across five dimensions: **platform coverage** (iOS + macOS with exact numeric values for every component), **state coverage** (default, pressed, disabled, focused, loading for all interactive elements), **mode coverage** (light, dark, high-contrast generated programmatically), **theme coverage** (any mood from sporty to minimalist via OKLCH parameterization), and **toolchain coverage** (W3C DTCG JSON → Style Dictionary → Swift/Figma outputs → AI prompt integration).

The most critical architectural insight is that parameterization lives *outside* the token hierarchy. The ThemeConfig specifies mood (hue, chroma curve, harmony strategy) and the generator produces primitives — semantic and component layers remain identical across themes. This means switching from a sporty blue palette to an earthy green requires changing **one JSON file**, not hundreds of token values. iOS 26's Liquid Glass adds a new material dimension that sits alongside solid colors in the component token layer, gracefully degrading to opaque semantic colors on older devices. The phased prompt system ensures Claude Code and Figma AI consume tokens at the right granularity — foundations first, components second, compositions third — with the CLAUDE.md file enforcing token-only styling as an unbreakable constraint.