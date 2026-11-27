# BakaSU 正式 Release 资产标准

适用：`haydn/stable` 的每一次正式发布。**只发 AnyKernel3 不合格。**

## 必发资产

| 资产 | 说明 |
|---|---|
| `HoshinoNeko_haydn_<sha>_Any3Kernel.zip` | TWRP 刷入，只替换 kernel，保留当前 ramdisk |
| `BakaSU-haydn-patched-clean-boot-<sha>-official.img` | 本仓库 Image + 干净 ramdisk 的 boot 镜像；可 `fastboot boot` 临时验证，也可 `fastboot flash boot` 永久刷入 |
| `BakaSU-<version>-arm64-v8a-release.apk` | BakaSU 上游配套管理器，arm64-v8a；包名、签名和版本必须与本线一致 |
| `Image-<sha>-official` | 原始内核 Image，不是 boot image，不能直接刷 |
| `haydn-config-used-<sha>.txt` | 云端实际 `.config` |
| `build-<sha>.log` | 对应构建 run 的日志 |
| `RELEASE-<sha>.md` | Release 说明存档 |
| `SHA256SUMS` | 覆盖以上所有资产的 SHA256 |

> 不发布带 Magisk/TWRP 的 stock boot。需要 boot 镜像时只用 clean boot，并先备份当前 boot。

## clean boot 要求

- 底包必须是 **BakaSU 自己的 stock/clean ramdisk**；不要直接使用 Nova 的 clean boot 镜像，也不要跨线混用。
- SM8350 是 boot image v3（独立 `vendor_boot`，无 `init_boot`）：4K header + kernel + ramdisk，按页对齐重建 AVB footer。
- 只替换 kernel；解出的 ramdisk 必须与底包 ramdisk 完全一致。
- AVB 参数按底包实际值处理；`avbtool info_image` 应为 `Algorithm: NONE`，并更新 digest。
- 校验：
  1. 解出的 kernel SHA256 等于本次 `Image`；
  2. 解出的 ramdisk 与底包一致；
  3. `avbtool verify_image` 通过；
  4. 上传后重新下载，核对远端大小和 SHA256。
- 当前 clean boot 仍是人工配方，尚未脚本化；脚本化并通过校验前，不得把未核对镜像写进 Release。

## 管理器 APK 要求

- 必须是 BakaSU 上游配套的 arm64-v8a APK，不能使用 Nova 的 `com.sukisu.nova` APK，也不能从旧安装包或第三方转载取包。
- 发布前核对包名、签名、版本号；上传后重新下载核对 SHA256。
- 当前工作区尚未确认 BakaSU 上游 APK 的稳定来源，**这是正式资产清单的阻塞项**；在来源确认前不宣称资产已齐。

## 发布脚本

把 AK3 以外的资产放进同一目录，创建 Release 时传入：

```bash
RELEASE_ASSETS_DIR=/path/to/release-assets \
  bash repo/scripts/ci/release.sh <tag> "<标题>" /path/to/RELEASE.md
```

`release.sh` 会先校验 AnyKernel3 的大写变量和当前槽位解析，再上传 AK3；随后调用 `scripts/ci/upload-release-assets.sh` 上传目录内其余文件。已存在的同名资产会跳过，不会覆盖。

先生成校验和，再上传：

```bash
bash scripts/ci/make-release-sha256sums.sh /path/to/release-assets
```

`SHA256SUMS` 生成后再放进同一目录，上传脚本会一并上传。

先跑预检：

```bash
DRY_RUN=1 RUN_ID=<run_id> bash scripts/ci/release.sh <tag> "<标题>" /path/to/RELEASE.md
```

## 刷入方式

- 临时：`fastboot boot ...clean-boot...img`，不写 boot 分区。
- 永久（推荐）：TWRP 刷 AnyKernel3，保留当前 ramdisk。
- 永久（PC）：`fastboot flash boot` clean boot；会替换当前 boot ramdisk，先备份。
- 管理器直接覆盖安装；不要混用 Nova 管理器。

## 禁止

- 不把不同 tag 的 AK3、clean boot、Image、APK 混在一起。
- 不刷 Nova 线包，不与 `com.sukisu.nova` 管理器混装。
- 不用 Nova 的 clean boot、管理器 APK 或 SUSFS 2.4 产物冒充 BakaSU 正式资产。
