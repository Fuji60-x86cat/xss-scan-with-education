"""
ペイロードリスト管理モジュール (payload_manager.py)
payloads.json を読み込み、コンテキストごとのペイロード定義を管理する。
各ペイロードの {ID} は、送信のたびにランダムな識別子へ置き換える。
"""

import json
import random
import string
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


@dataclass
class PayloadDef:
    """payloads.json 1件分の定義"""
    context: str
    template: str
    required_chars: List[str] = field(default_factory=list)

    def render(self, identifier: str) -> str:
        """{ID} をランダム識別子に置き換えた実際の送信文字列を返す"""
        return self.template.replace("{ID}", identifier)


class PayloadManager:
    """コンテキスト別ペイロードの読み込みと選択を行う"""

    def __init__(self, payloads_path: str = "payloads.json"):
        self.payloads_path = payloads_path
        self.payloads: List[PayloadDef] = self._load(payloads_path)

    @staticmethod
    def _load(path: str) -> List[PayloadDef]:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"ペイロードファイルが見つかりません: {path}")
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)

        result = []
        for item in data:
            result.append(
                PayloadDef(
                    context=item["context"],
                    template=item["payload"],
                    required_chars=item.get("required_chars", []),
                )
            )
        return result

    def for_context(self, context: str) -> List[PayloadDef]:
        """指定したコンテキストに合うペイロードだけを返す"""
        return [p for p in self.payloads if p.context == context]

    @staticmethod
    def generate_identifier(prefix: str = "xss") -> str:
        """反射チェック用・各送信用の、推測不能なランダム識別子を生成する"""
        suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"{prefix}{suffix}"
