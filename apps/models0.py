
from datetime import datetime



from apps import db


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    pwd = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    face = db.Column(db.String(255), unique=True, nullable=False)
    intro = db.Column(db.TEXT)
    uuid = db.Column(db.String(255), unique=True, nullable=False)
    addtime = db.Column(db.DATETIME, index=True, default=datetime.now)

    def __repr__(self):
        return '<User %r, 密码 %r>' % (self.name, self.pwd)


    def check_pwd(self, pwd):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.pwd, pwd)


if __name__ == '__main__':
    db.drop_all()
    db.create_all()