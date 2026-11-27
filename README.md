# haydn-kernel-bakasu

Redmi K40 Pro / K40 Pro+（`haydn` / `haydnpro`，SM8350）的 **BakaSU 稳定线内核仓库**。

本仓库只维护这一台机型，不做 Xiaomi 11 系列；SukiSU-Nova 线在另一个仓库，两条线不能混刷。

- Nova 线：<https://github.com/luanmuc/haydn-kernel-nova>
- 上游底座：<https://github.com/MiYume0721/android_kernel_xiaomi_sm8350_miyume>

## 当前状态

| 项 | 值 |
|---|---|
| 维护分支 | `haydn/stable`（唯一远端分支，默认分支） |
| 内核 | `5.4.302-HoshinoNeko-bakasu` |
| KSU | BakaSU `v4.2.0-rc3`（`239e1e88`，版本码 `35171`） |
| SUSFS | `v2.3.0`（5.4 适配） |
| 管理器 | BakaSU 管理器 |
| 工具链 | Clang / LLD `18.1.8` |
| 适用系统 | Android 14 |

发布页目前已清空（旧 `haydn-v1` / `haydn-v2` / `haydn-v3` 及其 tag 已移除）。当前代码在 `haydn/stable`；下一次正式版将按下方的完整资产规范发布，刷机请只使用新 Release 的产物。

## 仓库定位

这是 BakaSU 线的长期稳定仓库，优先保证：

- 能开机、能日常使用、能回刷；
- KSU / SUSFS / defconfig 的版本组合可复现；
- 发布产物可校验，不拿旧构建冒充新版本；
- 不追 SukiSU-Nova 的新功能，不与 Nova 线混合。

## 正式版资产规范

正式版 Release 应同时提供以下资产，缺一不可：

| 资产 | 说明 |
|---|---|
| AK3 | `HoshinoNeko_haydn_<短SHA>_Any3Kernel.zip`，AnyKernel3 可刷包 |
| clean boot | 原厂 ramdisk + 本仓库 `Image` 的 boot 镜像，用于 `fastboot boot` 临时验证或刷入 |
| 上游 APK | BakaSU 上游配套管理器 APK，不随内核源码构建 |
| Image | 未打包的原始内核 `Image`，供核对和自行组包 |
| 日志 | 对应构建 run 的 `build.log` / CI step summary |
| SHA256SUMS | 覆盖以上所有资产的校验和文件 |

> 旧 `haydn-v1` / `haydn-v2` / `haydn-v3` 已从发布页和 tag 中移除；下一次正式版必须按上述完整资产规范发布。

刷机前请保留原厂 boot，并确认设备是 `haydn` / `haydnpro`，不要刷到 K40（`alioth`）。

## 禁止混刷

- 不刷 Nova 线的包；
- 不与 `com.sukisu.nova` 管理器混装；
- 切换线前卸载旧管理器并重启；
- 不把不同 tag 的 AK3、clean boot、Image 混在一起用。

## 构建

### 云端构建

GitHub Actions 里的 **Build Kernel · haydn (K40 Pro/Pro+)** 是手动触发，不会在 push 时自动编译。

当前构建产出：

- `Image`
- `HoshinoNeko_haydn_<短SHA>_Any3Kernel.zip`
- `haydn-config-used.txt` / `.config`
- `build.log`
- Actions Step Summary

Artifact 保留 14 天。AnyKernel3 固定到指定 commit，避免上游包结构变动影响产物。

### 本地构建

```bash
bash build_device.sh haydn
```

需要自备 Clang / LLD `18.1.8`。本仓库只维护 `haydn_defconfig`，不要拿 Xiaomi 11 系列的 defconfig 来套。

## 发布流程

```text
提交到 haydn/stable
  -> 手动触发 Build Kernel
  -> 校验版本码 / hook / SUSFS / .config / build.log
  -> 打 annotated tag 并推送
  -> bash scripts/ci/release.sh <tag> "标题" body.md
```

`release.sh` 会校验：

- tag 存在且能解析到真实 commit；
- 构建 run 为 `completed + success`；
- run 的 `head_sha` 等于 tag commit；
- AK3 文件名包含该 commit 的 9 位短 SHA；
- Release 已存在时拒绝覆盖。

发布说明模板见 [`docs/RELEASE-TEMPLATE.md`](docs/RELEASE-TEMPLATE.md)。

> 注意：当前 `release.sh` 仍只上传 AK3；正式版资产规范里的 clean boot、上游 APK、Image、日志和 `SHA256SUMS` 还需要在发布流程中补齐。

## 维护约定

- 远端只保留 `haydn/stable`，不再维护 `main` / `haydn/test`。
- 实验性改动在本地临时分支或独立 fork 验证，整 Image 通过后再进 `haydn/stable`。
- BakaSU 子模块固定为 `Baka-SU/BakaSU.git`，不要改成 ReSukiSU 的指针。
- 上游巡检：BakaSU 每日、SUSFS / MiYume 每月；巡检只报警，不自动 bump、不建分支。

## 文档

- [分支模型](docs/BRANCHING.md)
- [BakaSU 线说明](docs/KSU-LINE.md)
- [发布说明模板](docs/RELEASE-TEMPLATE.md)
- [真机验证清单](docs/DEVICE-TEST.md)
- [上游巡检与月审](docs/UPSTREAM-AUDIT.md)
- [CI 日志分级策略](docs/CI-LOG-POLICY.md)

## 许可

内核代码遵循上游仓库的 GPL-2.0 许可；BakaSU、SUSFS、MiYume 等组件的许可以其上游仓库为准。
