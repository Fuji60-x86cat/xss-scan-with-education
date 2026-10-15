#!/usr/bin/env python3
"""
xss_scanner.py
反射型XSS脆弱性診断を自動化するスクリプト（チームB計画書 準拠）

指定したURLとパラメータに対して、
  1) 識別子を送って反射位置を探す
  2) 反射位置のコンテキスト（タグの間/属性値の中/script内/URL属性）を判定する
  3) コンテキストに合うペイロードだけを選んで送信する
  4) 特殊文字が変換されたか（エスケープ判定）と、
     実際にタグ/属性/スクリプトとして構文上成立するか（実行可能性の判定）を調べる
  5) 結果を result.csv に判定理由つきで出力する
"""

import argparse
import sys
import time
import urllib.parse
from typing import List, Optional
from urllib.parse import urlparse

from modules.context_detector import Reflection, detect_reflections
from modules.escape_checker import check_escaping
from modules.exploit_checker import exploit_success_for_context
from modules.logger_config import setup_logger
from modules.models import ScanItemResult, Verdict
from modules.payload_manager import PayloadManager
from modules.reporter import export_csv, print_summary
from modules.requester import HTTPResponseData, XSSRequester

LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="反射型XSSの脆弱性診断を自動化するスクリプト",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python xss_scanner.py --url http://localhost/xss-lab/tag_vuln.php --param keyword
  python xss_scanner.py --url http://localhost/xss-lab/post_vuln.php --param comment --method POST
        """,
    )
    parser.add_argument("--url", required=True, help="[必須] 診断対象のURL")
    parser.add_argument("--param", required=True, help="[必須] 診断対象のパラメータ名")
    parser.add_argument("--method", choices=["GET", "POST"], default="GET", help="HTTPメソッド (既定: GET)")
    parser.add_argument("--payloads", default="payloads.json", help="ペイロードファイル (既定: payloads.json)")
    parser.add_argument("--output", default="result.csv", help="結果CSVの出力先 (既定: result.csv)")
    parser.add_argument("--delay", type=float, default=0.0, help="各送信間の待機秒数 (既定: 0.0)")
    parser.add_argument("--timeout", type=float, default=5.0, help="タイムアウト秒数 (既定: 5.0)")
    parser.add_argument("--log-file", default="xss_scanner.log", help="ログ出力先 (既定: xss_scanner.log)")
    parser.add_argument("--yes", action="store_true", help="自分が管理する環境である確認プロンプトを省略する")
    return parser.parse_args()


def confirm_authorized_target(url: str, assume_yes: bool) -> bool:
    """対象がlocalhost以外の場合、許可を得た環境であることの確認を行う"""
    host = urlparse(url).hostname or ""
    if host.lower() in LOCAL_HOSTS:
        return True
    if assume_yes:
        return True
    print(f"[!] 対象ホスト '{host}' はローカル環境ではありません。")
    print("    このツールは、自分が管理する環境・許可を得た環境でのみ使用してください。")
    answer = input("    許可を得た環境であることを確認しましたか？ (yes/no): ").strip().lower()
    return answer in ("yes", "y")


def send_baseline(requester: XSSRequester, url: str, method: str, param: str) -> HTTPResponseData:
    """通常の値を送って、通常時の応答（ベースライン）を取得する"""
    return requester.send(url, method, param, "test")


def main() -> None:
    args = parse_arguments()
    logger = setup_logger(log_file=args.log_file)

    # --- 入力検証 ---
    if not (args.url.startswith("http://") or args.url.startswith("https://")):
        print("[エラー] --url は http:// または https:// で始まる必要があります。", file=sys.stderr)
        sys.exit(1)

    if not confirm_authorized_target(args.url, args.yes):
        print("[中止] 許可が確認できなかったため終了します。")
        sys.exit(1)

    print(f"[*] 対象: {args.url}  ({args.method}, param={args.param})")
    logger.info(f"スキャン開始 url={args.url} method={args.method} param={args.param}")

    requester = XSSRequester(logger=logger, timeout=args.timeout)

    # --- ベースライン取得 ---
    baseline = send_baseline(requester, args.url, args.method, args.param)
    if baseline.error:
        print(f"[エラー] 対象への接続に失敗しました: {baseline.error}", file=sys.stderr)
        sys.exit(1)
    print(f"[+] 接続成功 (HTTP {baseline.status_code}, {baseline.response_time_ms:.1f}ms)")

    try:
        payload_manager = PayloadManager(args.payloads)
    except FileNotFoundError as e:
        print(f"[エラー] {e}", file=sys.stderr)
        sys.exit(1)

    results: List[ScanItemResult] = []

    # --- ① 反射チェック：ランダムな識別子を送る ---
    reflect_identifier = PayloadManager.generate_identifier(prefix="xssr")
    reflect_resp = requester.send(args.url, args.method, args.param, reflect_identifier)
    if args.delay > 0:
        time.sleep(args.delay)

    if reflect_resp.error:
        results.append(
            ScanItemResult(
                url=args.url, param=args.param, method=args.method, context="",
                payload=reflect_identifier, unescaped_chars="",
                verdict=Verdict.MANUAL_CHECK,
                reason=f"通信エラーのため判定できません: {reflect_resp.error}",
            )
        )
        print_summary(results, args.output)
        export_csv(results, args.output)
        return

    reflections: List[Reflection] = detect_reflections(reflect_resp.text, reflect_identifier)

    if not reflections:
        print(f"[*] 反射チェック: 識別子 {reflect_identifier} は反射しませんでした")
        results.append(
            ScanItemResult(
                url=args.url, param=args.param, method=args.method, context="",
                payload=reflect_identifier, unescaped_chars="",
                verdict=Verdict.NOT_REFLECTED,
                reason="識別子がレスポンス本文に出現しませんでした。",
            )
        )
        path = export_csv(results, args.output)
        print_summary(results, path)
        return

    contexts_found = sorted({r.context for r in reflections})
    print(f"[*] 反射チェック: 識別子 {reflect_identifier} を送信 -> {len(reflections)} か所に反射 ({', '.join(contexts_found)})")

    # --- 要手動確認コンテキストの記録 ---
    if "other_manual" in contexts_found:
        results.append(
            ScanItemResult(
                url=args.url, param=args.param, method=args.method, context="other_manual",
                payload=reflect_identifier, unescaped_chars="",
                verdict=Verdict.MANUAL_CHECK,
                reason="コメントの中・タグ名/属性名など、自動判定の対象外の反射位置です。目視で確認してください。",
            )
        )

    # --- ② コンテキストに合うペイロードを選んで送信・判定 ---
    automatable_contexts = [c for c in contexts_found if c != "other_manual"]

    for context in automatable_contexts:
        payload_defs = payload_manager.for_context(context)
        if not payload_defs:
            continue

        for payload_def in payload_defs:
            identifier = PayloadManager.generate_identifier(prefix="xss")
            rendered = payload_def.render(identifier)

            resp = requester.send(args.url, args.method, args.param, rendered)
            if args.delay > 0:
                time.sleep(args.delay)

            if resp.error:
                results.append(
                    ScanItemResult(
                        url=args.url, param=args.param, method=args.method, context=context,
                        payload=rendered, unescaped_chars="",
                        verdict=Verdict.MANUAL_CHECK,
                        reason=f"通信エラーのため判定できません: {resp.error}",
                    )
                )
                continue

            if identifier not in resp.text:
                results.append(
                    ScanItemResult(
                        url=args.url, param=args.param, method=args.method, context=context,
                        payload=rendered, unescaped_chars="",
                        verdict=Verdict.SANITIZED,
                        reason="識別子ごと入力が除去/無視され、反射しませんでした。",
                    )
                )
                print(f"  [+対策済み] {context:<12} {payload_def.template}")
                continue

            escape_result = check_escaping(resp.text, identifier, payload_def.required_chars)
            exploit_ok = exploit_success_for_context(context, resp.text, identifier)

            if context == "url_attr":
                unescaped = [":"] if exploit_ok else []
            else:
                unescaped = escape_result.unescaped_chars

            if exploit_ok is True and unescaped:
                verdict = Verdict.VULNERABLE
                reason = (
                    f"{','.join(unescaped)} が未変換で、{context} コンテキストで"
                    "実行されうる構造（属性/要素）が成立しています。"
                )
                indicator = "[!疑いあり]"
            elif exploit_ok is False or not unescaped:
                verdict = Verdict.SANITIZED
                reason = "必要な文字が変換または除去され、実行されうる構造が成立していません。"
                indicator = "[+対策済み]"
            else:
                verdict = Verdict.MANUAL_CHECK
                reason = "実行可能性を自動確認できませんでした。目視で確認してください。"
                indicator = "[?要確認 ]"

            print(f"  {indicator} {context:<12} {payload_def.template}")

            results.append(
                ScanItemResult(
                    url=args.url,
                    param=args.param,
                    method=args.method,
                    context=context,
                    payload=rendered,
                    unescaped_chars=",".join(unescaped),
                    verdict=verdict,
                    reason=reason,
                )
            )

    saved_path = export_csv(results, args.output)
    print_summary(results, saved_path)
    logger.info(f"スキャン完了。総送信数: {len(results)}, CSV出力: {saved_path}")


if __name__ == "__main__":
    main()
