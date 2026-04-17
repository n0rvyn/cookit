---
name: minimax-coding-plan
description: "查询 MiniMax coding plan 剩余额度。Triggered by: check MiniMax quota, remains, usage, 额度。"
allowed-tools: Bash
---

# MiniMax Coding Plan

```bash
curl -s --location 'https://www.minimaxi.com/v1/token_plan/remains' \
  --header 'Authorization: Bearer '$MINIMAX_API_KEY \
  | jq -r '
    def pad2: tostring | if length < 2 then "0" + . else . end;
    def fmt_remains:
      ( . / 1000 | floor ) as $s |
      [ ($s / 3600 | floor | tostring | pad2),
        (($s % 3600) / 60 | floor | tostring | pad2),
        ($s % 60 | tostring | pad2) ] | join(":");
    def to_shanghai:
      ( . / 1000 | floor ) as $ts |
      ( $ts + 8 * 3600 ) |
      strftime("%m-%d %H:%M");
    .model_remains | sort_by(.model_name) |
    "| 模型 | 当次区间用量 | 当周用量 | 区间重置于 | 剩余时间 |",
    "|------|------------|----------|------------|----------|",
    (foreach .[] as $r (.; .; $r
      | "| \($r.model_name) |"
        + " \($r.current_interval_usage_count)/\($r.current_interval_total_count) |"
        + " \($r.current_weekly_usage_count)/\($r.current_weekly_total_count) |"
        + " \($r.end_time | to_shanghai) |"
        + " \($r.remains_time | fmt_remains) |"))'
```

输出示例：

| 模型 | 当次区间用量 | 当周用量 | 区间重置于 | 剩余时间 |
|------|------------|----------|------------|----------|
| MiniMax-M* | 629/4500 | 34460/45000 | 04-17 10:00 | 00:12:35 |
| speech-hd | 1788/19000 | 45561/133000 | 04-18 00:00 | 14:12:35 |
| ... | ... | ... | ... | ... |

`MINIMAX_API_KEY` 必填，从 platform.minimaxi.com 获取。
