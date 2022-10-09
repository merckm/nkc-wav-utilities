from time import clock_getres
import wave
import struct
import sys
import argparse
import logging
from pathlib import Path

framerate = 44100.  # Hz
serFreq = 1200.  # Hz
lenPuls = framerate / serFreq
halfPuls = lenPuls / 2
restPuls = halfPuls - int(halfPuls)
rest = 0
numframes = 0

posSignal = 16000
negSignal = -16000
leadBit = 0
curBit = leadBit
stopBit = 1
startBit = 0


def main() -> int:

    #    logging.basicConfig(filename='wavencoder.log',
    #                        format='%(asctime)s %(message)s', level=logging.DEBUG)

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', nargs='?',
                        help="CAS-Datei mit dem Programm")

    args = parser.parse_args()

    baseName = Path(args.filename).stem
    print(args.filename)
    print(baseName)

    wavFileName = baseName + ".wav"
    nchannels = 1
    sampwidth = 2
    comptype = 'NONE'
    compname = 'not compressed'
    print(lenPuls)
    print(halfPuls)
    print(restPuls)

    file = open(args.filename, "rb")
    data = file.read()
    file.close()
    print(len(data))

    nframes = int((2400 + (len(data) * 11)) * lenPuls)
    print(nframes)
    w = wave.open(wavFileName, 'wb')
    w.setnchannels(nchannels)
    w.setsampwidth(sampwidth)
    w.setframerate(framerate)
    w.setnframes(nframes)
    w.setcomptype(comptype, compname)

    for i in range(1200):
        writeBit(w, leadBit)

    for i in range(len(data)):

        writeBit(w, startBit)
        for j in range(8):
            bit = (data[i] >> j) & 1
            writeBit(w, bit)

        writeBit(w, stopBit)
        writeBit(w, stopBit)

    for i in range(1200):
        writeBit(w, stopBit)

    w.close

    return 0


def writeBit(w: wave.Wave_write, bit: int) -> None:
    global rest
    global numframes
    rest += restPuls

    numPos = 0
#    value = (posSignal, negSignal)[(1 ^ bit) == 0]
    # Invwerted wafwform
    value = (negSignal, posSignal)[(1 ^ bit) == 0]
    for j in range(int(halfPuls)):
        numPos += 1
        data = struct.pack('<h', value)
        w.writeframesraw(data)
        numframes += 1

    if rest >= 1:
        numPos += 1
        rest -= 1
        data = struct.pack('<h', value)
        w.writeframesraw(data)
        numframes += 1

    numNeg = 0
    rest += restPuls
#    value = (posSignal, negSignal)[(0 ^ bit) == 0]
    value = (negSignal, posSignal)[(0 ^ bit) == 0]
    for j in range(int(halfPuls)):
        numNeg += 1
        data = struct.pack('<h', value)
        w.writeframesraw(data)
        numframes += 1

    if rest >= 1:
        numNeg += 1
        rest -= 1
        data = struct.pack('<h', value)
        w.writeframesraw(data)
        numframes += 1

#    print(str(numPos) + " " + str(numNeg))


if __name__ == '__main__':
    sys.exit(main())
