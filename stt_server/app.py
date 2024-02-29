from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from time import perf_counter

from pyhocon import ConfigFactory
from sanic import Sanic, response
from sanic.exceptions import InvalidUsage

from stt_server.engine import SpeechToTextEngine

# Load app configs and initialize STT model
conf = ConfigFactory.parse_file("application.conf")
engine = SpeechToTextEngine(
    model_path=Path(conf["stt.model"]).absolute().as_posix(),
    scorer_path=Path(conf["stt.scorer"]).absolute().as_posix(),
)

# Initialze Sanic and ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=conf["server.threadpool.count"])
app = Sanic("stt_server")


@app.route("/", methods=["GET"])
async def healthcheck(_):
    return response.text("Welcome to STT Server!")


@app.route('/api/v1/stt', methods=['POST'])
async def stt(request):
    speech = request.body
    if not speech:
        raise InvalidUsage("Missing \"speech\" payload.")
    inference_start = perf_counter()
    text = await app.loop.run_in_executor(executor, lambda: engine.run(speech))
    inference_end = perf_counter() - inference_start
    return response.json({'text': text, 'time': inference_end})


if __name__ == "__main__":
    app.run(
        host=conf["server.http.host"],
        port=conf["server.http.port"],
        access_log=True,
        debug=True,
    )
