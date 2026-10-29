import numpy as np

SR = 16000
N_FFT = 400
WIN = 400
HOP = 160
N_MELS = 80
FMIN = 50
FMAX = 8000
N_FRAMES = 1001
N_SAMPLES = 160000
EPS = 1.1920929e-7
MEAN = -7.2617793
STD = 4.3511505

def hz_to_mel(freqs):
    fsp = 200.0 / 3.0
    out = []
    for fr in freqs:
        mel = fr / fsp
        min_log_hz = 1000.0
        min_log_mel = min_log_hz / fsp
        logstep = np.log(6.4) / 27.0
        if fr >= min_log_hz:
            mel = min_log_mel + np.log(fr / min_log_hz) / logstep
        out.append(mel)
    return np.asarray(out)

def mel_to_hz(mels):
    fsp = 200.0 / 3.0
    out = []
    for ml in mels:
        freq = fsp * ml
        min_log_hz = 1000.0
        min_log_mel = min_log_hz / fsp
        logstep = np.log(6.4) / 27.0
        if ml >= min_log_mel:
            freq = min_log_hz * np.exp(logstep * (ml - min_log_mel))
        out.append(freq)
    return np.asarray(out)

def build_mel_basis():
    n_freqs = N_FFT // 2 + 1
    fft_freqs = np.arange(n_freqs) * (SR / N_FFT)
    min_mel = hz_to_mel([FMIN])[0]
    max_mel = hz_to_mel([FMAX])[0]
    mels = min_mel + (max_mel - min_mel) * np.arange(N_MELS + 2) / (N_MELS + 1)
    mel_f = mel_to_hz(mels)
    weights = np.zeros((N_MELS, n_freqs), dtype=np.float64)
    for i in range(N_MELS):
        for j in range(n_freqs):
            lower = -(mel_f[i] - fft_freqs[j]) / (mel_f[i + 1] - mel_f[i])
            upper = (mel_f[i + 2] - fft_freqs[j]) / (mel_f[i + 2] - mel_f[i + 1])
            w = min(lower, upper)
            if w < 0:
                w = 0.0
            weights[i, j] = w
    enorm = 2.0 / (mel_f[2:] - mel_f[:-2])
    weights = weights * enorm[:, None]
    return weights, n_freqs

MEL_WEIGHTS, N_FREQS = build_mel_basis()

def hann_window(n):
    i = np.arange(n)
    return 0.5 - 0.5 * np.cos(2 * np.pi * i / n)

HANN = hann_window(WIN)

def reflect_pad(x, pad):
    n = x.shape[0]
    out = np.zeros(n + 2 * pad, dtype=np.float64)
    for i in range(pad):
        out[i] = x[pad - i]
    out[pad:pad + n] = x
    for i in range(pad):
        out[pad + n + i] = x[n - 2 - i]
    return out

def audio_to_mel(audio):
    audio = np.asarray(audio, dtype=np.float64)
    a = np.zeros(N_SAMPLES, dtype=np.float64)
    n = min(audio.shape[0], N_SAMPLES)
    a[:n] = audio[:n]
    padded = reflect_pad(a, N_FFT // 2)
    mel = np.zeros((N_MELS, N_FRAMES), dtype=np.float64)
    for t in range(N_FRAMES):
        start = t * HOP
        real = np.zeros(N_FREQS, dtype=np.float64)
        imag = np.zeros(N_FREQS, dtype=np.float64)
        for nn in range(N_FFT):
            sample = padded[start + nn] * HANN[nn]
            ang = 2 * np.pi * np.arange(N_FREQS) * nn / N_FFT
            real += sample * np.cos(ang)
            imag -= sample * np.sin(ang)
        power = real * real + imag * imag
        mel[:, t] = MEL_WEIGHTS @ power
    mel = np.log(mel + EPS)
    mel = (mel - MEAN) / STD
    out = mel.reshape(1, 1, N_MELS, N_FRAMES).astype(np.float32)
    return out
