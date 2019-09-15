import json
import pyaudio
from rev_ai.models import MediaConfig
from rev_ai.streamingclient import RevAiStreamingClient
from six.moves import queue
from threading import Lock
import time
from collections import deque
from numpy import median

import audioop


mic_values = []
mic1_values = []

def get_rms( block ):
    return audioop.rms(block, 2)


class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""
    def __init__(self, rate, chunk, start_time):
        self._rate = rate
        self._chunk = chunk
        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self._buff1 = queue.Queue()
        self.closed = True

        self.a_left = self.a_right = self.a_diff = 0

        self.timed_rms = deque()
        self.rms_lock = Lock()

        self.start_time = start_time

        self.delta_t1 = 0.5
        self.delta_t2 = 0.2

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            channels=1, rate=self._rate,
            input=True, frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
            input_device_index=0,
        )

        self._audio_stream1 = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            channels=1, rate=self._rate,
            input=True, frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer1,
            input_device_index=2,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream1.stop_stream()
        self._audio_stream.close()
        self._audio_stream1.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._buff1.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def _fill_buffer1(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff1.put(in_data)
        return None, pyaudio.paContinue

    def get_timed_rms(self, end_time):
        print(self.timed_rms)
        rms_values = []
        with self.rms_lock:
            while len(self.timed_rms) > 1:
                t, left, right = self.timed_rms.popleft()
                if (end_time - start_time) - self.delta_t1 < t <= (end_time - start_time) - self.delta_t2:
                    # print("appending")
                    rms_values.append(left - right)
                elif t > (end_time - start_time) - self.delta_t2:
                    if rms_values:
                        return median(rms_values)
                    else:
                        return
            # default case
            if self.timed_rms:
                t, left, right = self.timed_rms.popleft()
                return left - right

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            chunk1 = self._buff1.get()
            if chunk is None:
                return
            data = [chunk]
            data1 = [chunk1]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    chunk1 = self._buff1.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                    data1.append(chunk1)
                except queue.Empty:
                    break

            block = b''.join(data)
            block1 = b''.join(data1)
            amplitude = get_rms( block )
            amplitude1 = get_rms( block1 )
            self.a_diff = amplitude - amplitude1

            mic_values.append(amplitude)
            mic1_values.append(amplitude1)

            with self.rms_lock:
                self.timed_rms.append((time.time() - self.start_time, amplitude, amplitude1))
            # print(amplitude,amplitude1,amplitude - amplitude1)

            yield block


# Sampling rate of your microphone and desired chunk size
rate = 48000
chunk = int(rate/10)

# Insert your access token here
access_token = "02KT6QPJ8XPl0HTqTglpdvZeohnNwaUldCBPJOP_QKTu5JtUsNfUXIC-O_oniEwmpw3QxPjTfEKjVCX33xfwWkai9ypo0"

# Creates a media config with the settings set for a raw microphone input
example_mc = MediaConfig('audio/x-raw', 'interleaved', 48000, 'S16LE', 1)

streamclient = RevAiStreamingClient(access_token, example_mc)

start_time = time.time()

# Opens microphone input. The input will stop after a keyboard interrupt.
with MicrophoneStream(rate, chunk, start_time) as stream:
    # Uses try method to allow users to manually close the stream
    try:
        # Starts the server connection and thread sending microphone audio
        response_gen = streamclient.start(stream.generator())

        # Iterates through responses and prints them
        for response in response_gen:
            pass

    except KeyboardInterrupt:
        # Ends the websocket connection.
        streamclient.client.send("EOS")

        import numpy as np
        print("mean: {}  std: {}", np.mean(mic_values), np.std(mic_values))

        print("mean: {}  std: {}", np.mean(mic1_values), np.std(mic1_values))
        print()
        pass