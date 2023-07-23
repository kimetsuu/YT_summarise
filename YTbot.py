
import telebot
from pytube import YouTube
import openai
import os

API_KEY = ‘YOUR_API_KEY’
model_id = 'whisper-1'
openai.api_key = "YOUR_API_KEY"

bot = telebot.TeleBot('YOUR_API_KEY')

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f'Hello <b>{message.from_user.first_name}</b>', parse_mode='html')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    link = message.text
    video_info = download_and_extract_audio(link)
    if video_info:
        with open(video_info["audio_file"], 'rb') as audio_file:
            response = openai.Audio.transcribe(
                api_key=API_KEY,
                model=model_id,
                file=audio_file
            )
        converted_text = response['text']
        summary = summarise(converted_text)
        bot.send_message(message.chat.id, summary)

        if os.path.exists(video_info["audio_file"]):
            os.remove(video_info["audio_file"])
            print("Audio successfully removed")

    else:
        bot.send_message(message.chat.id, "Error: Unable to process the video.")

def download_and_extract_audio(url):
    try:
        yt = YouTube(url)
        video_stream = yt.streams.filter(file_extension='mp4', only_video=True).first()
        audio_stream = yt.streams.filter(only_audio=True).first()

        video_stream.download(filename="video")
        audio_file_path = f"{yt.title}.mp3"
        audio_stream.download(filename=audio_file_path)

        print("Audio successfully downloaded")

        return {
            "video_file": "video.mp4",
            "audio_file": audio_file_path
        }

    except Exception as e:
        print("Error:", str(e))
        return None

def summarise(text):
    completion = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"},
            {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
            {"role": "user", "content": text},
            {"role": "assistant", "content": "Summarise this text:"}
        ]
    )
    simplified_version = completion.choices[0].message.content.strip()
    return simplified_version

bot.polling(non_stop=True)
