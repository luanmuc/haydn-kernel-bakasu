# android_kernel_xiaomi_sm8350_miyume

> **本仓库只维护 BakaSU 稳定线（`haydn/stable`）。**
>
> SukiSU-Nova 线在另一个独立仓库：  
> https://github.com/luanmuc/haydn-kernel-nova
>
> 两条线不要混刷；BakaSU 线继续使用 BakaSU 管理器。

## KSU 版本线

- 分支：`haydn/stable`
- KSU：BakaSU `v4.2.0-rc3`（`239e1e88`）
- SUSFS：`v2.3.0`
- 适用设备：Redmi K40 Pro / Pro+（haydn）
- 禁止：不要刷 Nova 线的包，不要与 `com.sukisu.nova` 管理器混装

---

## Xiaomi SM8350 Device MiYume HoshinoNeko Kernel ##

## 维护设备 ##
- Xiaomi 11 (venus)
- Xiaomi 11 Pro (mars)
- Xiaomi 11 Ultra (star)
- Redmi K40 Pro(+) (haydn)

## 内核特性 ##
- 版本：5.4.302
- 更多描述在 Releases

## 相关配置 ##
- **Venus** 使用 `venus_defconfig`
- **Star/Mars** 使用 `star_defconfig`
- **Haydn** 使用 `haydn_defconfig`

## 默认配置 ##
- Clang 18.1.8 & LLD 18.1.8

## 开始编译 ##
bash build_device.sh (填设备代号, 不填默认venus)
