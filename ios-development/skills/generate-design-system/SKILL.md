---
name: generate-design-system
description: Generate Apple HIG-compliant SwiftUI Design System code from token specifications
---

# Generate Design System Skill

Generate complete Design System code based on Apple HIG token standards and OKLCH color generation.

## Input Parameters

From calling command or user:
- `theme`: sporty / diet / minimalist / custom
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

### 2. Generate Theme Colors

Based on theme selection, apply OKLCH algorithm:

**sporty**:
- primaryHue: 210
- chromaPeak: 0.30
- chromaBase: 0.08

**diet**:
- primaryHue: 145
- chromaPeak: 0.18
- chromaBase: 0.03

**minimalist**:
- primaryHue: 260
- chromaPeak: 0.10
- chromaBase: 0.01

Generate 11 color steps (50-950) using:
```
L = 0.97 - (i / 10) * (0.97 - 0.15)
C = chromaBase + sin(i/10 * π) * chromaPeak
H = primaryHue
```

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

### 4. Generate Colors+Tokens.swift

```swift
import SwiftUI

extension Color {
    // MARK: - Primary Colors

    static let appPrimary = Color("Primary500")
    static let appPrimaryLight = Color("Primary300")
    static let appPrimaryDark = Color("Primary700")

    // MARK: - Semantic Colors

    static let appBackground = Color("Background")
    static let appSurface = Color("Surface")
    static let appText = Color("TextPrimary")
    static let appTextSecondary = Color("TextSecondary")

    // MARK: - Status Colors

    static let appSuccess = Color("Success")
    static let appWarning = Color("Warning")
    static let appError = Color("Error")
}
```

### 5. Generate Typography+Tokens.swift

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
extension Font {
    static let macLargeTitle = Font.system(size: 26)
    static let macTitle = Font.system(size: 22)
    static let macBody = Font.system(size: 13)
}
```

### 6. (Optional) Generate Components

If `generateComponents == true`, create:
- `Components/DSButton.swift`
- `Components/DSCard.swift`
- `Components/DSTextField.swift`

Each component uses Design Token constants.

### 7. Output File List

Return:
```
✅ Generated:
- [ProjectName]/DesignSystem/DesignSystem.swift
- [ProjectName]/DesignSystem/Colors+Tokens.swift
- [ProjectName]/DesignSystem/Typography+Tokens.swift
- [ProjectName]/DesignSystem/Components/ (if requested)
```

## Success Criteria

- All spacing values are from 8pt grid
- Colors use OKLCH algorithm (no hardcoded hex)
- Typography uses Dynamic Type text styles
- Platform-specific values when platform=both
