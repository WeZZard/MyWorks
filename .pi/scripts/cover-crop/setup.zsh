#!/usr/bin/env zsh
# Bootstrap the cover-crop SAM 2 environment on Apple Silicon.
# Creates a local venv, installs PyTorch + SAM 2 (MPS build, no CUDA), and
# downloads the sam2_hiera_large checkpoint.
#
# Run once:  zsh scripts/cover-crop/setup.zsh
set -euo pipefail

HERE="${0:A:h}"
cd "$HERE"

VENV="$HERE/.venv"
CKPT_DIR="$HERE/checkpoints"
SAM2_SRC="$HERE/sam2-src"

if [ -d "$VENV" ] && [ "$1" != "--force" ]; then
  echo ">> venv already exists at $VENV (run with --force to rebuild)"
else
  # SAM 2 is tested through CPython 3.11/3.12/3.13. 3.14 is too new.
  PY=""
  for cand in python3.11 python3.12 python3.13; do
    command -v "$cand" >/dev/null 2>&1 && { PY="$cand"; break; }
  done
  [ -z "$PY" ] && { echo "!! no python3.11/3.12/3.13 found" >&2; exit 1; }
  echo ">> using $PY; creating venv at $VENV"
  "$PY" -m venv "$VENV"
fi

source "$VENV/bin/activate"

echo ">> upgrading pip / wheel / setuptools"
pip install --upgrade pip wheel setuptools >/dev/null

echo ">> installing PyTorch (MPS-capable CPU wheel) + deps"
pip install --upgrade "torch>=2.5.1" "torchvision>=0.20.1" "numpy>=1.26" "pillow>=10.4"

if [ ! -d "$SAM2_SRC" ]; then
  echo ">> cloning facebookresearch/sam2"
  git clone --depth 1 https://github.com/facebookresearch/sam2.git "$SAM2_SRC"
else
  echo ">> sam2-src already present; pulling latest"
  git -C "$SAM2_SRC" pull --ff-only
fi

echo ">> installing SAM 2 in editable mode (no CUDA extension)"
# The MPS fixes live in the latest repo. Build without the CUDA extension.
cd "$SAM2_SRC"
# Remove any stale built .so so the non-CUDA build is used.
find sam2 -name "*.so" -delete 2>/dev/null || true
SAM2_BUILD_CUDA=0 pip install -e . >/dev/null
cd "$HERE"

mkdir -p "$CKPT_DIR"
CKPT="$CKPT_DIR/sam2_hiera_large.pt"
if [ ! -f "$CKPT" ]; then
  echo ">> downloading sam2_hiera_large checkpoint (~1.1GB)"
  curl -L -o "$CKPT" \
    "https://dl.fbaipublicfiles.com/segment_anything_2/072824/sam2_hiera_large.pt"
else
  echo ">> checkpoint already present at $CKPT"
fi

echo ">> verifying import"
python - <<'PY'
import torch
print("torch", torch.__version__, "| mps available:", torch.backends.mps.is_available())
from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor
print("sam2 import OK")
PY

echo ">> setup complete."