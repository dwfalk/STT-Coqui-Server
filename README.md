# STT Coqui Server

REST API for local STT on Picrofts. Based on [websocket-based server coqui-ai python example](https://github.com/coqui-ai/STT-examples/tree/r1.0/python_websocket_server), [deepspeech rest api](https://github.com/zelo/deepspeech-rest-api) and [DeepSpeech Server](https://github.com/MainRo/deepspeech-server).

This project implements a REST API for Coqui.ai's Speech To Text models. It is intended to be integrated into Mycroft.ai's Picroft platform. For other usecases you're probably better off using any other [sample code](https://github.com/coqui-ai/STT-examples) from coqui.ai.

## Configuration

Server configuration is specified in the [`application.conf`](application.conf) file. 

## Usage

### Setup

Create and activate venv (you might want to do this in a seperate directory outside of this probject):
```
python3 -m venv stt-venv
source stt-venv/bin/activate
```
This likely fails on the picroft there you need to run `sudo apt get install python3-venv` first as suggested in the corresponding error message.

Clone this repo and install dependencies:
```
git clone https://github.com/dwfalk/STT-Coqui-Server.git
cd stt-coui-server
pip3 install https://github.com/coqui-ai/STT/releases/download/v1.3.0/stt-1.3.0-cp37-cp37m-linux_armv7l.whl
pip3 install -r requirements.txt
```
Note that installing `stt` using `pip` might fail on a raspberry pi (`ERROR: Could not find a version that satifies the requirement stt`). The command above worked for me and is documented [here](https://github.com/coqui-ai/stt-model-manager#usage)

Download pretrained model files into the `models` directory (or the path you specified in the `applications.conf`):
```
cd models
curl -O https://github.com/coqui-ai/STT-models/releases/download/english/coqui/v1.0.0-large-vocab/model.tflite"
curl -O https://github.com/coqui-ai/STT-models/releases/download/english/coqui/v1.0.0-large-vocab/large-vocabulary.scorer
```
Checkout the [model zoo](https://coqui.ai/models) to find versions matching your usecase.

### Starting the server

Make sure your model and scorer files are present in the directory specified in the `application.conf` file. Then execute:

```
python -m stt_server.app
```

### (Automatically) Starting the server as a service (on startup)
Put a file called `coquistt.service` in `/etc/systemd/system` with the following contents (paths need to be adjusted to where you created your venv and located this project):
```
[Unit]
Description=STT API Service
After=network.target

[Service]
User=pi
Restart=always
Type=simple
WorkingDirectory=/home/pi/coqui_stt/stt-coqui-server
ExecStart=/home/pi/coqui_stt/stt-venv/bin/python -m stt_server.app

[Install]
WantedBy=multi-user.target
```

Enable and start the new defined service:
```
sudo systemctl enable coquistt.service
sudo systemctl start coquistt.service
```

### Integration in mycroft
- Create according class in `mycroft-core/mycroft/stt/__init__.py`
```
class CoquiServerSTT(STT):
    """
        STT interface for the coqui stt server:
        https://gitlab.mi.hdm-stuttgart.de/heisler/stt-coqui-server
        use this if you want to host Coqui stt yourself
    """
    def __init__(self):
        super(CoquiServerSTT, self).__init__()

    def execute(self, audio, language=None):
        # language is currently not used, it should match the capabilities of your coqui server
        response = post(self.config.get("uri"), data=audio.get_wav_data())
        return response.json()['text']
```
- Add it to `STTFactory` in same file: 
- Adjust settings to use it: e.g. use `mycroft-config edit user` to edit the user config and add the following:
```
"stt": {
    "coqui_server": {
    "uri": "http://localhost:8080/api/v1/stt"
    },
    "module": "coqui_server"
}
```
