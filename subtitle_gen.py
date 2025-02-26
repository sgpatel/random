import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
import os

def generate_hindi_subtitles(audio_file_path, subtitle_file_path):
    """
    ऑडियो फ़ाइल से हिंदी में सबटाइटल बनाता है और SRT प्रारूप में सेव करता है।

    पैरामीटर्स:
    - audio_file_path: ऑडियो फ़ाइल का पाथ (जैसे 'audio.mp3', 'audio.wav')
    - subtitle_file_path: SRT फ़ाइल को सेव करने का पाथ (जैसे 'subtitles.srt')
    """
    # भाषण पहचानकर्ता को आरंभ करें
    recognizer = sr.Recognizer()

    # ऑडियो फ़ाइल लोड करें
    audio = AudioSegment.from_file(audio_file_path)

    # साइलेंस के आधार पर ऑडियो को हिस्सों में बाँटें
    chunks = split_on_silence(audio, min_silence_len=500, silence_thresh=-40)

    # सबटाइटल एंट्रीज़ स्टोर करने के लिए सूची
    subtitles = []
    start_time = 0  # सेकंड में शुरुआती समय

    # प्रत्येक ऑडियो हिस्से को प्रोसेस करें
    for i, chunk in enumerate(chunks):
        # हिस्से को अस्थायी WAV फ़ाइल में निर्यात करें
        chunk.export("temp.wav", format="wav")

        # हिस्से में भाषण को पहचानें
        with sr.AudioFile("temp.wav") as source:
            audio_data = recognizer.record(source)
            try:
                # Google Speech Recognition से हिंदी में ट्रांसक्राइब करें
                text = recognizer.recognize_google(audio_data, language='hi-IN')
            except sr.UnknownValueError:
                text = "[अस्पष्ट]"
            except sr.RequestError as e:
                print(f"API त्रुटि: {e}")
                text = "[API त्रुटि]"

        # हिस्से का समाप्ति समय कैलकुलेट करें
        end_time = start_time + (len(chunk) / 1000)

        # SRT के लिए टाइमस्टैम्प फॉर्मेट करें
        start_timestamp = format_timestamp(start_time)
        end_timestamp = format_timestamp(end_time)

        # SRT एंट्री बनाएँ
        subtitle_entry = f"{i + 1}\n{start_timestamp} --> {end_timestamp}\n{text}\n"
        subtitles.append(subtitle_entry)

        # अगले हिस्से के लिए शुरुआती समय अपडेट करें
        start_time = end_time

    # सबटाइटल को SRT फ़ाइल में लिखें
    with open(subtitle_file_path, "w", encoding="utf-8") as srt_file:
        srt_file.writelines(subtitles)

    # अस्थायी फ़ाइल हटाएँ
    if os.path.exists("temp.wav"):
        os.remove("temp.wav")

    print(f"सबटाइटल उत्पन्न हो गए और {subtitle_file_path} पर सेव हो गए")

def format_timestamp(seconds):
    """
    सेकंड को SRT टाइमस्टैम्प प्रारूप (HH:MM:SS,mmm) में बदलता है।
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

# उदाहरण उपयोग
if __name__ == "__main__":
    #audio_path = "path/to/your/audiofile.mp3"  # अपनी ऑडियो फ़ाइल का पाथ डालें
    #subtitle_path = "path/to/save/subtitles.srt"  # सबटाइटल फ़ाइल का पाथ डालें
    audio_path = "/content/Matar-paneer.mp3"  # Replace with your audio file path
    subtitle_path = "/content/matar_paneer.srt"
    generate_hindi_subtitles(audio_path, subtitle_path)
