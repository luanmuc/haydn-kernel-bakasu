#!/usr/bin/env python3
"""把 build.log 分成：真实 error、编译 warning、已知噪音（白名单）。

用法：
  python3 scripts/ci/classify-build-log.py build.log --summary
  python3 scripts/ci/classify-build-log.py build.log --errors --max 60

退出码始终为 0（CI 里只做报告，构建成败仍由 make 退出码决定）。
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass

ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")

# 真实 error：只认这些构建/链接/系统级失败特征。
ERROR_PATTERNS = [
    ("compiler error", re.compile(r"\berror:")),
    ("fatal error", re.compile(r"\bfatal error:")),
    ("undefined reference", re.compile(r"\bundefined reference to\b")),
    ("linker error", re.compile(r"\bld: cannot\b")),
    ("clang error", re.compile(r"\bclang: error:")),
    ("make failure", re.compile(r"\bmake(?:\[\d+\])?: \*\*\*")),
    ("KSU hook fatal", re.compile(r"TP hooks are incompatible with Non-GKI/GKI 1\.0 kernels\.+ +Stop\.?")),
    ("killed", re.compile(r"\bKilled\b")),
    ("disk full", re.compile(r"No space left on device")),
    ("make Error N", re.compile(r"\bError [0-9]+\b")),
]

# 已知噪音：必须精确匹配到具体来源，不做“not found / warning 全放行”。
WHITELIST = [
    (
        "SUSFS inline hook 的已知提示：检测到 manual guard，不代表编译失败",
        re.compile(r"ReSukiSU/susfs_inline: WARNING: Your build maybe broken\.?\s*$"),
    ),
    (
        "上一条提示的配套说明，非错误",
        re.compile(r"ReSukiSU/susfs_inline: - If you have any issue, please check your hook before submit an issue"),
    ),
    (
        "5.4 内核没有 post_execve 挂点，KSU 走 execveat 兼容路径，属预期",
        re.compile(r"ReSukiSU/(?:compat|manual_hook): ksu_handle_post_execve hook not found"),
    ),
]

WARNING_RE = re.compile(r"\bwarning:")


@dataclass
class Hit:
    line_no: int
    text: str
    reason: str


def clean(line: str) -> str:
    return ANSI_RE.sub("", line).rstrip("\n")


def classify(line: str) -> tuple[str, str] | None:
    for reason, pattern in WHITELIST:
        if pattern.search(line):
            return "noise", reason
    for reason, pattern in ERROR_PATTERNS:
        if pattern.search(line):
            return "error", reason
    if WARNING_RE.search(line):
        return "warning", "compiler warning"
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", help="build.log 路径")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--summary", action="store_true", help="输出 Markdown 汇总")
    group.add_argument("--errors", action="store_true", help="只输出真实 error 行")
    parser.add_argument("--max", type=int, default=60, help="--errors 最多输出多少行")
    parser.add_argument("--plain", action="store_true", help="配合 --errors：只输出原始行，不加 Markdown 围栏")
    args = parser.parse_args()

    errors: list[Hit] = []
    warnings: list[Hit] = []
    noises: list[Hit] = []

    try:
        with open(args.log, encoding="utf-8", errors="ignore") as f:
            for no, raw in enumerate(f, 1):
                line = clean(raw)
                kind = classify(line)
                if not kind:
                    continue
                bucket, reason = kind
                hit = Hit(no, line, reason)
                if bucket == "error":
                    errors.append(hit)
                elif bucket == "warning":
                    warnings.append(hit)
                else:
                    noises.append(hit)
    except OSError as exc:
        print(f"读取日志失败: {exc}", file=sys.stderr)
        return 0

    if args.errors:
        if args.plain:
            if not errors:
                print("(未匹配到真实 error；已知噪音已排除)")
                return 0
            for hit in errors[: args.max]:
                print(f"{hit.line_no}: {hit.text}")
            if len(errors) > args.max:
                print(f"... 其余 {len(errors) - args.max} 行未显示")
            return 0
        print("## 真实 error（已排除已知噪音）")
        print("")
        if not errors:
            print("(未匹配到真实 error；已知噪音已排除)")
            return 0
        print("```")
        for hit in errors[: args.max]:
            print(f"{hit.line_no}: {hit.text}")
        if len(errors) > args.max:
            print(f"... 其余 {len(errors) - args.max} 行未显示")
        print("```")
        return 0

    print("## 构建日志分级")
    print("")
    print("| 类别 | 数量 |")
    print("|---|---|")
    print(f"| 真实 error | {len(errors)} |")
    print(f"| 编译 warning | {len(warnings)} |")
    print(f"| 已知噪音（白名单） | {len(noises)} |")
    print("")
    if errors:
        print(f"> 有 {len(errors)} 条真实 error，构建失败属预期。")
    else:
        print("> 未发现真实 error。")
    if noises:
        print("")
        print("已知噪音明细（最多 5 条）：")
        print("")
        for hit in noises[:5]:
            text = hit.text if len(hit.text) <= 180 else hit.text[:177] + "..."
            print(f"- 第 {hit.line_no} 行：`{text}`")
            print(f"  - 归类：{hit.reason}")
        if len(noises) > 5:
            print(f"- 其余 {len(noises) - 5} 条同类噪音未展开")
    return 0


if __name__ == "__main__":
    sys.exit(main())
