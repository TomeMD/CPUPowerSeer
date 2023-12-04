#!/bin/bash
# Script to automate multiple models generation. Run to generate models for specified NODES using TRAIN_LOAD on specific
# TRAIN_LOAD_EXECUTION using TRAIN_CORES_DISTRIBUTION. Test the model with TEST_KERNELS from TEST_LOAD on specific
# TEST_LOAD_EXECUTION.
#NODES=("compute2" "compute3" "compute4") # Nodes where load is executed
#
#TRAIN_LOAD="all_sysinfo_mix" # Train load
#TRAIN_LOAD_EXECUTION="dft" # Useful to manage different execution from same train load
#TRAIN_CORES_DISTRIBUTION=("General") # Cores distribution used while running train load
#
#TEST_LOAD="smusket" # Test load
#TEST_LOAD_EXECUTION="dft" # Useful to manage different execution from same test load
#TEST_KERNELS=("Spark_Smusket") # List of test kernels
NODES=("compute2" "compute3" "compute4")

TRAIN_LOAD="all"
TRAIN_LOAD_EXECUTION="dft" # dft = default
TRAIN_CORES_DISTRIBUTION=("Group_PP_LL") #"Group_P" "Group_P_and_L" "Group_1P_2L" "Spread_P" "Spread_P_and_L" "General")

TEST_LOAD="all"
TEST_LOAD_EXECUTION="dft"
#TEST_KERNELS=("IS" "FT" "MG" "CG" "BT" "BT_IO")

for NODE in "${NODES[@]}"; do
 	TRAIN_DIR=log/${NODE}/train/${TRAIN_LOAD}/${TRAIN_LOAD_EXECUTION}
  TEST_DIR=log/${NODE}/test/${TEST_LOAD}/${TEST_LOAD_EXECUTION}
  BUCKET=${NODE}

  TEST_FILES=""
  for TEST_FILE in $(find "${TEST_DIR}" -name "*.timestamps"); do
    if [ -n "${TEST_FILES}" ]; then
      TEST_FILES="${TEST_FILES},${TEST_FILE}"
    else
      TEST_FILES+="${TEST_FILE}"
    fi
  done

  # Generate one model per specified cores distribution
 	for CORES_DISTRIBUTION in "${TRAIN_CORES_DISTRIBUTION[@]}"; do
      OUT_DIR=out/${NODE}/${TRAIN_LOAD}_${TRAIN_LOAD_EXECUTION}-${CORES_DISTRIBUTION}/${TEST_LOAD}_${TEST_LOAD_EXECUTION}
      TRAIN_FILE="${TRAIN_DIR}/${CORES_DISTRIBUTION}.timestamps"
      rm -rf "${OUT_DIR}"
      cpu-power-model -b "${BUCKET}" -n "${CORES_DISTRIBUTION}" -m user_load,system_load,freq -t "${TRAIN_FILE}" -a "${TEST_FILES}" -o "${OUT_DIR}"
 	done
done
