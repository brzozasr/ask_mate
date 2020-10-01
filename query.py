__query_all = {
    # DO NOT CHANGE THE FIRST KEY VALUE, IT HAS TO BE FIRST.
    'question_select_all_desc_by_date':
        'SELECT id, submission_time, view_number, vote_number, title, message, image FROM question ORDER BY submission_time DESC',
    'question_select_all_asc_by_date':
        'SELECT id, submission_time, view_number, vote_number, title, message, image FROM question ORDER BY submission_time ASC',
    'question_select_all_desc_by_view':
        'SELECT id, submission_time, view_number, vote_number, title, message, image FROM question ORDER BY view_number DESC',
    'question_select_all_asc_by_view':
        'SELECT id, submission_time, view_number, vote_number, title, message, image FROM question ORDER BY view_number ASC',
    'question_select_all_desc_by_vote':
        'SELECT id, submission_time, view_number, vote_number, title, message, image FROM question ORDER BY vote_number DESC',
    'question_select_all_asc_by_vote':
        'SELECT id, submission_time, view_number, vote_number, title, message, image FROM question ORDER BY vote_number ASC',
    'question_select_all_desc_by_title':
        'SELECT id, submission_time, view_number, vote_number, title, message, image FROM question ORDER BY title DESC',
    'question_select_all_asc_by_title':
        'SELECT id, submission_time, view_number, vote_number, title, message, image FROM question ORDER BY title ASC',
    'question_select_all_desc_by_question':
        'SELECT id, submission_time, view_number, vote_number, title, message, image FROM question ORDER BY message DESC',
    'question_select_all_asc_by_question':
        'SELECT id, submission_time, view_number, vote_number, title, message, image FROM question ORDER BY message ASC',
    'question_select_limit_5_desc_by_date':
        'SELECT id, submission_time, view_number, vote_number, title, message, image FROM question ORDER BY submission_time DESC LIMIT 5',
    'question_select_by_id':
        'SELECT id, submission_time, view_number, vote_number, title, message, image FROM question WHERE id = %s',
    'question_update_view_number_by_id':
        'UPDATE question SET view_number = view_number + 1 WHERE id = %s',
    'answer_select_by_id':
        'SELECT id, submission_time, vote_number, question_id, message, image FROM answer WHERE question_id = %s ORDER BY submission_time DESC',
    'question_update_vote_number_by_id':
        'UPDATE question SET vote_number = vote_number + %s WHERE id = %s',
    'answer_update_vote_number_by_id':
        'UPDATE answer SET vote_number = vote_number + %s WHERE id = %s',
    'question_insert':
        'INSERT INTO question (title, message) VALUES (%s, %s)',
    'answer_insert':
        'INSERT INTO answer (question_id, message) VALUES (%s, %s)',
    'answer_get_img_path':
        'SELECT image FROM answer WHERE question_id = %s',
    'question_delete':
        'DELETE FROM question WHERE id = %s RETURNING image',
    'question_update':
        'UPDATE question SET title = %s, message = %s WHERE id = %s',
    'question_update_img':
        'UPDATE question SET image = %s WHERE id = %s',
    'answer_update_img':
        'UPDATE answer SET image = %s WHERE id = %s',
    'answer_delete':
        'DELETE FROM answer WHERE id = %s RETURNING image, question_id',
    'answer_count_fk_question_id':
        'SELECT COUNT(question_id) FROM answer WHERE question_id = %s',
    'comment_insert_to_question':
        'INSERT INTO comment (question_id, message) VALUES (%s, %s)',
    'comment_insert_to_answer':
        'INSERT INTO comment (question_id, answer_id, message) VALUES (%s, %s, %s)',
    'comment_select_by_question_id':
        'SELECT id, question_id, answer_id, message, submission_time, edited_number FROM comment WHERE question_id = %s ORDER BY submission_time DESC',
    'comment_select_by_comment_id':
        'SELECT id, question_id, answer_id, message, submission_time, edited_number FROM comment WHERE id = %s',
    'comment_update_by_id':
        'UPDATE comment SET message = %s, submission_time = NOW(), edited_number = edited_number + 1 WHERE id = %s',
    'advanced_search':
        """SELECT question.id, 'Q' || question.id, question.title || ' ' || question.message, question.submission_time AS date
        FROM question
        WHERE question.title || ' ' || question.message ILIKE %(search)s
        UNION
        SELECT answer.question_id, 'A' || answer.question_id, answer.message, answer.submission_time AS date
        FROM answer
        WHERE answer.message ILIKE %(search)s
        UNION
        SELECT comment.question_id, 'C' || comment.question_id, comment.message, comment.submission_time AS date
        FROM comment
        WHERE comment.message ILIKE %(search)s
        ORDER BY date DESC""",
    'questions_search':
        """SELECT DISTINCT q.id, q.submission_time, q.view_number, q.vote_number, q.title, q.message, q.image
        FROM question q, answer a
        WHERE q.title ILIKE %(search)s OR q.message ILIKE %(search)s OR (q.id = a.question_id AND a.message ILIKE %(search)s)
        ORDER BY q.submission_time DESC""",
    'tag_select':
        'SELECT id, title FROM tag ORDER BY title',
    'question_tag_insert':
        'INSERT INTO question_tag (question_id, tag_id) VALUES (%s, %s)',
    'question_tag_select_by_question_id':
        'SELECT id, question_id, tag_id FROM question_tag WHERE question_id = %s',
    'tag_insert':
        'INSERT INTO tag (title) VALUES (%s)',
    'tag_question_tag_select_by_question_id':
    """SELECT question_tag.id, tag.title
    FROM tag, question_tag
    WHERE question_tag.tag_id = tag.id AND question_tag.question_id = %s
    ORDER BY tag.title""",
    'question_tag_delete_by_id':
        'DELETE FROM question_tag WHERE id = %s'
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
