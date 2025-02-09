from app import db
from SAApp import app
from app.main.models import Course, User, Student, Instructor, SA_Position, Enrollment, Application
from config import Config

import sqlalchemy as sqla
import sqlalchemy.orm as sqlo

app.app_context().push()

db.create_all()

