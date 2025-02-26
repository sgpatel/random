from googletrans import Translator
from gtts import gTTS
from pydub import AudioSegment
import tempfile
import os

# Function to parse .sbv file and extract timestamps and text
def parse_sbv(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    subtitles = []
    i = 0
    while i < len(lines):
        if lines[i].strip() == '':
            i += 1
            continue
        timestamp = lines[i].strip()
        text = lines[i + 1].strip()
        start_str, end_str = timestamp.split(',')
        start_ms = timestamp_to_ms(start_str)
        end_ms = timestamp_to_ms(end_str)
        subtitles.append({'start_ms': start_ms, 'end_ms': end_ms, 'text': text})
        i += 2
    return subtitles

# Function to convert timestamp (HH:MM:SS.mmm) to milliseconds
def timestamp_to_ms(timestamp):
    h, m, s = timestamp.split(':')
    s, ms = s.split('.')
    return (int(h) * 3600 + int(m) * 60 + int(s)) * 1000 + int(ms)

# Function to convert milliseconds back to timestamp (HH:MM:SS.mmm)
def ms_to_timestamp(ms):
    total_seconds = ms // 1000
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    ms_remain = ms % 1000
    return f"{h:02d}:{m:02d}:{s:02d}.{ms_remain:03d}"

# Function to write subtitles to .sbv file
def write_sbv(subtitles, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        for subtitle in subtitles:
            start_str = ms_to_timestamp(subtitle['start_ms'])
            end_str = ms_to_timestamp(subtitle['end_ms'])
            f.write(f"{start_str},{end_str}\n")
            f.write(subtitle['english_text'] + '\n\n')

# Main function to process the files
def main(hindi_sbv_path, english_sbv_path, output_audio_path):
    # Step 1: Parse the Hindi .sbv file
    subtitles = parse_sbv(hindi_sbv_path)

    # Step 2: Translate Hindi text to English
    translator = Translator()
    for subtitle in subtitles:
        hindi_text = subtitle['text']
        english_text = translator.translate(hindi_text, src='hi', dest='en').text
        subtitle['english_text'] = english_text

    # Step 3: Write English .sbv file
    write_sbv(subtitles, english_sbv_path)

    # Step 4: Generate and adjust audio
    for subtitle in subtitles:
        # Generate audio with gTTS
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_mp3:
            tts = gTTS(subtitle['english_text'], lang='en')
            tts.save(temp_mp3.name)
            audio = AudioSegment.from_mp3(temp_mp3.name)
            os.remove(temp_mp3.name)  # Clean up temporary file

        # Adjust audio duration to match timestamp
        desired_duration = subtitle['end_ms'] - subtitle['start_ms']
        original_duration = len(audio)
        if original_duration == 0:
            adjusted_audio = AudioSegment.silent(duration=desired_duration)
        else:
            speed_factor = original_duration / desired_duration
            new_frame_rate = int(audio.frame_rate * speed_factor)
            adjusted_audio = audio._spawn(audio.raw_data, overrides={'frame_rate': new_frame_rate})
        subtitle['adjusted_audio'] = adjusted_audio

    # Step 5: Combine audio segments with timing
    sorted_subtitles = sorted(subtitles, key=lambda x: x['start_ms'])
    main_audio = AudioSegment.silent(duration=0)
    previous_end = 0
    for subtitle in sorted_subtitles:
        start_ms = subtitle['start_ms']
        if start_ms > previous_end:
            silence = AudioSegment.silent(duration=start_ms - previous_end)
            main_audio += silence
        main_audio += subtitle['adjusted_audio']
        previous_end = subtitle['end_ms']

    # Export the final audio file
    main_audio.export(output_audio_path, format="mp3")

    print(f"English .sbv file saved to {english_sbv_path}")
    print(f"Dubbed audio saved to {output_audio_path}")

# Example usage
if __name__ == "__main__":
    main("/content/matar_paneer_recipe.sbv", "/content/english_subtitle.sbv", "/content/dubbed_audio.mp3")
