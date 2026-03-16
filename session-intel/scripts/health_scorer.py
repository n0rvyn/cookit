#!/usr/bin/env python3
"""Compute collaboration health scores from daily aggregate data."""

import argparse
import json
import sys


THRESHOLDS = {
    "efficiency": {
        "turns": {"good": 10, "ok": 20},
        "cache_hit_rate": {"good": 0.3, "ok": 0.15},
        "sessions_per_day": {"good": 10, "ok": 5},
    },
    "quality": {
        "build_first_pass_rate": {"good": 0.8, "ok": 0.5},
        "bash_error_rate": {"good": 0.05, "ok": 0.15},
        "repeated_edit_ratio": {"good": 0.1, "ok": 0.3},
    },
    "collaboration": {
        "corrections_per_session": {"good": 0.5, "ok": 1.5},
    },
    "growth": {
        "correction_decay": {"good": 0.3, "ok": 0.1},
        "session_growth": {"good": 0.2, "ok": 0},
    },
}


def score_metric(value, threshold, inverse=False):
    """Score a metric 0-100 based on thresholds.

    inverse=True means lower is better (e.g., error rates).
    """
    if value is None:
        return 50

    good = threshold["good"]
    ok = threshold["ok"]

    if inverse:
        if value <= good:
            return 100
        elif value <= ok:
            return 70
        else:
            max_val = ok * 2
            return max(0, 70 * (1 - (value - ok) / (max_val - ok))) if max_val > ok else 0
    else:
        if value >= good:
            return 100
        elif value >= ok:
            return 70
        else:
            return max(0, 70 * value / ok) if ok > 0 else 0


def score_efficiency(daily_metrics):
    """Score efficiency dimension."""
    if not daily_metrics:
        return {"score": 50, "components": {}}

    n = len(daily_metrics)
    avg_turns = sum(d.get("avg_turns_per_session", 0) for d in daily_metrics) / n
    avg_cache = sum(d.get("avg_cache_hit_rate") or 0 for d in daily_metrics) / n
    avg_sessions = sum(d.get("sessions_count", 0) for d in daily_metrics) / n

    turn_score = score_metric(avg_turns, THRESHOLDS["efficiency"]["turns"], inverse=True)
    cache_score = score_metric(avg_cache, THRESHOLDS["efficiency"]["cache_hit_rate"])
    session_score = score_metric(avg_sessions, THRESHOLDS["efficiency"]["sessions_per_day"])

    score = turn_score * 0.4 + cache_score * 0.3 + session_score * 0.3

    return {
        "score": round(score),
        "components": {
            "avg_turns_per_session": round(avg_turns, 1),
            "turn_score": round(turn_score),
            "cache_hit_rate": round(avg_cache, 3) if avg_cache else None,
            "cache_score": round(cache_score),
            "sessions_per_day": round(avg_sessions, 1),
            "session_score": round(session_score),
        },
    }


def score_quality(daily_metrics):
    """Score quality dimension."""
    if not daily_metrics:
        return {"score": 50, "components": {}}

    build_rates = [
        d["build_first_pass_rate"]
        for d in daily_metrics
        if d.get("build_first_pass_rate") is not None
    ]
    avg_build_rate = sum(build_rates) / len(build_rates) if build_rates else None

    n = len(daily_metrics)
    avg_error_rate = sum(d.get("bash_error_rate", 0) for d in daily_metrics) / n

    total_sessions = sum(d.get("sessions_count", 0) for d in daily_metrics)
    total_repeated = sum(d.get("repeated_edit_sessions", 0) for d in daily_metrics)
    repeated_ratio = total_repeated / total_sessions if total_sessions > 0 else 0

    build_score = score_metric(
        avg_build_rate or 0, THRESHOLDS["quality"]["build_first_pass_rate"]
    )
    error_score = score_metric(
        avg_error_rate, THRESHOLDS["quality"]["bash_error_rate"], inverse=True
    )
    repeat_score = score_metric(
        repeated_ratio, THRESHOLDS["quality"]["repeated_edit_ratio"], inverse=True
    )

    score = build_score * 0.4 + error_score * 0.35 + repeat_score * 0.25

    return {
        "score": round(score),
        "components": {
            "build_first_pass_rate": round(avg_build_rate, 2) if avg_build_rate else None,
            "build_score": round(build_score),
            "bash_error_rate": round(avg_error_rate, 3),
            "error_score": round(error_score),
            "repeated_edit_ratio": round(repeated_ratio, 2),
            "repeat_score": round(repeat_score),
        },
    }


def score_collaboration(daily_metrics):
    """Score collaboration dimension."""
    if not daily_metrics:
        return {"score": 50, "components": {}}

    total_sessions = sum(d.get("sessions_count", 0) for d in daily_metrics)
    total_corrections = sum(d.get("corrections_count", 0) for d in daily_metrics)
    corrections_per_session = total_corrections / total_sessions if total_sessions > 0 else 0

    dna_counts = {}
    for d in daily_metrics:
        for dna, count in d.get("dna_distribution", {}).items():
            dna_counts[dna] = dna_counts.get(dna, 0) + count

    total_dna = sum(dna_counts.values())
    if total_dna > 0 and dna_counts:
        dna_balance = len(dna_counts) / 5 * (1 - max(dna_counts.values()) / total_dna)
    else:
        dna_balance = 0

    correction_score = score_metric(
        corrections_per_session,
        THRESHOLDS["collaboration"]["corrections_per_session"],
        inverse=True,
    )
    dna_score = min(100, dna_balance * 150)

    # Emotion impact
    total_frustration = sum(d.get("frustration_count", 0) for d in daily_metrics)
    total_satisfaction = sum(d.get("satisfaction_count", 0) for d in daily_metrics)
    frustration_ratio = total_frustration / total_sessions if total_sessions > 0 else 0
    satisfaction_ratio = total_satisfaction / total_sessions if total_sessions > 0 else 0

    emotion_impact = 0
    if frustration_ratio > 0.3:
        emotion_impact = -15
    elif frustration_ratio > 0.1:
        emotion_impact = -5
    if satisfaction_ratio > 0.5:
        emotion_impact += 10
    elif satisfaction_ratio > 0.2:
        emotion_impact += 5

    base_score = correction_score * 0.5 + dna_score * 0.3 + 50 * 0.2
    score = max(0, min(100, base_score + emotion_impact))

    return {
        "score": round(score),
        "components": {
            "corrections_per_session": round(corrections_per_session, 2),
            "correction_score": round(correction_score),
            "dna_distribution": dna_counts,
            "dna_balance_score": round(dna_score),
            "frustration_ratio": round(frustration_ratio, 2),
            "satisfaction_ratio": round(satisfaction_ratio, 2),
            "emotion_impact": emotion_impact,
        },
    }


def score_growth(daily_metrics):
    """Score growth dimension (cross-session improvement)."""
    if not daily_metrics or len(daily_metrics) < 2:
        return {"score": 50, "components": {"reason": "insufficient_data"}}

    sorted_days = sorted(daily_metrics, key=lambda d: d.get("date", ""))
    mid = len(sorted_days) // 2
    first_half = sorted_days[:mid]
    second_half = sorted_days[mid:]

    first_corrections = sum(d.get("corrections_count", 0) for d in first_half)
    second_corrections = sum(d.get("corrections_count", 0) for d in second_half)

    if first_corrections > 0:
        correction_decay = (first_corrections - second_corrections) / first_corrections
    else:
        correction_decay = 0.5 if second_corrections == 0 else 0

    first_sessions = sum(d.get("sessions_count", 0) for d in first_half)
    second_sessions = sum(d.get("sessions_count", 0) for d in second_half)

    if first_sessions > 0:
        session_growth = (second_sessions - first_sessions) / first_sessions
    else:
        session_growth = 0

    decay_score = score_metric(correction_decay, THRESHOLDS["growth"]["correction_decay"])
    growth_score = score_metric(session_growth, THRESHOLDS["growth"]["session_growth"])

    score = decay_score * 0.6 + growth_score * 0.4

    return {
        "score": round(score),
        "components": {
            "correction_decay": round(correction_decay, 2),
            "decay_score": round(decay_score),
            "session_growth": round(session_growth, 2),
            "growth_score": round(growth_score),
        },
    }


def compute_health_score(daily_metrics):
    """Compute overall health score from daily aggregate data."""
    efficiency = score_efficiency(daily_metrics)
    quality = score_quality(daily_metrics)
    collaboration = score_collaboration(daily_metrics)
    growth = score_growth(daily_metrics)

    overall = (
        efficiency["score"] * 0.30
        + quality["score"] * 0.30
        + collaboration["score"] * 0.25
        + growth["score"] * 0.15
    )

    return {
        "overall_score": round(overall),
        "dimensions": {
            "efficiency": efficiency,
            "quality": quality,
            "collaboration": collaboration,
            "growth": growth,
        },
        "weights": {
            "efficiency": 0.30,
            "quality": 0.30,
            "collaboration": 0.25,
            "growth": 0.15,
        },
        "meta": {
            "days_analyzed": len(daily_metrics),
            "date_range": {
                "start": daily_metrics[0].get("date") if daily_metrics else None,
                "end": daily_metrics[-1].get("date") if daily_metrics else None,
            },
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="Compute health scores from daily aggregates"
    )
    parser.add_argument(
        "--input", required=True,
        help="JSON file with daily aggregates (from aggregate.py)",
    )
    parser.add_argument("--output", help="Output JSON file (default: stdout)")
    args = parser.parse_args()

    with open(args.input) as f:
        daily_metrics = json.load(f)

    if isinstance(daily_metrics, dict):
        daily_metrics = list(daily_metrics.values())

    result = compute_health_score(daily_metrics)

    output = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
    else:
        print(output)


if __name__ == "__main__":
    main()
