#!/usr/bin/env bash
# Build a self-contained Linux desktop bundle.  Run from the repository root.
set -Eeuo pipefail

project_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
output_dir=${1:-"$project_root/dist"}
version=$(python3 -c 'import pathlib, re, sys; print(re.search(r"^version = \"([^\"]+)\"", pathlib.Path(sys.argv[1]).read_text(), re.M).group(1))' "$project_root/pyproject.toml")
work_dir=$(mktemp -d)
app_dir="$work_dir/AnimLoid.AppDir"
cleanup() { rm -rf "$work_dir"; }
trap cleanup EXIT

mkdir -p "$output_dir" "$app_dir/usr/bin" "$app_dir/usr/lib"

python3 -m PyInstaller \
  --noconfirm --clean --windowed \
  --name AnimLoid \
  --distpath "$work_dir/dist" \
  --workpath "$work_dir/build" \
  --specpath "$work_dir" \
  --collect-all weeb_cli \
  --collect-all PyQt5 \
  "$project_root/gui_main.py"

cp -a "$work_dir/dist/AnimLoid" "$app_dir/usr/lib/AnimLoid"
cp "$project_root/packaging/linux/AnimLoid.desktop" "$app_dir/AnimLoid.desktop"
cp "$project_root/packaging/linux/animloid.svg" "$app_dir/animloid.svg"
install -m 755 "$project_root/packaging/linux/AppRun" "$app_dir/AppRun"

output_file="$output_dir/AnimLoid-${version}-x86_64.AppImage"
appimagetool --appimage-extract-and-run "$app_dir" "$output_file"
chmod +x "$output_file"
