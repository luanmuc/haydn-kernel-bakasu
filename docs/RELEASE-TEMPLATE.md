# BakaSU 线发布说明模板

标题：

```text
[BakaSU][haydn] 5.4.302 稳定版 <版本号>
```

正文必须包含：

- 版本线：BakaSU 稳定线
- KSU：BakaSU `<tag>` / `<commit>`
- SUSFS：`v2.3.0`
- 管理器：BakaSU 管理器（包名：`<package>`）
- 内核：`5.4.302-HoshinoNeko-bakasu-...`
- 仓库：<https://github.com/luanmuc/haydn-kernel-bakasu>
- 分支：`haydn/stable`
- 提交：`<commit>`
- 构建 run：`<run url>`
- SHA256：`<sha256>`
- 适用设备：Redmi K40 Pro / Pro+（haydn）

必须包含“禁止混刷”：

- 不刷 Nova 线包
- 不与 `com.sukisu.nova` 管理器混装
- 切换线前卸载旧管理器并重启
- 不把不同 tag 的 AK3、clean boot、Image、APK 混用

正式资产必须按 [`RELEASE-STANDARD.md`](RELEASE-STANDARD.md) 发齐：

- AnyKernel3
- clean boot
- BakaSU 上游配套 APK（来源确认前不宣称资产齐全）
- Image
- config
- build log
- `RELEASE-<sha>.md`
- `SHA256SUMS`
