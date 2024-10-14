import streamlit as st
import moviepy.editor as mp
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
from pydub import AudioSegment
import os
import base64

# Function to extract audio from video
def extract_audio(video_file, audio_file):
    try:
        video = mp.VideoFileClip(video_file)
        video.audio.write_audiofile(audio_file)
    finally:
        video.close()  # Ensure the video file is closed after processing

# Function to transcribe English audio to text
def transcribe_audio(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
        try:
            return recognizer.recognize_google(audio_data)
        except sr.UnknownValueError:
            return "Speech Recognition could not understand the audio"
        except sr.RequestError as e:
            return f"Could not request results; {e}"

# Function to translate text to Hindi
def translate_text(text, target_language='hi'):
    translator = Translator()
    translation = translator.translate(text, dest=target_language)
    return translation.text

# Function to convert Hindi text to speech
def text_to_speech(text, output_file):
    tts = gTTS(text=text, lang='hi')
    tts.save(output_file)

# Function to combine translated audio with video
def combine_audio_with_video(video_file, audio_file, output_video_file):
    try:
        video = mp.VideoFileClip(video_file)
        audio = mp.AudioFileClip(audio_file)
        video = video.set_audio(audio)
        video.write_videofile(output_video_file, audio_codec='aac')
    finally:
        video.close()  # Ensure the video file is closed after processing

# Streamlit Application
def main():
    # Inject custom CSS with background image and white text color
    def add_bg_from_local(image_file):
        with open(image_file, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            st.markdown(
                f"""
                <style>
                .stApp {{
                    background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
                    background-size: cover;
                    background-color: rgba(0, 0, 0, 0.6); /* Optional dark overlay for better text visibility */
                }}
                </style>
                """,
                unsafe_allow_html=True
            )
    
    add_bg_from_local('i1.jpg')
    
    # Custom styling for text color and button styling
    st.markdown(
        """
        <style>
        /* Main Content Styling */
        .css-18e3th9 {
            background-color: rgba(255, 255, 255, 0.85); /* Transparent white background */
            padding: 20px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }

        /* Text color */
        h1, h2, h3, p, div, span {
            color: white !important;
        }

        .stButton button {
            background-color: #ff7e5f;
            border: none;
            color: black;
            padding: 15px 32px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            transition-duration: 0.4s;
            cursor: pointer;
            border-radius: 10px;
        }

        .stButton button:hover {
            background-color: white;
            color: black;
            border: 2px solid #ff7e5f;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("🎥 Video Translator (English to Hindi)")
    st.markdown(
        """
        Convert the audio of your video from English to Hindi seamlessly!
        Upload your video file, and this app will:
        1. Extract the audio.
        2. Transcribe the English audio to text.
        3. Translate the text to Hindi.
        4. Convert Hindi text to speech.
        5. Create a new video with Hindi audio.
        """
    )

    # File uploader for video
    video_file = st.file_uploader("📤 Upload Video", type=["mp4", "mov", "avi"])
    
    if video_file is not None:
        st.video(video_file, start_time=0)

        if st.button("🎬 Convert to Hindi"):
            with st.spinner("Processing..."):
                input_video_path = video_file.name
                with open(input_video_path, mode='wb') as f:
                    f.write(video_file.read())  # Save uploaded video

                audio_file = "temp_audio.wav"
                hindi_audio_file = "hindi_audio.mp3"
                output_video_file = "output_video_in_hindi.mp4"
                
                # Step 1: Extract Audio from Video
                extract_audio(input_video_path, audio_file)
                st.write("Audio extracted.")

                # Step 2: Transcribe Audio
                english_text = transcribe_audio(audio_file)
                if "could not" in english_text:
                    st.error(f"Error: {english_text}")
                    return
                st.write("Audio transcribed.")

                # Step 3: Translate Text
                hindi_text = translate_text(english_text)
                st.write("Text translated to Hindi.")

                # Step 4: Convert Translated Text to Hindi Audio
                text_to_speech(hindi_text, hindi_audio_file)
                st.write("Hindi audio generated.")

                # Step 5: Combine Hindi Audio with Video
                combine_audio_with_video(input_video_path, hindi_audio_file, output_video_file)
                st.write("Hindi audio combined with video.")

                # Display the new video
                st.success("🎉 Video conversion complete!")
                st.video(output_video_file)

                # Provide a download link for the video
                with open(output_video_file, "rb") as file:
                    st.download_button("⬇️ Download Video", file, file_name=output_video_file)

            # Clean up temporary files safely by ensuring they are not in use
            try:
                os.remove(input_video_path)  # Now safe to remove the video file
                os.remove(audio_file)
                os.remove(hindi_audio_file)
                os.remove(output_video_file)
            except Exception as e:
                st.error(f"Error cleaning up files: {e}")

if __name__ == "__main__":
    main()
