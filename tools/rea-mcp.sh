#!/usr/bin/env bash
# Launch the repo-local REA MCP server (stdio) with the repo-local toolchain.
#
# Node and the JDK are pinned by nix gc roots inside the repo (.gc-roots/,
# gitignored, machine-specific). The rea-agents package is installed from this
# repo's package.json, so `npm cache clean` cannot break it.
set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# REA requires the Allegrex processor module at
# <install>/Ghidra/Extensions/ghidra-allegrex. The nix store is read-only and
# Ghidra resolves its install dir through realpath, so a symlinked mirror does
# not work; .gc-roots/ghidra-psp is a store tree with the module baked in.
export GHIDRA_INSTALL_DIR="$repo/.gc-roots/ghidra-psp/lib/ghidra"
# Force the pinned JDK: an inherited JAVA_HOME pointing at a missing path
# (e.g. /usr/lib/jvm/default) makes REA's Ghidra provider fail its java probe.
export JAVA_HOME="$repo/.gc-roots/jdk"

exec "$repo/.gc-roots/nodejs-22.23.4/bin/node" \
  "$repo/node_modules/rea-agents/scripts/rea.mjs" mcp "$@"
