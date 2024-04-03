#! /usr/bin/env bash

set -ex

LR=1e-5
NUM_GPUS=4
MAX_SOURCE_LEN=2048
MAX_TARGET_LEN=512
DEV_BATCH_SIZE=4
GRAD_ACCUMULARION_STEPS=4
MAX_STEP=1000
SAVE_INTERVAL=500

RUN_NAME=soayllama_v2-1_7b
# BASE_MODEL_PATH=/data/wangyuanchun/AMinerS/output/soayllama_v2_7b/checkpoint-1500
BASE_MODEL_PATH=/data2/wangyuanchun/home_mzy/MODELS/CodeLlama-7b-Instruct-hf
# BASE_MODEL_PATH=/data2/wangyuanchun/models/base_ckpt/llama2/CodeLlama-13b-Instruct-hf
# BASE_MODEL_PATH=/data2/wangyuanchun/models/base_ckpt/llama2/llama-2-7b-chat-hf

DATASET_PATH=/data/wangyuanchun/AMinerS/soayBench_v1-2-5-train-indent/merge_shuf.jsonl

DATESTR=`date +%Y%m%d-%H%M%S`
OUTPUT_DIR=/data/wangyuanchun/AMinerS/output/${RUN_NAME}
MASTER_PORT=$(shuf -n 1 -i 10000-65535)

mkdir -p $OUTPUT_DIR

export CUDA_VISIBLE_DEVICES=2,3,4,5

torchrun --standalone --nnodes=1 --nproc_per_node=$NUM_GPUS finetune.py \
    --train_format input-output \
    --train_file $DATASET_PATH \
    --preprocessing_num_workers 1 \
    --model_name_or_path $BASE_MODEL_PATH \
    --output_dir $OUTPUT_DIR \
    --max_source_length $MAX_SOURCE_LEN \
    --max_target_length $MAX_TARGET_LEN \
    --per_device_train_batch_size $DEV_BATCH_SIZE \
    --gradient_accumulation_steps $GRAD_ACCUMULARION_STEPS \
    --max_steps $MAX_STEP \
    --logging_steps 1 \
    --save_steps $SAVE_INTERVAL \
    --learning_rate $LR \
    --bf16 \
    --deepspeed config/deepspeed.json 2>&1 | tee ${OUTPUT_DIR}/train.log

# bash inference.sh