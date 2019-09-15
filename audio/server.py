from flask import Flask
import json
import pyaudio
from rev_ai.models import MediaConfig
from rev_ai.streamingclient import RevAiStreamingClient
from six.moves import queue
import threading
from MicrophoneStream import MicrophoneStream

app = Flask(__name__)

latest_phrase = []

@app.route("/")
def hello_world():
    return ' '.join(latest_phrase)



def getRev_ai():
    print('get rev ai started')
    # Sampling rate of your microphone and desired chunk size
    rate = 44100
    chunk = int(rate/10)

    # Insert your access token here
    access_token = "02KT6QPJ8XPl0HTqTglpdvZeohnNwaUldCBPJOP_QKTu5JtUsNfUXIC-O_oniEwmpw3QxPjTfEKjVCX33xfwWkai9ypo0"

    # Creates a media config with the settings set for a raw microphone input
    example_mc = MediaConfig('audio/x-raw', 'interleaved', 44100, 'S16LE', 1)

    streamclient = RevAiStreamingClient(access_token, example_mc)

    # Opens microphone input. The input will stop after a keyboard interrupt.
    with MicrophoneStream(rate, chunk) as stream:
        # Uses try method to allow users to manually close the stream
        try:
            # Starts the server connection and thread sending microphone audio
            response_gen = streamclient.start(stream.generator())

            # Iterates through responses and prints them
            for response in response_gen:
                try:
                    print( [a["value"] for a in json.loads(response)["elements"]])
                    global latest_phrase
                    latest_phrase = [a["value"] for a in json.loads(response)["elements"]]
                except:
                    print(response)

        except KeyboardInterrupt:
            # Ends the websocket connection.
            streamclient.client.send("EOS")
            pass


if __name__ == "__main__":  
    # app.run(debug=True)
    t1 = threading.Thread(target=app.run, args=())
    t2 = threading.Thread(target=getRev_ai, args=())
    t1.start()
    t2.start()