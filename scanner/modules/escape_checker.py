"""
エスケープ判定モジュール (escape_checker.py)
送信したペイロードに含まれる特殊文字（required_chars）が、レスポンス内で
そのまま出ているか（未変換）、文字参照に変換されているか（変換済み）を
識別子の周辺テキストから文字ごとに判定する。
"""

from dataclasses import dataclass, field
from typing import List


# 特殊文字ごとの代表的なHTMLエンティティ表記
_ENTITY_VARIANTS = {
    "<": ["&lt;"],
    ">": ["&gt;"],
    '"': ["&quot;", "&#34;", "&#x22;"],
    "'": ["&#39;", "&#x27;", "&apos;"],
}

WINDOW_RADIUS = 80


@dataclass
class EscapeResult:
    unescaped_chars: List[str] = field(default_factory=list)
    escaped_chars: List[str] = field(default_factory=list)
    removed_chars: List[str] = field(default_factory=list)  # 文字ごと除去された


def _window_around(text: str, pos: int, length: int) -> str:
    start = max(0, pos - WINDOW_RADIUS)
    end = min(len(text), pos + length + WINDOW_RADIUS)
    return text[start:end]


def check_escaping(response_text: str, identifier: str, required_chars: List[str]) -> EscapeResult:
    """
    識別子の周辺を切り出し、required_chars の各文字が未変換/変換済み/除去のいずれかを判定する。
    ':' のようにHTMLエンティティを持たない文字は url_attr 用の専用チェックで扱うため、ここでは対象外。
    """
    result = EscapeResult()

    idx = response_text.find(identifier)
    if idx == -1:
        # 識別子自体が見つからない＝この送信分は反射なし（別途ハンドリング）
        return result

    window = _window_around(response_text, idx, len(identifier))

    for c in required_chars:
        if c not in _ENTITY_VARIANTS:
            # ':' など、エンティティ判定の対象外文字はここでは評価しない
            continue

        entity_variants = _ENTITY_VARIANTS[c]
        # エンティティ表記を取り除いた残りの文字列で、生の文字が残っているか調べる
        stripped = window
        entity_hit = False
        for e in entity_variants:
            if e in stripped:
                entity_hit = True
                stripped = stripped.replace(e, "")

        raw_hit = c in stripped

        if raw_hit:
            result.unescaped_chars.append(c)
        elif entity_hit:
            result.escaped_chars.append(c)
        else:
            result.removed_chars.append(c)

    return result
