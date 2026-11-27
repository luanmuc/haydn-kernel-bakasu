# 分支模型（单分支维护）

本仓库是 `MiYume0721/android_kernel_xiaomi_sm8350_miyume` 的 fork，只服务 haydn（Redmi K40 Pro / K40 Pro+）。

自 2026-11-27 起，本仓库远端只保留一个分支：`haydn/stable`。原 `main` 和 `haydn/test` 已删除；上游只作为 `upstream` remote 的只读参考，不再在本仓库保留镜像分支。

## 唯一分支

| 分支 | 定位 | 允许的改动 |
|---|---|---|
| `haydn/stable` | 长期稳定产品线 | KSU/SUSFS/defconfig 升级、修复和发布都落在这里；每次发布从当前 HEAD 打 tag |

## 硬规则

1. **远端只保留 `haydn/stable`**。不要重新推 `main` 或 `haydn/test`；需要试验时用本地临时分支或独立 fork，不要在产品仓库建长期试验分支。
2. **KSU 子模块始终指向 BakaSU**。`.gitmodules` 必须保持 `Baka-SU/BakaSU.git`，不要改成上游的 `ReSukiSU/ReSukiSU.git` 指针；`main` 分支曾经保留的 ReSukiSU 子模块指针不适用于本产品线。
3. **任何 KSU/SUSFS/defconfig 改动**都必须先在本地临时分支或独立 fork 里完成整 Image 构建，核对版本码、hook 选路、SUSFS 版本和 `.config`，通过后再提交到 `haydn/stable`。
4. **tag 必须先建好并推送，才能跑 `scripts/ci/release.sh`**。脚本会校验 tag 存在且能解析到 commit，并校验构建 run 的 `head_sha` 与 tag commit 一致；否则拒绝发布，避免把旧内核发成新版本。
5. ccache 只在**编译成功**且体积 ≥20MB 时保存，失败轮不写缓存，避免残缺条目挤掉可用缓存。

## 发布与构建约定

- **tag 不重打**：`haydn-v2` 指向 `92c620be4`，之后的纯 CI 提交（如 ccache 门槛修复）不进 tag；tag 只标源码与产物。
- **产物只含 `Image`**，dtb/dtbo 沿用 ROM 原机；要做 dtbo 定制需另立工程，不在本仓库内混。
- **冷编耗时是预期**：KSU 换版 + 空缓存时约 28 分钟；缓存生效后目标 5~10 分钟（ThinLTO 链接时间省不掉）。
- defconfig 已删除两个幽灵开关 `CONFIG_KPM`、`CONFIG_KSU_DISABLE_IN_RECOVERY`（rc1/rc3 的 Kconfig 均不存在这两项，留着只会误导）。

## 发布流程

```text
提交到 haydn/stable -> 触发云端构建 -> 校验版本号/hook/SUSFS/FCM6/error
  -> git tag -a haydn-vN -m "..." <commit> && git push origin haydn-vN
  -> RELEASE_ASSETS_DIR=/path/to/assets bash scripts/ci/release.sh haydn-vN "标题" body.md
```

`release.sh` 会先上传 AK3，再通过 `RELEASE_ASSETS_DIR` 上传 clean boot、APK、Image、日志、`SHA256SUMS` 等额外资产。clean boot 和 APK 的来源/校验按 [`RELEASE-STANDARD.md`](RELEASE-STANDARD.md) 执行；当前 APK 来源尚未确认，不能宣称资产齐全。

`release.sh` 在工作区根执行时自动识别 `WORK_ROOT`（当前目录含 `PROGRESS.md` + `repo/`），也可显式指定：

```bash
WORK_ROOT=/path/to/workspace RUN_ID=123456789 bash scripts/ci/release.sh haydn-vN
```

建议先跑 `DRY_RUN=1` 校验 tag/run/产物，再正式发布：

```bash
DRY_RUN=1 RUN_ID=123456789 bash scripts/ci/release.sh haydn-vN
```

## 当前状态（2026-11-27）

- `haydn/stable`：KSU BakaSU `v4.2.0-rc3`（版本码 35171）+ SUSFS `v2.3.0`
- 远端分支：仅 `haydn/stable`
- 旧 Release：`haydn-v1` / `haydn-v2` / `haydn-v3` 已清空（含对应 tag）；等待下一次正式版
