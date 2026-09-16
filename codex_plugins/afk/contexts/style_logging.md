---
description: 日志宏调用规范
alwaysApply: true
---

## 指令(做什么)

在本工作区内**新建或修改 C++ 代码**时，所有日志调用必须符合日志宏规范。

## 日志宏规范

提供四个日志宏，按级别从低到高排列：

| 宏 | 级别 |
|---|---|
| `afk_debug` | DEBUG |
| `afk_info` | INFO |
| `afk_warn` | WARN |
| `afk_error` | ERROR |

### 调用格式

```cpp
afk_<level>("消息事件", var1, var2, var3);
```

- **第 1 个参数**（必填）：消息事件描述，必须是自然语句纯文本字符串。
  - 禁止使用任何格式化占位符（`{}`、`%s`、`%d` 等）。
  - 禁止手动拼接变量值到消息字符串中。
  - 消息应简要描述当前行为或场景。
  - 在极简情况下,消息事件可以是空字符串, 例如 afk_info("", var1, var2, var3);
- **第 2~N 个参数**（可选）：变量列表，宏会通过编译时反射自动将变量名以 JSON 格式输出到日志中。
  - 接受大部分原始类型（指针、字符串、数值、容器等），无需手动调用 `fmt::ptr()` 或类似转换。
  - 当参数为函数调用或表达式较长时，使用 `afk_named(别名, 表达式)` 为其命名，以精简日志输出。

- **日志输出示例**
```
[2099-09-06 12:09:00 300689 +08:00] [demo] [592272] [592272] [info] [demo.cpp:10] test() do something {"var1": 1, "var2": 2, "var3": 3}
```

### 日志调用示例

```cpp
// 正例 — 纯文本消息 + 变量列表
afk_info("update timestamp check", this, mUpdateTimestamp, mSwanUnitCreatePolling);

// 正例 — 包装长表达式
afk_error("init sam kv lun", afk_named(pool, getStorePoolInfo(storePoolInfo)), afk_named(error, e.toFullString()));

// 反例 — 消息中包含格式化占位符
afk_info("this[{}], mUpdateTimestamp[{}]", (void *)this, mUpdateTimestamp);

// 反例 — 手动拼接变量名到消息中
afk_info("handle request failed, id={}, retry={}", reqId, retryCount);

// 反例 — 使用 _T() 和 printf 风格
afk_error(_T("storePoolID[%s] not found."), storePoolID.c_str());
```
