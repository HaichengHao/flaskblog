# @Author    : 百年
# @FileName  :view.py
# @DateTime  :2025/8/27 16:50

from flask import Blueprint, request, render_template, session, g, redirect, jsonify, url_for
from sqlalchemy import and_, desc, or_

from apps.user.models import User
from apps.article.models import Article, Article_type, Comment
from exts.extensions import db

article_bp = Blueprint(name='article', import_name=__name__)


@article_bp.before_request
def load_user():
    """在每个请求前加载当前登录用户"""
    username = session.get('uname')
    article_types = Article_type.query.all()
    g.article_types = article_types
    # 未登录
    if not username:
        g.userme = None
        return

    # 已登录，查询有效用户（逻辑删除的不算）
    try:
        user = User.query.filter_by(username=username, isdelete=0).first()
        if user:
            g.userme = user
        else:
            # 用户不存在或已被删除
            session.clear()
            g.userme = None
    except Exception as e:
        # 数据库异常兜底
        print(f"⚠️ 加载用户失败: {e}")
        g.userme = None


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
@article_bp.route('/detail', endpoint='detail', methods=['GET', 'POST'])
def article_detail():
    # tips:新增处理评论
    if request.method == 'POST':
        pass

    username = session.get('uname')
    if username != None:
        # g.userme.username = username
        user = User.query.filter_by(username=username, isdelete=0).first()
        if user:
            g.userme = user
        article_id = request.args.get('article_id')
        article = Article.query.get(article_id)
        # tips:处理评论的分页
        page_num = int(request.args.get('page', 1))  # important:注意一定要将其转化为整形
        pagination = Comment.query.order_by(desc(Comment.cdatetime)).filter(Comment.aid == article_id).paginate(
            page=page_num, per_page=4)

        viewed_articles = session.get('viewed_articles', [])
        if article_id not in viewed_articles:
            article.click_num += 1
            db.session.commit()

            # 记录已查看
            viewed_articles.append(article_id)
            session['viewed_articles'] = viewed_articles
        return render_template('article/detail.html', article=article, pagination=pagination)
    else:

        g.userme = None
        article_id = request.args.get('article_id')
        article = Article.query.get(article_id)
        # tips:处理评论的分页
        page_num = int(request.args.get('page', 1))  # important:注意一定要将其转化为整形
        pagination = Comment.query.order_by(desc(Comment.cdatetime)).filter(Comment.aid == article_id).paginate(
            page=page_num, per_page=4)
        viewed_articles = session.get('viewed_articles', [])
        if article_id not in viewed_articles:
            article.click_num += 1
            db.session.commit()

            # 记录已查看
            viewed_articles.append(article_id)
            session['viewed_articles'] = viewed_articles
        return render_template('article/detail.html', article=article, pagination=pagination)


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


@article_bp.route('/searcharticle', methods=['GET'], endpoint='searcharticle')
def searcharticle_route():
    kw = request.args.get('kw', '').strip()
    uname = session.get('uname')
    if uname:
        print('当前用户>>>>>>', uname)
        user = User.query.filter_by(username=uname, isdelete=0).first()
        if user:
            g.userme = user
        # g.userme.username=uname
        articles = Article.query.filter(
            or_(Article.title.contains(kw), Article.content.contains(kw))
        ).all() if kw else Article.query.order_by(Article.pdatetime.desc()).all()
        # return render_template('article/all.html', all_article=articles, username=uname)
        return render_template('article/all.html', all_article=articles)
    else:
        g.userme = None
        articles = Article.query.filter(
            or_(Article.title.contains(kw), Article.content.contains(kw))
        ).all() if kw else Article.query.order_by(Article.pdatetime.desc()).all()
        # return render_template('article/all.html', all_article=articles, username=uname)
        return render_template('article/all.html', all_article=articles)


# tips:设置一个路由函数用于接受评论
@article_bp.route('/add_comment', methods=['GET', 'POST'], endpoint='addcomment')
def add_comment_route():
    if request.method == 'POST':
        comment_my = request.form.get('mycomment')
        comment = Comment()
        comment.uid = g.userme.id
        comment.aid = request.form.get('articleid')
        comment.comment = comment_my
        db.session.add(comment)
        db.session.commit()

        # tips:回到上一页来(也就是刚才的详情页面)
        pre_link = request.headers.get('referer')
        return redirect(f'{pre_link}')

        # tips:或者可以这样写
        # article_id = request.form.get('aid')
        # return redirect(url_for('article.article_detail'+"?aid="+article_id))


# #tips:新增一个路由用于管理自己的文章实现自己文章的管理
@article_bp.route('/manage_article', methods=['GET', 'POST'], endpoint='manar')
def manage_article():
    if request.method == 'POST':
        pass

    if request.method == 'GET':
        uid = g.userme.id
        articles = Article.query.filter_by(user_id=uid).all()  # 查找所有文章
        if articles != None:
            return render_template('article/manageuarticle.html', articles=articles)
        else:
            return render_template('article/manageuarticle.html', articles=None)


# tips:实现用户对自己文章的修改操作
@article_bp.route('/mofy_article', methods=['GET', 'POST'], endpoint='mofya')
def mofya_route():
    if request.method == 'POST':
        aid = request.form.get('aid', type=int)
        print('aid-----------------------------------------------------',aid)
        article = Article.query.filter_by(id=aid, user_id=g.userme.id).first()
        # 查询到文章后对文章进行操作
        if not article:
            return '文章不存在', 404
        else:
            title = request.form.get('title')
            content = request.form.get('content')
            uid = request.form.get('uid')
            typeid = request.form.get('typeid')
            print("🔍 typeid 的值:", repr(typeid))
            if not typeid:
                return '必须选择文章分类', 400
            print(f'========={title},{typeid}')
            article.title = title
            article.content = content
            article.user_id = uid
            article.type_id = typeid
            db.session.commit()
            return redirect(url_for('article.manar'))


    if request.method == 'GET':
        aid = request.args.get('aid', type=int)
        article = Article.query.filter_by(id=aid, user_id=g.userme.id).first()  # 这里相当于and操作
        if not article:
            return '文章不存在', 404
        else:
            return render_template('article/mofya.html', article=article)


# tips:实现用户对自己文章的删除工作del a(rticle)
@article_bp.route('/del_article', methods=['GET', 'POST'], endpoint='dela')
def dela_route():
    # 先拿到aid
    aid = request.args.get('aid', type=int)
    print('拿到的aid是-------------------------------', aid)
    # 查询并删除,直接利用主键查询的方式,可是这样是不保险的，需要双重验证,只能自己删自己的
    # article = Article.query.get(aid)
    # important:防止越权攻击
    article = Article.query.filter_by(id=aid, user_id=g.userme.id).first()
    if not article:
        return '文章不存在或您无权操作', 404

    # 然后进行删除(直接物理删除)
    db.session.delete(article)
    db.session.commit()

    # 删除过后回到文章管理的路由
    return redirect('/manage_article')
