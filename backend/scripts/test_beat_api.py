import wave
import struct
import math
import tempfile
import requests

def generate_sine_wav(path, duration_s=2.0, freq=440.0, rate=22050):
    nframes = int(duration_s * rate)
    amp = 32767 // 4
    with wave.open(path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        for i in range(nframes):
            t = i / rate
            v = int(amp * math.sin(2 * math.pi * freq * t))
            wf.writeframes(struct.pack('<h', v))

def main():
    tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    tmp.close()
    generate_sine_wav(tmp.name)
    print('Generated test WAV:', tmp.name)

    url = 'http://127.0.0.1:8000/api/analyze-beats'
    with open(tmp.name, 'rb') as fh:
        files = {'audio': (tmp.name, fh, 'audio/wav')}
        try:
            resp = requests.post(url, files=files, timeout=30)
            print('Status:', resp.status_code)
            try:
                print('JSON:', resp.json())
            except Exception:
                print('Body:', resp.text[:1000])
        except Exception as e:
            print('Request failed:', e)

if __name__ == '__main__':
    main()
