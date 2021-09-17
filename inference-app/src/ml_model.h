/*
 * Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 * 
 */

#ifndef _ML_MODEL_H_
#define _ML_MODEL_H_

#include "tensorflow/lite/micro/all_ops_resolver.h"
#include "tensorflow/lite/micro/micro_error_reporter.h"
#include "tensorflow/lite/micro/micro_interpreter.h"

class MLModel {
    public:
        MLModel(const unsigned char tflite_model[], int tensor_arena_size);
        virtual ~MLModel();

        int init();
        void* input_data();
        float predict();

        float input_scale() const;
        int32_t input_zero_point() const;
    private:
        const unsigned char* _tflite_model;
        int _tensor_arena_size;

        uint8_t* _tensor_arena;
        tflite::MicroErrorReporter _error_reporter;
        const tflite::Model* _model;
        tflite::MicroInterpreter* _interpreter;
        TfLiteTensor* _input_tensor;
        TfLiteTensor* _output_tensor;

        tflite::AllOpsResolver _opsResolver;
};

#endif
