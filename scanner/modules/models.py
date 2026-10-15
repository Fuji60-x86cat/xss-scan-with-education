"""
共通データ構造モジュール (models.py)
判定結果の区分（Verdict）と、1件の診断結果（ScanItemResult）を定義する。
"""

from dataclasses import dataclass
from enum import Enum


class Verdict(Enum):
    NOT_REFLECTED = "反射なし"
    VULNERABLE = "反射型XSSの疑いあり"
    SANITIZED = "対策済み"
    MANUAL_CHECK = "要手動確認"


@dataclass
class ScanItemResult:
    """送信1件分の診断結果"""
    url: str
    param: str
    method: str
    context: str
    payload: str
    unescaped_chars: str
    verdict: Verdict
    reason: str
