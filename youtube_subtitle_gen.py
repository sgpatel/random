import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
import os

def generate_hindi_sbv_subtitles(audio_file_path, subtitle_file_path):
    """
    Generate Hindi subtitles from an audio file and save them in .sbv format.
    
    Parameters:
    - audio_file_path: Path to the audio file (e.g., 'audio.mp3', 'audio.wav')
    - subtitle_file_path: Path where the .sbv subtitle file will be saved (e.g., 'subtitles.sbv')
    """
    # Initialize the speech recognizer
    recognizer = sr.Recognizer()

    # Load the audio file
    audio = AudioSegment.from_file(audio_file_path)

    # Split audio into chunks based on silence
    chunks = split_on_silence(audio, min_silence_len=500, silence_thresh=-40)

    # List to store subtitle entries
    subtitles = []
    start_time = 0  # Start time in seconds

    # Process each audio chunk
    for chunk in chunks:
        # Export the chunk to a temporary WAV file
        chunk.export("temp.wav", format="wav")

        # Recognize speech in the chunk
        with sr.AudioFile("temp.wav") as source:
            audio_data = recognizer.record(source)
            try:
                # Transcribe audio to Hindi text
                text = recognizer.recognize_google(audio_data, language='hi-IN')
            except sr.UnknownValueError:
                text = "[अस्पष्ट]"  # "Unclear" in Hindi
            except sr.RequestError as e:
                print(f"API error: {e}")
                text = "[API त्रुटि]"  # "API error" in Hindi

        # Calculate the end time of the chunk (in seconds)
        end_time = start_time + (len(chunk) / 1000)

        # Format timestamps for .sbv (HH:MM:SS.mmm)
        start_timestamp = format_sbv_timestamp(start_time)
        end_timestamp = format_sbv_timestamp(end_time)

        # Create the .sbv entry
        subtitle_entry = f"{start_timestamp},{end_timestamp}\n{text}\n\n"
        subtitles.append(subtitle_entry)

        # Update the start time for the next chunk
        start_time = end_time

    # Write subtitles to the .sbv file with UTF-8 encoding for Hindi text
    with open(subtitle_file_path, "w", encoding="utf-8") as sbv_file:
        sbv_file.writelines(subtitles)

    # Clean up the temporary file
    if os.path.exists("temp.wav"):
        os.remove("temp.wav")

    print(f"Subtitles generated and saved to {subtitle_file_path}")

def format_sbv_timestamp(seconds):
    """
    Convert seconds to .sbv timestamp format (HH:MM:SS.mmm).
    
    Parameters:
    - seconds: Time in seconds (float)
    Returns:
    - Formatted timestamp string (e.g., '00:01:23.456')
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

# Example usage
if __name__ == "__main__":
    audio_path = "path/to/your/audiofile.mp3"  # Replace with your audio file path
    subtitle_path = "path/to/save/subtitles.sbv"  # Replace with desired output path
    generate_hindi_sbv_subtitles(audio_path, subtitle_path)
