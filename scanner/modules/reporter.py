"""
診断結果出力モジュール (reporter.py)
送信ごとの判定結果を、画面には件数サマリーを表示し、
result.csv にはPDF仕様の列構成（url, param, method, context, payload,
unescaped_chars, verdict, reason）で1行ずつ出力する。
文字コードは Excel 互換の UTF-8（BOM付き）とする。
"""

import csv
from pathlib import Path
from typing import List

from modules.models import ScanItemResult, Verdict

FIELDNAMES = [
    "url",
    "param",
    "method",
    "context",
    "payload",
    "unescaped_chars",
    "verdict",
    "reason",
]


def print_summary(results: List[ScanItemResult], csv_path: str) -> None:
    """画面に判定ごとの件数サマリーを表示する"""
    counts = {v: 0 for v in Verdict}
    for r in results:
        counts[r.verdict] += 1

    print("\n" + "=" * 70)
    print("[*] 診断結果サマリー")
    print(
        f"    反射型XSSの疑いあり: {counts[Verdict.VULNERABLE]} 件 / "
        f"対策済み: {counts[Verdict.SANITIZED]} 件 / "
        f"反射なし: {counts[Verdict.NOT_REFLECTED]} 件 / "
        f"要手動確認: {counts[Verdict.MANUAL_CHECK]} 件"
    )
    print(f"[*] 詳細を {csv_path} に出力しました")
    print("=" * 70)

    if counts[Verdict.VULNERABLE] > 0:
        print(f"[!] 疑いあり {counts[Verdict.VULNERABLE]} 件あり。result.csv の reason 列を確認してください。")


def export_csv(results: List[ScanItemResult], output_path: str) -> str:
    """診断結果をCSV（UTF-8 with BOM）に出力する"""
    path = Path(output_path)
    if path.parent != Path("."):
        path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for r in results:
            writer.writerow(
                {
                    "url": r.url,
                    "param": r.param,
                    "method": r.method,
                    "context": r.context,
                    "payload": r.payload,
                    "unescaped_chars": r.unescaped_chars,
                    "verdict": r.verdict.value,
                    "reason": r.reason,
                }
            )

    return str(path.resolve())
