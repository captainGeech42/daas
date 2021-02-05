import os

from flask import Flask

from .exts import db
from .cmds import db_init

def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "goodsecretkeyhere")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_URI", "sqlite:///daas.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    
    #if not os.path.exists(app.config["SQLALCHEMY_DATABASE_URI"].split("sqlite:///")[1]):
    #    db.create_all(app)

    app.cli.add_command(db_init)
    
    from .auth import auth as auth_blueprint 
    app.register_blueprint(auth_blueprint)

    from .decompile import decompile as decompile_blueprint
    app.register_blueprint(decompile_blueprint)

    return app


