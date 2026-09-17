---
name: afk-install-plantuml
description: 安装本地 PlantUML 运行环境。当用户要求安装、准备或配置 PlantUML，或本地渲染 .puml、.plantuml 与 UML 图需要 Java、Graphviz 和 PlantUML JAR 时使用。
---

## 指令

按顺序执行以下原子脚本；任一脚本退出码非 0 时立即停止，并把它 stderr 里的 `[error]` 行原样报告给用户。

#### 1.探测环境（只读，不安装、不下载、不改文件）

```bash
python3 <AFK_PLUGIN_ROOT>/skills/afk-install-plantuml/scripts/check_env.py
```

- 输出三行状态：`[status] java=…`、`[status] graphviz=…`、`[status] plantuml_jar=…`。
- 退出码 0 表示环境已就绪，可直接结束，无需执行后续步骤。
- 后续步骤只对状态为 `no` 的项执行。

#### 2.安装 Java（仅当 `java=no`）

```bash
python3 <AFK_PLUGIN_ROOT>/skills/afk-install-plantuml/scripts/install_java.py
```

#### 3.安装 Graphviz（仅当 `graphviz=no`）

```bash
python3 <AFK_PLUGIN_ROOT>/skills/afk-install-plantuml/scripts/install_graphviz.py
```

#### 4.下载 PlantUML JAR（仅当 `plantuml_jar=no`）

```bash
python3 <AFK_PLUGIN_ROOT>/skills/afk-install-plantuml/scripts/install_plantuml.py
```

- jar 已存在时脚本自动跳过；需要强制重新下载时追加 `--force`。

#### 5.复核环境

```bash
python3 <AFK_PLUGIN_ROOT>/skills/afk-install-plantuml/scripts/check_env.py
```

- 只有退出码为 0 才能向用户报告"PlantUML 运行环境已就绪"。
- 该脚本内部即执行 `java -jar <jar> -version` 与 `dot -V` 两项校验。

补充说明：

- 若 `python3` 不可用，可用任意可用的 Python 解释器执行同一脚本。
- 所有脚本以退出码为结论：0 成功、1 失败；失败原因见 stderr 的 `[error] …` 行。
- 第 2、3、4 步的脚本都支持 `--dry-run`：只打印将要执行的安装命令或解析出的下载地址，不产生任何副作用。安装类操作需要管理员权限、或用户未明确同意安装软件时，应先用 `--dry-run` 预览并向用户确认，再实际执行。

## 约束

- 不得跳过第 1 步直接安装：探测是只读的，成本极低，且由它决定后面哪几步需要执行。
- 不得将 plantuml.jar 放到其它目录：目标路径固定为 `<AFK_PLUGIN_ROOT>/skills/afk-install-plantuml/assets/plantuml.jar`，即各脚本 `--assets-dir` 的默认值。
- 不得绕过 `install_plantuml.py` 自行用 curl / Invoke-WebRequest 下载 jar：该脚本采用"同目录临时文件 → 非空校验 → 移动落位"的原子写入。直接下载到目标路径一旦中断就会留下半个 jar，而后续运行会因"jar 已存在"永远跳过下载，环境无法自愈。
- 不得改写 jar 地址的选择逻辑：脚本优先解析官方下载页 `https://plantuml.com/download` 上的版本化 jar 链接（自动排除 `-sources.jar`、各 license 变体与 SNAPSHOT 包），仅在页面不可读或无匹配时回退到 `https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar`。
- 安装 Java 或 Graphviz 可能需要管理员权限、包管理器与网络访问；脚本只会尝试本机已存在的包管理器（Windows：winget / choco / scoop，macOS：brew，Linux：apt-get / dnf / yum / apk / pacman），全部失败时会给出手动安装提示。
- 若网络受代理或证书影响，脚本会以 `[error] URLError: … SSL …` 失败并返回 1；此时应向用户报告代理或根证书问题，而不是反复重试或改用其它下载方式。
