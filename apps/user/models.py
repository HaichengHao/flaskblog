"""
@File    :model.py
@Editor  : 百年
@Date    :2025/8/10 9:13 
"""
from exts.extensions import db
from datetime import datetime


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(128), nullable=False)  # 要放的是要加密的密码,所以大小应当是加密之后的大小,故db.String(Size) 的Size要谨慎设置
    phone = db.Column(db.String(11), unique=True, nullable=False)
    email = db.Column(db.String(30))
    icon = db.Column(db.String(100))
    regi_date = db.Column(db.DateTime, default=datetime.now)
    isdelete = db.Column(db.Boolean, default=False)  # 逻辑删除
    # start_cb:增减一个字段,不会在数据库中出现,用于链接字段,relationship是在view和templates中体现的
    articles = db.relationship('Article', backref='user', lazy='select')
    photo = db.relationship('Photo', backref='user')
    comment=db.relationship('Comment',backref='user')
    selfintro = db.Relationship('Aboutme',backref='user')
    # end_cb 需要注意它是模板层面的,所以不需要再做迁移操作
    def __str__(self):
        return self.username


class Photo(db.Model):
    __tablename__ = "photo"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    photo_name = db.Column(db.String(50), nullable=False)
    photo_datatime = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __str__(self):
        return self.photo_name


#tips:新建一个表用于存储'关于我的'
class Aboutme(db.Model):
    __tablename__='aboutme'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    selfintro = db.Column(db.String(50),nullable=True)
    #其实如果要做关于我这个板块,应该是一个用户只有一个“关于我”,所以要加上唯一约束unique=True
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    intro_datetime = db.Column(db.DateTime,default=datetime.now)
    def __str__(self):
        return self.id
