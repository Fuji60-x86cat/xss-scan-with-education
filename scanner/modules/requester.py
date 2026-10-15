"""
通信処理モジュール (requester.py)
対象URL・パラメータへの GET/POST リクエスト送信と、
応答時間・ステータスコードの計測を行う。
"""

import time
from dataclasses import dataclass, field
from logging import Logger
from typing import Dict, Optional
import requests


@dataclass
class HTTPResponseData:
    """HTTPレスポンスの計測データ"""
    url: str
    method: str
    status_code: int
    response_time_ms: float
    text: str
    headers: Dict[str, str] = field(default_factory=dict)
    error: Optional[str] = None
    content_type: str = ""


class XSSRequester:
    """HTTP通信を統括するクラス"""

    DEFAULT_USER_AGENT = "SimpleXSSScanner/2.0 (Authorized Local Security Testing)"

    def __init__(self, logger: Optional[Logger] = None, timeout: float = 5.0):
        self.logger = logger
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.DEFAULT_USER_AGENT})

    def send(self, url: str, method: str, param_name: str, value: str) -> HTTPResponseData:
        """指定パラメータに値を1つ入れてリクエストを送信する"""
        method_upper = method.upper()
        start = time.perf_counter()

        if self.logger:
            self.logger.debug(f"送信: [{method_upper}] {url} {param_name}={value!r}")

        try:
            if method_upper == "GET":
                resp = self.session.get(
                    url, params={param_name: value}, timeout=self.timeout
                )
            else:
                resp = self.session.post(
                    url, data={param_name: value}, timeout=self.timeout
                )
            duration_ms = (time.perf_counter() - start) * 1000.0
            return HTTPResponseData(
                url=resp.url,
                method=method_upper,
                status_code=resp.status_code,
                response_time_ms=duration_ms,
                text=resp.text,
                headers=dict(resp.headers),
                content_type=resp.headers.get("Content-Type", ""),
            )
        except requests.exceptions.Timeout:
            duration_ms = (time.perf_counter() - start) * 1000.0
            msg = f"タイムアウト（{self.timeout}秒超過）"
            if self.logger:
                self.logger.error(f"通信失敗: {url} - {msg}")
            return HTTPResponseData(
                url=url, method=method_upper, status_code=0,
                response_time_ms=duration_ms, text="", error=msg,
            )
        except requests.exceptions.RequestException as e:
            duration_ms = (time.perf_counter() - start) * 1000.0
            msg = f"接続エラー: {e}"
            if self.logger:
                self.logger.error(f"通信失敗: {url} - {msg}")
            return HTTPResponseData(
                url=url, method=method_upper, status_code=0,
                response_time_ms=duration_ms, text="", error=msg,
            )
