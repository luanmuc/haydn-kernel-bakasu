# CI 日志分级策略

构建成败**只由 `make` 退出码决定**。日志分级只负责把“真实错误”和“已知噪音”分开，避免巡检时被固定提示误导，也避免把真实错误当噪音放过去。

## 三个类别

| 类别 | 识别规则 | 是否阻断 |
|---|---|---|
| 真实 error | `error:`、`fatal error:`、`undefined reference to`、`ld: cannot`、`clang: error:`、`make: ***`、`Killed`、`No space left on device`、`Error N`、KSU 的 `TP hooks ... Stop.` | 是（`make` 非 0 即失败） |
| 编译 warning | `warning:` | 否，只统计 |
| 已知噪音 | 下表精确白名单 | 否 |

## 已知噪音白名单

| 精确特征 | 来源 | 为什么不是错误 |
|---|---|---|
| `ReSukiSU/susfs_inline: WARNING: Your build maybe broken.` | `drivers/kernelsu/tools/inline_hook_check.mk:61` | inline 模式检测到 manual guard 的固定提示；v3 构建 0 error 仍会出现 |
| `ReSukiSU/susfs_inline: - If you have any issue, please check your hook before submit an issue` | 同文件下一行 | 上一条的配套说明 |
| `ReSukiSU/compat: ksu_handle_post_execve hook not found` | `drivers/kernelsu/tools/kernel_compat.mk:301` | 5.4 内核没有 `post_execve` 挂点，KSU 走 `execveat` 兼容路径，属预期 |

## 硬规则

1. **只允许精确到具体来源的行**。禁止把 `not found`、`warning`、`maybe` 这类泛词整体放行。
2. 新增白名单必须同时更新本文件，写清来源文件和“为什么不是错误”；并在最近一次成功构建日志上验证。
3. 白名单只影响报告，不影响构建门禁；`make` 退出码仍是唯一失败判据。
4. 发现“真实 error 被白名单吃掉”时，先删白名单条目，再修分类脚本。

## 使用方式

```bash
# Markdown 汇总（CI Step Summary 用）
python3 scripts/ci/classify-build-log.py build.log --summary

# 只列真实 error（失败诊断用，已排除已知噪音）
python3 scripts/ci/classify-build-log.py build.log --errors --plain --max 60
```

CI 中：

- 步骤 `10b) 日志分级`：在编译后 `always()` 执行，把三类数量写进 Step Summary
- 步骤 `15b) 失败诊断`：只列真实 error，再附日志末尾 100 行
