import sys
import math
import numpy as np
import matplotlib.pyplot as plt

def bits_from_arg():
    if len(sys.argv) > 1:
        s = sys.argv[1].strip()
        return [1 if ch == "1" else 0 for ch in s]
    return [1, 0, 1, 1, 0, 0, 1, 0]

def generate_ask(bits, samples_per_bit=200, carrier_freq=5.0, a0=0.4, a1=1.0):
    t_all = []
    y_all = []
    for i, b in enumerate(bits):
        amp = a1 if b == 1 else a0
        t = np.linspace(i, i + 1, samples_per_bit, endpoint=False)
        y = amp * np.sin(2 * math.pi * carrier_freq * (t - i))
        t_all.append(t)
        y_all.append(y)
    return np.concatenate(t_all), np.concatenate(y_all)

def generate_fsk(bits, samples_per_bit=200, f0=3.0, f1=7.0, amp=1.0):
    t_all = []
    y_all = []
    for i, b in enumerate(bits):
        freq = f1 if b == 1 else f0
        t = np.linspace(i, i + 1, samples_per_bit, endpoint=False)
        y = amp * np.sin(2 * math.pi * freq * (t - i))
        t_all.append(t)
        y_all.append(y)
    return np.concatenate(t_all), np.concatenate(y_all)

def generate_bpsk(bits, samples_per_bit=200, carrier_freq=5.0, amp=1.0):
    t_all = []
    y_all = []
    for i, b in enumerate(bits):
        phase = 0 if b == 1 else math.pi
        t = np.linspace(i, i + 1, samples_per_bit, endpoint=False)
        y = amp * np.sin(2 * math.pi * carrier_freq * (t - i) + phase)
        t_all.append(t)
        y_all.append(y)
    return np.concatenate(t_all), np.concatenate(y_all)

def draw_bit_guides(bits, title):
    for i in range(len(bits) + 1):
        plt.axvline(i, linestyle='--', linewidth=0.7)
    for i, b in enumerate(bits):
        plt.text(i + 0.45, 1.15, str(b), ha='center')
    plt.ylim(-1.3, 1.3)
    plt.xlim(0, len(bits))
    plt.title(title)
    plt.xlabel('bit time')
    plt.ylabel('signal')

def main():
    bits = bits_from_arg()
    print("Bits:", "".join(str(b) for b in bits))

    t, y = generate_ask(bits)
    plt.figure()
    plt.plot(t, y)
    draw_bit_guides(bits, 'ASK: amplitude changes with bit')

    t, y = generate_fsk(bits)
    plt.figure()
    plt.plot(t, y)
    draw_bit_guides(bits, 'FSK: frequency changes with bit')

    t, y = generate_bpsk(bits)
    plt.figure()
    plt.plot(t, y)
    draw_bit_guides(bits, 'BPSK: phase changes with bit')

    plt.show()

if __name__ == "__main__":
    main()