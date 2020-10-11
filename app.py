import bcrypt
from flask import Flask

from tools import *
from upload_file import *

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.register_blueprint(upload_file, url_prefix='/upload')
app.jinja_env.globals.update(highlight_phrase=highlight_phrase, is_list=is_list, cut_url=cut_url)
app.secret_key = SESSION_SECRET_KEY


@app.context_processor
def inject_global():
    return dict(user_id=SESSION_USER_ID, user_email=SESSION_USER_EMAIL)


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
        if session.get(SESSION_USER_ID) and session.get(SESSION_USER_EMAIL):
            title = request.form['title']
            question = request.form['question']
            db.execute_sql(query.question_insert, [title, question, session.get(SESSION_USER_ID)])
            return redirect(url_for('question_list'))
        else:
            return render_template('not_sign_in_page.html')
    else:
        return render_template('add_edit_question.html')


@app.route('/question/<int:question_id>/new_answer', endpoint='add_answer', methods=['GET', 'POST'])
@app.route('/answer/<int:question_id>/<int:answer_id>/edit', endpoint='edit_answer', methods=['GET', 'POST'])
def new_answer(question_id, answer_id=None):
    if request.method == 'POST':
        if session.get(SESSION_USER_ID) and session.get(SESSION_USER_EMAIL):
            answer = request.form['answer']
            if request.endpoint == 'add_answer':
                db.execute_sql(query.answer_insert, [question_id, answer, session.get(SESSION_USER_ID)])
                return redirect(url_for('question_view', question_id=question_id, boolean="False"))
            elif request.endpoint == 'edit_answer':
                db.execute_sql(query.answer_update_by_id, [answer, answer_id])
                return redirect(url_for('question_view', question_id=question_id, boolean="False"))
        else:
            return render_template('not_sign_in_page.html')
    else:
        answer_txt = db.execute_sql(query.answer_select_message_by_id, [answer_id])
        return render_template('new_answer.html', question_id=question_id, answer_id=answer_id,
                               answer_txt=answer_txt)


@app.route('/accept/<int:accept_sts>/<int:answer_id>/<int:answer_user_id>/<int:question_user_id>/<int:question_id>')
def accept_answer(accept_sts, answer_id, answer_user_id, question_user_id, question_id):
    if session.get(SESSION_USER_ID) and session.get(SESSION_USER_EMAIL) and session.get(SESSION_USER_ID) == question_user_id:
        if accept_sts == 1:
            accept = True
            db.execute_sql(query.users_gain_lost_reputation, [15, answer_user_id])
        elif accept_sts == 0:
            accept = False
            db.execute_sql(query.users_gain_lost_reputation, [-15, answer_user_id])
        else:
            accept = False
        db.execute_sql(query.answer_update_acceptance_by_id, [accept, answer_id])
        return redirect(url_for('question_view', question_id=question_id, boolean="True"))
    else:
        return render_template('not_sign_in_page.html')


@app.route('/question/<int:question_id>/new-comment', endpoint='comment_question', methods=['GET', 'POST'])
@app.route('/answer/<int:question_id>/<int:answer_id>/new-comment', endpoint='comment_answer', methods=['GET', 'POST'])
@app.route('/comment/<int:question_id>/<int:comment_id>/edit', endpoint='comment_edit', methods=['GET', 'POST'])
def add_comment(question_id, answer_id=None, comment_id=None):
    if request.method == 'POST':
        if session.get(SESSION_USER_ID) and session.get(SESSION_USER_EMAIL):
            if request.endpoint == 'comment_question':
                comment_question = request.form['comment']
                db.execute_sql(query.comment_insert_to_question, [question_id, comment_question, session.get(SESSION_USER_ID)])
                return redirect(url_for('question_view', question_id=question_id, boolean="False"))
            elif request.endpoint == 'comment_answer':
                comment_answer = request.form['comment']
                db.execute_sql(query.comment_insert_to_answer, [question_id, answer_id, comment_answer, session.get(SESSION_USER_ID)])
                return redirect(url_for('question_view', question_id=question_id, boolean="False"))
            elif request.endpoint == 'comment_edit':
                comment_edit = request.form['comment']
                db.execute_sql(query.comment_update_by_id, [comment_edit, comment_id])
                return redirect(url_for('question_view', question_id=question_id, boolean="False"))
        else:
            return render_template('not_sign_in_page.html')
    else:
        comment = db.execute_sql(query.comment_select_by_comment_id, [comment_id])
        return render_template('form_comment.html', question_id=question_id, answer_id=answer_id, comment_id=comment_id,
                               comment=comment)


@app.route('/comments/<int:comment_id>/delete')
def del_comment(comment_id):
    if session.get(SESSION_USER_ID) and session.get(SESSION_USER_EMAIL):
        quest_id = db.execute_sql(query.comment_delete, [comment_id])
        return redirect(url_for('question_view', question_id=quest_id[0][0], boolean="False"))
    else:
        return render_template('not_sign_in_page.html')


@app.route('/question/<int:question_id>/delete')
def delete_question(question_id):
    if session.get(SESSION_USER_ID) and session.get(SESSION_USER_EMAIL):
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
    else:
        return render_template('not_sign_in_page.html')


@app.route('/answer/<int:answer_id>/delete')
def delete_answer(answer_id):
    if session.get(SESSION_USER_ID) and session.get(SESSION_USER_EMAIL):
        path_and_id = db.execute_sql(query.answer_delete, [answer_id])

        if len(path_and_id) > 0 and path_and_id[0][0] is not None:
            delete_img(path_and_id[0][0])

        return redirect(url_for('question_view', question_id=path_and_id[0][1], boolean="False"))
    else:
        return render_template('not_sign_in_page.html')


@app.route('/question/<int:question_id>/edit', methods=['GET', 'POST'])
def edit_question(question_id):
    if request.method == 'POST':
        if session.get(SESSION_USER_ID) and session.get(SESSION_USER_EMAIL):
            title = request.form['title']
            question = request.form['question']
            db.execute_sql(query.question_update, [title, question, question_id])
            return redirect(url_for('question_view', question_id=question_id, boolean="False"))
        else:
            return render_template('not_sign_in_page.html')
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
    if session.get(SESSION_USER_ID) and session.get(SESSION_USER_EMAIL):
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
        elif (tag := request.args.get('add-new-tag')) is not None and len(tag) > 0:
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
    else:
        return render_template('not_sign_in_page.html')


@app.route('/question/<int:question_id>/tag/<int:tag_id>/delete')
def tag_delete(question_id, tag_id):
    if session.get(SESSION_USER_ID) and session.get(SESSION_USER_EMAIL):
        db.execute_sql(query.question_tag_delete_by_id, [tag_id])
        return redirect(url_for('question_view', question_id=question_id, boolean=False))
    else:
        return render_template('not_sign_in_page.html')


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form['log-email']
        first_pwd = request.form['first-pwd']
        second_pwd = request.form['second-pwd']
        if not is_email_correct(email):
            error = {'email': 'Invalid email address!'}
            return render_template('sign_up.html', email=email, first_pwd=first_pwd, second_pwd=second_pwd, error=error)
        elif not is_same_pwp(first_pwd, second_pwd):
            error = {'pass': 'Passwords must be the same!'}
            return render_template('sign_up.html', email=email, first_pwd=first_pwd, second_pwd=second_pwd, error=error)
        else:
            pwd_hash = bcrypt.hashpw(first_pwd.encode('utf-8'), bcrypt.gensalt())
            error_txt = db.execute_sql(query.users_registration, [email, pwd_hash.decode('utf-8')])
            if error_txt:
                error = {'db_error': str(error_txt)}
                return render_template('sign_up.html', email=email, first_pwd=first_pwd, second_pwd=second_pwd,
                                       error=error)
            else:
                info = 'You have been successfully registered'
                return render_template('sign_up.html', info=info)
    else:
        return render_template('sign_up.html')


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        user_name = request.form['user-name']
        log_pwd = request.form['log-pwd']
        log_data = db.execute_sql(query.users_select_by_email, [user_name])
        if log_data and type(log_data) == list and len(log_data) == 1:
            user_data = {}
            dict_key = [SESSION_USER_ID, SESSION_USER_EMAIL, 'user_pwd']
            i = 0
            for data in log_data[0]:
                user_data[dict_key[i]] = data
                i += 1
            if user_name == user_data[SESSION_USER_EMAIL] and bcrypt.checkpw(log_pwd.encode('utf-8'),
                                                                             user_data['user_pwd'].encode('utf-8')):
                session[SESSION_USER_ID] = user_data[SESSION_USER_ID]
                session[SESSION_USER_EMAIL] = user_data[SESSION_USER_EMAIL]
                return redirect(url_for('index'))
            else:
                error = {'log_error': 'Invalid email address or password!'}
                return render_template('sign_in.html', error=error)
        else:
            if type(log_data) == list:
                error = {'log_error': 'Invalid email address or password!'}
            else:
                error = {'db_error': str(log_data)}
            return render_template('sign_in.html', error=error)
    else:
        return render_template('sign_in.html')


@app.route('/sign_out')
def sign_out():
    if session.get(SESSION_USER_ID) and session.get(SESSION_USER_EMAIL):
        session.pop(SESSION_USER_ID, None)
        session.pop(SESSION_USER_EMAIL, None)
        session.clear()
        return redirect(url_for('index'))
    else:
        return render_template('not_sign_in_page.html')


@app.route('/users')
def users():
    if session.get(SESSION_USER_ID) and session.get(SESSION_USER_EMAIL):
        users_data = db.execute_sql(query.users_activation)
        if users_data and type(users_data) == list and len(users_data) > 0:
            error = None
            return render_template('users.html', error=error, users=users_data)
        else:
            if type(users_data) == list:
                error = 'There are no users!'
            else:
                error = str(users_data)

            return render_template('users.html', error=error)
    else:
        return render_template('not_sign_in_page.html')


@app.route('/user/<int:user_id>')
def user_page(user_id):
    if session.get(SESSION_USER_ID) and session.get(SESSION_USER_EMAIL):
        user_data = db.execute_sql(query.user_activation_page, [user_id])
        user_questions = db.execute_sql(query.question_select_by_user_id, [user_id])
        user_answer = db.execute_sql(query.answer_select_by_user_id, [user_id])
        user_comment = db.execute_sql(query.comment_select_by_user_id, [user_id])
        if user_data and type(user_data) == list and len(user_data) == 1:
            error = None
            titles = ['User ID:', 'User\'s email address:', 'Registration date:', 'Asked questions:',
                      'Given answers:', 'Posted comments:', 'Reputation:']
            user_dict = {}
            i = 0
            for cell in user_data[0]:
                user_dict[titles[i]] = cell
                i += 1
            return render_template('user.html', error=error, user_dict=user_dict, user_questions=user_questions,
                                   user_answer=user_answer, user_comment=user_comment)
        else:
            if type(user_data) == list:
                error = 'There is no such user!'
            else:
                error = str(user_data)

            return render_template('users.html', error=error)
    else:
        return render_template('not_sign_in_page.html')


@app.errorhandler(404)
def page_not_found():
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run()
