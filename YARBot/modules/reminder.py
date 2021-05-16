# added for adding/creating/sending reminders
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode,Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, Filters,CallbackContext
from telegram.utils.helpers import mention_markdown, escape_markdown


from YARBot import dispatcher
from YARBot.modules.disable import DisableAbleCommandHandler
from YARBot.modules.helper_funcs.chat_status import user_admin, user_admin_no_reply


# Enable logging --Commented by Shailja
'''
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)
'''

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def set_reminder(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('Hi! Use /set <seconds> to set a timer')


def alarm(context: CallbackContext) -> None:
    """Send the alarm message."""
    job = context.job
    context.bot.send_message(job.context, text='Beep!')


def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


def set_timer(update: Update, context: CallbackContext) -> None:
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(context.args[0])
        if due < 0:
            update.message.reply_text('Sorry time travelling is not possible yet!')
            return

        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_once(alarm, due, context=chat_id, name=str(chat_id))

        text = 'YAY! You have Successfully set the timer.'
        if job_removed:
            text += ' Previous timer is deleted'
        update.message.reply_text(text)

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <seconds>')


def unset(update: Update, context: CallbackContext) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Timer successfully cancelled!' if job_removed else 'You have no active timer.'
    update.message.reply_text(text)


__help__ = """
- `/reminder`*:* Set the reminder using /set <seconds>
"""


    updater = Updater("TOKEN")

    # Get the dispatcher to register handlers
    #dispatcher = updater.dispatcher
    # on different commands - answer in Telegram
    #dispatcher.add_handler(CommandHandler("start", start))
    #dispatcher.add_handler(CommandHandler("help", help))
    
    SET_REMINDER = DisableAbleCommandHandler("reminder", set_reminder)
    SET_TIMER = CommandHandler("set",set_timer)
    SET_UNSET = CommandHandler("unset",unset)
    
    dispatcher.add_handler(SET_REMINDER)
    dispatcher.add_handler(SET_TIMER)
    dispatcher.add_handler(SET_UNSET)
    
    __mod_name__ = "Reminder"
    __command_list__ = ["reminder"]
    __handlers__ = [
                    SET_REMINDER,
                    SET_TIMER,
                    SET_UNSET
                   ]

