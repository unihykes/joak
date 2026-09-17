#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import platform
import shlex
import sys
from pathlib import Path


def parse_options(options: str) -> str:
    try:
        data = json.loads(options)
    except json.JSONDecodeError as e:
        raise ValueError(f"--options 必须为 skill_prerun.py 返回的 JSON：{e}") from e

    if not isinstance(data, dict):
        raise ValueError("--options 必须为 JSON 对象")

    log_path = data.get("log_path")
    if not isinstance(log_path, str) or not log_path:
        raise ValueError("--options JSON 中必须包含非空字符串字段 log_path")

    return log_path


def detect_platform() -> str:
    machine = platform.machine().strip().lower()
    if machine in ("aarch64", "arm64") or machine.startswith("arm"):
        return "Linux_el7a3_aarcj64"
    if machine in ("x86_64", "amd64", "i386", "i686", "x86") or "x86" in machine:
        return "Linux_el7a3_x64"

    raise ValueError(f"不支持的 CPU 架构：{platform.machine()!r}")


def generate_command(kind: str, module: str) -> list[str]:
    """生成待执行命令。"""
    bt = kind.strip().lower()
    if bt not in ("debug", "release"):
        raise ValueError(f"--kind 须为 debug 或 release，收到: {kind!r}")

    if module and Path(module).is_absolute():
        raise ValueError("仅支持项目内相对路径（不得为绝对路径）")

    project_root = Path.cwd().resolve()
    build_platform = detect_platform()
    script = (
        "set -eo pipefail && "
        f'ABPLATFORM="{build_platform}" && '
        f"PROJECT_ROOT={shlex.quote(str(project_root))} && "
        f"MODULE_PATH={shlex.quote(module)} && "
        f"cd {shlex.quote(str(project_root / 'cmake'))} && "
        "source ./abenv.sh && "
        'if [ -n "$MODULE_PATH" ]; then cd "$PROJECT_ROOT/$MODULE_PATH"; fi && '
        f"makec.sh -j8 {bt}"
    )
    return ["bash", "-lc", script]


def main() -> int:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "common"))
    from skill_run import skill_run  # noqa: PLC0415 — 需在补全 import 路径之后（``skills/common``）

    parser = argparse.ArgumentParser(description="C++ 代码构建")
    parser.add_argument(
        "--module",
        default="",
        help="项目内相对路径（可选；为空表示编译所有模块；不得为绝对路径）",
    )
    parser.add_argument(
        "--kind",
        dest="kind",
        default="debug",
        metavar="debug|release",
        help="debug 或 release（忽略大小写；默认 debug）",
    )
    parser.add_argument(
        "--options",
        required=True,
        help="由 skill_prerun.py 返回的 JSON 信息",
    )
    args = parser.parse_args()

    try:
        log_path = parse_options(args.options)
        command = generate_command(args.kind, args.module)
    except ValueError as e:
        sys.stderr.write(f"{e}\n")
        return 1

    return skill_run(Path(__file__).stem, command, log_path)


if __name__ == "__main__":
    raise SystemExit(main())
