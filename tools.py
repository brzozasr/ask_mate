from query import *
from query import __query_all as qu
import re


def get_sort_query(sort=None, column=None):
    statement = f"question_select_all_{sort}_by_{column}"
    if statement in qu:
        return qu[statement]
    else:
        return query.question_select_all_desc_by_date


def highlight_phrase(phrase, text, short=False):
    phrase = phrase.lower()
    text_copy = text.lower()
    length_txt = len(text)
    length_phrase = len(phrase)
    short_len = 30
    occurrence = text_copy.count(phrase)
    cursor = 0
    txt = ""
    first = ""
    last = ""

    if short:
        for i in range(occurrence):
            position = text_copy.find(phrase, cursor)
            spaces = text[cursor:position].count(' ')

            if position - cursor > short_len and spaces > 6:
                list_words = text[cursor:position].split(' ')

                for j in range(len(list_words) - 2):
                    if list_words[j] != "":
                        first += list_words[j]
                        break
                    else:
                        first += ' '

                for k in range(len(list_words) - 1, 1, -1):
                    if list_words[k] != "":
                        last = list_words[k] + last
                        break
                    else:
                        last += ' '
                short_txt = f'{first} (...) {last}'
                first = ""
                last = ""
            else:
                short_txt = text[cursor:position]

            txt += f'{short_txt}<mark>{text[position:position + length_phrase]}</mark>'
            cursor = position + length_phrase
            if i == occurrence - 1:
                txt += text[cursor:length_txt]
    else:
        for i in range(occurrence):
            position = text_copy.find(phrase, cursor)
            txt += f'{text[cursor:position]}<mark>{text[position:position + length_phrase]}</mark>'
            cursor = position + length_phrase
            if i == occurrence - 1:
                txt += text[cursor:length_txt]
    return txt


def is_list(to_check):
    if type(to_check) == list:
        return True
    else:
        return False


def is_email_correct(email):
    regex = r'^[a-z0-9]+[\._-]?[a-z0-9]+[@]\w+[-]?\w+[.]?\w+[.]\w+$'
    if re.fullmatch(regex, email):
        return True
    else:
        return False


def is_same_pwp(first, second):
    if first == second:
        return True
    else:
        return False


def cut_url(request_url: str, request_url_root: str) -> str:
    if request_url_root in request_url:
        return request_url.replace(request_url_root, '/')
    else:
        return ''
