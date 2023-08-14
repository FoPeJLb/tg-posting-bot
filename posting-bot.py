from telegram import ParseMode
from telegram.error import TelegramError
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters

# Замените 'YOUR_BOT_TOKEN' на токен вашего бота, полученный у BotFather
TOKEN = 'YOUR_BOT_TOKEN'

# Словарь для хранения каналов, на которые нужно отправлять сообщения
channels = {}

def start(update, context):
    update.message.reply_text("Привет! Я буду отправлять все твои сообщения и файлы в указанные каналы.\n " 
                              "Пожалуйста, добавь меня в свои каналы в качестве администратора, чтобы я мог отправлять сообщения туда. \n"
                              "Используй команду /setchannels, чтобы выбрать каналы, на которые мне нужно отправлять сообщения.")

def set_channels(update, context):
    chat_id = update.message.chat_id
    if len(context.args) > 0:
        channel_list = []
        error_message = ""
        for channel in context.args:
            if channel.startswith('@'):
                try:
                    # Проверяем, является ли бот администратором канала
                    bot_member = context.bot.get_chat_member(channel, context.bot.id)
                    if bot_member.status == "member":
                        error_message += f"\n- {channel} – бот не является администратором этого канала."
                    else:
                        channel_list.append(channel)
                except TelegramError:
                    error_message += f"\n- {channel} – канал не найден или бот отсутствует в нем."
            else:
                error_message += f"\n- {channel} – неверный формат канала."
        
        if channel_list:
            channels[chat_id] = channel_list
            update.message.reply_text(f"Теперь все сообщения и файлы будут отправляться в каналы: {', '.join(channel_list)}")
        else:
            update.message.reply_text(f"Ошибка в выборе каналов:{error_message}")
    else:
        update.message.reply_text("Пожалуйста, укажи хотя бы один канал. Используй команду /setchannels @channel1 @channel2 ...")

def send_to_channels(update, context):
    chat_id = update.message.chat_id
    if chat_id in channels:
        channel_list = channels[chat_id]

        message = update.message
        for channel in channel_list:
            if message.text:
                context.bot.send_message(chat_id=channel, text=message.text, parse_mode='HTML', disable_notification=True)

            if message.photo:
                context.bot.send_photo(chat_id=channel, photo=message.photo[-1].file_id, caption=message.caption, parse_mode='HTML', disable_notification=True)

            if message.video:
                context.bot.send_video(chat_id=channel, video=message.video.file_id, caption=message.caption, parse_mode='HTML', disable_notification=True)

            if message.audio:
                context.bot.send_audio(chat_id=channel, audio=message.audio.file_id, caption=message.caption, parse_mode='HTML', disable_notification=True)

            if message.document:
                context.bot.send_document(chat_id=channel, document=message.document.file_id, caption=message.caption, parse_mode='HTML', disable_notification=True)

            if message.sticker:
                context.bot.send_sticker(chat_id=channel, sticker=message.sticker.file_id, disable_notification=True)

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("setchannels", set_channels, pass_args=True))
    dp.add_handler(MessageHandler(Filters.all & ~Filters.command, send_to_channels))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
