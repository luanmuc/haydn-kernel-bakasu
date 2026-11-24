# 上游巡检记录

## 2026-11-24 首次月审 · BakaSU

### 基线

| 项 | 值 |
|---|---|
| 产品线 tag pin | `v4.2.0-rc3` / `239e1e887` / 版本码 35171 |
| 上游 `main` HEAD | `57b2db607`（2026-11-23） |
| 距 tag | 114 个提交，其中 `kernel/` 相关 43 个 |
| 最新 tag / Release | 仍是 `v4.2.0-rc3`，没有 rc4 |
| 对比文件 | 300 个（API 上限），命中 `kernel/` 124 个 |
| 估算版本码 | 35285（按 30700 + 114，仅参考） |

### 分类

**A 类：必须先补 SUSFS，才能 bump**

- `kernel/Kconfig` 新增 `CONFIG_KSU_SUSFS_PRIORITY_UID_FILTER`，`default y`
- 上游新增 SUSFS 调用，本地 `v2.3.0` 没有这些符号：
  - `susfs_add_sus_avd_allowed_by_type`
  - `susfs_add_sus_type`
  - `susfs_set_priority_uid_filter`
  - `susfs_set_sus_path_uid_filter`
  - `susfs_parse_priority_app_strings`
  - `susfs_parse_sus_path_app_strings`
- `kernel/selinux/sepolicy.c` 里 `susfs_add_sus_avd_allowed_by_type` / `susfs_add_sus_type` 在 `CONFIG_KSU_SUSFS` 下是无 guard 调用 → 当前 SUSFS 直接 bump 预计编译/链接失败
- 相关提交：`0799a678 kernel, ksud, manager: sync with latest susfs`、`48fa4bb7 kernel: suspend susfs build`

**B 类：值得在 rc4 时一起评估的内核修复**

- `de80463b` fix regression of more than one sid target one context
- `2b558ca5` fix detection point caused by susfs skip commits
- `f6513993` synchronization for track_throne in pkg_observer
- `7ae97867` Fix SELinux generation tracking for policy updates
- `bd5ca014` align SELinux hide policy parsing
- `f397410c` Fix avtab removal length calculation and xperms update
- `b0fa24df` escape to root when reading allowlist
- `8450dd28` pkg_observer: defer track_throne to task_work
- `c4bdcaae` don't path_put when 3.6- in dentry_open
- `448eaca2` check `ksu_handle_vfs_fstat`

**C 类：与 haydn 无关或暂不需要**

- RISC-V / x86_64 相关：`325265c5`、`587bf8e4`、`5fbf06ff`、`ece84330`、`33cca775`、`a769d962`
- 新功能：module preinit、`shell_su_adb_only`、module_blacklist、`ksu_config` 强制特性
- manager / 翻译 / CI / 文档 / 依赖升级

**hook 名称变化**

- 上游把 `ksu_handle_execve` / `ksu_handle_post_execve` 标记为 deprecated，要求迁移到 `ksu_handle_execve_common` / `ksu_handle_post_execve_common`
- 我们当前 `fs/exec.c` 用的是 `ksu_handle_execveat`，SUSFS inline 路径不受影响；只有将来切 manual hook 时才需要重新做接线

### 结论

**暂不跟 `main`。**

理由：

1. 没有新 tag，`main` 是开发线，114 个提交混着 A/B/C 三类，不适合按单点 cherry-pick。
2. A 类依赖新的 SUSFS API；本地 `v2.3.0` 没有这些符号，直接 bump `KernelSU` 会在 `CONFIG_KSU_SUSFS=y` 下失败。
3. 等 `v4.2.0-rc4` 或正式 Release，先确认上游 SUSFS 5.4 是否同步这些 API；如果没有，再评估小范围回填。

### 已更新

- `maintenance/upstream-pins.json`：`audited_commit` 更新到 `57b2db607`，日巡从该基线看增量
- 下一次例行月审：2026-12-24；若 rc4 先到，则提前
- 跟进条件：新 tag / Release，或 SUSFS 5.4 分支出现新提交
