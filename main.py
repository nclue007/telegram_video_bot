import os
import telebot
from flask import Flask, request
from audiocraft_app.musicgen import generate_music
from moviepy.editor import VideoFileClip, AudioFileClip

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أرسل لي نصاً وسأحوّله إلى فيديو مع موسيقى!")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    text = message.text
    bot.reply_to(message, "جاري إنشاء الموسيقى والفيديو...")

    music_path = "static/generated_music.wav"
    generate_music(text, output_path="static/generated_music")

    video_path = "static/sample_video.mp4"
    final_path = "static/final_output.mp4"

    video = VideoFileClip(video_path)
    music = AudioFileClip(music_path).subclip(0, video.duration)
    final_video = video.set_audio(music)
    final_video.write_videofile(final_path, codec='libx264')

    with open(final_path, 'rb') as f:
        bot.send_video(message.chat.id, f)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    return '', 403

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 8000)))
