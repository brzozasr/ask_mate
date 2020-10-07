import os

from flask import Blueprint, render_template, request, redirect, flash, url_for, current_app, session
from werkzeug.utils import secure_filename

from database_tools import *
from query import *

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_CONTENT_LENGTH = 0.5 * 1024 * 1024  # 0.5 MB (512 KB - Kilobyte)

upload_file = Blueprint('upload_file', __name__, static_folder='static', template_folder='templates')


def create_dir(dir_to_create):
    try:
        current_dir = os.getcwd()
        entire_path = os.path.join(current_dir, dir_to_create)
        if not os.path.isdir(entire_path):
            os.mkdir(entire_path)
    except OSError as error:
        print(error)


def delete_img(file_name):
    try:
        current_dir = os.getcwd()
        entire_path = os.path.join(current_dir, file_name[1:])
        if os.path.exists(entire_path):
            os.remove(entire_path)
        else:
            print(f'There is no such file: {file_name}!')
    except OSError as e:
        print(f'Error: {e.filename}: {e.strerror}!')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_file.route('/question/<int:question_id>', methods=['GET', 'POST'])
def upload_img_question(question_id):
    if session.get(SESSION_USER_ID) and session.get(SESSION_USER_EMAIL):
        create_dir(UPLOAD_FOLDER)

        current_app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
        # current_app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
        current_app.secret_key = SESSION_SECRET_KEY

        if request.method == 'POST':
            file = request.files['file_img']
            if file.filename == '':
                flash('No selected file!')
                return redirect(request.url)
            elif not allowed_file(file.filename):
                flash('Allowed file extensions: *.png, *.jpg, *.jpeg!')
                return redirect(request.url)
            elif request.content_length > MAX_CONTENT_LENGTH:
                flash('Allowed max size of file is 512 KB (Kilobyte)!')
                return redirect(request.url)
            elif file and allowed_file(file.filename):
                file_img = secure_filename(file.filename)
                file_list = file_img.rsplit('.', 1)
                file_img = f'q{question_id}.{file_list[1].lower()}'
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file_img)
                file_path_db = os.path.join('/', file_path)
                db.execute_sql(query.question_update_img, [file_path_db, question_id])
                file.save(file_path)
                return redirect(url_for('question_view', question_id=question_id, boolean="False"))
            else:
                flash('There is something wrong with upload process!')
                return redirect(request.url)
        else:
            return render_template('upload.html', question_id=question_id)
    else:
        return render_template('not_sign_in_page.html')


@upload_file.route('/answer/<int:answer_id>/<int:question_id>', methods=['GET', 'POST'])
def upload_img_answer(answer_id, question_id):
    if session.get(SESSION_USER_ID) and session.get(SESSION_USER_EMAIL):
        create_dir(UPLOAD_FOLDER)

        current_app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
        current_app.secret_key = SESSION_SECRET_KEY

        if request.method == 'POST':
            file = request.files['file_img']
            if file.filename == '':
                flash('No selected file!')
                return redirect(request.url)
            elif not allowed_file(file.filename):
                flash('Allowed file extensions: *.png, *.jpg, *.jpeg!')
                return redirect(request.url)
            elif request.content_length > MAX_CONTENT_LENGTH:
                flash('Allowed max size of file is 512 KB (Kilobyte)!')
                return redirect(request.url)
            elif file and allowed_file(file.filename):
                file_img = secure_filename(file.filename)
                file_list = file_img.rsplit('.', 1)
                file_img = f'a{answer_id}.{file_list[1].lower()}'
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file_img)
                file_path_db = os.path.join('/', file_path)
                db.execute_sql(query.answer_update_img, [file_path_db, answer_id])
                file.save(file_path)
                return redirect(url_for('question_view', question_id=question_id, boolean="False"))
            else:
                flash('There is something wrong with upload process!')
                return redirect(request.url)
        else:
            return render_template('upload.html', answer_id=answer_id, question_id=question_id)
    else:
        return render_template('not_sign_in_page.html')
