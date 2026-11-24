# 上游巡检与月审

## 频率

| 对象 | 日巡 | 月审 | 说明 |
|---|---|---|---|
| BakaSU `main` | 自动 | 人工 | 内核改动活跃，日巡只看 `kernel/` 路径 |
| SUSFS `Zhanfg/susfs4ksu` `kernel-5.4` | 不做 | 人工 | 5.4 分支长期休眠，月巡足够 |
| MiYume 基础内核 `main` | 不做 | 人工 | 只做 rebase 风险评估 |

## 日巡（BakaSU）

- workflow：`.github/workflows/upstream-watch.yml`
- 时间：每天北京时间 09:00（GitHub cron 可能有延迟）
- pin 文件：`maintenance/upstream-pins.json`
- 行为：
  - 新 tag / Release：一定报警
  - `main` HEAD 相对 `audited_commit`：只有 `kernel/` 路径变化才报警
  - manager / 翻译 / CI / 文档：忽略
  - **不编译、不 bump、不建分支、不合并**
- 报警方式：创建/更新 GitHub Issue `[upstream-watch] BakaSU 内核相关变更`，标签 `upstream-watch`
- 无变化时只写 Step Summary，不建 Issue
- `audited_commit` 是“上次月审确认过的上游 HEAD”，不是 tag pin；月审后更新它，日巡才会从新基线继续看增量

## 前置条件

- 仓库必须开启 GitHub Issues（Settings → Features → Issues）。关闭时，日巡在 `changed=true` 时会在 `actions/github-script` 步骤报 `Issues has been disabled in this repository.`，workflow 直接失败。
- 2026-11-24 已做强制测试：临时分支把 `audited_commit` 改回 tag pin，run `45342820214` 创建 Issue #1 并自动创建 `upstream-watch` 标签；run `45342910659` 验证“已存在则更新”路径。测试 Issue 已评论并关闭（not_planned），临时分支已删除。

## 月审（人工，约 30 分钟）

1. 打开 `upstream-watch` Issue（没有就手动跑一次 workflow）
2. BakaSU：从 **tag pin** 做全量对比，而不是只看日巡增量
   ```bash
   git -C KernelSU fetch origin main
   git -C KernelSU log --oneline <pinned_commit>..origin/main -- kernel
   git -C KernelSU diff --stat <pinned_commit>..origin/main -- kernel
   git -C KernelSU diff <pinned_commit>..origin/main -- kernel/Kconfig
   ```
3. 重点看四类：
   - `kernel/Kconfig` 新增开关
   - hook 选路 / manual hook 名称变化
   - 新增 `susfs_*` API 调用（对照本地 `include/linux/susfs.h`）
   - 版本码公式（当前 `KSU_VERSION = 30000 + local + 700`）
4. SUSFS：`Zhanfg/susfs4ksu` 的 `kernel-5.4` HEAD 是否变；变了就跑
   ```bash
   bash susfs/scripts/check-baseline.sh
   ```
5. MiYume 基础内核：只判断是否影响 haydn 的 rebase，不自动合
6. 给出决定：**跟 / 不跟 / 只回填某几个提交**，写入 `docs/upstream-log.md`
7. 决定后：
   - 更新 `maintenance/upstream-pins.json` 的 `audited_commit` / `audited_at`
   - 关闭对应 Issue
   - 如果“跟”，才进入下面的验证流程

## 决定跟之后的验证

```bash
git checkout -b upstream/baksu-<tag> haydn/test
# bump KernelSU 子模块到目标 commit
# 触发云端整 Image 构建
# 核对：版本码、hook 选路、SUSFS 版本、.config
# 通过 -> 合入 haydn/stable -> 打 tag -> 发 Release
```

验证不通过就删临时分支，产品线保持原 tag。

## 硬规则

1. 日巡和月审都不自动改产品分支。
2. `main` 只镜像上游 + 通用 CI，不直接放 KSU/SUSFS 升级。
3. 任何 bump 都必须先 `haydn/test` 整 Image 通过，再进 `haydn/stable`。
4. 决定“不跟”也要更新 `audited_commit`，否则日巡会反复报同一批提交。
5. 新增/修改白名单或巡检路径，必须同时更新本文档。
