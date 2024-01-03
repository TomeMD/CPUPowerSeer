#!/bin/bash
# Script to automate multiple models generation.
#   MODEL_NAMES: Names given to the models you're going to test
#   MODELS_VARS: Dictionary to link model names with the variables it use
#   MODEL_PRED_METHOD: Dictionary to link model names with the prediction method it use
#   NODES: Available nodes where data to train and test the models was previously gathered and sent to InfluxDB bucket
#          named as $NODE
#   TRAIN_LOADS: Array of comma-separated values following the format "TRAIN_LOAD,TRAIN_LOAD_EXECUTION"
#   TRAIN_CORES_DISTRIBUTION: Array from cores distributions to be used when training model
#   TEST_LOAD: Load to test the models
#   TEST_LOAD_EXECUTION: Specific execution from TEST_LOAD to test the models

MODEL_NAMES=("user_system" "user_system_freq" "user_system_freq_custom" "user_system_sumfreq")

declare -A MODEL_VARS=(
  [user_system]="user_load,system_load"
  [user_system_freq]="user_load,system_load,freq"
  [user_system_freq_custom]="user_load,system_load,freq"
  [user_system_sumfreq]="user_load,system_load,sumfreq"
)
declare -A MODEL_PRED_METHOD=(
  [user_system]="polynomial"
  [user_system_freq]="polynomial"
  [user_system_freq_custom]="freqwointeractionterms"
  [user_system_sumfreq]="freqwointeractionterms"
)

NODES=("compute2")
TRAIN_LOADS=("all_sysinfo_mix,dft" "all_sysinfo_iomix_ssd,dft")
TRAIN_CORES_DISTRIBUTION=("General")
TEST_LOAD="all"
TEST_LOAD_EXECUTION="dft"

# For each model we want to test...
for MODEL in "${MODEL_NAMES[@]}"; do
  PREDICTION_METHOD=${MODEL_PRED_METHOD[${MODEL}]}
  VARS=${MODEL_VARS[${MODEL}]}
  # For each workload to train the model being tested
  for LOAD in "${TRAIN_LOADS[@]}"; do
    IFS=',' read -r TRAIN_LOAD TRAIN_LOAD_EXECUTION <<< "${LOAD}"
    # For each available node to test the model
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
      # Train the model with each specified cores distribution of TRAIN_LOAD in TRAIN_LOAD_EXECUTION from NODE to test
      # it with TEST_LOAD in TEST_LOAD_EXECUTION
      for CORES_DISTRIBUTION in "${TRAIN_CORES_DISTRIBUTION[@]}"; do
          OUT_DIR=out/${MODEL}/${NODE}/${TRAIN_LOAD}_${TRAIN_LOAD_EXECUTION}-${CORES_DISTRIBUTION}/${TEST_LOAD}_${TEST_LOAD_EXECUTION}
          TRAIN_FILE="${TRAIN_DIR}/${CORES_DISTRIBUTION}.timestamps"
          rm -rf "${OUT_DIR}"
          powerseer -b "${BUCKET}" -n "${CORES_DISTRIBUTION}" -p ${PREDICTION_METHOD} --vars "${VARS}" -t "${TRAIN_FILE}" -o "${OUT_DIR}" -a "${TEST_FILES}"
      done
    done
  done
done
