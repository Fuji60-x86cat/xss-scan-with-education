"""
通信ログ・システムログ記録モジュール (logger_config.py)
送信したペイロード、HTTPステータスコード、応答時間などを
logging モジュールでファイルおよびコンソールに時系列で記録する。
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(
    log_file: Optional[str] = "xss_scanner.log",
    verbose: bool = False,
    logger_name: str = "XSS_Scanner",
) -> logging.Logger:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    if logger.hasHandlers():
        logger.handlers.clear()

    file_formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)-7s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_formatter = logging.Formatter("[%(levelname)-7s] %(message)s")

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if verbose else logging.WARNING)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    if log_file:
        try:
            log_path = Path(log_file)
            if log_path.parent != Path("."):
                log_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_path, encoding="utf-8", mode="a")
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        except OSError as e:
            logger.warning(f"ログファイル '{log_file}' の作成に失敗しました: {e}")

    return logger
