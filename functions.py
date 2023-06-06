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
                self.bot.edit_message_text(chat_id=self.user_id, message_id=self.parametr_message.message_id,
                                           text='Текущий: %s' % (value))
                self.prev_percent = 0

    def showSticker(self):
        self.sticker_message = self.bot.send_animation(self.user_id,
                                                       r'https://media.tenor.com/-2me41xDUsIAAAAC/working-cat-cat.gif')

    def hideSticker(self):
        self.bot.delete_message(chat_id=self.user_id, message_id=self.sticker_message.message_id)
        self.progress_message = None
        self.parametr_message = None
        self.sticker_message = None
        self.total_message = None
        self.prev_percent = 0

    # калбак каждого обновления logger progress
    def bars_callback(self, bar, _, value, old_value=None):
        percent = (value / self.bars[bar]['total']) * 100
        if self.progress_message is None:
            self.progress_message = self.bot.send_message(self.user_id, 'Загрузка: 0%')
        else:
            if round(percent - self.prev_percent) >= 30:
                self.bot.edit_message_text(chat_id=self.user_id, message_id=self.progress_message.message_id,
                                           text=f'Загрузка: {percent:.2f}%')
                self.prev_percent = percent


class Error:
    error_gif_url = 'https://goo.su/t8mNi'

    def __init__(self, bot, markup):
        super().__init__()
        self.bot = bot
        self.markup = markup

    def sendError(self, user_id):
        self.bot.send_animation(user_id, self.error_gif_url)
        self.bot.send_message(user_id, 'Что-то пошло не так..❌\nПовтори пожалуйста попытку', reply_markup=self.markup)


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
        if not self.isLoading:
            self.isLoading = True
            self.loading_message = self.bot.send_animation(self.user_id, self.loader_gif_url)

    def hideLoader(self):
        if self.isLoading:
            self.isLoading = False
            self.bot.delete_message(chat_id=self.user_id, message_id=self.loading_message.message_id)
            self.bot.send_message(self.user_id, "✅")


def downloadVideo(bot, message):
    user_id = message.chat.id
    loader = Loader(user_id, bot)
    loader.showLoader()
    file_info = bot.get_file(message.video.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    local_file_name = f'{user_id}_{getUniqID()}_video.mp4'
    with open(local_file_name, 'wb') as new_file:
        new_file.write(downloaded_file)
    loader.hideLoader()
    return local_file_name


def getUniqID():
    # генерирует случайную строку из букв и цифр длиной 5 символов
    letters_and_digits = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(letters_and_digits) for _ in range(5))
    return random_string


def extractAudio(bot, message, local_file_name):
    logger = MyBarLogger(message.chat.id, bot)
    try:
        video = mp.VideoFileClip(local_file_name)
        audio = video.audio
        local_audio_file_name = f'{message.chat.id}_{getUniqID()}_audio.mp3'
        audio.write_audiofile(local_audio_file_name, logger=logger)
        logger.hideSticker()
        return local_audio_file_name
    except:
        return ''
    finally:
        audio.close()
        video.close()


def downloadConvertVoice(bot, message):
    user_id = message.chat.id
    loader = Loader(user_id, bot)
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
    loader.hideLoader()
    return local_mp3_file_name


def downloadAudio(bot, message):
    user_id = message.chat.id
    loader = Loader(user_id, bot)
    loader.showLoader()
    file_info = bot.get_file(message.audio.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    local_file_name = f'{user_id}_{getUniqID()}_audio.mp3'
    with open(local_file_name, 'wb') as new_file:
        new_file.write(downloaded_file)

    loader.hideLoader()
    return local_file_name


def overlayMedia(bot, user_id, local_file_name, local_mp3_file_name):
    logger = MyBarLogger(user_id, bot)
    try:
        video = mp.VideoFileClip(local_file_name)
        audio = mp.AudioFileClip(local_mp3_file_name)
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


def concatenateAudio(bot, user_id, local_file_name, local_file_name2):
    logger = MyBarLogger(user_id, bot)
    try:
        audio_clip1 = mp.AudioFileClip(local_file_name)
        audio_clip2 = mp.AudioFileClip(local_file_name2)
        final_audio = mp.concatenate_audioclips([audio_clip1, audio_clip2])
        local_final_audio = f'{user_id}_{getUniqID()}_final_audio.mp3'
        final_audio.write_audiofile(local_final_audio, logger=logger)
        logger.hideSticker()
        return local_final_audio
    except:
        return ''
    finally:
        audio_clip1.close()
        audio_clip2.close()


def deleteUserFiles(user_id):
    files = os.listdir()
    for file_name in files:
        if str(user_id) in file_name:
            os.remove(file_name)
    print("> files deleted")
