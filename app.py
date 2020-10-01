from flask import Flask

from tools import *
from upload_file import *

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.register_blueprint(upload_file, url_prefix='/upload')
app.jinja_env.globals.update(highlight_phrase=highlight_phrase, is_list=is_list)
app.secret_key = b'secret_key!@#$%'


@app.route('/')
def index():
    last_5 = db.execute_sql(query.question_select_limit_5_desc_by_date)
    cols_to_show = {'Date': 1, 'View': 2, 'Vote': 3, 'Title': 4, 'Question': 5}
    return render_template('index.html', last_5=last_5, cols=cols_to_show)


@app.route('/list')
def question_list():
    cols_to_show = {'Date': 1, 'View': 2, 'Vote': 3, 'Title': 4, 'Question': 5}
    if (order_by := request.args.get('order_by')) is None:
        order_by = 'date'
    if (order_direction := request.args.get('order_direction')) is None:
        order_direction = 'desc'
    order_data = (order_by, order_direction)
    sorting_query = get_sort_query(order_direction, order_by)
    questions_list = db.execute_sql(sorting_query)
    return render_template('list.html', questions=questions_list, cols=cols_to_show, order_data=order_data)


@app.route('/question/<int:question_id>')
@app.route('/question/<int:question_id>/<boolean>')
def question_view(question_id, boolean="True"):
    if eval(boolean):
        db.execute_sql(query.question_update_view_number_by_id, [question_id])

    tags = db.execute_sql(query.tag_question_tag_select_by_question_id, [question_id])
    answer_count = db.execute_sql(query.answer_count_fk_question_id, [question_id])
    question = db.execute_sql(query.question_select_by_id, [question_id])
    answer = db.execute_sql(query.answer_select_by_id, [question_id])
    comment = db.execute_sql(query.comment_select_by_question_id, [question_id])
    return render_template('question.html', question=question, answer=answer, comment=comment,
                           answer_count=answer_count, tags=tags)


@app.route('/vote/<element>/<int:question_id>/<int:value>/')
@app.route('/vote/<element>/<int:question_id>/<int:value>/<int:answer_id>')
def vote(question_id, element, value, answer_id=None):
    elements = {'question': 'question', 'answer': 'answer', 'comment': 'comment'}

    if value == 2:
        value = -1

    if element == elements['question']:
        db.execute_sql(query.question_update_vote_number_by_id, [value, question_id])
    elif element == elements['answer']:
        db.execute_sql(query.answer_update_vote_number_by_id, [value, answer_id])

    return redirect(url_for('question_view', question_id=question_id, boolean="False"))


@app.route('/add_question', methods=['GET', 'POST'])
def add_question():
    if request.method == 'POST':
        title = request.form['title']
        question = request.form['question']
        db.execute_sql(query.question_insert, [title, question])
        return redirect(url_for('question_list'))
    else:
        return render_template('add_edit_question.html')


@app.route('/question/<int:question_id>/new_answer', methods=['GET', 'POST'])
def new_answer(question_id):
    if request.method == 'POST':
        answer = request.form['answer']
        db.execute_sql(query.answer_insert, [question_id, answer])
        return redirect(url_for('question_view', question_id=question_id, boolean="False"))
    else:
        return render_template('new_answer.html', question_id=question_id)


@app.route('/question/<int:question_id>/new-comment', endpoint='comment_question', methods=['GET', 'POST'])
@app.route('/answer/<int:question_id>/<int:answer_id>/new-comment', endpoint='comment_answer', methods=['GET', 'POST'])
@app.route('/comment/<int:question_id>/<int:comment_id>/edit', endpoint='comment_edit', methods=['GET', 'POST'])
def add_comment(question_id, answer_id=None, comment_id=None):
    if request.method == 'POST':
        if request.endpoint == 'comment_question':
            comment_question = request.form['comment']
            db.execute_sql(query.comment_insert_to_question, [question_id, comment_question])
            return redirect(url_for('question_view', question_id=question_id, boolean="False"))
        elif request.endpoint == 'comment_answer':
            comment_answer = request.form['comment']
            db.execute_sql(query.comment_insert_to_answer, [question_id, answer_id, comment_answer])
            return redirect(url_for('question_view', question_id=question_id, boolean="False"))
        elif request.endpoint == 'comment_edit':
            comment_edit = request.form['comment']
            db.execute_sql(query.comment_update_by_id, [comment_edit, comment_id])
            return redirect(url_for('question_view', question_id=question_id, boolean="False"))
    else:
        comment = db.execute_sql(query.comment_select_by_comment_id, [comment_id])
        return render_template('form_comment.html', question_id=question_id, answer_id=answer_id, comment_id=comment_id,
                               comment=comment)


@app.route('/question/<int:question_id>/delete')
def delete_question(question_id):
    list_img = []
    answer_path_img = db.execute_sql(query.answer_get_img_path, [question_id])
    if len(answer_path_img) > 0:
        for answer_img in answer_path_img:
            if answer_img[0] is not None:
                list_img.append(answer_img[0])

    question_path_img = db.execute_sql(query.question_delete, [question_id])
    if len(question_path_img) > 0:
        if question_path_img[0][0] is not None:
            list_img.append(question_path_img[0][0])

    if len(list_img) > 0:
        for path_img in list_img:
            delete_img(path_img)
    return redirect(url_for('question_list'))


@app.route('/answer/<int:answer_id>/delete')
def delete_answer(answer_id):
    path_and_id = db.execute_sql(query.answer_delete, [answer_id])

    if len(path_and_id) > 0 and path_and_id[0][0] is not None:
        delete_img(path_and_id[0][0])

    return redirect(url_for('question_view', question_id=path_and_id[0][1], boolean="False"))


@app.route('/question/<int:question_id>/edit', methods=['GET', 'POST'])
def edit_question(question_id):
    if request.method == 'POST':
        title = request.form['title']
        question = request.form['question']
        db.execute_sql(query.question_update, [title, question, question_id])
        return redirect(url_for('question_view', question_id=question_id, boolean="False"))
    else:
        question = db.execute_sql(query.question_select_by_id, [question_id])
        return render_template('add_edit_question.html', question=question)


@app.route('/search')
def search():
    if request.args.get('advanced_search') is None:
        phrase = request.args.get('search')
        query_phrase = f'%{phrase}%'
        question_search = db.execute_sql(query.questions_search, {'search': query_phrase})
        cols_to_show = {'Date': 1, 'View': 2, 'Vote': 3, 'Title': 4, 'Question': 5}
        return render_template('search.html', search=question_search, cols=cols_to_show, phrase=phrase)
    elif request.args.get('advanced_search') == 'on':
        phrase = request.args.get('search')
        query_phrase = f'%{phrase}%'
        adv_search = db.execute_sql(query.advanced_search, {'search': query_phrase})
        return render_template('advanced_search.html', adv_search=adv_search, phrase=phrase)
    else:
        return redirect(url_for('question_list'))


@app.route('/question/<int:question_id>/new-tag', methods=['GET', 'POST'])
def new_tag(question_id):
    if request.method == 'POST':
        posted_tags = request.form.to_dict()
        if len(posted_tags) > 0:
            tags_list = []
            for tag_id in posted_tags.keys():
                tags_list.append([question_id, int(tag_id)])

            db.execute_multi_sql(query.question_tag_insert, tags_list)
            return redirect(url_for('question_view', question_id=question_id, boolean=False))
        else:
            flash('To send the form you need to select at least one tag!')
            return redirect(request.url)
    elif (tag := request.args.get('add-new-tag')) is not None and len(tag) > 1:
        error = db.execute_sql(query.tag_insert, [tag])
        if error:
            flash(error)
        return redirect(url_for('new_tag', question_id=question_id))
    else:
        list_add_tags = []
        quest_tags = db.execute_sql(query.question_tag_select_by_question_id, [question_id])
        for tag in quest_tags:
            list_add_tags.append(tag[2])
        tags = db.execute_sql(query.tag_select)
        return render_template('tags.html', question_id=question_id, tags=tags, add_tags=list_add_tags)


@app.route('/question/<int:question_id>/tag/<int:tag_id>/delete')
def tag_delete(question_id, tag_id):
    db.execute_sql(query.question_tag_delete_by_id, [tag_id])
    return redirect(url_for('question_view', question_id=question_id, boolean=False))


@app.errorhandler(404)
def page_not_found():
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run()
