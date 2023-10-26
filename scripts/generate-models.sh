#!/bin/bash

NODES=("compute2" "compute4")
TRAIN_LOADS=("General") #"Group_P" "Group_P_and_L" "Group_1P_2L" "Spread_P" "Spread_P_and_L" "General")
LOAD_TYPE="all"
LOAD_EXECUTION="2"
TEST_BOOL=1
TEST_LOAD="npb"
TEST_LOAD_EXECUTION="1"
TEST_KERNELS=("IS" "FT" "MG" "CG" "BT")

for NODE in "${NODES[@]}"; do
 	LOG_DIR=log/${NODE}/${LOAD_TYPE}/${LOAD_EXECUTION}
  TEST_DIR=log/${NODE}/${TEST_LOAD}/${TEST_LOAD_EXECUTION}
  BUCKET=${NODE}
  #BUCKET="glances"

  # Generate one model per experiment
 	for TRAIN_LOAD in "${TRAIN_LOADS[@]}"; do

 	  for TEST_KERNEL in "${TEST_KERNELS[@]}"; do
      OUT_DIR=out/${NODE}/${LOAD_TYPE}/${TRAIN_LOAD}/${TEST_KERNEL}

      mkdir -p "${OUT_DIR}"
      rm -rf "${OUT_DIR}"/img/*
      if [ $TEST_BOOL -gt 0 ]; then
        python3 main.py -i -b ${BUCKET} -n "${TRAIN_LOAD}" -t "${LOG_DIR}/${TRAIN_LOAD}.timestamps" -m load,freq -a "${TEST_DIR}/${TEST_KERNEL}.timestamps" -o "${OUT_DIR}"
      else
        python3 main.py -b ${BUCKET} -n "${TRAIN_LOAD}" -t "${LOG_DIR}/${TRAIN_LOAD}.timestamps" -o "${OUT_DIR}"
      fi
 		done

 	done
done
