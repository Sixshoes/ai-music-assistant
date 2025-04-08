from .user import db, User
from .music import Music

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all() 