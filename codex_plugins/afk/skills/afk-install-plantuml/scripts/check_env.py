#!/usr/bin/env python3
"""探测 Java、Graphviz 与 plantuml.jar 是否就绪；全部就绪返回 0，否则返回 1。

只读脚本：不安装、不下载、不修改任何文件。
"""

from __future__ import annotations

import argparse
from pathlib import Path

import _common as c


def main() -> int:
    parser = argparse.ArgumentParser(description="探测 PlantUML 运行环境是否就绪。")
    parser.add_argument(
        "--assets-dir",
        type=Path,
        default=c.ASSETS_DIR,
        help="plantuml.jar 所在目录（默认取本技能的 assets 目录）。",
    )
    args = parser.parse_args()

    jar_path = args.assets_dir / c.JAR_NAME
    has_java = c.probe(["java", "-version"], "[java]")
    has_graphviz = c.probe(["dot", "-V"], "[graphviz]")
    print(f"[status] java={'yes' if has_java else 'no'}", flush=True)
    print(f"[status] graphviz={'yes' if has_graphviz else 'no'}", flush=True)
    print(f"[status] plantuml_jar={'yes' if jar_path.exists() else 'no'} {jar_path}", flush=True)

    if not jar_path.exists():
        return c.fail(f"缺少 plantuml.jar: {jar_path}，请执行 install_plantuml.py")

    if has_java:
        result = c.run_command(["java", "-jar", str(jar_path), "-version"])
        c.print_output("[plantuml]", result)
        if result.returncode != 0:
            return c.fail("plantuml.jar 校验失败")
    else:
        print("[warn] 缺少 Java，已跳过 plantuml.jar 校验", flush=True)

    missing = [name for name, ok in (("Java", has_java), ("Graphviz", has_graphviz)) if not ok]
    if missing:
        return c.fail("仍缺少: " + ", ".join(missing))

    print("[ok] PlantUML 运行环境已就绪", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(c.cli(main))
