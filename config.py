import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///' + os.path.join(basedir, 'student.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ROOT_PATH = basedir
    STATIC_FOLDER = os.path.join(basedir, 'app//static')
    TEMPLATE_FOLDER_MAIN = os.path.join(basedir, 'app//main//templates')
    TEMPLATE_FOLDER_ERRORS = os.path.join(basedir, 'app//errors//templates')
    TEMPLATE_FOLDER_AUTH = os.path.join(basedir, 'app//auth//templates')
    AUTHORITY= os.getenv("AUTHORITY")
    # Application (client) ID of app registration
    CLIENT_ID = os.getenv("CLIENT_ID")
    # Application's generated client secret: never check this into source control!
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    
    REDIRECT_PATH = "/getAToken"  # Used for forming an absolute URL to your redirect URI.

    ENDPOINT = 'https://graph.microsoft.com/v1.0/me'  
    SCOPE = ["User.Read"]

    # Tells the Flask-session extension to store sessions in the filesystem
    SESSION_TYPE = "filesystem"