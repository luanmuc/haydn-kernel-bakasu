# 分支模型（本 fork 的维护约定）

本仓库是 `MiYume0721/android_kernel_xiaomi_sm8350_miyume` 的 fork，只服务 haydn（Redmi K40 Pro / K40 Pro+）。

## 三条分支的分工

| 分支 | 定位 | 允许的改动 |
|---|---|---|
| `main` | **上游镜像 + 通用 CI** | 同步 MiYume 上游；CI 基建（子模块 unshallow、AnyKernel3 锁 commit、ccache）可以存在；**不做 KSU/SUSFS/defconfig 升级** |
| `haydn/stable` | 长期稳定产品线 | 只接收在 `haydn/test` 验证过的改动；每次发布从这里打 tag |
| `haydn/test` | 先行验证线 | KSU/SUSFS/defconfig 升级、实验性补丁先落这里，云端构建通过后再合入 stable |

## 硬规则

1. **KSU 子模块 bump 只允许出现在 `haydn/*`**，`main` 保持上游当前指针（现为 rc1）。这样以后 rebase MiYume 上游时，main 不会因为子模块冲突而卡住。
   - defconfig 的**清理性改动**（如删除上游已不存在的幽灵开关）可以随通用修复进 `main`；功能开关的增删仍只在 `haydn/*`。
2. `main` 上的 `.gitmodules` 保持上游写法（`ReSukiSU/ReSukiSU.git`，301 到 Baka-SU）；`haydn/*` 用 `Baka-SU/BakaSU.git`。
3. `haydn/test` 验证通过后，用 **fast-forward** 合入 `haydn/stable`，再打 tag、发 Release。
4. **tag 必须先建好并推送，才能跑 `scripts/ci/release.sh`**。脚本会校验 tag 存在且能解析到 commit，并校验构建 run 的 `head_sha` 与 tag commit 一致；否则拒绝发布，避免把旧内核发成新版本。
5. ccache 只在**编译成功**且体积 ≥20MB 时保存，失败轮不写缓存，避免残缺条目挤掉可用缓存。

## 发布与构建约定（P2 结论）

- **tag 不重打**：`haydn-v2` 指向 `92c620be4`，之后的纯 CI 提交（如 ccache 门槛修复）不进 tag；tag 只标源码与产物。
- **产物只含 `Image`**，dtb/dtbo 沿用 ROM 原机；要做 dtbo 定制需另立工程，不在本仓库内混。
- **冷编耗时是预期**：KSU 换版 + 空缓存时约 28 分钟；缓存生效后目标 5~10 分钟（ThinLTO 链接时间省不掉）。
- defconfig 已删除两个幽灵开关 `CONFIG_KPM`、`CONFIG_KSU_DISABLE_IN_RECOVERY`（rc1/rc3 的 Kconfig 均不存在这两项，留着只会误导）。

## 发布流程

```
haydn/test 提交 -> 触发云端构建 -> 校验版本号/hook/SUSFS/error
  -> git checkout haydn/stable && git merge --ff-only haydn/test
  -> git tag -a haydn-vN -m "..." <commit> && git push origin haydn-vN
  -> bash scripts/ci/release.sh haydn-vN "标题" body.md
```

`release.sh` 在工作区根执行时自动识别 `WORK_ROOT`（当前目录含 `PROGRESS.md` + `repo/`），也可显式指定：

```bash
WORK_ROOT=/path/to/workspace RUN_ID=123456789 bash scripts/ci/release.sh haydn-vN
```

建议先跑 `DRY_RUN=1` 校验 tag/run/产物，再正式发布：

```bash
DRY_RUN=1 RUN_ID=123456789 bash scripts/ci/release.sh haydn-vN
```

## 当前状态（2026-11-24）

- `haydn/stable`：KSU `v4.2.0-rc3`（版本码 35171）+ SUSFS `v2.3.0`
- `haydn/test`：与 stable 同源，后续升级先动这里
- `main`：上游基线 + 通用 CI，KSU 仍为 `v4.2.0-rc1`
- 已发布：`haydn-v1`、`haydn-v2`、`haydn-v3`
