from flask import Flask

from tools import *
from upload_file import *

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.register_blueprint(upload_file, url_prefix='/upload')


@app.route('/')
def index():
    return render_template('index.html')


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

    answer_count = db.execute_sql(query.answer_count_fk_question_id, [question_id])
    question = db.execute_sql(query.question_select_by_id, [question_id])
    answer = db.execute_sql(query.answer_select_by_id, [question_id])
    return render_template('question.html', question=question, answer=answer, answer_count=answer_count)


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
        if '/question/' in request.path:
            comment_question = request.form['comment']
            db.execute_sql(query.comment_insert_to_question, [question_id, comment_question])
            return redirect(url_for('question_view', question_id=question_id, boolean="False"))
        elif '/answer/' in request.path:
            comment_answer = request.form['comment']
            db.execute_sql(query.comment_insert_to_answer, [question_id, answer_id, comment_answer])
            return redirect(url_for('question_view', question_id=question_id, boolean="False"))
        elif '/comment/' in request.path:
            return redirect(url_for('question_view', question_id=question_id, boolean="False"))
    else:
        return render_template('form_comment.html', question_id=question_id, answer_id=answer_id, comment_id=comment_id)


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


@app.errorhandler(404)
def page_not_found():
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run()
