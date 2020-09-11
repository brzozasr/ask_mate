from flask import Flask, render_template, request, redirect, url_for
from database_tools import *
from query import *


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/list')
def question_list():
    questions_list = db.execute_sql(query.question_select_all_desc_by_date)
    cols_to_show = {'Date': 1, 'View': 2, 'Vote': 3, 'Title': 4, 'Question': 5}
    return render_template('list.html', questions=questions_list, cols=cols_to_show)


@app.route('/question/<int:question_id>')
@app.route('/question/<int:question_id>/<boolean>')
def question_view(question_id, boolean="True"):
    if eval(boolean):
        view_counter = db.execute_sql(f"SELECT view_number FROM question WHERE id = {question_id}")
        db.execute_sql(f"UPDATE question SET view_number = {view_counter[0][0] + 1} WHERE id = {question_id}")

    question = db.execute_sql(f"SELECT * FROM question WHERE id = {question_id}")
    answer = db.execute_sql(f"SELECT * FROM answer WHERE question_id = {question_id}")
    return render_template('question.html', question=question, answer=answer)


@app.route('/vote/<element>/<int:question_id>/<int:value>/')
@app.route('/vote/<element>/<int:question_id>/<int:value>/<int:vote_id>')
def vote(question_id, element, value, vote_id=None):
    elements = {'question': 'question', 'answer': 'answer', 'comment': 'comment'}
    if value == 2:
        value = -1

    if element == elements['question']:
        vote_counter = db.execute_sql(f"SELECT vote_number FROM question WHERE id = {question_id}")
        db.execute_sql(f"UPDATE question SET vote_number = {vote_counter[0][0] + value} WHERE id = {question_id}")
    return redirect(url_for('question_view', question_id=question_id, boolean="False"))


@app.route('/add_question', methods=['GET', 'POST'])
def add_question():
    if request.method == 'POST':
        title = request.form['title']
        question = request.form['question']
        db.execute_sql(f"""INSERT INTO question (title, message) VALUES (%s, %s)""", (title, question))
        return redirect(url_for('question_list'))
    else:
        return render_template('add_question.html')


@app.errorhandler(404)
def page_not_found():
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run()
