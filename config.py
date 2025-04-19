import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'CopperTin2950')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    FLASKY_MAIL_SUBJECT_PREFIX = '[Octamedic]'
    FLASKY_MAIL_SENDER = 'Octamedic Admin <octamedicc@gmail.com>'
    FLASKY_ADMIN = os.environ.get('OCTAMEDIC_ADMIN')
    UPLOADED_PHOTOS_DEST= './app/images/'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.googlemail.com'
    # MAIL_SERVER = 'localhost'
    # MAIL_PORT = 1025
    MAIL_DEFAULT_SENDER = 'Octamedic <octamedicc@gmail.com>'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    # MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL', 'mysql://mediblitz:Copper_Tin2950@localhost:3306/mediblitz')

class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL')

config = {
'development': DevelopmentConfig,
'testing': TestingConfig,
'default': DevelopmentConfig
}
