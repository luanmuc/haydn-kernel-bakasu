# Nova → BakaSU 移植方案与审计记录

适用设备：Redmi K40 Pro / K40 Pro+（`haydn` / `haydnpro`，SM8350，Android 14）
BakaSU 线：`haydn/stable`，内核 `5.4.302-HoshinoNeko-bakasu`
Nova 参考线：`haydn/nova-builtin-new`（HEAD `d2a17032c`）

## 目标

从 Nova 线吸收**不会破坏 BakaSU KSU/SUSFS 组合**的修复，按风险从低到高分批落地。Nova 的 KSU、SUSFS 2.4、管理器 APK 不能直接混入 BakaSU。

## 执行顺序

1. **AnyKernel3 分区/TWRP 修复**：直接修 BakaSU 当前小写变量导致的 `BLOCK` 为空问题。
2. **Android 14 FCM6 配置**：只取 `27a492b20` 的非 KSU 配置和 `arch/Kconfig` / `arch/arm64/Kconfig` 变更，单独构建验证。
3. **HWRNG 内置与初始化修复**：`CONFIG_HW_RANDOM=y`，并修 `hwui_mon.c` / `fpc1020_tee.c` 的未初始化返回。
4. **正式版资产管线**：接入 `RELEASE_ASSETS_DIR`、额外资产上传、发布标准文档；APK 和 clean boot 仍需人工确认来源与底包。
5. **后续单独立项**：SUSFS 2.4、stock 安全/errata 配置组；未验证前不进 `haydn/stable`。

## 验收门槛

- 第 1 项：`bash -n`、包内变量检查、TWRP 刷入和回滚实测。
- 第 2 项：`make haydn_defconfig` 后 8 项 FCM6 配置全部为 `y`；完整 Image 构建；真机确认无“设备内部出现问题”弹窗，触摸/WiFi/相机/通话/充电正常。
- 第 3 项：完整 Image 构建；`CONFIG_HW_RANDOM=y`、`CONFIG_HW_RANDOM_MSM_LEGACY=y`；启动日志无相关回归。
- 第 4 项：`DRY_RUN=1` 发布预检；Release 资产逐项核对大小和 SHA256；AK3/clean boot/Image 不混用。
- 全部通过后才允许推送 `haydn/stable` 和发正式 Release；当前只做本地提交。

## 明确不做

- 不把 Nova 的 `KernelSU` 子模块、整份 defconfig、管理器 APK 搬进 BakaSU。
- 不把 Nova 的 KSU inline safe-mode 补丁直接套到 BakaSU（BakaSU 走不同的 input hook 保护路径）。
- 不把 Nova 的 SUSFS 2.4 直接 cherry-pick 到 BakaSU 2.3.0。
- 不在本轮编译、刷机或推送远端。

## 当前状态

本地分支：`port/nova-adapt-20261127`，基于 `haydn/stable` 的 `d65ccb9b8`。远端 `haydn/stable` 尚未变动。

已落地（仅本地提交）：

- `ee9d855e2` `fix(ci): make AnyKernel3 TWRP-compatible for haydn`
- `846876e55` `config(haydn): port Nova FCM6 and HWRNG fixes`
- `720b7e3a3` `ci(release): support full BakaSU release assets`

尚未完成 / 尚未验证：

- 没有完整编译，没有真机刷入；AnyKernel 只做了语法和变量静态检查。
- 本地环境缺 `flex`，`make haydn_defconfig` 未跑完；云端 CI 会重新生成 `.config` 并执行 FCM6/HWRNG 断言。
- BakaSU 上游 APK 来源仍未确认；clean boot 仍需按标准人工生成并校验。
- 没有推送远端，没有创建 Release，没有改 Nova 仓库。