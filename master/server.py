from flask import Flask
import json
import pyaudio
from rev_ai.models import MediaConfig
from rev_ai.streamingclient import RevAiStreamingClient
from six.moves import queue
import threading
from MicrophoneStream import MicrophoneStream
import cv2
import sys
import logging as log
import datetime as dt
from time import sleep


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
                    if json.loads(response)["type"] != 'final':
                        elements = json.loads(response)["elements"]
                        print([a["value"]
                               for a in elements])
                        global latest_phrase
                        values = [a["value"] for a in elements]
                        if '<unk>' in values:
                            values.remove('<unk>')
                        latest_phrase = values
                except:
                    print(response)

        except KeyboardInterrupt:
            # Ends the websocket connection.
            streamclient.client.send("EOS")
            pass

def webcam():
    cascPath = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascPath)
    log.basicConfig(filename='webcam.log', level=log.INFO)

    video_capture = cv2.VideoCapture(0)
    anterior = 0

    while True:
        if not video_capture.isOpened():
            print('Unable to load camera.')
            sleep(5)
            pass

        # Capture frame-by-frame
        ret, frame = video_capture.read()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor = 1.1,
            minNeighbors = 5,
            minSize = (100, 100)
        )

        # Put subtitles below faces
        for (x, y, w, h) in faces:
            y += 35
            global latest_phrase
            fontscale = 0.65
            if len(latest_phrase):
                for i in range(0, len(latest_phrase), 6):
                    display_txt = ' '.join(latest_phrase[i:i+5])
                    (text_width, text_height) = cv2.getTextSize(display_txt,
                        cv2.FONT_HERSHEY_SIMPLEX, fontScale=fontscale, thickness=1)[0]

                    box_coords = ((x - 1,y+h + 5), (x + text_width + 1, y+h - text_height - 5))
                    cv2.rectangle(frame, box_coords[0], box_coords[1], (0,0,0), cv2.FILLED)

                    cv2.putText(frame, display_txt, (x, y+h),
                                cv2.FONT_HERSHEY_SIMPLEX, fontscale, (255, 255, 255), 1)

                    y += text_height + 10

        if anterior != len(faces):
            anterior=len(faces)
            log.info("faces: "+str(len(faces))+" at "+str(dt.datetime.now()))

        # Display the resulting frame

        cv2.namedWindow('Video', cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty('Video', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # # Display the resulting frame
        # cv2.imshow('Video', frame)

    # When everything is done, release the capture
    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # app.run(debug=True)
    t1=threading.Thread(target = app.run, args = ())
    t2=threading.Thread(target = getRev_ai, args = ())
    t3=threading.Thread(target = webcam, args = ())
    t1.start()
    t2.start()
    t3.start()
