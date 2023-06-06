import telebot
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

import functions

TOKEN = "6079306018:AAEg2PhJjhgLkVs18yAmwM_ef8R6YA3TQuk"
bot = telebot.TeleBot(TOKEN)

btn1 = KeyboardButton('video ➡️ audio')
btn2 = KeyboardButton('video ➕ audio')
btn3 = KeyboardButton('audio ➕ audio')
markup = ReplyKeyboardMarkup(resize_keyboard=True)
markup.row(btn1, btn2, btn3)
btn1 = KeyboardButton("Голосовое 🎤")
btn2 = KeyboardButton("Аудиофайл 🎵")
selectAudioMarkup = ReplyKeyboardMarkup(resize_keyboard=True)
selectAudioMarkup.add(btn1, btn2)

hideBoard = ReplyKeyboardRemove()
error = functions.Error(bot, markup)


# инициализация бота
@bot.message_handler(commands=['start'])
def handle_start(message: Message):
    bot.send_message(message.chat.id,
                     "Привет, {}👋.\n"
                     "Я бот для работы с медиа файлами, используй кнопки для управления задачами:".format(
                         message.from_user), reply_markup=markup)


# обработка всех текстовых сообщений
@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_id = message.chat.id
    if message.text == 'video ➡️ audio':
        msg = bot.send_message(user_id, "жду видео для экспорта аудио 🎦", reply_markup=hideBoard)
        bot.register_next_step_handler(msg, video2audio)
    elif message.text == 'video ➕ audio':
        msg = bot.send_message(user_id, "жду видео для наложения 🎦", reply_markup=hideBoard)
        bot.register_next_step_handler(msg, overlay)
    elif message.text == 'audio ➕ audio':
        msg = bot.send_message(user_id, "жду первое аудио 🎵", reply_markup=hideBoard)
        bot.register_next_step_handler(msg, audio_audio)

    else:
        bot.send_message(user_id, "пожалуйста используй кнопки для управления 🤞", reply_markup=markup)


def video2audio(message: Message):
    user_id = message.chat.id
    local_file_name = functions.downloadVideo(bot, message)
    result_audio = functions.extractAudio(bot, message, local_file_name)
    if result_audio:
        with open(result_audio, 'rb') as audio_file:
            bot.send_audio(user_id, audio_file, title=f"{message.video.file_name.split('.')[0]}_audio-bot.mp3")
        bot.send_message(user_id, "задачу выполнил, буду ждать следующее задание 😊", reply_markup=markup)
    else:
        error.sendError(user_id)
    functions.deleteUserFiles(user_id)


def overlay(message: Message):
    local_file_name = functions.downloadVideo(bot, message)
    msg = bot.send_message(message.chat.id, "Выбери с каким типом аудио мне работать:", reply_markup=selectAudioMarkup)
    bot.register_next_step_handler(msg, overlay_select_type, local_file_name)


def overlay_select_type(message: Message, local_file_name):
    text = 'Жду аудио 🎵'
    if message.text == "Голосовое 🎤":
        text = 'Жду голосовое 🎤'
    msg = bot.send_message(message.chat.id, text, reply_markup=hideBoard)
    bot.register_next_step_handler(msg, overlay_audio, local_file_name, text)


def overlay_audio(message: Message, local_file_name, text):
    user_id = message.chat.id
    if message.content_type == "voice":
        local_mp3_file_name = functions.downloadConvertVoice(bot, message)
    elif message.content_type == "audio":
        local_mp3_file_name = functions.downloadAudio(bot, message)
    else:
        return bot.send_message(user_id, text)
    result_video = functions.overlayMedia(bot, user_id, local_file_name, local_mp3_file_name)
    if result_video:
        with open(result_video, 'rb') as final_video:
            bot.send_video(user_id, final_video)
        bot.send_message(user_id, "задачу выполнил, буду ждать следующее задание 😊", reply_markup=markup)
    else:
        error.sendError(user_id)
    functions.deleteUserFiles(user_id)


def audio_audio(message: Message):
    local_file_name = functions.downloadAudio(bot, message)
    msg = bot.send_message(message.chat.id, "жду второе аудио 🎵")
    bot.register_next_step_handler(msg, audio_audio2, local_file_name)


def audio_audio2(message: Message, local_file_name):
    user_id = message.chat.id
    local_file_name2 = functions.downloadAudio(bot, message)
    result_audio = functions.concatenateAudio(bot, user_id, local_file_name, local_file_name2)
    if result_audio:
        with open(result_audio, 'rb') as audio_file:
            bot.send_audio(user_id, audio_file, title=f"{message.audio.file_name.split('.')[0]}_audio-bot.mp3")
        bot.send_message(user_id, "задачу выполнил, буду ждать следующее задание 😊", reply_markup=markup)
    else:
        error.sendError(user_id)
    functions.deleteUserFiles(user_id)


# запуск бота в Loop
bot.polling(none_stop=True)
