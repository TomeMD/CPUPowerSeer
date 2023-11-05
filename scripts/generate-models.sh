#!/bin/bash

NODES=("compute2")
TRAIN_LOADS=("Group_P") #"Group_P" "Group_P_and_L" "Group_1P_2L" "Spread_P" "Spread_P_and_L" "General")
LOAD_TYPE="all"
LOAD_EXECUTION="1"
TEST_LOAD="npb_btio"
TEST_LOAD_EXECUTION="1"
TEST_KERNELS=("IS" "FT" "MG" "CG" "BT" "BT_IO") #
TEST_BOOL=1

for NODE in "${NODES[@]}"; do
 	LOG_DIR=log/${NODE}/${LOAD_TYPE}/${LOAD_EXECUTION}
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
 	for TRAIN_LOAD in "${TRAIN_LOADS[@]}"; do
      OUT_DIR=out/${NODE}/${LOAD_TYPE}/${TRAIN_LOAD}/${LOAD_EXECUTION}
      TRAIN_FILE="${LOG_DIR}/${TRAIN_LOAD}.timestamps"
      rm -rf "${OUT_DIR}"
      if [ $TEST_BOOL -gt 0 ]; then
        cpu-power-model -b "${BUCKET}" -n "${TRAIN_LOAD}" -m user_load,system_load,freq -t "${TRAIN_FILE}" -a "${TEST_FILES}" -o "${OUT_DIR}"
      else
        cpu-power-model -b "${BUCKET}" -n "${TRAIN_LOAD}" -m load,freq -t "${TRAIN_FILE}" -o "${OUT_DIR}"
      fi
 	done
done
