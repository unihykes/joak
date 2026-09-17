#!/usr/bin/env python3
"""各原子脚本共用的探测、执行与退出码辅助。"""

from __future__ import annotations

import argparse
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable

ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets"
JAR_NAME = "plantuml.jar"


def run_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    """执行命令并回显，stderr 合并进 stdout 一并返回。"""
    print(f"[run] {' '.join(args)}", flush=True)
    return subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def command_available(command: str) -> bool:
    """命令是否可在 PATH 中找到。"""
    return shutil.which(command) is not None


def print_output(prefix: str, result: subprocess.CompletedProcess[str]) -> None:
    """原样打印命令输出，便于用户与 agent 排查。"""
    output = (result.stdout or "").strip()
    if output:
        print(f"{prefix}\n{output}", flush=True)


def probe(command: list[str], prefix: str) -> bool:
    """命令存在且返回码为 0 才算已安装（可识别 PATH 里有但已损坏的情况）。"""
    if not command_available(command[0]):
        return False
    result = run_command(command)
    print_output(prefix, result)
    return result.returncode == 0


def install_with_candidates(candidates: list[list[str]], label: str) -> bool:
    """按顺序尝试本机已存在的包管理器命令，任一成功即返回 True。"""
    attempted: list[str] = []
    for command in candidates:
        if not command_available(command[0]):
            continue
        attempted.append(" ".join(command))
        result = run_command(command)
        print_output(f"[{label} installer]", result)
        if result.returncode == 0:
            print(f"[ok] {label} 安装成功", flush=True)
            return True

    if attempted:
        fail(f"{label} 安装失败；已尝试: {' | '.join(attempted)}")
    else:
        fail(f"未找到可用于安装 {label} 的包管理器，请手动安装")
    return False


def fail(message: str) -> int:
    """输出错误到 stderr 并返回退出码 1。"""
    print(f"[error] {message}", file=sys.stderr, flush=True)
    return 1


def cli(main_fn: Callable[[], int]) -> int:
    """统一入口包装：把未捕获异常转成 [error] 输出与退出码 1。"""
    try:
        return main_fn()
    except Exception as exc:
        return fail(f"{type(exc).__name__}: {exc}")


def platform_candidates(table: dict[str, list[list[str]]]) -> list[list[str]]:
    """按当前平台取候选安装命令；未知平台回退到 linux 列表。"""
    return table.get(platform.system().lower(), table["linux"])


def parse_dry_run(description: str) -> bool:
    """解析 --dry-run 开关：只列出将要尝试的命令，不产生任何副作用。"""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只列出将要尝试的安装命令，不实际执行。",
    )
    return parser.parse_args().dry_run


def install_tool(
    probe_command: list[str],
    probe_prefix: str,
    label: str,
    table: dict[str, list[list[str]]],
    dry_run: bool = False,
) -> int:
    """通用的"探测 → 按需安装 → 复检"流程，返回进程退出码。"""
    if probe(probe_command, probe_prefix):
        print(f"[skip] {label} 已安装", flush=True)
        return 0

    candidates = platform_candidates(table)
    if dry_run:
        print(f"[dry-run] {label} 缺失；将按顺序尝试以下命令：", flush=True)
        for command in candidates:
            mark = "" if command_available(command[0]) else "   (包管理器不存在，会跳过)"
            print(f"[dry-run]   {' '.join(command)}{mark}", flush=True)
        return 0

    if not install_with_candidates(candidates, label):
        return 1
    if not probe(probe_command, probe_prefix):
        return fail(f"安装后 {label} 仍不可用")
    return 0
