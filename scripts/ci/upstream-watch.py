#!/usr/bin/env python3
"""BakaSU 日巡：只报告需要人看的变化，不编译、不 bump、不建分支。

- 新 tag / Release：一定报告
- main HEAD 相对 pin：只有 kernel/ 路径有变化才报告
- manager、翻译、CI、文档变化：忽略

用法：
  python3 scripts/ci/upstream-watch.py --report upstream-watch.md --json upstream-watch.json

退出码：0 = 巡检完成（无论有没有变化）；1 = 查询失败。
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API_URL = os.environ.get("GITHUB_API_URL", "https://api.github.com").rstrip("/")
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "haydn-upstream-watch/1.0",
}
if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"

ISSUE_TITLE = "[upstream-watch] BakaSU 内核相关变更"


def api_get(path: str):
    url = f"{API_URL}{path}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        raise RuntimeError(f"GET {path} -> HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"GET {path} -> {exc}") from exc


def short(sha: str) -> str:
    return (sha or "")[:9]


def build_issue(cfg: dict, state: dict) -> str:
    b = cfg
    lines = [
        "<!-- upstream-watch:baksu -->",
        "# BakaSU 日巡：自上次审计有新变化",
        "",
        f"- 巡检时间（UTC）：`{state['checked_at']}`",
        f"- tag pin：`{b['pinned_ref']}` / `{short(b['pinned_commit'])}`",
        f"- 上次审计基线：`{short(state['base'])}`（{state['audited_at']}）",
        f"- 上游 HEAD：`{short(state['head'])}`（{state['head_date']}）",
        f"- 最新 tag：`{state['latest_tag'] or '无'}`",
        f"- 最新 Release：`{state['latest_release'] or '无'}`",
        f"- 距上次审计：**{state['delta_by']}** 个提交",
        f"- 距 tag 基线：**{state['ahead_by']}** 个提交",
        f"- 估算版本码：**{state['estimated_version_code']}**（按 30700 + 距 tag 提交数，仅参考）",
        f"- 本次新命中 kernel 文件：**{len(state['relevant_files'])}**",
    ]
    if state["files_truncated"]:
        lines.append("- 注意：GitHub compare 的文件列表已截断（300 条），实际文件可能更多")
    lines += [
        "",
        "## 触发原因",
        "",
    ]
    lines += [f"- {r}" for r in state["reasons"]]
    lines += [
        "",
        "## 本次新增的 kernel 相关文件（前 25 条）",
        "",
        "| 文件 | 状态 | +/− |",
        "|---|---|---|",
    ]
    for f in state["relevant_files"][:25]:
        lines.append(f"| `{f['filename']}` | {f['status']} | +{f['additions']}/−{f['deletions']} |")
    if len(state["relevant_files"]) > 25:
        lines.append(f"| ... | 其余 {len(state['relevant_files']) - 25} 个文件未展开 | |")
    lines += [
        "",
        "## 最近 kernel 提交（前 10 条）",
        "",
    ]
    for c in state["recent_kernel_commits"][:10]:
        msg = c["commit"]["message"].splitlines()[0]
        lines.append(f"- `{short(c['sha'])}` {c['commit']['author']['date'][:10]} {msg}")
    if not state["recent_kernel_commits"]:
        lines.append("- （无）")
    lines += [
        "",
        "## 月审清单",
        "",
        "- [ ] 新 tag / Release 是否已到（rc4 或正式版）",
        "- [ ] `kernel/Kconfig` 是否有新增开关",
        "- [ ] hook 选路是否变化（manual / inline / tracepoint）",
        "- [ ] 是否新增 SUSFS API 调用（对照本地 `include/linux/susfs.h`）",
        "- [ ] 版本码是否仍为 `30700 + 提交数`",
        "- [ ] 决定：跟 / 不跟 / 只回填某几个提交；记录到 `docs/upstream-log.md`",
        "",
        f"> 本次对比：https://github.com/{b['repo']}/compare/{state['base']}...{state['head']}",
        f"> 对 tag 全量对比：https://github.com/{b['repo']}/compare/{b['pinned_commit']}...{state['head']}",
        "",
        "> 本 Issue 由日巡自动维护；月审做出决定后，把 `maintenance/upstream-pins.json` 的 `audited_commit` 更新到当前 HEAD，再关闭。",
        "",
    ]
    return "\n".join(lines)


def build_quiet_report(cfg: dict, state: dict) -> str:
    lines = [
        "<!-- upstream-watch:baksu -->",
        "# BakaSU 日巡：无新变化",
        "",
        f"- 巡检时间（UTC）：`{state['checked_at']}`",
        f"- tag pin：`{cfg['pinned_ref']}` / `{short(cfg['pinned_commit'])}`",
        f"- 上次审计基线：`{short(state['base'])}`（{state['audited_at']}）",
        f"- 上游 HEAD：`{short(state['head'])}`（{state['head_date']}）",
        f"- 距上次审计：{state['delta_by']} 个提交",
        f"- 最新 tag：`{state['latest_tag'] or '无'}`",
        "",
        "## 结论",
        "",
    ]
    if state["head"] == state["base"]:
        lines.append("自上次审计以来 HEAD 没有变化。")
    elif state["delta_by"]:
        lines.append("有提交，但没有命中 `kernel/` 路径；只涉及 manager / 翻译 / CI / 文档等，不触发内核审计。")
    else:
        lines.append("没有命中 `kernel/` 路径的新提交。")
    lines.append("")
    if state["latest_tag"] and state["latest_tag"] != cfg["pinned_ref"]:
        lines += [f"- 但有新 tag：`{state['latest_tag']}`，请月审确认。", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pins", default="maintenance/upstream-pins.json")
    parser.add_argument("--report", default="upstream-watch.md")
    parser.add_argument("--json", default="upstream-watch.json")
    args = parser.parse_args()

    cfg_all = json.loads(Path(args.pins).read_text(encoding="utf-8"))
    cfg = cfg_all["baksu"]
    repo = cfg["repo"]
    branch = cfg.get("branch", "main")
    pinned = cfg["pinned_commit"]
    pinned_ref = cfg["pinned_ref"]
    watch_paths = cfg["watch_paths"]

    head_info = api_get(f"/repos/{repo}/branches/{urllib.parse.quote(branch, safe='')}")
    head = head_info["commit"]["sha"]
    head_date = head_info["commit"]["commit"]["author"]["date"][:10]

    tags = api_get(f"/repos/{repo}/tags?per_page=10")
    latest_tag = tags[0]["name"] if tags else None
    releases = api_get(f"/repos/{repo}/releases?per_page=5")
    latest_release = releases[0]["tag_name"] if releases else None

    base = cfg.get("audited_commit") or pinned
    audited_at = cfg.get("audited_at", "未审计")
    compare = api_get(f"/repos/{repo}/compare/{base}...{head}")
    files = compare.get("files", []) or []
    relevant = [
        f for f in files
        if any(f.get("filename", "").startswith(p) for p in watch_paths)
    ]
    delta_by = int(compare.get("ahead_by") or 0)

    if base != pinned:
        total_compare = api_get(f"/repos/{repo}/compare/{pinned}...{head}")
        ahead_by = int(total_compare.get("ahead_by") or 0)
    else:
        ahead_by = delta_by
    estimated_version = int(cfg.get("version_code", 0)) + ahead_by
    recent = api_get(f"/repos/{repo}/commits?sha={urllib.parse.quote(branch, safe='')}&path=kernel&per_page=10")

    reasons = []
    if latest_tag and latest_tag != pinned_ref:
        reasons.append(f"出现新 tag：`{latest_tag}`")
    if latest_release and latest_release != pinned_ref:
        reasons.append(f"出现新 Release：`{latest_release}`")
    if relevant:
        reasons.append(f"自上次审计（{short(base)}）以来，`kernel/` 路径有 {len(relevant)} 个文件变化")
    if head != base and not reasons:
        reasons.append("HEAD 有移动，但没有命中 `kernel/` 路径")

    changed = bool((latest_tag and latest_tag != pinned_ref) or (latest_release and latest_release != pinned_ref) or relevant)
    state = {
        "checked_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "base": base,
        "audited_at": audited_at,
        "head": head,
        "head_date": head_date,
        "latest_tag": latest_tag,
        "latest_release": latest_release,
        "delta_by": delta_by,
        "ahead_by": ahead_by,
        "estimated_version_code": estimated_version,
        "relevant_files": relevant,
        "recent_kernel_commits": recent,
        "files_truncated": len(files) >= 300,
        "reasons": reasons,
        "changed": changed,
    }

    report = build_issue(cfg, state) if changed else build_quiet_report(cfg, state)
    Path(args.report).write_text(report + "\n", encoding="utf-8")

    payload = {
        "component": "baksu",
        **state,
        "repo": repo,
        "pinned_ref": pinned_ref,
        "pinned_commit": pinned,
        "issue_title": ISSUE_TITLE,
    }
    Path(args.json).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as fh:
            fh.write(f"changed={'true' if changed else 'false'}\n")
            fh.write(f"estimated_version_code={estimated_version}\n")

    print(f"BakaSU: pin={short(pinned)} audited={short(base)} head={short(head)} "
          f"delta={delta_by} ahead={ahead_by} kernel_files={len(relevant)} changed={str(changed).lower()}")
    print(f"report: {args.report}")
    return 0


    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"upstream-watch failed: {exc}", file=sys.stderr)
        sys.exit(1)
