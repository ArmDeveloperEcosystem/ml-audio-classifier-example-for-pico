/*
 * Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 * 
 */

#include "tensorflow/lite/schema/schema_generated.h"
#include "tensorflow/lite/version.h"

#include "ml_model.h"

MLModel::MLModel(const unsigned char tflite_model[], int tensor_arena_size) :
    _tflite_model(tflite_model),
    _tensor_arena_size(tensor_arena_size),
    _tensor_arena(NULL),
    _model(NULL),
    _interpreter(NULL),
    _input_tensor(NULL),
    _output_tensor(NULL)
{
}

MLModel::~MLModel()
{
    if (_interpreter != NULL) {
        delete _interpreter;
        _interpreter = NULL;
    }

    if (_tensor_arena != NULL) {
        delete [] _tensor_arena;
        _tensor_arena = NULL;
    }
}

int MLModel::init()
{
    _model = tflite::GetModel(_tflite_model);
    if (_model->version() != TFLITE_SCHEMA_VERSION) {
        TF_LITE_REPORT_ERROR(&_error_reporter,
                            "Model provided is schema version %d not equal "
                            "to supported version %d.",
                            _model->version(), TFLITE_SCHEMA_VERSION);

        return 0;
    }

    _tensor_arena = new uint8_t[_tensor_arena_size];
    if (_tensor_arena == NULL) {
        TF_LITE_REPORT_ERROR(&_error_reporter,
                            "Failed to allocate tensor area of size %d",
                            _tensor_arena_size);
        return 0;
    }

    _interpreter = new tflite::MicroInterpreter(
        _model, _opsResolver,
        _tensor_arena, _tensor_arena_size,
        &_error_reporter
    );
    if (_interpreter == NULL) {
        TF_LITE_REPORT_ERROR(&_error_reporter,
                            "Failed to allocate interpreter");
        return 0;
    }

    TfLiteStatus allocate_status = _interpreter->AllocateTensors();
    if (allocate_status != kTfLiteOk) {
        TF_LITE_REPORT_ERROR(&_error_reporter, "AllocateTensors() failed");
        return 0;
    }

    _input_tensor = _interpreter->input(0);
    _output_tensor = _interpreter->output(0);

    return 1;
}

void* MLModel::input_data()
{
    if (_input_tensor == NULL) {
        return NULL;
    }

    return _input_tensor->data.data;
}

float MLModel::predict()
{
    TfLiteStatus invoke_status = _interpreter->Invoke();

    if (invoke_status != kTfLiteOk) {
        return NAN;
    }

    float y_quantized = _output_tensor->data.int8[0];
    float y = (y_quantized - _output_tensor->params.zero_point) * _output_tensor->params.scale;

    return y;
}

float MLModel::input_scale() const
{
    if (_input_tensor == NULL) {
        return NAN;
    }

    return _input_tensor->params.scale;
}

int32_t MLModel::input_zero_point() const
{
    if (_input_tensor == NULL) {
        return 0;
    }

    return _input_tensor->params.zero_point;
}