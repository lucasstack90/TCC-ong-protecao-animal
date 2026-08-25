from flask import flask 

app = flask (__name__)

from views.views import *

if __name__ == "__main__":
    app.run()