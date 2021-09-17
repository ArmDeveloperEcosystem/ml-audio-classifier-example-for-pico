/*
 * Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 * 
 */

#include "dsp_pipeline.h"

DSPPipeline::DSPPipeline(int fft_size) :
    _fft_size(fft_size),
    _hanning_window(NULL)
{
}

DSPPipeline::~DSPPipeline()
{
    if (_hanning_window != NULL) {
        delete [] _hanning_window;

        _hanning_window = NULL;
    }
}

int DSPPipeline::init()
{
    _hanning_window = new int16_t[_fft_size];
    if (_hanning_window == NULL) {
        return 0;
    }
    
    for (size_t i = 0; i < _fft_size; i++) {
       float32_t f = 0.5 * (1.0 - arm_cos_f32(2 * PI * i / _fft_size));

       arm_float_to_q15(&f, &_hanning_window[i], 1);
    }

    if (arm_rfft_init_q15(&_S_q15, _fft_size, 0, 1) != ARM_MATH_SUCCESS) {
        return 0;
    }

    return 1;
}

void DSPPipeline::calculate_spectrum(const int16_t* input, int8_t* output, int32_t scale_divider, float scale_zero_point)
{
    int16_t windowed_input[_fft_size];
    int16_t fft_q15[_fft_size * 2];
    int16_t fft_mag_q15[_fft_size / 2 + 1];

    // apply the DSP pipeline: Hanning Window + FFT
    arm_mult_q15(_hanning_window, input, windowed_input, _fft_size);
    arm_rfft_q15(&_S_q15, windowed_input, fft_q15);
    arm_cmplx_mag_q15(fft_q15, fft_mag_q15, (_fft_size / 2) + 1);

    int8_t* dst = output;

    for (int j = 0; j < ((_fft_size / 2) + 1); j++) {
        *dst++ = __SSAT((fft_mag_q15[j] / scale_divider) + scale_zero_point, 8);
    }
}

void DSPPipeline::shift_spectrogram(int8_t* spectrogram, int shift_amount, int spectrogram_width)
{
    int spectrogram_height = _fft_size / 2 + 1;

    memmove(spectrogram, spectrogram + (spectrogram_height * shift_amount), spectrogram_height * (spectrogram_width - shift_amount) * sizeof(spectrogram[0]));
}
