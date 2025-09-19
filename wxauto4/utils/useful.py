"""实用的授权相关命令行工具。"""

from __future__ import annotations

import json
import platform
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

ENCODING = "utf-8"
LICENSE_DIR = Path.home() / ".wxauto4"
LICENSE_FILE = LICENSE_DIR / "license.json"
REQUEST_FILE = LICENSE_DIR / "license_request.json"
DEBUG_REQUEST_FILE = LICENSE_DIR / "license_request.debug.json"


def _ensure_dir() -> None:
    LICENSE_DIR.mkdir(parents=True, exist_ok=True)


def _machine_fingerprint() -> Dict[str, Any]:
    uname = platform.uname()
    return {
        "system": uname.system,
        "node": uname.node,
        "release": uname.release,
        "version": uname.version,
        "machine": uname.machine,
        "processor": uname.processor,
        "mac": f"{uuid.getnode():012x}",
    }


def _write_json(path: Path, data: Dict[str, Any]) -> None:
    _ensure_dir()
    payload = {
        **data,
        "generated_at": datetime.utcnow().isoformat(timespec="seconds"),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding=ENCODING)
    print(f"已生成文件: {path}")


def authenticate(code: str) -> None:
    """使用授权码写入授权文件。"""

    if not code:
        raise ValueError("授权码不能为空")

    payload = {
        "license_code": code.strip(),
        "machine": _machine_fingerprint(),
    }
    _write_json(LICENSE_FILE, payload)
    print("授权信息已写入，重启程序后生效。")


def authenticate_with_file(path: str) -> None:
    """从授权文件导入授权信息。"""

    file_path = Path(path).expanduser()
    if not file_path.exists():
        raise FileNotFoundError(f"未找到授权文件: {file_path}")

    text = file_path.read_text(encoding=ENCODING).strip()
    try:
        data = json.loads(text)
        code = data.get("license_code") or data.get("code")
    except json.JSONDecodeError:
        data = {}
        code = text

    if not code:
        raise ValueError("授权文件中没有找到授权码")

    payload: Dict[str, Any] = {
        "license_code": str(code).strip(),
        "machine": _machine_fingerprint(),
    }
    payload.update({k: v for k, v in data.items() if k not in payload})
    _write_json(LICENSE_FILE, payload)
    print("已从授权文件导入授权信息。")


def get_licence_file() -> None:
    """导出授权申请文件，便于提交管理员授权。"""

    payload = {
        "machine": _machine_fingerprint(),
        "type": "request",
    }
    _write_json(REQUEST_FILE, payload)
    print("请将该文件发送给管理员完成授权。")


def debug_license() -> None:
    """导出调试用授权文件。"""

    payload = {
        "machine": _machine_fingerprint(),
        "type": "debug_request",
    }
    _write_json(DEBUG_REQUEST_FILE, payload)
    print("已生成调试授权文件。")


__all__ = [
    "authenticate",
    "authenticate_with_file",
    "get_licence_file",
    "debug_license",
]
