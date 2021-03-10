import pyaudio
import wave
from tkinter import *
from tkinter.ttk import *
CHUNK = 1024
chunk = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
root=Tk()
RATE = 44100
INPUT_BLOCK_TIME = 0.05
INPUT_FRAMES_PER_BLOCK = int(RATE*INPUT_BLOCK_TIME)
SHORT_NORMALIZE = 1.0 / 32768.0
RATE = 44100
root.recording=False
root.playing=False
root.resizable(False, False)
root.iconbitmap('play.ico')
root.title('Audio Recorder')
root.meter1=DoubleVar()
root.meter2=DoubleVar()
import math
import struct
from tkinter import filedialog
root.FILENAME = ""
root.filename=''
SHORT_NORMALIZE = 1.0 / 32768.0
s = Style()
s.configure("red.Vertical.TProgressbar", foreground='red', background='red')
s.configure("green.Vertical.TProgressbar", foreground='green', background='green')
def browse(v):
    if not(root.playing or root.recording):
        if v==1:
            root.FILENAME=filedialog.asksaveasfilename(filetypes=[('WAV Files', '*.wav')])
        elif v==2:
            root.filename=filedialog.askopenfilename(filetypes=[('WAV Files', '*.wav')])
class Amplitude(object): #VU Meters
    ''' an abstraction for Amplitudes (with an underlying float value)
    that packages a display function and many more '''

    def __init__(self, value=0):
        self.value = value

    def __add__(self, other):
        return Amplitude(self.value + other)

    def __sub__(self, other):
        return Amplitude(self.value - other)

    def __gt__(self, other):
        return self.value > other

    def __lt__(self, other):
        return self.value < other

    def __eq__(self, other):
        return self.value == other

    def to_int(self, scale=1):
        ''' convert an amplitude to an integer given a scale such that one can
        choose the precision of the resulting integer '''
        return int(self.value * scale)

    def __int__(self):
        return self.to_int()

    def __str__(self):
        return self.value + " dB"

    @staticmethod
    def from_data(block):
        ''' generate an Amplitude object based on a block of audio input data '''
        count = len(block) / 2
        shorts = struct.unpack("%dh" % count, block)
        sum_squares = sum(s**2 * SHORT_NORMALIZE**2 for s in shorts)
        try:
            return Amplitude(math.sqrt(sum_squares / count))
        except:
            return 0
    def display(self, mark, scale=50):
        ''' display an amplitude and another (marked) maximal Amplitude
        graphically '''
        int_val = self.to_int(scale)
        return int(int_val)
def record(): #crashing when this is executed
    if not root.FILENAME=='':
        FILENAME=root.FILENAME+'.wav'
    else:
        return
    CHUNK = 1024
    root.recording=True
    root.playing=False
    recordButton.config(text='\u23f9')
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)
    frames = []
    while root.recording:
        data = stream.read(CHUNK)
        frames.append(data)
        amp = Amplitude.from_data(data)
        maximal=100
        if amp > maximal:
             maximal = amp
        try:
            value1=Amplitude.display(scale=100, mark=maximal)
            root.meter1.set(int(value1)*3)
        except:
            root.meter1.set(0)
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open(FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    recordButton.config(text='\u23fa')
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    root.meter1.set(0)
    wf.close()
def play(): #plays audio
    if not root.filename=='':
        FILENAME=root.filename
    else:
        return
    root.recording=False
    root.playing=True
    chunk = 1024
    playButton.config(text='\u23f9')
    p = pyaudio.PyAudio()
    wf = wave.open(FILENAME, 'rb')
    stream = p.open(format = p.get_format_from_width(wf.getsampwidth()),
                channels = wf.getnchannels(),
                rate = wf.getframerate(),
                output = True)
    data = wf.readframes(chunk)
    while data != '' and root.playing:
        stream.write(data)
        data = wf.readframes(chunk)
        amp = Amplitude.from_data(data)
        maximal=100
        if amp > maximal:
             maximal = amp
        try:
            value2=amp.display(scale=100, mark=maximal)
            root.meter2.set(int(value2)*3)
        except:
            root.meter2.set(0)
        root.update()
    root.meter2.set(0)
    playButton.config(text='\u25b6')
    stream.close()
    p.terminate()
def record_on_off():
    if not root.recording:
        record()
    else:
        root.recording=False
        recordButton.config(text='\u23fa')
def play_on_off():
    if not root.playing:
        play()
    else:
        root.playing=False
vumeter1=Progressbar(root, mode='determinate', orient=VERTICAL, variable=root.meter1)
vumeter1.grid(column=1, row=0)
vumeter2=Progressbar(root, mode='determinate', orient=VERTICAL, variable=root.meter2)
vumeter2.grid(column=2, row=0)
recordButton=Button(root, text='\u23fa', command=record_on_off)
recordButton.grid(column=1, row=1)
Button(root, text='Output File', command=lambda: browse(1)).grid(column=1, row=2)
Button(root, text='Input File', command=lambda: browse(2)).grid(column=2, row=2)
playButton=Button(root, text='\u25b6', command=play_on_off)
playButton.grid(column=2, row=1)
root.mainloop()
