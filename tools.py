from query import *
from query import __query_all as qu


def get_sort_query(sort=None, column=None):
    statement = f"question_select_all_{sort}_by_{column}"
    if statement in qu:
        return qu[statement]
    else:
        return query.question_select_all_desc_by_date


