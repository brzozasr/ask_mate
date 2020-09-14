from flask import Blueprint, render_template, current_app

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

upload_file = Blueprint('upload_file', __name__, static_folder='static', template_folder='templates')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


print(allowed_file("test.jpg"))


@upload_file.route('/question/<int:question_id>')
def upload_img_question(question_id):
    current_app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    current_app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024
    return render_template('404.html')


@upload_file.route('/answer/<int:answer_id>')
def upload_img_answer(answer_id):
    current_app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    current_app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024
    return render_template('404.html')
