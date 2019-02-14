#!/usr/bin/python
# -*- coding: utf-8 -*-
import io
import json

code1 = '{"298465764": [298465764, "AlexOdnakov", "@CoolkaOS", ["2019-01-24 14:17:25.606708", {}, ["2019-01-24 14:24:35.609711", {}], ["2019-01-24 14:24:56.559005", {"1": 3, "2": 0, "3": 3, "4": 4}], ["2019-01-24 14:25:54.895257", {}], ["2019-01-24 14:26:08.515342", {"1": 3, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0}]]]}'


def write_results(results):
    res = open('results.json', 'w')
    writer = res.write
    writer(json.dumps(results, indent=4, sort_keys=True))


def read_results():
    res = open('results.json', 'r')
    reader = res.read()
    return json.loads(reader)


def pretty_print():
    print(json.dumps(read_results(), indent=4, sort_keys=True))


def clear(id):
    results = read_results()
    results.pop(id)
    write_results(results)


def read_problems():
    pr = open('problems.json', 'r', encoding='utf-8-sig')
    reader = pr.read()
    return json.loads(reader)


def read_feedback():
    fb = open('feedback.json', 'r', encoding='utf-8')
    reader = fb.read()
    return json.loads(reader)


def write_feedback(feedback):
    fb = open('feedback.json', 'w', encoding='utf-8')
    writer = fb.write
    writer(json.dumps(feedback, ensure_ascii=False))


# indent=4, sort_keys=True


def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu
