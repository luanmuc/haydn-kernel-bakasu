# haydn-v3 真机验证清单

适用：Redmi K40 Pro / K40 Pro+（codename `haydn`，SM8350，boot image v3）
不适用：K40（`alioth`）等其它机型。AnyKernel3 脚本里 `do.devicecheck=0`，不会替我们拦机型，刷错会直接变砖。

## 0. 结论口径

本次只验证 `haydn-v3` 这一个已发布包，不混入后续 CI 产物。验收必须同时满足：

- 能正常开机，首屏到桌面，无 bootloop
- 内核版本为 `5.4.302-HoshinoNeko-g21091ea1`
- KernelSU 版本码为 `35171`，`su` 能正常授权
- SUSFS 初始化日志为 `v2.3.0`
- 核心硬件可用，30 分钟内无 kernel panic / oops
- 银行类 App 只做兼容性记录：能正常打开/登录为通过；若检测到 root 后拒绝，记录为不通过，不做绕过处理

## 1. 包信息

| 项 | 值 |
|---|---|
| Release | `haydn-v3` |
| 包名 | `HoshinoNeko_haydn_21091ea1f_Any3Kernel.zip` |
| 大小 | `23,942,834` 字节 |
| zip SHA-256 | `8dd77cfd28dd736558db53957257c623e447eefcda160636ba2a80f83aca1f62` |
| 包内 `Image` 大小 | `46,193,152` 字节 |
| 包内 `Image` SHA-256 | `a4db450aee84a0399ce527d291b43f4f7e9775a0b1483521ff9bc3dc4e6a7932` |
| 内核版本串 | `5.4.302-HoshinoNeko-g21091ea1` |
| SUSFS | `v2.3.0` |
| 下载 | `https://github.com/luanmuc/android_kernel_xiaomi_sm8350_miyume/releases/download/haydn-v3/HoshinoNeko_haydn_21091ea1f_Any3Kernel.zip` |

下载后先在电脑上核对，不要只看文件名：

```bash
sha256sum HoshinoNeko_haydn_21091ea1f_Any3Kernel.zip
unzip -l HoshinoNeko_haydn_21091ea1f_Any3Kernel.zip | head
unzip -p HoshinoNeko_haydn_21091ea1f_Any3Kernel.zip Image | sha256sum
```

期望 zip 哈希为 `8dd77cfd...aca1f62`，包内 `Image` 哈希为 `a4db450a...e6a7932`。

## 2. 刷机前

- [ ] bootloader 已解锁；知道怎么进 fastboot 和 recovery
- [ ] 电量 > 50%，或插着电
- [ ] 已备份重要数据；至少备份 `boot` 分区
- [ ] 当前系统能正常进 recovery，且 recovery 支持安装 AnyKernel3 zip（TWRP / OrangeFox 等）
- [ ] 已把 zip 放到 `/sdcard/`，并记下路径
- [ ] 已确认机型是 `haydn`，不是 K40 标准版

备份当前 boot（如果当前已有 root）：

```bash
adb shell su -c 'ls -l /dev/block/by-name/boot'
adb shell su -c 'dd if=/dev/block/by-name/boot of=/sdcard/boot-current.img bs=4096'
adb pull /sdcard/boot-current.img
```

如果路径不存在，换 `/dev/block/bootdevice/by-name/boot` 再试。没有 root 的话，在 recovery 里备份 Boot 分区，或先准备一份可用的 stock boot 镜像。把备份文件拉到电脑上留一份，不要只放手机里。

## 3. 刷入

1. `adb reboot recovery`，或关机后按音量上 + 电源进 recovery。
2. 在 recovery 里再备份一次 Boot（如果前面没备份）。
3. 安装 `/sdcard/HoshinoNeko_haydn_21091ea1f_Any3Kernel.zip`。
4. **不要 wipe data**；cache/dalvik 可清可不清。
5. 重启系统。首次开机可能 5–10 分钟，期间不要反复断电。
6. 如果超过 15 分钟仍停在开机动画，或反复重启，直接进第 5 节回滚。

不要把 Magisk 再刷一遍，也不要在刷完后装另一个 root 管理器；这个包已经内置 KernelSU。

## 4. 验证

### 4.1 启动与内核

```bash
adb shell getprop ro.product.device
adb shell getprop ro.build.version.release
adb shell uname -a
adb shell cat /proc/version
```

期望：

- `ro.product.device` 为 `haydn`
- `uname -a` / `/proc/version` 包含 `5.4.302-HoshinoNeko-g21091ea1`

### 4.2 Root / KernelSU

```bash
adb shell su -v
adb shell su -V
adb shell su -c id
```

期望：

- `su -v` 输出 `35171`
- `su -c id` 输出 `uid=0(root)`
- KernelSU 管理器能正常打开，显示已安装 / 工作中；授权一个测试应用能弹窗并记住

### 4.3 SUSFS

优先看启动日志：

```bash
adb shell su -c 'dmesg | grep -i susfs | tail -20'
```

期望能看到类似：

```text
susfs is initialized! version: v2.3.0
```

如果 BakaSU 管理器里有 SUSFS 状态页，也记录看到的版本；没有就以 dmesg 为准。不要用来源不明的“SUSFS 检测”App 下结论。

### 4.4 兼容性

逐项勾，出问题记下现象和复现步骤：

- [ ] WiFi 2.4G / 5G 能连，能上网
- [ ] 移动数据 / 5G / 通话正常
- [ ] 蓝牙能开关、能连耳机
- [ ] NFC 能开关（如果平时用）
- [ ] GPS / 定位正常
- [ ] 前后相机拍照、录像正常
- [ ] 指纹解锁、人脸解锁正常
- [ ] 扬声器、麦克风、耳机正常
- [ ] 充电、USB 传输、ADB 正常
- [ ] 热点、自动亮度、传感器、震动正常
- [ ] 银行类 App 能打开并登录（只记录，不绕过检测）
- [ ] 常用 KernelSU 模块（如有）能正常加载

### 4.5 稳定性

- [ ] 正常使用 30 分钟，无自动重启、无卡死
- [ ] `adb shell su -c 'dmesg | grep -iE "panic|oops|Unable to handle|BUG:" | tail -20'` 无 panic / oops
- [ ] 息屏待机 1 小时，耗电可接受（可选）

## 5. 回滚

能进 fastboot：

```bash
fastboot devices
fastboot flash boot boot-current.img
fastboot reboot
```

`boot-current.img` 是刷机前备份的当前 boot；如果备份的是纯 stock boot，回滚后 root 会消失，但系统能正常开机。

进不了 fastboot 时，用 recovery 的 Restore 恢复 Boot 备份；再不行就重刷当前 ROM 的 boot 镜像。不要为了回滚去锁 bootloader，也不要刷 dtbo。

## 6. 记录

建议把结果留在 `device-test/haydn-v3/`，不要把含个人信息的截图直接发到公开 Issue：

```bash
mkdir -p device-test/haydn-v3
adb shell uname -a > device-test/haydn-v3/uname.txt
adb shell su -v > device-test/haydn-v3/su-v.txt
adb shell su -V > device-test/haydn-v3/su-V.txt
adb shell getprop > device-test/haydn-v3/getprop.txt
adb shell su -c 'dmesg' > device-test/haydn-v3/dmesg.txt
adb exec-out screencap -p > device-test/haydn-v3/kernel-su.png
```

最终回填：

- `haydn-v3` 真机结论：通过 / 不通过
- 不通过项：具体现象、复现步骤、是否回滚
- 是否可以作为 `haydn/stable` 的当前推荐版本
