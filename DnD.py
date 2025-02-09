from app import db, create_app
from config import Config
from app.main.models import MonsterGroup, PlayerGroup, Combat
import sqlalchemy as sqla
import sqlalchemy.orm as sqlo
from flask_wtf.csrf import CSRFProtect

#from flask_session import Session
#from flask import session

app = create_app(Config)
csrf = CSRFProtect(app)

@app.shell_context_processor
def make_shell_context():
    return {'sqla': sqla, 'sqlo': sqlo, 'db': db, 'MonsterGroup': MonsterGroup, 'PlayerGroup': PlayerGroup, 'Combat' : Combat}

@app.before_request
def initDB(*args, **kwargs):
    if app._got_first_request:
        db.create_all()
        

if __name__ == "__main__":
    app.run(debug=True)