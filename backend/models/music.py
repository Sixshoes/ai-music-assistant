from datetime import datetime
from .user import db

class Music(db.Model):
    __tablename__ = 'musics'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 建立與用戶的關聯
    user = db.relationship('User', backref=db.backref('musics', lazy=True))
    
    def __repr__(self):
        return f'<Music {self.title}>' 