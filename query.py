__query_all = {
    'question_select_all_desc_by_date':
        'SELECT * FROM public.question ORDER BY submission_time DESC'
}


class Query:
    def __init__(self, query_dict):
        self.__query = query_dict

    def __getattr__(self, key):
        try:
            return self.__query[key]
        except KeyError as e:
            raise AttributeError(e)


query = Query(__query_all)
