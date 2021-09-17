cmake_minimum_required(VERSION 3.12)

# initialize pico_sdk from GIT
# (note this can come from environment, CMake cache etc)
# set(PICO_SDK_FETCH_FROM_GIT on)

# pico_sdk_import.cmake is a single file copied from this SDK
# note: this must happen before project()
include(pico_sdk_import.cmake)

project(pico_inference_app)

# initialize the Pico SDK
pico_sdk_init()

# Define ARM_CPU, CMSIS ROOT and DSP to use CMSIS-DSP
set(ARM_CPU "cortex-m0plus")
set(ROOT ${CMAKE_CURRENT_LIST_DIR}/lib/CMSIS_5)
set(DSP ${ROOT}/CMSIS/DSP)

set(CONFIGTABLE ON)
set(RFFT_Q15_256 ON)
set(ALLFAST ON)

# include CMSIS-DSP .cmake for GCC Toolchain
include(${DSP}/Toolchain/GCC.cmake)

# add CMSIS-DSP Source directory as subdirectory
add_subdirectory(${DSP}/Source EXCLUDE_FROM_ALL)

# rest of your project
add_executable(pico_inference_app
    ${CMAKE_CURRENT_LIST_DIR}/src/main.cpp
    ${CMAKE_CURRENT_LIST_DIR}/src/dsp_pipeline.cpp
    ${CMAKE_CURRENT_LIST_DIR}/src/ml_model.cpp
)

target_link_libraries(pico_inference_app
    pico_stdlib
    hardware_pwm
    pico-tflmicro
    pico_pdm_microphone
    CMSISDSPTransform CMSISDSPSupport CMSISDSPCommon CMSISDSPComplexMath CMSISDSPFastMath CMSISDSPBasicMath
)

# enable usb output, disable uart output
pico_enable_stdio_usb(pico_inference_app 1)
pico_enable_stdio_uart(pico_inference_app 0)

# create map/bin/hex/uf2 file in addition to ELF.
pico_add_extra_outputs(pico_inference_app)

add_subdirectory("lib/microphone-library-for-pico" EXCLUDE_FROM_ALL)
add_subdirectory("lib/pico-tflmicro" EXCLUDE_FROM_ALL)
