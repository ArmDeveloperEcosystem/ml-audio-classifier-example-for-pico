/*
 * Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 * 
 */

#ifndef _DSP_PIPELINE_H_
#define _DSP_PIPELINE_H_

#include "arm_math.h"

class DSPPipeline {
    public:
        DSPPipeline(int fft_size);
        virtual ~DSPPipeline();

        int init();
        void calculate_spectrum(const int16_t* input, int8_t* output, int32_t scale_divider, float scale_zero_point);
        void shift_spectrogram(int8_t* spectrogram, int shift_amount, int spectrogram_width);

    private:
        int _fft_size;
        int16_t* _hanning_window;
        arm_rfft_instance_q15 _S_q15;
};

#endif
