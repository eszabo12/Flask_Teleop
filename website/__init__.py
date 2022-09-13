from flask import Flask

def create_app():
    app = Flask(__name__) #represents name of file
    app.config['SECRET_KEY'] = 'ksndf2nD4n2DosX8REnd4eE'
    
    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    return app