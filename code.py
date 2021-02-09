#!/usr/bin/python
# -*- coding: utf-8 -*-

import telegram
import requests
import json
import pytz
import datetime as dt
from telegram.ext import Updater
import logging
from telegram.ext import CommandHandler, BaseFilter
from telegram.ext import MessageHandler, Filters, CallbackQueryHandler
from telegram.ext.dispatcher import run_async
import wr
import logging
import time
import totable
import random
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher
job_queue = updater.job_queue
DAY = [3]

problems = wr.read_problems()


def pidr_cd(bot, updater, args=[]):
    time.sleep(random.uniform(0, 0.7))
    try:
        DAY[0] = int(args[0])
        bot.send_message(chat_id=updater.message.chat.id, text='Успешно!' )
    except IndexError:
        pass
    today = dt.datetime.now(tz=pytz.timezone('Europe/Moscow'))
    contest = False
    if today.weekday() == DAY[0] or today.weekday() == (DAY[0]+1) % 7:
        contest = True
    return contest, today


@run_async
def confirmation(bot, updater):
    time.sleep(random.uniform(0, 0.7))
    players = wr.read_results()
    if str(updater.message.chat.id) in players:
        bot.send_message(chat_id=updater.message.chat.id,
                         text='Йо, ты уже в системе. Просто используй команды.')
        show_menu(bot, updater)
    else:
        btnlist = [
            telegram.InlineKeyboardButton('Согласен.', callback_data='agree'),
            telegram.InlineKeyboardButton('Не согласен.', callback_data='disagree'),
        ]
        markup = telegram.InlineKeyboardMarkup(wr.build_menu(btnlist, n_cols=2))
        bot.send_message(chat_id=updater.message.chat.id,
                         text='Для начала необходимо согласиться с Согласием на обработку персональный данных.')
        bot.send_message(chat_id=updater.message.chat.id,
                         text='Я даю своё согласие на обработку и публикацию моих персональных данных, таких как: результат участия в Экономической Карусели и никнейм в телеграмм.',
                         reply_markup=markup)


@run_async
def query_h(bot, updater, job_queue):
    time.sleep(random.uniform(0, 0.7))
    call = updater.callback_query
    if call.message:
        if call.data == "contest":
            players = wr.read_results()
            id = call.from_user.id
            try:
                if not pidr_cd(bot, updater)[0]:
                    bot.send_message(chat_id=id, text='Контест не сегодня!')
                elif players[str(id)][2][len(players[str(id)][2]) - 1][3] == 'not contestFalse' and pidr_cd(bot, updater)[0]:
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text)
                    start_carousel(bot, updater, 1, job_queue)
                else:
                    bot.send_message(chat_id=id, text='Ты уже писал контест!')
            except KeyError:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=call.message.text)
                start_carousel(bot, updater, 1, job_queue)

    if call.data == 'agree':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text)
        send_welcome(bot, updater)
    if call.data == 'disagree':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text)
        bot.send_message(chat_id=call.message.chat.id, text='Если всё же передумаешь, то нажми старт ещё раз.')

    if call.data == 'want':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text)
        start_carousel(bot, updater, 1, job_queue)
    if call.data == 'not want':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text)
        start_carousel(bot, updater, 0, job_queue)

    if call.data == 'rules':
        if updater.callback_query.message.text != 'Меню:':
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text)
        print_rules(bot, updater)

    if call.data == 'problems':
        if call.message.text != 'Меню:':
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text )
        select_problems(bot, updater)

    if call.data[:3] == 'pr_':
        print_problem(bot, updater, int(call.data[3:]))

    if call.data == 'result':
        result(bot, updater)
    if call.data == 'allresults':
        allresults(bot, updater)

    if call.data == 'others':
        btnlist = [
        telegram.InlineKeyboardButton('Поддержать проект!', callback_data='donate'),
        telegram.InlineKeyboardButton('Отправить отзыв.', callback_data='feedback'),
            telegram.InlineKeyboardButton('Последний результат.', callback_data='result'),
            telegram.InlineKeyboardButton('Все результаты.', callback_data='allresults'),
            telegram.InlineKeyboardButton('Основное меню.', callback_data='menu')
        ]
        markup = telegram.InlineKeyboardMarkup(wr.build_menu(btnlist, n_cols=2))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, reply_markup=markup)

    if call.data == 'menu':
        btnlist = [
            telegram.InlineKeyboardButton('Показать задачки.', callback_data='problems'),
            telegram.InlineKeyboardButton('Правила.', callback_data='rules'),
            telegram.InlineKeyboardButton('Другое.', callback_data='others')
        ]
        btn = telegram.InlineKeyboardButton('Начать Контест!', callback_data='contest')
        markup = telegram.InlineKeyboardMarkup(wr.build_menu(btnlist, n_cols=2, footer_buttons=[btn]))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, reply_markup=markup)


    if call.data == 'donate':
        donate(bot, updater)

    if call.data == 'feedback':
        feedback(bot, updater)

    if call.data == 'yes':
        send_xlxs(bot, updater)

    return


@run_async
def send_welcome(bot, updater):
    time.sleep(random.uniform(0, 0.7))
    if pidr_cd(bot, updater)[0]:
        btnlist = [
            telegram.InlineKeyboardButton('Контест!', callback_data='contest'),
            telegram.InlineKeyboardButton('Дорешка!', callback_data='problems'),
            telegram.InlineKeyboardButton('Правила.', callback_data='rules')
        ]
        markup = telegram.InlineKeyboardMarkup(wr.build_menu(btnlist, n_cols=2))
        bot.send_message(chat_id=updater.callback_query.message.chat.id, text="Привет. Ты попал на Карусель! И она сегодня!\nЧто хочешь выбрать?",
                         reply_markup=markup)
    else:
        btnlist=[
            telegram.InlineKeyboardButton('Задачи предыдущего тура. ', callback_data='problems'),
            telegram.InlineKeyboardButton('Правила.', callback_data='rules')
        ]
        markup = telegram.InlineKeyboardMarkup(wr.build_menu(btnlist, n_cols=2))
        bot.send_message(chat_id=updater.callback_query.message.chat.id, text="Привет. Ты попал на Карусель! Но она не сегодня(\nЧто хочешь выбрать?", reply_markup=markup)


@run_async
def compete_conf(bot, updater):
    time.sleep(random.uniform(0, 0.7))
    btnlist = [
        telegram.InlineKeyboardButton('Желаю.', callback_data='want'),
        telegram.InlineKeyboardButton('Не желаю.', callback_data='not want')
    ]
    markup = telegram.InlineKeyboardMarkup(wr.build_menu(btnlist, n_cols=2))
    bot.send_message(chat_id=updater.callback_query.message.chat.id,
                     text='Хотите ли вы учавствовать с соревновательном режиме, где ваши результаты будут учтены в общем рейтинге?',reply_markup=markup)


def print_rules(bot, updater):
    time.sleep(random.uniform(0, 0.7))
    if 'callback_query' in str(updater):
        id = updater.callback_query.message.chat.id
    else:
        id = updater.message.chat.id
    bot.send_message(chat_id=id, text='''Правила: 

Как сдавать ответ: 

Во время тура необходимо ответить боту на сообщение вида:\n\"Ваш ответ к задаче # :\"\nсообщинем с ТОЛЬКО ОТВЕТОМ НА ЗАДАЧУ, которым будет являться десятичное число. Числа записываются в виде десятичной дроби с математическим округлением до двух знаков после запятой, через точку.

Ход тура и подведение его итогов:

Время, которое даётся на решение задач, ограничено временем проведения тура.

Вы можете выбрать любой промежуток времени в который вам будет удобно решить задачи, начиная с 8:00am 4ого марта, заканчивая 1:00am 6ого марта. (время указано по Мск)

Вопросы по условию можно задавать авторам задач на протяжении всего тура в вк:
Александр - vk.com/sashashivarov
Игорь - vk.com/ostlane

Во время тура Вы получаете задание, решаете его и даете только ответ. Независимо от результата (верный ответ или нет), Вы получаете следующее задание. 

Время на решение каждого задания не ограничено, определено только общее время проведения тура.

Процесс решения заканчивается, если Вы прошли все задачи или если закончилось время на решение.

Места распределяются согласно количеству набранных баллов. Если кто-то набирает равное количество баллов, то выше ставится тот, у которого больше верных ответов.

Начисление баллов:

Первая задача стоит 3 балла.

Если к задаче дан верный ответ, то Вы получает её полную стоимость, а следующая задача будет стоить на 1 балл больше. 

Если на задачу дан неверный ответ, то команда получает за решение 0 баллов, а следующая задача будет стоить на 3 балла меньше (но не менее 3 баллов она стоить не может).

По всем техническим вопросам - vk.com/coolkaos, @CoolkaOS''')
    try:
        if updater.callback_query.message.text != 'Меню:':
            send_welcome(bot, updater)
    except AttributeError:
        pass


@run_async
def start_carousel(bot, updater, compete, job_queue):
    time.sleep(random.uniform(0, 0.7))
    today = pidr_cd(bot, updater)[1]
    players = wr.read_results()
    name = str(updater.callback_query.message.chat.username) + '  ' + str(updater.callback_query.message.chat.first_name) + '  ' + str(updater.callback_query.message.chat.last_name)
    if str(updater.callback_query.message.chat.id) in players:
        players[str(updater.callback_query.message.chat.id)][2].append([today.strftime("%Y-%m-%d %H:%M:%S.%f"),
                                         {'1': [0],
                                          '2': [0],
                                          '3': [0],
                                          '4': [0],
                                          '5': [0],
                                          '6': [0],
                                          '7': [0],
                                          '8': [0],
                                          '9': [0],
                                          '10': [0],
                                          '11': [0],
                                          '12': [0]},
                                         compete,
                                         'started'])
    else:
        players[str(updater.callback_query.message.chat.id)] = [updater.callback_query.message.chat.id,
                                 '@' + name,
                                 [[today.strftime("%Y-%m-%d %H:%M:%S.%f"),
                                   {'1': [0],
                                    '2': [0],
                                    '3': [0],
                                    '4': [0],
                                    '5': [0],
                                    '6': [0],
                                    '7': [0],
                                    '8': [0],
                                    '9': [0],
                                    '10': [0],
                                    '11': [0],
                                    '12': [0]},
                                   compete,
                                   'started']]]
    wr.write_results(players)
    time.sleep(random.uniform(0, 0.7))
    bot.send_message(
        chat_id=updater.callback_query.message.chat.id,
        text='Тур стартует! Решайте внимательно и осторожно...')
    time.sleep(random.uniform(0, 0.7))
    print_problem(bot, updater, 1)
    if pidr_cd(bot, updater):
        end = dt.datetime(2019, 3, 6, 1, tzinfo=pytz.timezone('Europe/Moscow'))
        job_queue.run_once(timer, (end-today).total_seconds(), context=updater.callback_query.message.chat.id)


def timer(bot, job):
    players = wr.read_results()
    if players[str(job.context)][2][len(
        players[str(job.context)][2]) - 1][3] == 'started':
        bot.send_message(chat_id=job.context, text='ВРЕМЯ ИСТЕКЛО!')
        players[str(job.context)][2][len(
            players[str(job.context)][2]) - 1][3] = 'ended'
        wr.write_results(players)
        bot.send_message(
            chat_id=job.context,
            text='Ура! Тур завершён!\nРезультаты будут опубликованы в боте и на странице: vk.com/sashashivarov')
        result(bot, job.context)
        bot.send_message(
            chat_id=job.context,
            text='А сейчас вы сможете оставить свой комментарий/пожелания, например, какая задача вам понравилась больше всего, какая меньше.\nСпасибо большое, за то что приняли участие в проекты, если вы хотите поддержать нас, то ')
        donate(bot, job.context)
        select_problems(bot, updater)


@run_async
def select_problems(bot, updater):
    time.sleep(random.uniform(0, 0.7))
    if 'callback_query' in str(updater):
        message = updater.callback_query.message
    else:
        message = updater.message
    players = wr.read_results()
    today = pidr_cd(bot, updater)[1]
    state = pidr_cd(bot, updater)[0]
    name = str(message.chat.username) + '  ' + str(message.chat.first_name) + '  ' + str(message.chat.last_name)
    contest = players[str(message.chat.id)][2][len(players[str(message.chat.id)][2])-1][3]
    if str(message.chat.id) not in players:
        players[str(message.chat.id)] = [message.chat.id,
                                         '@' + name,
                                         [[today.strftime("%Y-%m-%d %H:%M:%S.%f"),
                                           {'1': [0],
                                            '2': [0],
                                            '3': [0],
                                            '4': [0],
                                            '5': [0],
                                            '6': [0],
                                            '7': [0],
                                            '8': [0],
                                            '9': [0],
                                            '10': [0],
                                            '11': [0],
                                            '12': [0]},
                                           2,
                                           'not contest{}'.format(state)]]]
        wr.write_results(players)
    elif contest[:11] != 'not contest':
        players[str(message.chat.id)][2].append([today.strftime("%Y-%m-%d %H:%M:%S.%f"),
                                           {'1': [0],
                                            '2': [0],
                                            '3': [0],
                                            '4': [0],
                                            '5': [0],
                                            '6': [0],
                                            '7': [0],
                                            '8': [0],
                                            '9': [0],
                                            '10': [0],
                                            '11': [0],
                                            '12': [0]},
                                           2,
                                           'not contest{}'.format(state)])
        wr.write_results(players)
    if contest[:11] == 'not contest':
        btnlist = []
        for i in range(1, 8, 6):
            btnlist.append(telegram.InlineKeyboardButton(
                str(i), callback_data='pr_{}'.format(i)))
            btnlist.append(telegram.InlineKeyboardButton(
                str(i + 1), callback_data='pr_{}'.format(i + 1)))
            btnlist.append(telegram.InlineKeyboardButton(
                str(i + 2), callback_data='pr_{}'.format(i + 2)))
            btnlist.append(telegram.InlineKeyboardButton(
                str(i + 3), callback_data='pr_{}'.format(i + 3)))
            btnlist.append(telegram.InlineKeyboardButton(
                str(i + 4), callback_data='pr_{}'.format(i + 4)))
            btnlist.append(telegram.InlineKeyboardButton(
                str(i + 5), callback_data='pr_{}'.format(i + 5)))
            markup = telegram.InlineKeyboardMarkup(wr.build_menu(btnlist, n_cols=6))
        bot.send_message(
            chat_id=message.chat.id,
            text='Выбери задачу из списка!',
            reply_markup=markup)
    else:
        bot.send_message(chat_id=message.chat.id, text='Ты уже начал контест!')


@run_async
def print_problem(bot, updater, *args):
    time.sleep(random.uniform(0, 0.7))
    num = args[0]
    if 'callback_query' in str(updater):
        message = updater.callback_query.message
    else:
        message = updater.message
    markup = telegram.ForceReply()
    players = wr.read_results()
    if players[str(message.chat.id)][2][len(players[str(message.chat.id)][2]) - 1][2] == 'started':
        bot.send_message(chat_id=message.chat.id, text=problems[num - 1][0])
        if num == 12:
            bot.send_photo(chat_id=message.chat.id, photo=open('12.jpg', 'rb'))
        bot.send_message(chat_id=message.chat.id, text='Ваш ответ к задаче {} :'.format(num), reply_markup=markup)
    else:
        try:
            ass = players[str(message.chat.id)][2][len(players[str(message.chat.id)][2]) - 1][1][str(num)]
            if len(ass) == 1:
                bot.send_message(chat_id=message.chat.id, text=problems[num - 1][0])
                if num == 12:
                    bot.send_photo(chat_id=message.chat.id, photo=open('12.jpg', 'rb'))
                bot.send_message(
                    chat_id=message.chat.id,
                    text='Ваш ответ к задаче {} :'.format(num),
                    reply_markup=markup)
            else:
                bot.send_message(
                    chat_id=message.chat.id,
                    text='Ты уже решил эту задачу)\nИ ответ был {}.'.format(
                        ass[1]))
        except KeyError:
            bot.send_message(chat_id=message.chat.id, text='Всё плохо.')


def calc(id, players):
    for k in range(0, len(players[str(id)][2])):
        res = players[str(id)][2][k][1]
        if players[str(id)][2][k][3][:11] != 'not contest':
            for num in list(i for i in range(1, 13) if len(res[str(i)]) != 1):
                if problems[num - 1][1] == res[str(num)][1]:
                    if num == 1:
                        res[str(num)][0] = 3
                    elif res[str(num - 1)][0] == 0:
                        nnn = [num-1]
                        for i in range(num-1, 0, -1):
                            if res[str(i)][0] != 0:
                                nnn[0] = i
                                break
                        points = res[str(nnn[0])][0] - (num - nnn[0] - 1) * 3
                        if points > 3:
                            res[str(num)][0] = points
                        else:
                            res[str(num)][0] = 3
                    else:
                        res[str(num)][0] = res[str(num - 1)][0] + 1
                else:
                    res[str(num)][0] = 0
        else:
            for num in list(i for i in range(1, 13) if len(res[str(i)]) != 1):
                if problems[num - 1][1] == res[str(num)][1]:
                    res[str(num)][0] = 1
    return players


@run_async
def answer_problem(bot, updater):
    time.sleep(random.uniform(0, 0.7))
    message = updater.message
    players = wr.read_results()
    try:
        if players[str(message.from_user.id)][2][len(
                players[str(message.from_user.id)][2]) - 1][3] == 'ended':
            bot.send_message(chat_id=message.chat.id, text='Уже всё(')
        else:
            res = players[str(message.from_user.id)][2][len(
                players[str(message.from_user.id)][2]) - 1][1]
            markup = telegram.ReplyKeyboardRemove(selective=False)
            ans = message.text
            rep = message.reply_to_message.text
            num = int(rep[19:-2])
            try:
                a = float(ans)
                if len(res[str(num)]) == 2:
                    bot.send_message(
                        chat_id=message.chat.id,
                        text='Ты уже ответил на этот вопрос!')
                else:
                    if players[str(message.chat.id)][2][len(players[str(message.chat.id)][2]) - 1][3] == 'started':
                        res[str(num)].append(ans)
                        if ans == problems[num-1][1]:
                            bot.send_message(chat_id=message.chat.id, text='Ответ верный!')
                        else:
                            bot.send_message(chat_id=message.chat.id, text='Ответ неверный!')
                        if num == len(problems):
                            players[str(message.from_user.id)][2][len(
                                players[str(message.from_user.id)][2]) - 1][3] = "ended"
                            wr.write_results(players)
                            bot.send_message(
                                chat_id=message.chat.id,
                                text='Ура! Тур завершён!\nРезультаты будут опубликованы в группе:\nvk.com/economic_carousel')
                            result(bot, updater)
                            bot.send_message(
                                chat_id=message.chat.id,
                                text='А сейчас вы сможете оставить свой комментарий/пожелания, например, какая задача вам понравилась больше всего, какая меньше.\nhttps://goo.gl/forms/XBIyXoYEEQUrB9IB2\nСпасибо большое, за то что приняли участие в проекты, если вы хотите поддержать нас, то ')
                            donate(bot, updater)
                            select_problems(bot, updater)
                        else:
                            wr.write_results(players)
                            print_problem(bot, updater, num + 1)
                    else:
                        if problems[num - 1][1] == ans:
                            if len(res[str(num)]) == 1:
                                res[str(num)].append(ans)
                            else:
                                res[str(num)][1] = ans
                            wr.write_results(players)
                            bot.send_message(
                                chat_id=message.chat.id,
                                text="Верно!",
                                reply_markup=markup)
                        else:
                            bot.send_message(
                                chat_id=message.chat.id,
                                text="Неправильно(\nПопробуй еще!",
                                reply_markup=markup)
                            markup = telegram.ForceReply(selective=False)
                            bot.send_message(
                                chat_id=message.chat.id,
                                text='Ваш ответ к задаче {} :'.format(num),
                                reply_markup=markup)
            except ValueError:
                bot.send_message(
                    chat_id=message.chat.id,
                    text="Неправильный формат ответа!\nПопробуй еще!",
                    reply_markup=markup)
                markup = telegram.ForceReply(selective=False)
                bot.send_message(
                    chat_id=message.chat.id,
                    text='Ваш ответ к задаче {} :'.format(num),
                    reply_markup=markup)
    except KeyError:
        bot.send_message(chat_id=message.chat.id, text='Ты ещё не начал.')


def clear(bot, updater):
    try:
        wr.clear(str(updater.message.chat.id))
    except KeyError:
        pass
    bot.send_message(chat_id=updater.message.chat.id, text='Чисто.')


def rest(bot, updater):
    bot.send_message(chat_id=updater.message.chat.id, text='Auch!')


@run_async
def result(bot, updater):
    time.sleep(random.uniform(0, 0.7))
    if type(updater) is int:
        id = updater
    elif 'callback_query' in str(updater):
        id = updater.callback_query.message.chat.id
    else:
        id = updater.message.chat.id
    try:
        players = wr.read_results()
        players = calc(id, players)
        wr.write_results(players)
        resu = players[str(id)][2][len(players[str(id)][2]) - 1]
        text = 'Ваш финальный результат '
        if resu[3][:11] != 'not contest':
            text += 'на Карусели :\n'
        else:
            text += 'на Дорешке :\n'
        for res in list(str(i) for i in range(1, 7)):
            text += '№{} - {} |'.format(res, resu[1][res][0]) + ' '
        text = text[:-2] + '\n'
        for res in list(str(i) for i in range(7, 13)):
            text += '№{} - {} |'.format(res, resu[1][res][0]) + ' '
        text = text[:-2] + '\n'
        if resu[3][:11] != 'not contest':
            text += 'И сумма ваших очков: ' + \
                str(sum(resu[1][i][0] for i in resu[1].keys())) + '.'
        else:
            text += 'И количество решённых вами задач: ' + \
                str(sum(resu[1][i][0] for i in resu[1].keys())) + '.'
        bot.send_message(chat_id=id, text=text)
    except KeyError:
        bot.send_message(chat_id=id, text='Ты ещё не начал этот раз.')


@run_async
def allresults(bot, updater):
    time.sleep(random.uniform(0, 0.7))
    if 'callback_query' in str(updater):
        id = updater.callback_query.message.chat.id
    else:
        id = updater.message.chat.id
    try:
        players = wr.read_results()
        players = calc(id, players)
        wr.write_results(players)
        resus = players[str(id)][2]
        for resu in resus:
            if resu[1]:
                text = 'Ваш финальный результат на {} '.format(
                    str(resu[0])[:-7])
                if resu[3][:11] != 'not contest':
                    text += 'на Карусели :\n'
                else:
                    text += 'на Дорешке :\n'
                for res in list(str(i) for i in range(1, 7)):
                    text += '№{} - {} |'.format(res, resu[1][res][0]) + ' '
                text = text[:-2] + '\n'
                for res in list(str(i) for i in range(7, 13)):
                    text += '№{} - {} |'.format(res, resu[1][res][0]) + ' '
                text = text[:-2] + '\n'
                if resu[3][:11] != 'not contest':
                    text += 'И сумма ваших очков: ' + \
                        str(sum(resu[1][i][0] for i in resu[1].keys())) + '.'
                else:
                    text += 'И количество решённых вами задач: ' + \
                        str(sum(resu[1][i][0] for i in resu[1].keys())) + '.'
                bot.send_message(chat_id=id, text=text)
    except KeyError:
        bot.send_message(chat_id=id, text='Ты ещё не начал.')



def send_res(bot, updater):
    #GD.find_file('res.json').GetContentFile('res.json')
    doc = open('results.json', 'rb')
    btnlist = [
        telegram.InlineKeyboardButton('Да.', callback_data='yes')
    ]
    markup = telegram.InlineKeyboardMarkup(wr.build_menu(btnlist, n_cols=1))
    bot.send_document(chat_id=updater.message.chat.id, document=doc)
    bot.send_message(
        chat_id=updater.message.chat.id,
        text='Отправить тебе xlxs?',
        reply_markup=markup)


def send_xlxs(bot, updater):
    if 'callback_query' in str(updater):
        id = updater.callback_query.message.chat.id
    else:
        id = updater.message.chat.id
    totable.totable()
    doc1 = open('res.xlsx', 'rb')
    bot.send_document(chat_id=id, document=doc1)


def send_fb(bot, updater):
    #GD.find_file('feedback.json').GetContentFile('feedback.json')
    doc = open('feedback.json', 'rb')
    bot.send_document(chat_id=updater.message.chat.id, document=doc)


@run_async
def show_menu(bot, updater):
    time.sleep(random.uniform(0, 0.7))
    if 'callback_query' in str(updater):
        id = updater.callback_query.message.chat.id
    else:
        id = updater.message.chat.id
    btnlist = [
        telegram.InlineKeyboardButton('Показать задачки.', callback_data='problems'),
        telegram.InlineKeyboardButton('Правила.', callback_data='rules'),
        telegram.InlineKeyboardButton('Другое.', callback_data='others')

    ]
    btn = telegram.InlineKeyboardButton('Начать Контест!', callback_data='contest')
    markup = telegram.InlineKeyboardMarkup(wr.build_menu(btnlist, n_cols=2, footer_buttons=[btn]))
    bot.send_message(chat_id=id, text='Меню:', reply_markup=markup)


def cheats(bot, updater):
    bot.send_message(chat_id=updater.message.chat.id, text='''
/pidr_cd 'day'
/pidr_cl
/pidr_sr
/pidr_sf
/pidr_sall
/pidr_repost
/pidr_congrats
    ''')


@run_async
def feedback(bot, updater):
    time.sleep(random.uniform(0, 0.7))
    if 'callback_query' in str(updater):
        id = updater.callback_query.message.chat.id
    else:
        id = updater.message.chat.id
    bot.send_message(
        chat_id=id,
        text='Ответив на это сообщение, вы сможете послать нам свой отзыв!',
        reply_markup=telegram.ForceReply(selective=False))


class FilterFB(BaseFilter):
    def filter(self, message):
        try:
            return 'Ответив на это сообщение, вы сможете послать нам свой отзыв!' == message.reply_to_message.text
        except AttributeError:
            return False


filter_fb = FilterFB()


def thx_fb(bot, updater):
    fb = wr.read_feedback()
    if str(updater.message.from_user.id) in fb:
        fb[str(updater.message.from_user.id)].append(updater.message.text)
    else:
        fb[str(updater.message.from_user.id)] = [updater.message.text]
    bot.send_message(chat_id=updater.message.chat.id, text='Спасибо за отзыв!')
    wr.write_feedback(fb)


@run_async
def donate(bot, updater):
    time.sleep(random.uniform(0, 0.7))
    if type(updater) is int:
        id = updater
    elif 'callback_query' in str(updater):
        id = updater.callback_query.message.chat.id
    else:
        id = updater.message.chat.id
    bot.send_message(
        chat_id=id,
        text='Донаты можно кидать на эту карту Сбербанка с сообщением \"Экономическая Карусель\"')
    bot.send_message(chat_id=id, text='2202 2011 4263 4639')
    bot.send_message(
        chat_id=id,
        text='Спасибо большое за желание поддержать наш проект, участвая в нём!')


def repost(bot, updater):
    for id in wr.read_results():
        try:
            bot.send_message(chat_id=id, text='''''')
        except telegram.error.Unauthorized:
            pass


def congrats(bot, updater):
    ids = []
    for id in ids:
        bot.send_message(chat_id=id, text='Напишите пожалуйста своё ФИО сюда)\n@sasha_shivarov или\nhttps://vk.com/sashashivarov\nНо только в одно место!')


dispatcher.add_handler(CallbackQueryHandler(query_h, pass_job_queue=True))
dispatcher.add_handler(CommandHandler('pidr_cl', clear))
dispatcher.add_handler(CommandHandler('pidr_cd', pidr_cd, pass_args=True))
dispatcher.add_handler(CommandHandler('problems', select_problems))
dispatcher.add_handler(CommandHandler('start', confirmation))
dispatcher.add_handler(CommandHandler('result', result))
dispatcher.add_handler(CommandHandler('allresults', allresults))
dispatcher.add_handler(CommandHandler('pidr_sr', send_res))
dispatcher.add_handler(CommandHandler('menu', show_menu))
dispatcher.add_handler(CommandHandler('pidr_cheats', cheats))
dispatcher.add_handler(CommandHandler('feedback', feedback))
dispatcher.add_handler(CommandHandler('donate', donate))
dispatcher.add_handler(CommandHandler('pidr_sf', send_fb))
dispatcher.add_handler(CommandHandler('pidr_repost', repost))
dispatcher.add_handler(CommandHandler('rules', print_rules))
dispatcher.add_handler(CommandHandler('pidr_congrats', congrats))
dispatcher.add_handler(MessageHandler(filter_fb & Filters.reply, thx_fb))
dispatcher.add_handler(MessageHandler(Filters.reply, answer_problem))
dispatcher.add_handler(MessageHandler(Filters.chat, rest))
updater.start_polling(read_latency=2)



