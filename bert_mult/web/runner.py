from app import app
from flask_script import Manager, Shell
from app.controller import Rest, Server
from nltk.tokenize import sent_tokenize
import nltk
import logging
from logging.handlers import RotatingFileHandler
import os
from logging import Formatter

manager = Manager(app)
rest1 = Rest(5000, "pavlov_rest_1")
rest2 = Rest(5001, "pavlov_rest_2")
rest2.stop()
server = Server(rest1, rest2, "/web", "/root/.deeppavlov", "/saved_models", "/current_model")

try:
      sent_tokenize("Test.")
except LookupError:
    nltk.download('punkt')


# эти переменные доступны внутри оболочки без явного импорта
def make_shell_context():
    return dict(app=app)


manager.add_command('shell', Shell(make_context=make_shell_context))
#manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    if not os.path.exists('/web/logs'):
        os.mkdir('/web/logs')
    file_handler = RotatingFileHandler('/web/logs/server.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info("Server started")
    manager.run()
        
