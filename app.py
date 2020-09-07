from flask import Flask, url_for, render_template
from database_tools import *
from query import *


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/list')
def question_list():
    questions_list = db.execute_sql(query.question_select_all_desc_by_date)
    header_table = ['ID', 'Date', 'Views', 'Vote', 'Title', 'Question', 'Image']
    # TODO sort in query for DB
    return render_template('list.html', header_table=header_table, questions=questions_list)


@app.route('/question/<int:question_id>')
def question_view(question_id):
    quest_answers = db.execute_sql(query.question_select_all_desc_by_date)
    return render_template('question.html', quest_answers=quest_answers, question_id=question_id)


@app.errorhandler(404)
def page_not_found(error):
    # TODO html page
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run()
