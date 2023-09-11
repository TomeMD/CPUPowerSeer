#!/bin/bash

NODES=("compute0" "compute2") #"core_i9" "ryzen_3900x"
TRAIN_LOADS=("Group_P" "Group_P_and_L" "Group_1P_2L" "Spread_P" "Spread_P_and_L" "General") #TESTS=("Only_P" "Test_P_and_L" "Test_1P_2L")
LOAD_TYPE="geekbench"
TEST_BOOL=1
TEST_LOAD="npb"
TEST_KERNELS=("IS" "FT" "MG" "CG" "BT")

for NODE in "${NODES[@]}"; do
 	LOG_DIR=log/${NODE}/${LOAD_TYPE}
  TEST_DIR=log/${NODE}/${TEST_LOAD}

  rm -f "${LOG_DIR}/General.timestamps"

  # Generate one model per experiment
 	for TRAIN_LOAD in "${TRAIN_LOADS[@]}"; do

 	  for TEST_KERNEL in "${TEST_KERNELS[@]}"; do
      OUT_DIR=out/${NODE}/${LOAD_TYPE}/${TRAIN_LOAD}/${TEST_KERNEL}/
      mkdir -p "${OUT_DIR}"
      if [ $TEST_BOOL -gt 0 ]; then
        python3 main.py -n "${TRAIN_LOAD}" -t "${LOG_DIR}/${TRAIN_LOAD}.timestamps" -a "${TEST_DIR}/${TEST_KERNEL}.timestamps" -o "${OUT_DIR}"
      else
        python3 main.py -n "${TRAIN_LOAD}" -t "${LOG_DIR}/${TRAIN_LOAD}.timestamps" -o "${OUT_DIR}"
      fi
 		done

 		if [ "$TRAIN_LOAD" != "General" ]; then
 		  cat "${LOG_DIR}/${TRAIN_LOAD}.timestamps" >> "${LOG_DIR}/General.timestamps"
 		fi
 	done

done
