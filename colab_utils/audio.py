#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#

from IPython import display 
from google.colab import output
import base64
from datetime import datetime
from os import path

def record_wav_file(folder):
  def save_wav_file(folder, s):
    b = base64.b64decode(s.split(',')[1])
    
    file_path = path.join(folder, datetime.now().strftime("%d-%m-%Y-%H-%M-%S.wav"))
    
    print(f'Saving file: {file_path}')
    
    with open(file_path, 'wb') as f:
      f.write(b)

  output.register_callback('notebook.save_wav_file', save_wav_file)

  display.display(display.Javascript("""
    const recorderJsScript = document.createElement("script");
    const audioInputSelect = document.createElement("select");
    const recordButton = document.createElement("button");

    recorderJsScript.src = "https://sandeepmistry.github.io/Recorderjs/dist/recorder.js";
    recorderJsScript.type = "text/javascript";

    recordButton.innerHTML = "⏺ Start Recording";

    document.body.append(recorderJsScript);
    document.querySelector("#output-area").appendChild(audioInputSelect);
    document.querySelector("#output-area").appendChild(recordButton);

    async function updateAudioInputSelect() {
      while (audioInputSelect.firstChild) {
        audioInputSelect.removeChild(audioInputSelect.firstChild);
      }

      const deviceInfos = await navigator.mediaDevices.enumerateDevices();

      for (let i = 0; i !== deviceInfos.length; ++i) {
        const deviceInfo = deviceInfos[i];
        const option = document.createElement("option");
        
        option.value = deviceInfo.deviceId;
        
        if (deviceInfo.kind === "audioinput") {
          option.text = deviceInfo.label || "Microphone " + (audioInputSelect.length + 1);
          option.selected = (option.text.indexOf("MicNode") !== -1);
          audioInputSelect.appendChild(option);
        }
      }
    }

    const blob2text = (blob) => new Promise(resolve => {
      const reader = new FileReader();
      reader.onloadend = e => resolve(e.srcElement.result);
      reader.readAsDataURL(blob)
    });

    let recorder = undefined;
    let stream = undefined;

    // https://www.html5rocks.com/en/tutorials/getusermedia/intro/
    recordButton.onclick = async () => {
      if (recordButton.innerHTML != "⏺ Start Recording") {
        recordButton.disabled = true;
        recorder.stop();

        recorder.exportWAV(async (blob) => {
          const text = await blob2text(blob);

          google.colab.kernel.invokeFunction('notebook.save_wav_file', ['###folder###', text], {});
          
          recordButton.innerHTML = "⏺ Start Recording";
          recordButton.disabled = false;

          stream.getTracks().forEach(function(track) {
          if (track.readyState === 'live') {
              track.stop();
            }
          });
        });

        return;
      }

      const constraints = {
        audio: {
          deviceId: {
          },
          sampleRate: 16000
        },
        video: false
      };

      stream = await navigator.mediaDevices.getUserMedia(constraints);

      if (audioInputSelect.value === "") {
        await updateAudioInputSelect();

        stream.getTracks().forEach(function(track) {
          if (track.readyState === 'live') {
            track.stop();
          }
        });

        constraints.audio.deviceId.exact = audioInputSelect.value;
        stream = await navigator.mediaDevices.getUserMedia(constraints);
      }

      const audioContext = new AudioContext({
        sampleRate: 16000
      });
      
      const input = audioContext.createMediaStreamSource(stream);

      recorder = new Recorder(input, {
         numChannels: 1
      });

      recordButton.innerHTML = "⏹ Stop Recording";

      recorder.record();
    };

    updateAudioInputSelect();
  """.replace('###folder###', folder)))
