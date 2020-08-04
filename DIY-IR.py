from scipy.io import wavfile
import numpy as np
import random as r
import os
import re
samplerate = 48000
##output location
filepath = '/Library/Audio/Samples/Impulse Responses/DIY/DIY-IR/'
##Generators
def makenoise(length):
    global signaltype
    signaltype.append('noise')
    noise = []
    for i in range(length):
        noise.append(r.randint(-32768, 32767)/32767)

    noise_info = {'max': max(noise), 'min': min(noise), 'mean': (sum(noise)/len(noise))}
    return noise

def makelinear(length, ascending=False):
    global signaltype
    signaltype.append('linear')
    line = []
    for i in range(length):
        line.append((2*(length-i)/length)-1)
    if ascending:
        line = sorted(line)
    return line

def makelog(length, base=10, reverse=False):
    global signaltype
    signaltype.append('log')
    logline = []
    for i in range(0, length):
        if i == 0:
            i += .001
        log = np.log(i)/np.log(base)
        logline.append((log/base/2)-1)
    if reverse:
        logline = sorted(logline, reverse=True)
    return logline

def makesine(length, intensity=100, hz=100):
    global signaltype
    signaltype.append('sinusoid')
    sine = []
    for i in range(length):
        freq = hz/samplerate
        sine.append(np.cos(i*freq)*(intensity/100))
    return sine
##Filtering
def squarify(signal, hz=50):
    new_signal = []
    freq = int(samplerate/hz)
    for i in range(len(signal)):
        if i > freq and i // freq % 2 == 0:
            new_signal.append(0)
        else:
            new_signal.append(signal[i])
    signaltype.append('squarified')
    return new_signal
            
def truncate(signal, threshold=75):
    new_signal = []
    for i in range(len(signal)):
        if abs(signal[i]) > threshold/100:
            new_signal.append(threshold/100 * ([-1,1][int(signal[i]>0)]))
        else:
            new_signal.append(signal[i])
    signaltype.append('truncated')
    return new_signal
##Signal Creator
def make_impulse(generators, seconds=1, combination='add', trunc=100, square=0):
    length = int(seconds*samplerate)
    global signaltype
    #gen_list = ['noise','line', 'line_rev','log','log_rev','sine-amp-hz']
    signaltype = []
    signal = {}
    for i in generators:
        if i == 'noise':
            signal[i] = makenoise(length)
        elif i == 'line':
            signal[i] = makelinear(length)
        elif i == 'line_rev':
            signal[i] = makelinear(length, ascending=True)
        elif i == 'log':
            signal[i] = makelog(length)
        elif i == 'log_rev':
            signal[i] = makelog(length, reverse=True)
        elif 'sin' in i:
            parts = i.split('-')
            if len(parts) > 1:
                amplitude = int(parts[1])
                freq = int(parts[2])
                signal[i] = makesine(length, intensity=amplitude, hz=freq)
            else:
                signal[i] = makesine(length)
    out = []
    if combination == 'add':
        for i in range(length):
            out.append(sum([signal[j][i] for j in signal.keys()])/len(signal.keys()))
    if combination == 'multiply':
        for i in range(length):
            out.append(np.prod([signal[j][i] for j in signal.keys()]))
        top = max([abs(i) for i in out])
        for i in range(len(out)):
            out[i] = out[i]/top
    if combination == 'divide':
        for i in range(length):
            out.append(signal[[i for i in signal.keys()][0]][i] * np.prod(([(signal[j][i]+(int(signal[j][i]==0)/1000))**-1 for j in signal.keys()])))
        top = max([abs(i) for i in out])
        for i in range(len(out)):
            out[i] = out[i]/top
    if trunc<100:
        out = truncate(out, threshold=trunc)
    if square > 0:
        out = squarify(out, hz=square)
    return out
##Output
def save_wav(signal):
    most_recent_file_num = max([int(i) for i in re.findall('\d+', "".join(os.listdir(filepath)))])
    filename = str(most_recent_file_num + 1) + "_".join(signaltype) + '.wav'
    signal = np.array(signal)
    wavfile.write(filepath+filename, samplerate, signal)
##Randomization
options = {'generators': ['noise','line', 'line_rev','log','log_rev','sine-amp-hz'],
          'combination': ['add', 'multiply', 'divide']}
def rand_sin():
    return 'sin-' + str(r.randint(50, 100)) + '-' + str(r.randint(2, 20000))

def impulsive():
    trunc_range = [i+(70*int(r.randint(0, 100)>20)) for i in range(1, 30)]
    if r.randint(0,100) > 50:
        trunc_range = [100]
    gens = []
    for i in range(1, r.randint(2,len(options['generators']))):
        gens.append(options['generators'][r.randint(0,len(options['generators'])-1)])
    for i in range(len(gens)):
        if 'sin' in gens[i]:
            gens[i] = rand_sin()
    #print(gens)
    signal = make_impulse(gens, seconds=(r.randint(1,5)*.25), combination=r.choice(options['combination']), trunc=r.choice(trunc_range), square=r.randint(2,5000))
    print(signaltype)
    save_wav(signal)

##Interface begins
q = int(str(input('How many new impulse files would you like?')))
for i in range(q):
    print('File '+ str(i+1))
    impulsive()