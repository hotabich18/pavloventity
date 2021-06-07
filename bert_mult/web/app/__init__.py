from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# создание экземпляра приложения
app = Flask(__name__)
app.config.from_object(os.environ.get('FLASK_ENV') or 'config.ProductionConfig')
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.jinja_options['enable_async'] = True

# инициализирует расширения
db = SQLAlchemy(app)

# import views
from . import views
from . import api
