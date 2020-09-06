from flask import Flask
from database_tools import *


app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World! Ala ma kot'


if __name__ == '__main__':
    app.run()
