# @Author    : 百年
# @FileName  :view.py
# @DateTime  :2025/8/27 16:50

from flask import Blueprint, request, render_template, session
from sqlalchemy import and_

from apps.user.models import User
from apps.article.models import Article
from exts.extensions import db

article_bp = Blueprint(name='article', import_name=__name__)


@article_bp.route('/publish', methods=['POST', 'GET'], endpoint='publish')
def article_publish():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        uid = request.form.get('uid')
        article = Article()
        article.title = title
        article.content = content
        article.user_id = uid
        db.session.add(article)
        db.session.commit()
        return '添加成功'
    uname = session.get('uname')
    print('要发布文章的用户是'+uname)
    user = User.query.filter(and_(User.isdelete == False, User.username == uname)).first()
    print(user)
    print(user.id,user.username)
    return render_template('article/add_article.html', username=uname,user=user)


@article_bp.route('/all_article', methods=['POST', 'GET'], endpoint='all_article')
def article_all():
    if request.method == 'POST':
        pass
    username = session.get('uname')
    all_article = Article.query.all()
    return render_template('article/all.html', all_article=all_article,username=username)


@article_bp.route('/all1', endpoint='all1')
def all_article():
    id = request.args.get('id')
    user = User.query.get(id)
    return render_template('article/all1.html', user=user)
