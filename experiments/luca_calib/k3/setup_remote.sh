#!/usr/bin/env bash
# K3 (prereg v5c): set up a fresh Ubuntu 24.04 machine. Run from ~/luca_calib on the machine.
set -euxo pipefail
sudo apt-get update -q
sudo DEBIAN_FRONTEND=noninteractive apt-get install -yq build-essential cmake git libboost-all-dev libopenmpi-dev rsync bzip2 curl
cd ~ && curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xj bin/micromamba
~/bin/micromamba create -y -q -p ~/mamba/envs/phylo -c conda-forge -c bioconda python=3.11 ete3=3.1.3 numpy scipy six bayesian-optimization=1.4.3 networkx=3.6.1 "iqtree>=3"
~/mamba/envs/phylo/bin/pip install -q pyvolve==1.1.0 biopython==1.88
IQ=$(ls ~/mamba/envs/phylo/bin/iqtree3 ~/mamba/envs/phylo/bin/iqtree2 ~/mamba/envs/phylo/bin/iqtree 2>/dev/null | head -1 || true)
[ "$IQ" = "$HOME/mamba/envs/phylo/bin/iqtree3" ] || ln -sf "$IQ" ~/mamba/envs/phylo/bin/iqtree3
cd ~/luca_calib
cmake -S ext/ale -B ext/ale_build -DCMAKE_BUILD_TYPE=Distribution -DALE_ENV_PREFIX=/usr \
  -DCMAKE_PROJECT_ale_INCLUDE="$PWD/pipeline/local/ale_boost_shim.cmake" -DCMAKE_POLICY_VERSION_MINIMUM=3.5
make -C ext/ale_build -j"$(nproc)" ALEobserve ALEml_undated
{ echo "ale_commit $(git -C ext/ale rev-parse HEAD 2>/dev/null || echo b59dfaf)"; g++ --version | head -1
  dpkg -s libboost-dev | grep Version; ~/mamba/envs/phylo/bin/iqtree3 --version | head -1; uname -a
  sha256sum ext/ale_build/bin/ALEobserve ext/ale_build/bin/ALEml_undated; } > ~/luca_calib/BUILD_INFO_aws.txt
echo SETUP_OK
