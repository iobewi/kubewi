#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT="${SCRIPT_DIR}/cidata.iso"

if ! command -v xorriso &>/dev/null && ! command -v genisoimage &>/dev/null; then
  echo "Erreur : xorriso ou genisoimage requis"
  echo "  sudo apt install xorriso   # ou genisoimage"
  exit 1
fi

if command -v xorriso &>/dev/null; then
  xorriso -as mkisofs \
    -output "$OUTPUT" \
    -volid CIDATA \
    -joliet -rock \
    -input-charset utf-8 \
    "${SCRIPT_DIR}/user-data" \
    "${SCRIPT_DIR}/meta-data"
else
  genisoimage \
    -output "$OUTPUT" \
    -volid CIDATA \
    -joliet -rock \
    -input-charset utf-8 \
    "${SCRIPT_DIR}/user-data" \
    "${SCRIPT_DIR}/meta-data"
fi

echo "ISO créée : $OUTPUT"
echo "Copier cidata.iso à la racine de la clé Ventoy."
