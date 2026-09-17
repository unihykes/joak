#!/usr/bin/env python3
"""下载最新 PlantUML jar 到 assets 目录（原子写入），并在 Java 可用时校验。"""

from __future__ import annotations

import argparse
import re
import shutil
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

import _common as c

OFFICIAL_DOWNLOAD_PAGE = "https://plantuml.com/download"
FALLBACK_LATEST_JAR_URL = "https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar"
USER_AGENT = "afk-install-plantuml/1.0"
PAGE_TIMEOUT = 60
DOWNLOAD_TIMEOUT = 300
JAR_PATTERNS = (
    r"https://github\.com/plantuml/plantuml/releases/download/v[0-9.]+/plantuml-[0-9.]+\.jar",
    r"https://github\.com/plantuml/plantuml/releases/latest/download/plantuml\.jar",
)


def read_url(url: str, timeout: int) -> str:
    """读取 URL 文本内容。"""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def resolve_latest_jar_url() -> str:
    """从官方下载页解析版本化 jar 地址；页面不可读或无匹配时回退到 GitHub latest。"""
    try:
        html = read_url(OFFICIAL_DOWNLOAD_PAGE, PAGE_TIMEOUT)
    except (urllib.error.URLError, OSError, ValueError) as exc:
        print(f"[warn] 读取官方下载页失败: {exc}", flush=True)
        return FALLBACK_LATEST_JAR_URL

    for pattern in JAR_PATTERNS:
        matches = re.findall(pattern, html)
        if matches:
            return matches[0]

    print("[warn] 官方页面未暴露 jar 链接，回退到 GitHub latest", flush=True)
    return FALLBACK_LATEST_JAR_URL


def download_atomic(url: str, target: Path) -> None:
    """先写同目录临时文件，校验非空后再移动落位，避免中断留下半个 jar。"""
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jar", dir=str(target.parent)) as tmp_file:
        tmp_path = Path(tmp_file.name)
    try:
        print(f"[download] {url}", flush=True)
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=DOWNLOAD_TIMEOUT) as response:
            with tmp_path.open("wb") as output:
                shutil.copyfileobj(response, output)
        if tmp_path.stat().st_size <= 0:
            raise RuntimeError("下载得到的 jar 为空")
        shutil.move(str(tmp_path), str(target))
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError as exc:
            print(f"[warn] 临时文件清理失败: {tmp_path} ({exc})", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="下载最新 PlantUML jar 到 assets 目录。")
    parser.add_argument(
        "--assets-dir",
        type=Path,
        default=c.ASSETS_DIR,
        help="plantuml.jar 的存放目录（默认取本技能的 assets 目录）。",
    )
    parser.add_argument("--force", action="store_true", help="即使 jar 已存在也重新下载。")
    parser.add_argument("--dry-run", action="store_true", help="只解析并打印将要下载的地址，不实际下载。")
    args = parser.parse_args()

    jar_path = args.assets_dir / c.JAR_NAME
    if args.dry_run:
        print(f"[dry-run] 目标路径: {jar_path}", flush=True)
        print(f"[dry-run] 已存在: {'yes' if jar_path.exists() else 'no'}", flush=True)
        print(f"[dry-run] 下载地址: {resolve_latest_jar_url()}", flush=True)
        return 0

    if jar_path.exists() and not args.force:
        print(f"[skip] plantuml.jar 已存在于 {jar_path}", flush=True)
    else:
        download_atomic(resolve_latest_jar_url(), jar_path)
        print(f"[ok] plantuml.jar 已安装到 {jar_path}", flush=True)

    if c.command_available("java"):
        result = c.run_command(["java", "-jar", str(jar_path), "-version"])
        c.print_output("[plantuml]", result)
        if result.returncode != 0:
            return c.fail("plantuml.jar 校验失败")
    else:
        print("[warn] 缺少 Java，已跳过 plantuml.jar 校验", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(c.cli(main))
