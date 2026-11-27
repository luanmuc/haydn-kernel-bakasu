#!/usr/bin/env bash
# 为正式 Release 资产目录生成 SHA256SUMS（不覆盖已有文件，除 SHA256SUMS 外全部纳入）。
# 用法：bash scripts/ci/make-release-sha256sums.sh <assets_dir>
set -euo pipefail

ASSETS_DIR="${1:?用法: make-release-sha256sums.sh <assets_dir>}"
[ -d "$ASSETS_DIR" ] || { echo "资产目录不存在: $ASSETS_DIR" >&2; exit 1; }

cd "$ASSETS_DIR"
tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT
find . -maxdepth 1 -type f ! -name 'SHA256SUMS' -print0 \
  | sort -z \
  | xargs -0 -r sha256sum > "$tmp"
mv "$tmp" SHA256SUMS
echo "已生成: $ASSETS_DIR/SHA256SUMS"
cat SHA256SUMS
