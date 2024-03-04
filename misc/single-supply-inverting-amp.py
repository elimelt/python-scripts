import numpy as np
import matplotlib.pyplot as plt

def gain(f, C=220e-9):
    w = 2 * np.pi * f
    R1 = 2000
    R2 = 20000
    Z1 = R1 + (w * C * 1j) ** -1
    Z2 = R2
    gain_val = np.abs(-Z2 / Z1)
    return gain_val

def vout(vin, f, C=220e-9):
    max_out = 9
    return min(np.abs(vin * gain(f, C)), max_out)

def plot3d(fmin, fmax, fstep, vmin, vmax, vstep, angle=0):
    f = np.arange(fmin, fmax, fstep)
    v = np.arange(vmin, vmax, vstep)
    X, Y = np.meshgrid(f, v)
    Z = np.zeros(X.shape)
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            Z[i][j] = vout(Y[i][j], X[i][j])
    fig = plt.figure()
    ax = fig.add_subplot(121, projection='3d')
    s = ax.plot_surface(X, Y, Z, cmap='viridis')
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Input Voltage (V)')
    ax.set_zlabel('Output Voltage (V)')
    ax.set_title('Output Voltage vs. Input Voltage and Frequency')
    plt.show()

def plotwave(data):
    plt.plot(data)
    mi, ma = min(data), max(data)
    pp = ma - mi
    plt.ylim(mi - pp / 2, ma + pp / 2)
    plt.xlabel('Time')
    plt.ylabel('Voltage')
    plt.title('Square Wave')
    plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    plt.tick_params(axis='y', which='both', left=False, right=False, labelleft=False)
    plt.show()

def plot3dgainvscap(fmin, fmax, fstep, Cmin, Cmax, Cstep, angle=0):
    f = np.arange(fmin, fmax, fstep)
    C = np.arange(Cmin, Cmax, Cstep)
    X, Y = np.meshgrid(f, C)
    Z = np.zeros(X.shape)
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            Z[i][j] = gain(X[i][j], Y[i][j])
    fig = plt.figure()
    ax = fig.add_subplot(121, projection='3d')
    ax2 = fig.add_subplot(122, projection='3d')
    ax.plot_surface(X, Y, Z)
    ax2.scatter(X, Y, Z, c='r', marker='o', label='Observed Gain for f = 1000Hz', s=100)
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Capacitance (F)')
    ax.set_zlabel('Gain (Vout/Vin)')
    ax.set_title('Gain vs. Frequency and Capacitance')
    ax2.set_xlabel('Frequency (Hz)')
    ax2.set_ylabel('Capacitance (F)')
    ax2.set_zlabel('Gain (Vout/Vin)')
    ax2.set_title('Gain vs. Frequency and Capacitance')
    plt.show()

def plot2d(fmin, fmax, fstep, vin):
    f = np.arange(fmin, fmax, fstep)
    glabel = np.zeros(f.shape)
    gbadcap = np.zeros(f.shape)
    for i in range(f.shape[0]):
        glabel[i] = gain(f[i], C=220e-9)
        gbadcap[i] = gain(f[i], C=100e-9)
    plt.plot(f, glabel, 'r', label='Calculated C = 220nF')
    plt.plot(f, gbadcap, 'g', label='Calculated C = 100nF')
    plt.plot(1000, 7.64, 'bo', label='Measured Gain')
    plt.plot(100, 1.286, 'bo')
    plt.plot(10, 0.202, 'bo')
    plt.legend()
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Gain (Vout/Vin)')
    plt.title('Gain vs. Frequency')
    plt.show()

if __name__ == "__main__":
    square_wave = np.loadtxt('square', delimiter=',')
    plotwave(square_wave[:200])
