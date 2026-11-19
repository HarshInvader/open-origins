#!/usr/bin/env bash
# Build ALE (ALEobserve, ALEml_undated) from ext/ale at the pinned commit, natively on macOS arm64.
#
# Usage: build_ale.sh [configure|build]     (default: build = configure + make)
#
# Route used, and why:
#   * ext/ale (b59dfaf) is written against the Bio++ 2.4 API. Against bioconda's Bio++ 3.0 (the only
#     Bio++ on osx-arm64) it does not compile: parenthesisToTree now returns unique_ptr, and
#     ALEml_undated's optimiser classes (Function, Optimizer, Parameter constructors) changed.
#     Porting the optimiser would change ALE's numerics, so we do not patch ALE.
#   * Instead we use ALE's own CMakeLists unmodified: it fetches Bio++ v2.4.1 from GitHub, applies
#     ALE's own build patches (ext/ale/patches), and links statically. Boost (with mpi, serialization,
#     timer) and OpenMPI come from the alebuild micromamba env (conda-forge), which CMake finds first.
#   * ale_boost_shim.cmake (injected with CMAKE_PROJECT_ale_INCLUDE) defines the header-only targets
#     Boost::algorithm and Boost::math, which conda-forge's BoostConfig lacks.
#   * Compiler: clang/clang++ from the alebuild env. make -j1 under nice -n 20 (heavy: run under the lock).
# Outputs: ext/ale_build/bin/{ALEobserve,ALEml_undated}; ext/ale_build/BUILD_INFO.txt records versions.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXP="$(cd "$HERE/../.." && pwd)"
SRC="$EXP/ext/ale"
BLD="${ALE_BUILD_DIR:-$EXP/ext/ale_build}"
ENV="${ALE_ENV:-$HOME/mamba/envs/alebuild}"
PIN="b59dfaf"
MODE="${1:-build}"

export PATH="$ENV/bin:$PATH"
export CC="$ENV/bin/clang" CXX="$ENV/bin/clang++"
export CMAKE_PREFIX_PATH="$ENV"
NICE=(nice -n 20)
command -v taskpolicy >/dev/null 2>&1 && NICE=(taskpolicy -b nice -n 20)

head=$(git -C "$SRC" rev-parse --short=7 HEAD)
[ "$head" = "$PIN" ] || { echo "ext/ale is at $head, expected $PIN" >&2; exit 1; }
[ -z "$(git -C "$SRC" status --porcelain --untracked-files=no)" ] || { echo "ext/ale has local modifications" >&2; exit 1; }

mkdir -p "$BLD"
if [ ! -f "$BLD/CMakeCache.txt" ] || [ "$MODE" = "configure" ]; then
  "${NICE[@]}" cmake -S "$SRC" -B "$BLD" \
      -DCMAKE_BUILD_TYPE=Distribution \
      -DCMAKE_PREFIX_PATH="$ENV" \
      -DCMAKE_C_COMPILER="$CC" -DCMAKE_CXX_COMPILER="$CXX" \
      -DMPI_C_COMPILER="$ENV/bin/mpicc" -DMPI_CXX_COMPILER="$ENV/bin/mpicxx" \
      -DALE_ENV_PREFIX="$ENV" \
      -DCMAKE_PROJECT_ale_INCLUDE="$HERE/ale_boost_shim.cmake" \
      -DCMAKE_POLICY_VERSION_MINIMUM=3.5
fi
[ "$MODE" = "configure" ] && { echo "configure done: $BLD"; exit 0; }

"${NICE[@]}" make -C "$BLD" -j1 ALEobserve ALEml_undated
BIN="$BLD/bin"
[ -x "$BIN/ALEobserve" ] && [ -x "$BIN/ALEml_undated" ] || { echo "ALE binaries missing" >&2; exit 1; }
{
  echo "ale_commit $(git -C "$SRC" rev-parse HEAD)"
  echo "bpp fetched by ALE CMake: v2.4.1 (+ ext/ale/patches)"
  echo "compiler $("$CXX" --version | head -1)"
  echo "boost $(grep -h 'define BOOST_LIB_VERSION' "$ENV/include/boost/version.hpp")"
  echo "openmpi $("$ENV/bin/mpirun" --version 2>/dev/null | head -1)"
  echo "uname $(uname -sm)"
  shasum -a 256 "$BIN/ALEobserve" "$BIN/ALEml_undated"
} > "$BLD/BUILD_INFO.txt"
cat "$BLD/BUILD_INFO.txt"
