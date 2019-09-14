import pyaudio
import struct
import math
import datetime
import time
import audioop

INITIAL_TAP_THRESHOLD = 1500
INITIAL_TAP_THRESHOLD1 = 1500
FORMAT = pyaudio.paInt16 
SHORT_NORMALIZE = (1.0/32768.0)
CHANNELS = 1
RATE = 44100
INPUT_FRAMES_PER_BLOCK = 4410
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
                                 input_device_index = 0,
                                 frames_per_buffer = 4410
                                 )        
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
        global printed
        if amplitude > self.tap_threshold and printed < i:
            global timeKonig
            timeKonig = datetime.datetime.now()
            global detectedmic1
            detectedmic1 = True
            printed = i + 1000           
        global printed1
        if amplitude1 > self.tap_threshold1 and printed1 < i:
            global timeKonig1
            timeKonig1 = datetime.datetime.now()
            global detectedmic2
            detectedmic2 = True
            printed1 = i + 1000           
        if detectedmic1 and detectedmic2:
            if timeKonig > timeKonig1:
                if (timeKonig - timeKonig1).microseconds < 20000:
                    print("1. ", (timeKonig - timeKonig1).microseconds)
            else:
                if timeKonig < timeKonig1:
                    if (timeKonig1 - timeKonig).microseconds < 20000:
                        print("2. ", (timeKonig1 - timeKonig).microseconds)
            detectedmic1, detectedmic2 = False, False



if __name__ == "__main__":
    tt = TapTester()

    for i in range(10000000):
        tt.listen()