import telebot
from telebot import types
from proglog import ProgressBarLogger
import moviepy.editor as mp
import os
import random
import string

class MyBarLogger(ProgressBarLogger):
    progress_message = None
    parametr_message = None
    sticker_message = None
    total_message = None
    prev_percent = 0

    def __init__(self, user_id, bot):
        super().__init__()
        self.user_id = user_id
        self.bot = bot
    
    # калбак каждого вызова logger message
    def callback(self, **changes):
        if self.total_message is None:
            self.showSticker()
            self.total_message = self.bot.send_message(self.user_id, f'Кол-во параметров: {len(changes.items())}')

        for (_, value) in changes.items():
            print("> bot work status:", value)
            if self.parametr_message is None:
                self.parametr_message = self.bot.send_message(self.user_id, 'Текущий: %s' % (value))
            else:
                self.bot.edit_message_text(chat_id=self.user_id, message_id=self.parametr_message.message_id, text='Текущий: %s' % (value))
                self.prev_percent = 0

    def showSticker(self):
        self.sticker_message = bot.send_animation(self.user_id,r'https://media.tenor.com/-2me41xDUsIAAAAC/working-cat-cat.gif')

    def hideSticker(self):
        bot.delete_message(chat_id=self.user_id, message_id=self.sticker_message.message_id)
        self.progress_message = None
        self.parametr_message = None
        self.sticker_message = None
        self.total_message = None
        self.prev_percent = 0

    # калбак каждого обновления logger progress       
    def bars_callback(self, bar, _, value,old_value=None):
        percent = (value / self.bars[bar]['total']) * 100
        if self.progress_message is None:
            self.progress_message = self.bot.send_message(self.user_id, 'Загрузка: 0%')
        else:
            if round(percent - self.prev_percent) >= 30:
                self.bot.edit_message_text(chat_id=self.user_id, message_id=self.progress_message.message_id, text=f'Загрузка: {percent:.2f}%')
                self.prev_percent = percent

class Loader:
    loading_message = None
    isLoading = False
    loader_gif_url = r'https://media.tenor.com/fjdydcAjFo8AAAAi/capoo-blue.gif'
    # todo сделать выбор оформления темы типо (котики, строгий вуз, универсальное)
    
    def __init__(self, user_id, bot):
        super().__init__()
        self.user_id = user_id
        self.bot = bot

    def showLoader(self):
        if(not self.isLoading):
            self.isLoading = True
            self.loading_message = bot.send_animation(self.user_id, self.loader_gif_url)

    def hideLoader(self):
        if(self.isLoading):
            self.isLoading=False
            bot.delete_message(chat_id=self.user_id, message_id=self.loading_message.message_id)
            bot.send_message(self.user_id,"✅")

class Error:
    error_gif_url = 'https://goo.su/t8mNi'

    def __init__(self, user_id, bot):
        super().__init__()
        self.user_id = user_id
        self.bot = bot

    def sendError(self):
        bot.send_animation(self.user_id, self.error_gif_url)
        bot.send_message(self.user_id,'Что-то пошло не так..❌\nПовтори пожалуйста попытку',reply_markup=markup)
        resetBotAction()

def resetBotAction():
    global currAction
    currAction = ''

def getUniqID():
    # генерирует случайную строку из букв и цифр длиной 5 символов
    letters_and_digits = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(letters_and_digits) for _ in range(5))
    return random_string

def downloadVideo(message):
    user_id = message.chat.id
    loader.showLoader()
    file_info = bot.get_file(message.video.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    local_file_name = f'{user_id}_{getUniqID()}_video.mp4'
    with open(local_file_name, 'wb') as new_file:
        new_file.write(downloaded_file)
    users_data[user_id]['video'].append(local_file_name)
    loader.hideLoader()

def downloadAudio(message):
    user_id = message.chat.id
    loader.showLoader()
    file_info = bot.get_file(message.audio.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    local_file_name = f'{user_id}_{getUniqID()}_audio.mp3'
    with open(local_file_name, 'wb') as new_file:
        new_file.write(downloaded_file)
    
    users_data[user_id]['audio'].append(local_file_name)
    loader.hideLoader()

def downloadConvertVoice(message):
    user_id = message.chat.id
    loader.showLoader()
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    local_ogg_file_name = f'{user_id}_{getUniqID()}_voice-audio.ogg'
    with open(local_ogg_file_name, 'wb') as new_file:
        new_file.write(downloaded_file)
    
    audio = mp.AudioFileClip(local_ogg_file_name)
    local_mp3_file_name = f'{user_id}_{getUniqID()}_audio.mp3'
    audio.write_audiofile(local_mp3_file_name)
    audio.close()

    users_data[user_id]['audio'].append(local_mp3_file_name)
    loader.hideLoader()

def overlayMedia(user_id):
    try:
        video = mp.VideoFileClip(users_data[user_id]['video'][0])
        audio = mp.AudioFileClip(users_data[user_id]['audio'][0])
        final_video = video.set_audio(audio)
        local_final_video_name = f'{user_id}_{getUniqID()}_final.mp4'
        final_video.write_videofile(local_final_video_name, codec='libx264', logger=logger)
        logger.hideSticker()
        return local_final_video_name
    except:
        return ''
    finally:
        audio.close()
        video.close()
    
def extractAudio(user_id):
    try:
        video = mp.VideoFileClip(users_data[user_id]['video'][0])
        audio = video.audio
        local_audio_file_name = f'{user_id}_{getUniqID()}_audio.mp3'
        audio.write_audiofile(local_audio_file_name, logger=logger)
        logger.hideSticker()
        return local_audio_file_name
    except:
        return ''
    finally:
        audio.close()
        video.close()

def deleteUserFiles(user_id):
    files = os.listdir()
    for file_name in files:
        if str(user_id) in file_name:
            os.remove(file_name)
    print("> files deleted")

def cleanUp(user_id):
    deleteUserFiles(user_id)
    if len(users_data[user_id]['video'])>0:
        users_data[user_id]['video'] = []
    if len(users_data[user_id]['audio'])>0:
        users_data[user_id]['audio'] = []
    if 'isVoice' in users_data[user_id]:
        del users_data[user_id]['isVoice']

def sendWaitingMsg(user_id):
    sendText(user_id,"задачу выполнил, буду ждать следующее задание 😊",markup)
    resetBotAction()

def showAudioTypeDialog(user_id):
    global selectAudioMarkup
    selectAudioMarkup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Голосовое 🎤")
    btn2 = types.KeyboardButton("Аудиофайл 🎵")
    selectAudioMarkup.add(btn1, btn2)
    sendText(user_id,"Выбери с каким типом аудио мне работать:",selectAudioMarkup)

def concatenateAudio(user_id):
    try:
        audio_clip1 = mp.AudioFileClip(users_data[user_id]['audio'][0])
        audio_clip2 = mp.AudioFileClip(users_data[user_id]['audio'][1])
        final_audio = mp.concatenate_audioclips([audio_clip1, audio_clip2])
        local_final_audio = f'{user_id}_{getUniqID()}_final_audio.mp3'
        final_audio.write_audiofile(local_final_audio,logger=logger)
        logger.hideSticker()
        return local_final_audio
    except:
        return ''
    finally:
        audio_clip1.close()
        audio_clip2.close()

def video_overlay_handler(user_id):
    if('isVoice' in users_data[user_id]):
        sendText(user_id,'Жду голосовое 🎤' if users_data[user_id]['isVoice'] else 'Жду аудио 🎵')
    else:
        sendText(user_id, 'Команду не понял, пожалуйста используй только кнопки',selectAudioMarkup)

def sendVideo(user_id,filename):
    with open(filename, 'rb') as final_video:
        bot.send_video(user_id, final_video)

def sendAudio(user_id,fileName,user_file_name):
    with open(fileName, 'rb') as audio_file:
        bot.send_audio(user_id, audio_file, title=f"{user_file_name}_audio-bot.mp3")

def sendText(user_id,text,markup=''):
    bot.send_message(user_id,text,reply_markup=hideBoard if markup == '' else markup)

TOKEN = "6079306018:AAEg2PhJjhgLkVs18yAmwM_ef8R6YA3TQuk"
bot = telebot.TeleBot(TOKEN)

users_data = {}

global currAction
currAction = ''

btn1 = types.KeyboardButton('video ➡️ audio')
btn2 = types.KeyboardButton('video ➕ audio')
btn3 = types.KeyboardButton('audio ➕ audio')
markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
markup.row(btn1,btn2,btn3)

hideBoard = types.ReplyKeyboardRemove()

# инициализация бота
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.chat.id
    users_data[user_id] = {'video': [], 'audio': []}
    global loader
    loader = Loader(user_id,bot)
    global logger
    logger = MyBarLogger(user_id, bot)
    global error
    error = Error(user_id,bot)
    sendText(user_id, "Привет, {0.first_name}👋.\nЯ бот для работы с медиа файлами, используй кнопки для управления задачами:".format(message.from_user), markup)

# обработка всех текстовых сообщений
@bot.message_handler(content_types=['text'])
def handle_text(message):
    global currAction
    user_id = message.chat.id
    if(message.text == 'video ➡️ audio'):
        currAction = 'video2audio'
        sendText(user_id, "жду видео для экспорта аудио 🎦")
    elif(message.text == 'video ➕ audio'):
        currAction = 'overlay'
        sendText(user_id, "жду видео для наложения 🎦")
    elif(currAction == 'overlay'):
        if(message.text == 'Аудиофайл 🎵'):
            users_data[user_id]['isVoice'] = False
            video_overlay_handler(user_id)
        elif(message.text == 'Голосовое 🎤'):
            users_data[user_id]['isVoice'] = True
            video_overlay_handler(user_id)
        else:
            sendText(user_id, 'Команду не понял, пожалуйста используй только кнопки',selectAudioMarkup)
    elif(message.text == 'audio ➕ audio'):
        currAction = 'audio+audio'
        sendText(user_id, "жду первое аудио 🎵")
    else:
        sendText(user_id,"пожалуйста используй кнопки для управления 🤞",markup)

# обработка всех видео сообщений
@bot.message_handler(content_types=["video"])
def handle_video(message):
    global currAction
    user_id = message.chat.id
    if(currAction == 'video2audio'):
        downloadVideo(message)
        result_audio = extractAudio(user_id)
        if(result_audio != ''):
            sendAudio(user_id,result_audio,message.video.file_name.split('.')[0])
            sendWaitingMsg(user_id)
        else:
            error.sendError()
        cleanUp(user_id)
        # проверка что видео отправляется первым файлом
    elif (currAction=='overlay' and len(users_data[user_id]['audio']) == 0):
        downloadVideo(message)
        showAudioTypeDialog(user_id)
    else:
        bot.send_message(message.chat.id,"Не знаю что делать с файлом, возвращаю на главное меню",reply_markup=markup)

# обработка всех аудио сообщений     
@bot.message_handler(content_types=['audio'])
def handle_audio(message,isVoiceHandler=False):
    user_id = message.chat.id
    # проверка что аудио отправляется вторым файлом
    if (currAction=='overlay' and len(users_data[user_id]['video'])>0):
        if not isVoiceHandler:
            downloadAudio(message)
        else:
            downloadConvertVoice(message)
        result_video = overlayMedia(user_id)
        if(result_video != ''):
            sendVideo(user_id, result_video) #todo поменять все user_id и message на понятную единственную перемененую
            sendWaitingMsg(user_id)
        else:
            error.sendError()
        cleanUp(user_id)
    elif (currAction == 'audio+audio'):
        if(len(users_data[user_id]['audio']) == 0):
            downloadAudio(message)
            sendText(user_id, "жду второе аудио 🎵")
        else:
            downloadAudio(message)
            result_audio = concatenateAudio(user_id)
            if(result_audio != ''):
                sendAudio(user_id, result_audio,message.audio.file_name.split('.')[0]) #todo поменять все user_id и message на понятную единственную перемененую
                sendWaitingMsg(user_id)
            else:
                error.sendError()
            cleanUp(user_id)
    else:
        sendText(user_id,"Не знаю что делать с файлом, возвращаю на главное меню",reply_markup=markup)

# обработка всех голосовых сообщений
@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    user_id = message.chat.id
    if(currAction == 'overlay'):
        handle_audio(message,users_data[user_id]['isVoice'])
    else:
        sendText(user_id,"Не знаю что делать с файлом, возвращаю на главное меню",markup)

# запуск бота в Loop
bot.polling(none_stop=True)



