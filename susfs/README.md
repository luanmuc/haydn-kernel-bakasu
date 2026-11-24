# SUSFS v2.3.0 基线（Linux 5.4 / haydn）

> **本目录不参与编译**，只用于长期维护：记录来源、校验漂移、保存可复现补丁。

## 基线锚点

- Git 提交：`87137c7810055837e92c5138b4351d0820f44fcc`（`fs: upgrade SuSFS from v2.1.0 to v2.3.0`）
- Git tag：`susfs-baseline-v2.3.0`（指向上述提交）
- 内核版本：5.4.302 / haydn
- 本地 SUSFS 版本：`include/linux/susfs.h` → `v2.3.0`

## 来源与许可证

- 上游：SUSFS v2.3.0（作者 `simonpunk`，官方仓库在 GitLab；GitHub 镜像 `Zhanfg/susfs4ksu`）
- 5.4 适配：由上游作者 `hhsbjbsj` 手工 port 到 5.4，本地以 `87137c781` 固化
- 许可证：GPL-3.0-or-later（与上游一致）

## 基线文件（10 个）

| 文件 | 作用 |
|---|---|
| `fs/susfs.c` | SUSFS 主体实现 |
| `include/linux/susfs.h` | 对外 API / 版本号 |
| `include/linux/susfs_def.h` | 常量、结构体、flag |
| `fs/notify/fdinfo.c` | fdinfo 伪装 |
| `fs/proc/fd.c` | fd 重验证 |
| `fs/proc/task_mmu.c` | maps 伪装（SRCU） |
| `fs/proc_namespace.c` | mountinfo/mounts 伪装 |
| `fs/stat.c` | stat/statx kstat 伪装 |
| `fs/statfs.c` | statfs 伪装 |
| `fs/super.c` | KSU 匿名块设备隔离 |

编译入口：`fs/Makefile` 的 `obj-$(CONFIG_KSU_SUSFS) += susfs.o`；所有调用点均有 `CONFIG_KSU_SUSFS` guard。

## 目录说明

```
susfs/
├── README.md                 # 本文件
├── baseline.sha256           # 10 个文件的指纹清单
├── patches/
│   └── 0001-v2.1.0-to-v2.3.0.patch  # 由 87137c781 导出（1750 行）
└── scripts/
    └── check-baseline.sh     # 校验工作树是否仍等于基线
```

## 校验

```bash
bash susfs/scripts/check-baseline.sh
```

输出全部 `OK` 表示工作树与基线一致；有任何 `FAILED` 说明有人改了 SUSFS 相关文件——要么是有意升级（需更新基线），要么是误改（需回退）。

## 更新基线的规则

1. 只在 `haydn/test` 上做 SUSFS 变更
2. 通过 SUSFS=y / SUSFS=n 双构建 + 真机验证后，才合入 `haydn/stable`
3. 合并后重新生成 `baseline.sha256`，把 tag `susfs-baseline-vN` 打到新的基线提交
4. 不追新功能，只接 KSU 新 API、实测 bug、稳定性/安全修复（详见 `PORTING.md`）
