# @Author    : 百年
# @FileName  :view.py
# @DateTime  :2025/8/27 16:50

from flask import Blueprint, request, render_template, session, g, redirect, jsonify
from sqlalchemy import and_, desc

from apps.user.models import User
from apps.article.models import Article, Article_type
from exts.extensions import db

article_bp = Blueprint(name='article', import_name=__name__)


@article_bp.route('/publish', methods=['POST', 'GET'], endpoint='publish')
def article_publish():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        uid = request.form.get('uid')
        typeid = request.form.get('typeid')
        print("🔍 typeid 的值:", repr(typeid))
        if not typeid:
            return '必须选择文章分类', 400
        print(f'========={title},{typeid}')
        article = Article()
        article.title = title
        article.content = content
        article.user_id = uid
        article.type_id = typeid
        db.session.add(article)
        db.session.commit()
        return redirect('/all_article')
    uname = session.get('uname')
    print('要发布文章的用户是' + uname)
    user = User.query.filter(and_(User.isdelete == False, User.username == uname)).first()
    # article_types = Article_type.query.all() 因为设置了全局g这里就不需要了
    print(user)
    print(user.id, user.username)
    # return render_template('article/add_article.html', username=uname, user=user, article_types=article_types)
    return render_template('article/add_article.html', username=uname, user=user)


@article_bp.route('/all_article', methods=['POST', 'GET'], endpoint='all_article')
def article_all():
    if request.method == 'POST':
        pass
    username = session.get('uname')
    # article_types = Article_type.query.all()
    # g.article_types = article_types
    if username != None:
        all_article = Article.query.order_by(desc(Article.pdatetime)).all()
        return render_template('article/all.html', all_article=all_article, username=username)
        # return render_template('article/all.html', all_article=all_article)
    else:
        article_types = Article_type.query.all()
        g.article_types = article_types
        all_article = Article.query.order_by(desc(Article.pdatetime)).all()
        return render_template('article/all.html', all_article=all_article)


@article_bp.route('/all1', endpoint='all1')
def all_article():
    id = request.args.get('id')
    user = User.query.get(id)
    return render_template('article/all1.html', user=user)


# tips:制定文章详情页路由
@article_bp.route('/detail', endpoint='detail')
def article_detail():
    username = session.get('uname')
    article_id = request.args.get('article_id')
    article = Article.query.get(article_id)
    viewed_articles = session.get('viewed_articles',[])
    if article_id not in viewed_articles:
        article.click_num+=1
        db.session.commit()

        #记录已查看
        viewed_articles.append(article_id)
        session['viewed_articles'] =viewed_articles
    return render_template('article/detail.html', article=article, username=username)


# @article_bp.route('/clicknumadd', endpoint='clicknumadd')
# def clicknumadd_route():
#     artid = request.args.get('artid')
#     article = Article.query.get(artid)
#     article.click_num += 1
#     db.session.commit()
#     return jsonify(
#         {
#             'success': True,
#             'num': article.click_num,
#             'artid': artid
#         }
#     )


@article_bp.route('/love', endpoint='love')
def article_love():
    artid = request.args.get('artid')
    article = Article.query.get(artid)
    article.love_num += 1
    db.session.commit()
    return jsonify(
        {
            'success': True,
            'num': article.love_num,
            'artid': artid
        }
    )
