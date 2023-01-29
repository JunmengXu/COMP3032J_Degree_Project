import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config():
    # SECRET_KEY
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    # RECAPTCHA_PUBLIC_KEY
    RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY') or 'you-will-never-guess'

    # Database configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_NUM_PER_PAGE = 12

class DevelopmentConfig(Config):
    DEBUG=True
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data-dev.db')

class TestingConfig(Config):
    TESTING=True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data-test.db')

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data.db')

config={"development":DevelopmentConfig,
        "testing":TestingConfig,
        "production":ProductionConfig,
        "default":DevelopmentConfig}