"""
反射位置・反射コンテキスト判定モジュール (context_detector.py)
レスポンスHTML本文の中から識別子（マーカー）が出現した位置をすべて探し、
各出現位置が HTML のどのような役割の場所（コンテキスト）かを判定する。

判定できるコンテキスト:
  - tag_between : タグとタグの間（テキスト部分）
  - attr_double  : 属性値の中（ダブルクォートで囲まれている）
  - attr_single  : 属性値の中（シングルクォートで囲まれている）
  - url_attr     : href/src/action などURL系属性の値の中
  - script       : <script> タグの中（文字列リテラル部分）
  - other_manual : コメントの中・タグ名/属性名など、自動判定の対象外（要手動確認）
"""

import re
from dataclasses import dataclass
from typing import List, Optional


URL_ATTR_NAMES = {"href", "src", "action", "formaction"}

# tag_prefix（タグ開始 "<" から判定したい位置までの文字列）の末尾が
# 「属性名 = "クォート開始後の文字列（まだ閉じていない）」になっているかを調べる
_ATTR_DOUBLE_OPEN_RE = re.compile(r'([a-zA-Z_:][-a-zA-Z0-9_:.]*)\s*=\s*"[^"]*$')
_ATTR_SINGLE_OPEN_RE = re.compile(r"([a-zA-Z_:][-a-zA-Z0-9_:.]*)\s*=\s*'[^']*$")


@dataclass
class Reflection:
    """1か所の反射（出現箇所）の情報"""
    position: int
    context: str
    attr_name: Optional[str] = None
    quote: Optional[str] = None


def find_identifier_positions(html_text: str, identifier: str) -> List[int]:
    """識別子がレスポンス本文中に出現する全位置（開始インデックス）を探す"""
    if not identifier:
        return []
    positions = []
    start = 0
    while True:
        idx = html_text.find(identifier, start)
        if idx == -1:
            break
        positions.append(idx)
        start = idx + 1
    return positions


def _in_script_block(html_text: str, pos: int) -> bool:
    """pos が <script> ... </script> の内側かどうかを調べる"""
    head = html_text[:pos].lower()
    last_open = head.rfind("<script")
    if last_open == -1:
        return False
    last_close = head.rfind("</script")
    return last_open > last_close


def _in_comment(html_text: str, pos: int) -> bool:
    """pos が <!-- ... --> コメントの内側かどうかを調べる"""
    head = html_text[:pos]
    last_open = head.rfind("<!--")
    if last_open == -1:
        return False
    last_close = head.rfind("-->")
    return last_open > last_close


def _find_enclosing_tag_start(html_text: str, pos: int) -> Optional[int]:
    """
    pos が「タグの定義部分（< から > まで）」の内側にいる場合、
    その開始位置（< の位置）を返す。内側でなければ None。
    """
    head = html_text[:pos]
    last_lt = head.rfind("<")
    if last_lt == -1:
        return None
    # 最後の "<" より後ろに ">" があれば、pos は既に閉じたタグの外側
    if ">" in html_text[last_lt:pos]:
        return None
    return last_lt


def _classify_within_tag(html_text: str, tag_start: int, pos: int) -> Reflection:
    """タグ定義の内側（tag_start から pos まで）にいる場合の詳細分類"""
    tag_prefix = html_text[tag_start:pos]

    m_double = _ATTR_DOUBLE_OPEN_RE.search(tag_prefix)
    m_single = _ATTR_SINGLE_OPEN_RE.search(tag_prefix)

    # ダブルクォートの開始が、シングルクォートの開始より後ろ（＝より内側）なら
    # ダブルクォート属性値の中にいると判断する
    if m_double and (not m_single or m_double.start() >= m_single.start()):
        attr_name = m_double.group(1).lower()
        if attr_name in URL_ATTR_NAMES:
            return Reflection(pos, "url_attr", attr_name=attr_name, quote='"')
        return Reflection(pos, "attr_double", attr_name=attr_name, quote='"')

    if m_single:
        attr_name = m_single.group(1).lower()
        if attr_name in URL_ATTR_NAMES:
            return Reflection(pos, "url_attr", attr_name=attr_name, quote="'")
        return Reflection(pos, "attr_single", attr_name=attr_name, quote="'")

    # どちらのクォートにも入っていない＝タグ名／属性名／値なし属性などの中
    return Reflection(pos, "other_manual")


def classify(html_text: str, pos: int) -> Reflection:
    """識別子の1出現位置について、コンテキストを判定する"""
    if _in_comment(html_text, pos):
        return Reflection(pos, "other_manual")

    if _in_script_block(html_text, pos):
        return Reflection(pos, "script")

    tag_start = _find_enclosing_tag_start(html_text, pos)
    if tag_start is not None:
        return _classify_within_tag(html_text, tag_start, pos)

    return Reflection(pos, "tag_between")


def detect_reflections(html_text: str, identifier: str) -> List[Reflection]:
    """識別子の全出現位置について反射コンテキストを判定して返す"""
    positions = find_identifier_positions(html_text, identifier)
    return [classify(html_text, p) for p in positions]
