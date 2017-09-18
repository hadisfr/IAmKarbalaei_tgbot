#!/usr/bin/env python3


import os
from sys import stderr
from io import BytesIO
from datetime import datetime
import json

import telebot
from PIL import Image

from config import *


class Ui(object):
    """user interface message provider"""

    def __init__(self, lang = "fa"):
        super(Ui, self).__init__()
        with open(ui_json_addr) as f:
            self.db = json.loads(f.read())
        self.set_lang(lang)

    def get_message(self, key):
        return self.db[self.lang][key]

    def set_lang(self, lang):
        if(lang not in self.db.keys()):
            raise ValueError("%s language not found in %s." % (lang, ui_json_addr))
        self.lang = lang


bot = telebot.TeleBot(TOKEN, num_threads = 3)
ui = Ui(lang)
with open(templates_json_addr) as f:
    templates = json.loads(f.read())
for template in templates:
    template["templat_addr"] = templates_addr_prefix + template["templat_addr"]
    template["mask_addr"] = templates_addr_prefix + template["mask_addr"]


@bot.message_handler(commands = ['start'])
def msghndlr_welcome(msg):
    chat_id = msg.chat.id
    log(chat_id, "start")
    bot.send_message(chat_id, ui.get_message("welcome"))
    start(chat_id)


@bot.message_handler(regexp = ui.get_message("use_profile_photo_btn"))
def msghndlr_use_profile_photo(msg):
    chat_id = msg.chat.id
    log(chat_id, "use_profile_photo")
    try:
        send_photos(chat_id, bot.get_user_profile_photos(msg.from_user.id, offset = 0, limit = 1).photos[0])
    except IndexError:
        bot.send_message(chat_id, "use_profile_photo_err", reply_markup = telebot.types.ReplyKeyboardRemove())
        start(chat_id)


@bot.message_handler(content_types = ["photo"])
def msghndlr_use_uploaded_photo(msg):
    chat_id = msg.from_user.id
    log(chat_id, "use_uploaded_photo")
    send_photos(chat_id, msg.photo)


def start(chat_id):
    keyboard_markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard = True, resize_keyboard = True)
    keyboard_markup.add(telebot.types.KeyboardButton(ui.get_message("use_profile_photo_btn")))
    bot.send_message(chat_id, ui.get_message("give_photo"), reply_markup = keyboard_markup)


def send_photos(chat_id, source_photos):
    for template in templates:
        log(chat_id, "send_photo " + template["templat_addr"])
        send_photo(chat_id, source_photos, **template)
    start(chat_id)


def send_photo(chat_id, source_photos, source_photo_size, source_photo_position, templat_addr, mask_addr):
    chosen_source_photo = None
    for p in source_photos:
        if(p.width >= source_photo_size[0] and p.height >= source_photo_size[1]):
            chosen_source_photo = p
            break
    if not chosen_source_photo:
        chosen_source_photo = source_photos[-1]
    
    source_stream = BytesIO(bot.download_file(bot.get_file(chosen_source_photo.file_id).file_path))
    bot.send_chat_action(chat_id, "upload_photo")
    
    source_photo = Image.open(source_stream)
    source_photo.load()
    source_stream.close()

    photo = Image.open(templat_addr)
    photo.load()

    mask = Image.open(mask_addr)
    mask.load()
    mask = mask.resize(source_photo_size)

    photo.paste(source_photo.resize(source_photo_size), source_photo_position, mask)

    photo_stream = BytesIO()
    photo.save(photo_stream, format = "png")
    photo_stream.seek(0)
    bot.send_photo(chat_id, photo_stream)
    photo_stream.close()


def log(chat_id, txt):
    print("%s\t%r\t%s" % (datetime.now(), chat_id, txt))


def main():
    try:
        bot.polling(none_stop = True)
    except Exception as ex:
        log(None, ex)


if __name__ == '__main__':
    main()
