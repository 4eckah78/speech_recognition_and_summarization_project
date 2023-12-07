import telebot;
from telebot import types
from extract_speech_from_video import get_text_from_audio, get_text_from_video
from download_from_youtube import download_video

import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer
import sentencepiece

model = T5ForConditionalGeneration.from_pretrained("model")
tokenizer = T5Tokenizer.from_pretrained("model")


def split_text(text, max_length=600):
    sentences = text.split('. ')
    parts = []
    current_part = ''
    
    for sentence in sentences:
        if len(current_part) + len(sentence) + 2 <= max_length:
            current_part += sentence + '. '
        else:
            parts.append(current_part[:-1])  
            current_part = sentence + '. '
  
    if current_part:
        parts.append(current_part[:-1])   
    return parts

def summarization(text, n_words=None, compression=None,
    max_length=600, num_beams=3, do_sample=False, repetition_penalty=10.0, 
    **kwargs
):
    result = ''
    texts = split_text(text, max_length)
    for chunk in texts:
      if n_words:
          chunk = '[{}] '.format(n_words) + chunk
      elif compression:
          chunk = '[{0:.1g}] '.format(compression) + chunk
      x = tokenizer(chunk, return_tensors='pt', padding=True).to(model.device)
      with torch.inference_mode():
          out = model.generate(
              **x, 
              max_length=max_length, num_beams=num_beams, 
              do_sample=do_sample, repetition_penalty=repetition_penalty, 
              **kwargs
         )
      result = result + tokenizer.decode(out[0], skip_special_tokens=True) + ' '        
    
    return result

global text_to_send
bot = telebot.TeleBot("TOKEN")

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "Привет":
        bot.send_message(message.from_user.id, "Привет, чем я могу тебе помочь?")
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Напиши привет")
    elif message.text == "/start":
        bot.send_message(message.from_user.id, "Привет, я умный бот! Я умею преобразовывать видео и аудио в текст! \nОтправь мне видео (mp4) или аудио (mp3) файл не более 20Мб и я отправлю тебе его текстовую версию. \nТакже ты можешь отправить мне ссылку на видео с ютуба, и я его тоже транскрибирую :)")
    elif "https://www.youtube.com" in message.text:
        download_video(message.text)
        global text_to_send
        text_to_send = get_text_from_video("youtube_video.mp4")
        bot.send_message(message.from_user.id, text_to_send)
        ask_if_need_summarization(message)
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")    

def ask_if_need_summarization(message):
    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')
    keyboard.add(key_yes)
    key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_no)
    question = 'Хотите сделать суммаризацию текста?'
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "yes":
        bot.send_message(call.message.chat.id, 'Сейчас сделаю')
        bot.send_message(call.message.chat.id, summarization(text_to_send))
    elif call.data == "no":
        bot.send_message(call.message.chat.id, 'Хорошо, нет так нет :)')


@bot.message_handler(content_types=['audio'])
def get_audio_message(message):
    file_id = message.audio.file_id
    downloading_file = bot.get_file(file_id)
    downloaded_file = bot.download_file(downloading_file.file_path)
    with open("audio.mp3", "wb") as file:
        file.write(downloaded_file)
    file.close()
    global text_to_send
    text_to_send = get_text_from_audio("audio.mp3")
    bot.send_message(message.from_user.id, text_to_send)
    ask_if_need_summarization(message)

@bot.message_handler(content_types=["video"])
def get_video_message(message):
    file_id = message.video.file_id
    downloading_file = bot.get_file(file_id)
    downloaded_file = bot.download_file(downloading_file.file_path)
    with open("video.mp4", "wb") as file:
        file.write(downloaded_file)
    file.close()
    global text_to_send
    text_to_send = get_text_from_video("video.mp4")
    bot.send_message(message.from_user.id, text_to_send)
    ask_if_need_summarization(message)


@bot.message_handler(content_types=["video_note"])
def get_video_message(message):
    file_id = message.video_note.file_id
    downloading_file = bot.get_file(file_id)
    downloaded_file = bot.download_file(downloading_file.file_path)
    with open("video.mp4", "wb") as file:
        file.write(downloaded_file)
    file.close()
    global text_to_send
    text_to_send = get_text_from_video("video.mp4")
    bot.send_message(message.from_user.id, text_to_send)
    ask_if_need_summarization(message)


# @bot.message_handler(content_types=["voice"]) # ПРОБЛЕМЫ
# def get_video_message(message):
#     file_id = message.voice.file_id
#     downloading_file = bot.get_file(file_id)
#     downloaded_file = bot.download_file(downloading_file.file_path)
#     with open("audio.mp3", "wb") as file:
#         file.write(downloaded_file)
#     file.close()
#     text = get_text_from_audio("audio.mp3")
#     print(text)

bot.polling(non_stop=True, interval=0) 