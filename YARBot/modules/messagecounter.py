from telegram import ParseMode
from telegram.ext import CommandHandler, MessageHandler, Filters
from telegram.utils.helpers import mention_markdown, escape_markdown

from YARBot import dispatcher
from YARBot.modules.disable import DisableAbleCommandHandler
from YARBot.modules.helper_funcs.chat_status import user_admin

from datetime import datetime


def count_messages(update, context):
    user_id = int(update.effective_user.id)
    if user_id in context.chat_data['message_count']:
        context.chat_data['message_count'][user_id]['count'] += 1
    else:
        context.chat_data['message_count'][user_id] = {
            'name': escape_markdown(update.effective_user.full_name),
            'count': 1,
        }


@user_admin
def start_count(update, context):
    if ('count_flag' in context.chat_data) and (context.chat_data['count_flag'] == 1):
        update.message.reply_text(
            "A count is already running. Please close it to start another count.",
        )
    else:
        context.chat_data['count_flag'] = 1
        context.chat_data['count_time'] = datetime.now().strftime("%I:%M %p")
        context.chat_data['message_count'] = {}
        context.chat_data['count_handler'] = MessageHandler(
            Filters.chat(
                update.effective_chat.id,
            ) & (~Filters.command), count_messages,
        )
        dispatcher.add_handler(context.chat_data['count_handler'])
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="Message count has been started",
        )


@user_admin
def end_count(update, context):
    if ('count_flag' in context.chat_data) and (context.chat_data['count_flag'] == 1):
        dispatcher.remove_handler(context.chat_data['count_handler'])
        time_str = f'From {context.chat_data["count_time"]} to {datetime.now().strftime("%I:%M %p")}\n\n'
        try:
            user_dict = context.chat_data["message_count"]
            print(user_dict)
            text = "\n-".join(
                map(lambda x: f'{mention_markdown(x["id"],x["name"])} : {x["count"]}', user_dict.keys()),
            )
        except KeyError:
            text = "No messages."
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=time_str + text,
            parse_mode=ParseMode.MARKDOWN,
        )
        context.chat_data.pop('count_flag')
        context.chat_data.pop('message_count')
        context.chat_data.pop('count_time')
        context.chat_data.pop('count_handler')
    else:
        update.message.reply_text("No count is running.")


START_MSG_COUNT = DisableAbleCommandHandler("start_count", start_count)
END_MSG_COUNT = CommandHandler("end_count", end_count)

dispatcher.add_handler(START_MSG_COUNT)
dispatcher.add_handler(END_MSG_COUNT)

__help__ = '''
`/start_count` *:* Start the message count
`/end_count` *:* End the message count
'''
__mod_name__ = "Message Counter"
__command_list__ = ["start_count", "end_count"]
__handlers__ = [START_MSG_COUNT, END_MSG_COUNT]
