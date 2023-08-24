import telebot
from telebot import types
import requests
from jira import JIRA
bot = telebot.TeleBot('6149123517:AAFJTsq-WnspU0XJ2tivi3AkYO5ICEy0IGo')
bot.remove_webhook()

login = 'sagandyksmat'
api_key = 'qwerty'  # token of jira acc
jira_options = {'server': 'https://jira.adamants.kz'}
jira = JIRA(options=jira_options, basic_auth=(login, api_key))


@bot.message_handler(commands=["start"])
def bot_messages(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Создать задачу")
    markup.add(item1)
    item2 = types.KeyboardButton("Найти задачу")
    markup.add(item2)
    item3 = types.KeyboardButton("Открыть задачу")
    markup.add(item3)

    bot.send_message(
        message.chat.id, 'Я могу исполнить три желания:\n Создать задачу\n Найти задачу\n Открыть задачу',  reply_markup=markup)


@bot.message_handler(content_types=["text"])
def handle_text(message):

    if message.text.strip() == 'Создать задачу':
        bot.send_message(
            message.chat.id, 'Создание задачи. Введите название задачи.')
        bot.register_next_step_handler(message, get_create_issue_summary)
    elif message.text.strip() == 'Найти задачу':
        bot.register_next_step_handler(message, get_search_issue)
    elif message.text.strip() == 'Открыть задачу':
        bot.send_message(
            message.chat.id, 'Открытые задачи. Введите номер задачи ISNAREG-...')
        bot.register_next_step_handler(message, get_open_issue)


def get_create_issue_summary(message):
    global jira_summary
    jira_summary = message.text.strip()
    bot.send_message(message.chat.id, 'Создание задачи. Введите приоритет.')
    bot.register_next_step_handler(message, get_create_issue_priority)


def get_create_issue_priority(message):
    global jira_priority
    jira_priority = message.text.strip()
    bot.send_message(message.chat.id, 'Создание задачи. Введите описание')
    bot.register_next_step_handler(message, get_create_issue_description)


def get_create_issue_description(message):
    global jira_description
    jira_description = message.text.strip()
    bot.send_message(message.chat.id, 'Название: ' + jira_summary + '\n' +
                                      'Приоритет: ' + jira_priority + '\n' +
                                      'Описание: ' + jira_description)
    bot.send_message(message.chat.id, 'Создать задачу? (Да/Нет)')
    bot.register_next_step_handler(message, get_create_issue)


def get_create_issue(message):
    if message.text.strip() == 'Да':
        issue = jira.create_issue(project='ISNAREG',
                                  summary=jira_summary,
                                  issuetype={'name': 'Task'},
                                  priority={'name': jira_priority},
                                  description=jira_description)
        bot.send_message(message.chat.id, 'Задача ' + issue.key + ' создана')
    elif message.text.strip() == 'Нет':
        bot.send_message(message.chat.id, 'Создание задачи отменено.')


def get_search_issue(message):
    issues = jira.search_issues(message.text.strip(), maxResults=False)
    ans = []
    for issue in issues:
        ans.append(issue.key)
    bot.send_message(message.chat.id, 'Найдены задачи:'+'\n'.join(ans))


def get_open_issue(message):
    issue = jira.issue('ISNAREG-'+message.text.strip())
    desc = issue.fields.description if issue.fields.description is not None else '-'
    bot.send_message(message.chat.id, 'Ключ: ' + issue.key + '\n' +
                                      'Название: ' + issue.fields.summary + '\n' +
                                      'Приоритет: ' + issue.fields.priority.name + '\n' +
                                      'Описание: ' + desc)


if __name__ == '__main__':
    bot.infinity_polling()
