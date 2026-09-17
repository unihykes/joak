#!/usr/bin/env python3
"""检测 Java；缺失时按平台候选包管理器安装，安装后复检。支持 --dry-run 预览命令。"""

from __future__ import annotations

import _common as c

CANDIDATES: dict[str, list[list[str]]] = {
    "windows": [
        [
            "winget", "install", "--id", "EclipseAdoptium.Temurin.21.JRE", "--exact",
            "--accept-package-agreements", "--accept-source-agreements",
        ],
        ["choco", "install", "temurinjre", "-y"],
        ["scoop", "install", "temurin21-jre"],
    ],
    "darwin": [["brew", "install", "openjdk"]],
    "linux": [
        ["apt-get", "install", "-y", "default-jre"],
        ["dnf", "install", "-y", "java-21-openjdk"],
        ["yum", "install", "-y", "java-21-openjdk"],
        ["apk", "add", "openjdk21-jre"],
        ["pacman", "-S", "--noconfirm", "jre-openjdk"],
    ],
}


def main() -> int:
    return c.install_tool(
        ["java", "-version"], "[java]", "Java", CANDIDATES, c.parse_dry_run("检测并按需安装 Java（JRE 21）。")
    )


if __name__ == "__main__":
    raise SystemExit(c.cli(main))
