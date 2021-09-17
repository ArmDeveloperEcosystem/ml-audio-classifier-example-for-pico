#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#

from IPython import display 
from google.colab import output
import base64

def flash_pico(binary_file):
  def read_binary_base64(binary_file):
    with open(binary_file, 'rb') as f:
      return base64.b64encode(f.read()).decode('ascii')

  output.register_callback('notebook.read_binary_base64', read_binary_base64)

  display.display(display.Javascript("""
    const picotoolJsScript = document.createElement("script");

    picotoolJsScript.src = "https://armdeveloperecosystem.github.io/picotool.js/src/picotool.js";
    picotoolJsScript.type = "text/javascript";

    document.body.append(picotoolJsScript);

    async function readBinary() {
      const result = await google.colab.kernel.invokeFunction('notebook.read_binary_base64', ['###binary_file###']);
      let str = result.data['text/plain'];

      str = str.substring(1, str.length - 1);

      return Uint8Array.from(atob(str), c => c.charCodeAt(0));
    }

    async function flashPico() {
      statusDiv.innerHTML = '';

      try {
        statusDiv.innerHTML += "requesting device ... <br/>";
        const usbDevice = await PicoTool.requestDevice();

        const fileData = (await readBinary()).buffer;
        const writeData = new ArrayBuffer(PicoTool.FLASH_SECTOR_ERASE_SIZE);
    
        const srcDataView = new DataView(fileData);
        const dstDataView = new DataView(writeData);

        const picoTool = new PicoTool(usbDevice);
    
        statusDiv.innerHTML += "opening device ... <br/>";
        await picoTool.open();
      
        // statusDiv.innerHTML += "reset ... <br/>";
        await picoTool.reset();
      
        // statusDiv.innerHTML += "exlusive access device ... <br/>";
        await picoTool.exlusiveAccess(1);
      
        // statusDiv.innerHTML += "exit xip ... <br/>";
        await picoTool.exitXip();

        for (let i = 0; i < fileData.byteLength; i += PicoTool.FLASH_SECTOR_ERASE_SIZE) {
          let j = 0;
          for (j = 0; j < PicoTool.FLASH_SECTOR_ERASE_SIZE && (i + j) < fileData.byteLength; j++) {
            dstDataView.setUint8(j, srcDataView.getUint8(i + j));
          }

          statusDiv.innerHTML += "erasing ... ";
          await picoTool.flashErase(PicoTool.FLASH_START + i, PicoTool.FLASH_SECTOR_ERASE_SIZE);

          statusDiv.innerHTML += "writing ... ";
          await picoTool.write(PicoTool.FLASH_START + i, writeData);

          statusDiv.innerHTML += " " + ((i + j) * 100 / fileData.byteLength).toFixed(2) + "% <br/>";
        }

        statusDiv.innerHTML += "rebooting device ... <br/>";
        await picoTool.reboot(0, PicoTool.SRAM_END, 512);
    
        statusDiv.innerHTML += "closing device ... <br/>";
        await picoTool.close();
      } catch (e) {
        statusDiv.innerHTML = 'Error: ' + e.message;
      }
    }

    let statusDiv = undefined; 

    if ('usb' in navigator) {
      const flashButton = document.createElement("button");

      flashButton.innerHTML = "Flash";
      flashButton.onclick = flashPico;

      document.querySelector("#output-area").appendChild(flashButton);

      statusDiv = document.createElement("div");
      statusDiv.style = "margin: 5px";

      document.querySelector("#output-area").appendChild(statusDiv);
    } else {
      document.querySelector("#output-area").appendChild(document.createTextNode(
        "Oh no! Your browser does not support WebUSB!"
      ));
    }
  """.replace('###binary_file###', binary_file)))
