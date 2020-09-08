from flask import Flask, render_template
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
def question_view(question_id):
    view_counter = db.execute_sql(f"SELECT view_number FROM question WHERE id = {question_id}")
    db.execute_sql(f"UPDATE question SET view_number = {view_counter[0][0] + 1} WHERE id = {question_id}")
    question = db.execute_sql(f"SELECT * FROM question WHERE id = {question_id}")
    answer = db.execute_sql(f"SELECT * FROM answer WHERE question_id = {question_id}")
    return render_template('question.html', question=question, answer=answer)


@app.errorhandler(404)
def page_not_found():
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run()
