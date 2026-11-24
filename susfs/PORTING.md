# SUSFS 回填流程（PORTING）

## 只接三类改动

| 类型 | 判定标准 | 处理 |
|---|---|---|
| A. KSU 新 API 兼容 | BakaSU 新版本调用 `susfs_*` 函数，编译报未定义/签名不匹配 | 必接，编译不过才动 |
| B. haydn 实测 bug | SUS_PATH / SUS_MOUNT / KSTAT / SPOOF 在真机上失效或异常 | 接，先复现再改 |
| C. 稳定性/安全修复 | 内存泄漏、seqlock、UAF、越界、竞态 | 接，优先 |
| D. 新功能 | 新 spoof 类型、新 hide 策略、新 ioctl/flag | **不接**，除非有明确需求 |

## 操作步骤

1. 从 `haydn/test` 开分支：`susfs/port-<上游短sha>`
2. 找到上游 GKI 5.10/6.x 的对应提交，判断是否依赖新内核 API：
   - `mount` / `mountinfo` 相关：6.x 的 mount API 与 5.4 差异大，通常要手工改写
   - `statfs` / `f_flags`：注意 5.4 结构体字段差异
   - 纯逻辑修复（引用计数、seqlock、越界）：通常可直接适配
3. 只取最小 hunk，不整段合并；保持 `CONFIG_KSU_SUSFS` guard 完整
4. 验证四件套：
   - `CONFIG_KSU_SUSFS=y` 云端构建 0 error
   - guard 完整性：`SUSFS=n` 时集成文件仍能编译（见下节，**不能要求整 Image 成功**）
   - `version code` / `SUSFS_VERSION` 符合预期
   - 真机：`su -v`、SUS_PATH / SUS_MOUNT / SPOOF 实际生效
5. 合并 `haydn/test` → `haydn/stable`（fast-forward），更新 `baseline.sha256`，打新 tag

## SUSFS=n 的 guard 验证（2026-11-24 实测）

本内核上 `SUSFS=n` **整 Image 编不过**，原因不是 guard 漏洞：

- BakaSU 在 `CONFIG_KSU_SUSFS` 关闭时会退回 **tracepoint hook**
- 但本内核是 GKI 1.0 / 非 GKI，`drivers/kernelsu/Kbuild:175` 直接报
  `TP hooks are incompatible with Non-GKI/GKI 1.0 kernels. Stop.`
- 也就是说：**SUSFS 关闭会连带 KSU hook 选路失败**，这是 KSU 的设计耦合

正确的 guard 验证方式：

1. 临时分支 defconfig 改 `# CONFIG_KSU_SUSFS is not set`
2. 触发构建，允许在 `drivers/kernelsu` 处失败
3. 检查 `build.log`：
   - `fs/stat.o`、`fs/statfs.o`、`fs/super.o`、`fs/proc/fd.o`、`fs/proc_namespace.o`、`fs/proc/task_mmu.o`、`fs/notify/fdinfo.o` 全部有 `CC` 行
   - `fs/susfs.o` 不应出现
   - 除 KSU 的 TP 检查外无其他 `error`
4. 实测结果：上述文件在 SUSFS=n 下全部编译通过，`fs/susfs.o` 未编译，无其他 error → **guard 完整**
5. 若确实要整 Image 成功，需同时 `CONFIG_KSU_MANUAL_HOOK=y`（未验证）或保持 `SUSFS=y`；正式发布始终 `SUSFS=y`

验证完删除临时分支，不合入任何产品分支。

## 季度检查表

- [ ] 上游 `Zhanfg/susfs4ksu` 的 `next` / GKI 分支是否有影响 5.4 的 A/B/C 类提交
- [ ] BakaSU 是否有新 tag、是否新增 susfs API 调用
- [ ] haydn 真机 SUSFS 功能抽查（银行/检测类 App）
- [ ] `bash susfs/scripts/check-baseline.sh` 是否仍全部 OK

## 禁止事项

- 不在 `haydn/stable` 上直接改 SUSFS
- 不把 6.x 的整段 susfs 代码直接覆盖到 5.4
- 不为了“跟新”而引入未验证的新功能
- 改完不更新 `baseline.sha256` 就合并
