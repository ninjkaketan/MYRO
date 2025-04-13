import whisper
import sounddevice as sd
import numpy as np
import re
import os
import subprocess
import wave
from datetime import datetime

def get_audio_device():
    try:
        devices = sd.query_devices()
        input_devices = [(i, d) for i, d in enumerate(devices) if d['max_input_channels'] > 0]

        if not input_devices:
            raise ValueError("No audio input devices found")

        for i, dev in input_devices:
            if 'USB' in dev['name'].upper():
                print(f"Using USB device {i}: {dev['name']}")
                return i

        print(f"Using first available device {input_devices[0][0]}: {input_devices[0][1]['name']}")
        return input_devices[0][0]

    except Exception as e:
        print(f"Device detection error: {e}")
        raise

def find_supported_samplerate(device_id, test_rates=(16000, 22050, 44100, 48000)):
    for rate in test_rates:
        try:
            sd.check_input_settings(device=device_id, samplerate=rate, channels=1)
            return rate
        except Exception:
            continue
    raise ValueError(f"No supported sample rates found for device {device_id}")

def record_audio(duration=5):
    try:
        device_id = get_audio_device()
        sample_rate = find_supported_samplerate(device_id)
        print(f"Using sample rate: {sample_rate} Hz")

        sd.default.device = device_id
        sd.default.samplerate = sample_rate
        sd.default.channels = 1
        sd.default.dtype = 'int16'

        for card in [0, 1]:
            try:
                subprocess.run(
                    ['amixer', '-c', str(card), 'set', 'Mic', '100%'],
                    check=True,
                    stderr=subprocess.DEVNULL
                )
                break
            except subprocess.CalledProcessError:
                continue

        print("Recording... Speak now!")
        audio = sd.rec(int(duration * sample_rate))
        sd.wait()

        peak = np.max(np.abs(audio))
        print(f"Audio peak level: {peak}")

        if peak < 500:  # raised threshold for better silence detection
            np.save("debug_recording.npy", audio)
            save_debug_wav(audio, sample_rate, "debug_recording.wav")
            raise ValueError("Microphone not capturing enough audio (peak too low)")

        return audio, sample_rate

    except Exception as e:
        print(f"Recording error: {e}")
        raise

def save_debug_wav(audio, sample_rate, filename):
    audio_int16 = (audio * 32767).astype(np.int16)
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit audio
        wf.setframerate(sample_rate)
        wf.writeframes(audio_int16.tobytes())
    print(f"[DEBUG] Audio saved to {filename}")

def transcribe_username(audio, sample_rate):
    model = whisper.load_model("base.en", device="cpu")

    audio_array = audio.flatten().astype(np.float32) / 32768.0
    audio_array = audio_array / np.max(np.abs(audio_array))  # normalize
    audio_array *= 2.5  # gain boost

    # Whisper expects 16kHz mono, so resample if needed
    if sample_rate != 16000:
        from scipy.signal import resample
        target_length = int(len(audio_array) * 16000 / sample_rate)
        audio_array = resample(audio_array, target_length)
        sample_rate = 16000

    audio_array = whisper.pad_or_trim(audio_array)

    result = model.transcribe(
        audio_array,
        language="en",
        temperature=0.2,
        suppress_tokens=[-1],
        without_timestamps=True
    )

    raw = result["text"].strip().upper()
    print(f"Raw transcription: {raw}")
    return re.sub(r"[^A-Z0-9]", "", raw)

def process_user_request(db):
    try:
        audio, sample_rate = record_audio()
        username = transcribe_username(audio, sample_rate)

        if not username:
            return False, '<div style="color:red;text-align:center">NO SPEECH DETECTED</div>'

        user = db.users.find_one(
            {"username": {"$regex": f"^{username}$", "$options": "i"}},
            {"_id": 0, "email": 1, "Vitamin_D_Level_ngmL": 1, "lastTested": 1}
        )

        if not user:
            return False, f'<div style="color:red;text-align:center">USER "{username}" NOT FOUND</div>'

        html = f"""
        <div style="color:white;background:rgba(0,0,0,0.7);padding:20px;text-align:center">
            <h2>{user['email']}</h2>
            <p>Vitamin D: {user['Vitamin_D_Level_ngmL']} ng/mL</p>
            <p>Last Tested: {user.get('lastTested', datetime.now()).strftime('%Y-%m-%d')}</p>
        </div>
        """

        # Write the HTML to a file
        try:
            with open("/home/ketan/MagicMirror/public/vitaminD.html", "w") as f:
                f.write(html)
        except Exception as e:
            print(f"[File Error] Could not write HTML: {e}")

        return True, html

    except Exception as e:
        print(f"Processing error: {e}")
        return False, f'<div style="color:red;text-align:center">ERROR: {str(e)[:50]}</div>'
