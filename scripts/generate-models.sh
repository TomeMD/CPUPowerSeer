#!/bin/bash

NODES=("compute2" "compute3" "compute4")
TRAIN_LOAD="all_sysinfo_iomix_ssd"
TRAIN_LOAD_EXECUTION="dft"
TEST_LOAD="npb"
TEST_LOAD_EXECUTION="dft"
MODEL_NAMES=("General") #"Group_P" "Group_P_and_L" "Group_1P_2L" "Spread_P" "Spread_P_and_L" "General")
TEST_KERNELS=("IS" "FT" "MG" "CG" "BT" "BT_IO")

for NODE in "${NODES[@]}"; do
 	LOG_DIR=log/${NODE}/${TRAIN_LOAD}/${TRAIN_LOAD_EXECUTION}
  TEST_DIR=log/${NODE}/${TEST_LOAD}/${TEST_LOAD_EXECUTION}
  BUCKET=${NODE}

  TEST_FILES=""
  for TEST_KERNEL in "${TEST_KERNELS[@]}"; do
    if [ -n "${TEST_FILES}" ]; then
      TEST_FILES="${TEST_FILES},${TEST_DIR}/${TEST_KERNEL}.timestamps"
    else
      TEST_FILES+="${TEST_DIR}/${TEST_KERNEL}.timestamps"
    fi
  done

  # Generate one model per experiment
 	for MODEL in "${MODEL_NAMES[@]}"; do
      OUT_DIR=out/${NODE}/${TRAIN_LOAD}_${TRAIN_LOAD_EXECUTION}-${MODEL}/${TEST_LOAD}_${TEST_LOAD_EXECUTION}
      TRAIN_FILE="${LOG_DIR}/${MODEL}.timestamps"
      rm -rf "${OUT_DIR}"
      cpu-power-model -b "${BUCKET}" -n "${MODEL}" -m user_load,system_load,freq -t "${TRAIN_FILE}" -a "${TEST_FILES}" -o "${OUT_DIR}"
 	done
done
