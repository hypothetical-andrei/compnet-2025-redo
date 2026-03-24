import sys
import matplotlib.pyplot as plt

def bits_from_arg():
    if len(sys.argv) > 1:
        s = sys.argv[1].strip()
        return [1 if ch == "1" else 0 for ch in s]
    return [1,0,1,1,0,0,1,1,1,0,0,0]

def nrz(bits):
    levels = []
    for b in bits:
        levels.append(1 if b == 1 else -1)
    return levels

def nrzi(bits, start_level=-1):
    level = start_level
    levels = []
    for b in bits:
        if b == 1:
            level *= -1
        levels.append(level)
    return levels

def manchester(bits):
    # convention: 0 = high->low, 1 = low->high (can vary; we fix one)
    half_levels = []
    for b in bits:
        if b == 0:
            half_levels.extend([1, -1])
        else:
            half_levels.extend([-1, 1])
    return half_levels

def step_plot(levels, title, half=False):
    if half:
        x = [i for i in range(len(levels) + 1)]
        y = levels + [levels[-1]]
        plt.figure()
        plt.step(x, y, where="post")
        plt.ylim(-1.5, 1.5)
        plt.title(title)
        plt.xlabel("half-bit time")
        plt.ylabel("level")
        return

    x = [i for i in range(len(levels) + 1)]
    y = levels + [levels[-1]]
    plt.figure()
    plt.step(x, y, where="post")
    plt.ylim(-1.5, 1.5)
    plt.title(title)
    plt.xlabel("bit time")
    plt.ylabel("level")

def main():
    bits = bits_from_arg()
    print("Bits:", "".join(str(b) for b in bits))

    step_plot(nrz(bits), "NRZ")
    step_plot(nrzi(bits), "NRZI (toggle on 1)")
    step_plot(manchester(bits), "Manchester", half=True)

    plt.show()

if __name__ == "__main__":
    main()