#!/usr/bin/env python3
"""检测 Graphviz；缺失时按平台候选包管理器安装，安装后复检。支持 --dry-run 预览命令。"""

from __future__ import annotations

import _common as c

CANDIDATES: dict[str, list[list[str]]] = {
    "windows": [
        [
            "winget", "install", "--id", "Graphviz.Graphviz", "--exact",
            "--accept-package-agreements", "--accept-source-agreements",
        ],
        ["choco", "install", "graphviz", "-y"],
        ["scoop", "install", "graphviz"],
    ],
    "darwin": [["brew", "install", "graphviz"]],
    "linux": [
        ["apt-get", "install", "-y", "graphviz"],
        ["dnf", "install", "-y", "graphviz"],
        ["yum", "install", "-y", "graphviz"],
        ["apk", "add", "graphviz"],
        ["pacman", "-S", "--noconfirm", "graphviz"],
    ],
}


def main() -> int:
    return c.install_tool(
        ["dot", "-V"], "[graphviz]", "Graphviz", CANDIDATES, c.parse_dry_run("检测并按需安装 Graphviz（dot）。")
    )


if __name__ == "__main__":
    raise SystemExit(c.cli(main))
