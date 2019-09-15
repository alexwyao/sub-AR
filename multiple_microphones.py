import pyaudio
import struct
import math
import datetime
import time
import audioop

<<<<<<< HEAD
INITIAL_TAP_THRESHOLD = 20
INITIAL_TAP_THRESHOLD1 = 20
FORMAT = pyaudio.paInt16
SHORT_NORMALIZE = (1.0/32768.0)
CHANNELS = 1
RATE = 44100
INPUT_FRAMES_PER_BLOCK = int(RATE/10)
=======
INITIAL_TAP_THRESHOLD = 1500
INITIAL_TAP_THRESHOLD1 = 1500
FORMAT = pyaudio.paInt16 
SHORT_NORMALIZE = (1.0/32768.0)
CHANNELS = 1
RATE = 44100
INPUT_FRAMES_PER_BLOCK = 4410
>>>>>>> 15daf69d36f8c7483a2fa1e6ce2ffe185e97e731
printed = 1000
printed1 = 1000
timeKonig1 = None
timeKonig = None
detectedmic1 = False
detectedmic2 = False

def get_rms( block ):
    return audioop.rms(block, 2)

def get_rms1( block1 ):
    return audioop.rms(block1, 2)

class TapTester(object):
    def __init__(self):
        self.pa = pyaudio.PyAudio()
        self.stream = self.open_mic_stream()
        self.stream1 = self.open_mic_stream1()
        self.tap_threshold = INITIAL_TAP_THRESHOLD
        self.tap_threshold1 = INITIAL_TAP_THRESHOLD1

    def stop(self):
        self.stream.close()

    def open_mic_stream( self ):

        stream = self.pa.open(   format = pyaudio.paInt16,
                                 channels = 1,
                                 rate = 44100,
                                 input = True,
<<<<<<< HEAD
                                 input_device_index = 1,
                                 frames_per_buffer = INPUT_FRAMES_PER_BLOCK
                                 )
=======
                                 input_device_index = 0,
                                 frames_per_buffer = 4410
                                 )        
>>>>>>> 15daf69d36f8c7483a2fa1e6ce2ffe185e97e731
        return stream

    def open_mic_stream1( self ):

        stream1 = self.pa.open(  format = FORMAT,
                                 channels = 1,
                                 rate = 48000,
                                 input = True,
                                 input_device_index = 2,
                                 frames_per_buffer = 4800
                                 )
        return stream1

    def listen(self):
        block = self.stream.read(INPUT_FRAMES_PER_BLOCK, exception_on_overflow = False)
        amplitude = get_rms( block )
        block1 = self.stream1.read(INPUT_FRAMES_PER_BLOCK, exception_on_overflow = False)
        amplitude1 = get_rms( block1 )
        print(amplitude,amplitude1,amplitude-amplitude1)
        time.sleep(.2)

if __name__ == "__main__":
    tt = TapTester()

    for i in range(10000000):
        tt.listen()
