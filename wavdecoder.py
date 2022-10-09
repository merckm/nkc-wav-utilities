import wave
import struct
import sys
import argparse
import logging
from pathlib import Path

# importing the statistics module
import statistics


def main() -> int:

    #    logging.basicConfig(filename='wavdecoder.log',
    #                        format='%(asctime)s %(message)s', level=logging.DEBUG)

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', nargs='?',
                        help="WAV-Datei mit dem Programm")

    args = parser.parse_args()

    print(args)

    baseName = Path(args.filename).stem
    print(args.filename)
    print(baseName)

    wavfreq = 44100.  # Hz
    serFreq = 1200.  # Hz
    lenPuls = wavfreq / serFreq
    readPoint = int(lenPuls * 3. / 4.)
    curPoint = 0

    w = wave.open(args.filename, 'rb')
    print(w.getcompname())
    print(w.getcomptype())
    print(w.getnchannels())
    print(w.getframerate())
    print(w.getsampwidth())
    print(w.getnframes())
    length = w.getnframes()

    curPoint = 0

    samplesPlus = []
    samplesMinus = []
    bits = []
    lastval = 0
    numbits = 0
    firstbit = -1
    bytes = []
    byte = 0x00
    bitPos = 0

    active = False

    for i in range(0, length):
        # for i in range(0, 50000):

        trigger = False
        wavedata = w.readframes(1)
        data = struct.unpack("<h", wavedata)
        val = int(data[0])
    #    print(val)

        if curPoint == readPoint:
            bit = (0, 1)[val > 0]
            bits.append(bit)
            if firstbit == -1:
                firstbit = bit
            else:
                if (not active and bit != firstbit):
                    active = True
                    bitPos = 1

            if active and bitPos > 0 and bitPos <= 8:
                byte = (byte >> 1) + bit * 128
            if active and bitPos > 8 and bit != 1:
                print("Frame Error: Stopbit is not 1")
            if active and bitPos == 0 and bit != 0:
                #                print("Frame Error: Startbit is not 0")
                break
            bitPos += 1
            if active and bitPos == 11:
                bitPos = 0
                bytes.append(byte)
                byte = 0

            curPoint = 0
            numbits += 1
        if curPoint != 0:
            curPoint += 1

        if (val > 0):
            if (lastval == 0):
                lastval = 1
                if (curPoint == 0):
                    trigger = True
                    curPoint = 1
            samplesPlus.append(val)
        else:
            if (lastval == 1):
                lastval = 0
                if (curPoint == 0):
                    trigger = True
                    curPoint = 1
            samplesMinus.append(val)

    print(numbits)
    print(statistics.mean(samplesPlus))
    print(statistics.stdev(samplesPlus))
    print(statistics.mean(samplesMinus))
    print(statistics.stdev(samplesMinus))
    print(len(bits))

    casFileName = baseName + ".cas"
    with open(casFileName, "wb") as out_file:
        out_file.write(bytearray(bytes))

    for i in range(0, len(bytes)):
        print(hex(bytes[i])+' ', end='')
        if i % 16 == 15:
            print("")

    return 0


if __name__ == '__main__':
    sys.exit(main())
