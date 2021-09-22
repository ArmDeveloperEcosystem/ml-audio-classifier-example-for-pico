#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#

from IPython import display

def run_serial_monitor():
  display.display(display.Javascript('''
    if ('serial' in navigator) {
      const scriptElement = document.createElement("script");
      scriptElement.src = "https://cdnjs.cloudflare.com/ajax/libs/xterm/3.14.5/xterm.min.js";
      document.body.appendChild(scriptElement);

      const linkElement = document.createElement("link");
      linkElement.rel = "stylesheet"
      linkElement.href = "https://cdnjs.cloudflare.com/ajax/libs/xterm/3.14.5/xterm.min.css";
      document.body.appendChild(linkElement);

      const connectDisconnectButton = document.createElement("button");

      connectDisconnectButton.innerHTML = "Connect Port";

      document.querySelector("#output-area").appendChild(connectDisconnectButton);

      terminalDiv = document.createElement("div");
      terminalDiv.style = "margin: 5px";

      document.querySelector("#output-area").appendChild(terminalDiv);

      let port = undefined;
      let reader = undefined;
      let keepReading = true;
      let term = undefined;

      connectDisconnectButton.onclick = async () => {
        if (port !== undefined) {
          if (reader !== undefined) {
            keepReading = false;
            try {
              await reader.cancel();
            } catch (e) {}
          }
          port = undefined;
          reader = undefined;

          connectDisconnectButton.innerHTML = "Connect Port";

          return;
        }

        port = await navigator.serial.requestPort();
        keepReading = true;

        connectDisconnectButton.innerHTML = "Disconnect Port";
        
        await port.open({ baudRate: 115200 });

        if (term === undefined) {
          term = new Terminal();
          term.open(terminalDiv);
        }
        term.clear();
    
        const decoder = new TextDecoder();

        while (port && keepReading) {
          try {
            reader = port.readable.getReader();
          
            while (true) {
              const { value, done } = await reader.read();
              if (done) {
                keepReading = false;
                break;
              }

              term.write(decoder.decode(value, { stream: true }));
            }
          } catch (error) {
            keepReading = false;
          } finally {
            await reader.releaseLock();
          }
        }
        
        await port.close();

        port = undefined;
        reader = undefined;

        connectDisconnectButton.innerHTML = "Connect Port";
      };
    } else {
      document.querySelector("#output-area").appendChild(document.createTextNode(
        "Oh no! Your browser does not support Web Serial!"
      ));
    }
  '''))
