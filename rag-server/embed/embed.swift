import Foundation
import NaturalLanguage

// Usage: embed <text>
// Outputs two lines to stdout:
//   Line 1 — Latin script embedding (comma-separated floats, L2-normalized)
//   Line 2 — CJK (Simplified Chinese) embedding (same format)
// Informational messages go to stderr.

func meanPool(tokenVectors: [[Double]]) -> [Double] {
    guard !tokenVectors.isEmpty else { return [] }
    let dim = tokenVectors[0].count
    var result = [Double](repeating: 0.0, count: dim)
    for vec in tokenVectors {
        for i in 0..<dim { result[i] += vec[i] }
    }
    let n = Double(tokenVectors.count)
    return result.map { $0 / n }
}

func l2Normalize(_ vec: [Double]) -> [Double] {
    let norm = sqrt(vec.reduce(0.0) { $0 + $1 * $1 })
    guard norm > 1e-10 else { return vec }
    return vec.map { $0 / norm }
}

func embedText(_ text: String, script: NLScript) -> [Double]? {
    guard let embedding = NLContextualEmbedding(script: script) else {
        fputs("Error: NLContextualEmbedding unavailable for script \(script.rawValue)\n", stderr)
        return nil
    }

    if !embedding.hasAvailableAssets {
        fputs("Info: Downloading model assets for script \(script.rawValue) (~50 MB)...\n", stderr)
        let semaphore = DispatchSemaphore(value: 0)
        var downloadError: Error?
        embedding.requestAssets { result, error in
            if result == .error || result == .notAvailable {
                downloadError = error ?? NSError(domain: "embed", code: 1,
                    userInfo: [NSLocalizedDescriptionKey: "Assets not available (result: \(result.rawValue))"])
            }
            semaphore.signal()
        }
        semaphore.wait()
        if let err = downloadError {
            fputs("Error: Asset download failed: \(err.localizedDescription)\n", stderr)
            return nil
        }
        guard embedding.hasAvailableAssets else {
            fputs("Error: Assets still unavailable after download attempt\n", stderr)
            return nil
        }
        fputs("Info: Download complete.\n", stderr)
    }

    do {
        try embedding.load()
    } catch {
        fputs("Error: Failed to load model: \(error.localizedDescription)\n", stderr)
        return nil
    }

    let embeddingResult: NLContextualEmbeddingResult
    do {
        embeddingResult = try embedding.embeddingResult(for: text, language: nil)
    } catch {
        fputs("Error: embeddingResult failed: \(error.localizedDescription)\n", stderr)
        return nil
    }

    var tokenVectors: [[Double]] = []
    embeddingResult.enumerateTokenVectors(
        in: text.startIndex..<text.endIndex
    ) { vector, _ in
        tokenVectors.append(vector)
        return true
    }

    guard !tokenVectors.isEmpty else {
        fputs("Error: No token vectors produced for input text\n", stderr)
        return nil
    }

    return l2Normalize(meanPool(tokenVectors: tokenVectors))
}

guard CommandLine.arguments.count >= 2 else {
    fputs("Usage: embed <text>\n", stderr)
    exit(1)
}

let inputText = CommandLine.arguments[1...].joined(separator: " ")

guard let latinVec = embedText(inputText, script: .latin) else { exit(1) }
print(latinVec.map { String(format: "%.8f", $0) }.joined(separator: ","))

guard let cjkVec = embedText(inputText, script: .simplifiedChinese) else { exit(1) }
print(cjkVec.map { String(format: "%.8f", $0) }.joined(separator: ","))
