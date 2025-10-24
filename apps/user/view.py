"""
@File    :view.py
@Editor  : 百年
@Date    :2025/8/10 10:04 
"""
import os.path
from settings import Config
from sqlalchemy import and_, or_, desc
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from .models import User
from exts.extensions import db
from ..utils.qiniu_cloud import upload_qiniu, del_qiniu
from flask import Blueprint, request, render_template, redirect, url_for, session, jsonify, make_response, g
from .models import User, Photo, Aboutme
from apps.article.models import Article, Article_type

user_bps = Blueprint(name='user', import_name=__name__)
import hashlib


# important:新增一个蓝图请求前函数
@user_bps.before_request
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


# @user_bps.route('/',endpoint='index')
# def index():
#     # username = session.get('uname')
#     # # print('当前用户名:'+username)
#     # # username = session.get('uname')
#     # userme = User.query.filter_by(username=username).first()
#     # if g.userme:
#     #     return render_template('user/index.html', username=g.userme.username, userme=g.userme)
#     # else:
#     #     return redirect('/login')
#
#
#     if request.method == 'POST':
#         pass
#     username = session.get('uname')
#     # article_types = Article_type.query.all()
#     # g.article_types = article_types
#     if username != None:
#         all_article = Article.query.order_by(desc(Article.pdatetime)).all()
#         # return render_template('article/all.html', all_article=all_article, username=username)
#         # return render_template('article/all.html', all_article=all_article)
#         return render_template('user/index.html', all_article=all_article, username=username)
#     else:
#         article_types = Article_type.query.all()
#         g.article_types = article_types
#         all_article = Article.query.order_by(desc(Article.pdatetime)).all()
#         # return render_template('article/all.html',all_article=all_article)
#         return render_template('user/index.html', all_article=all_article)

@user_bps.route('/index', endpoint='index')
def index():
    # username = session.get('uname')
    # # print('当前用户名:'+username)
    # # username = session.get('uname')
    # userme = User.query.filter_by(username=username).first()
    # if g.userme:
    #     return render_template('user/index.html', username=g.userme.username, userme=g.userme)
    # else:
    #     return redirect('/login')

    if request.method == 'POST':
        pass

    # important:新增处理文章分类!!!
    articletype = request.args.get('articletype', default='')
    # if articletype==None:
    # important：注意这里一定要做强制类型转换否则就会报错
    page_num = int(request.args.get('page', 1))  # important:接受页码数
    print(page_num)
    username = session.get('uname')
    article_types = Article_type.query.all()
    g.article_types = article_types
    if articletype == "":
        pagination = Article.query.order_by(desc(Article.pdatetime)).paginate(page=page_num, per_page=3)
    else:
        pagination = Article.query.filter(Article.type_id == articletype).order_by(desc(Article.pdatetime)).paginate(
            page=page_num, per_page=3)

    if username != None:
        # all_article = Article.query.order_by(desc(Article.pdatetime)).all()
        # all_article = Article.query.order_by(-Article.pdatetime).all() #important:sqlalchemy中可以直接写-来进行desc查询约束
        # return render_template('article/all.html', all_article=all_article, username=username)
        # return render_template('article/all.html', all_article=all_article)
        # return render_template('user/index.html', all_article=all_article, username=username)

        # tips:新修改加上分页
        return render_template('user/index.html', pagination=pagination, username=username)
    else:  # tips:即使没登陆也要显示首页的文章分类
        # article_types = Article_type.query.all()
        # g.article_types = article_types
        # all_article = Article.query.order_by(desc(Article.pdatetime)).all()
        # # important:新的问题,对文章进行分页,采用sqlalchemy的pageinate()对其进行分页,
        # pagination = Article.query.order_by(desc(Article.pdatetime)).paginate(page=1, per_page=3)
        # print('======~~~~~======~~~~~====******')
        # print(pagination.items)  # important:按照paginate制定的page和per_page第一顺位在数据库中命中的对象
        # print(pagination.page)  # important:当前页数！！！！注意它是从1开始的
        # # print(pagenation.total_pages)
        # print(pagination.prev_num)  # important:上一页
        # print(pagination.next_num)  # important:下一页
        # print(pagination.has_next)  # important:判断是否有下一页,返回的是布尔类型
        # print(pagination.has_prev)  # important: 判断是否有上一页
        # print(pagination.pages)  # important:总页数,这是最方便的一点,paginate直接帮我们计算好所需要的页数,方便我们进行分页
        # print(pagination.total)  # important:数据库中一共有几条记录
        '''
        [<Article 18>, <Article 17>, <Article 16>]
        1
        None
        2
        True
        False
        6
        16

        '''

        # return render_template('article/all.html',all_article=all_article)
        # return render_template('user/index.html', all_article=all_article)

        # important:因为我们要使用paginate,那么要进行相应的修改

        return render_template('user/index.html', pagination=pagination)


@user_bps.route('/usercenter', endpoint='usercenter', methods=['GET', 'POST'])
def usercenter():
    # username = session.get('uname')
    # userme = User.query.filter_by(username=username).first()

    if request.method == 'GET':
        return render_template('user/center.html', username=g.userme.username, userme=g.userme)
    else:
        # 获取表单数据
        username = request.form.get('userme')  # 当前用户名（用于查询）
        newusername = request.form.get('newusername')
        password = request.form.get('password')
        repassword = request.form.get('repassword')
        phone = request.form.get('phone')
        icon = request.files.get('icon')

        user = User.query.filter_by(username=username).first()
        if not user:
            return "用户不存在", 404

        # 1. 更新用户名
        if newusername:
            user.username = newusername

        # 2. 只有当用户输入了新密码时才更新密码
        if password:
            if password != repassword:
                return render_template('user/center.html', errorinfo='两次输入的密码不一致，请重新输入')
            user.password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

        # 3. 更新手机号
        if phone:
            user.phone = phone

        # 4. 更新头像
        if icon:
            icon_name = icon.filename  # important:首先调用files的属性来获取其名称
            secure_name = check_img(icon_name)  # 然后调用自己的函数来进行检查名称
            if secure_name:
                file_path = os.path.join(Config.UPLOAD_ICON_FOLDER, secure_name)
                icon.save(file_path)  # important 调用files的save方法对头像进行存储
                user.icon = os.path.join('upload/icon', secure_name).replace('\\', '/')
                # tips:关于为啥这里要写的是upload/icon而不是使用绝对路径，
                # 因为在前端页面中我们可以使用jinja的url_for('static',filename='')来进行前置路径的获取
            else:
                return render_template('user/center.html', errorinfo='不支持此格式')

        db.session.commit()

        # 如果用户名变了，更新 session
        if newusername:
            session['uname'] = newusername

        session.clear()  # 强制重新登录
        return redirect('/login')


ALLOWED_EXTENSIONS = ['jpg', 'png', 'svg', 'gif', 'bmp', 'jpeg']


def check_img(file_name):
    suffix = file_name.split('.')[-1]
    if suffix in ALLOWED_EXTENSIONS:
        icon_name = secure_filename(file_name)
        return icon_name
    else:
        return False


# 删除数据
@user_bps.route('/deldata')
def del_data():
    username = request.args.get('username')
    # tips:从前端拿到
    # 先查询到
    # res = db.session.query(username)
    # print(res)
    # 2025-08-11 12:44:33,318 INFO sqlalchemy.engine.Engine [cached since 1631s ago] {}
    # [<User 1>]

    # tips:执行删除操作
    user = User.query.filter_by(username=username).first()

    # tips:或者这样写
    # username = db.session.query(User).filter_by(username=username)
    # tips:做逻辑删除比较好
    user.isdelete = 1
    # db.session.delete(user)
    db.session.commit()
    # 然后重定向到用户中心界面
    return redirect('/')


# 用户注册
@user_bps.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        repassword = request.form.get('repassword')
        phone = request.form.get('phone')
        if password == repassword:
            # tips:与模型进行结合,来完成数据库的添加
            # step1:找到模型类并创建对象
            user = User()
            # step2:给对象的属性进行赋值
            user.username = username

            # important:调用加密算法对密码进行加密 新方法:generate_password_hash(password.encode('utf-8')),但是注意长度需要是64,那么model就要对应修改
            # user.password = hashlib.sha256(password.encode('utf-8')).hexdigest()
            user.password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
            user.phone = phone
            # step3:往数据库里添加
            db.session.add(user)
            # step4:进行提交
            db.session.commit()
            # return '用户注册成功'
            return redirect(url_for('user.login'))
        else:
            return render_template('user/register.html', errorinfo='两次输入的密码不一致请重新输入')
    return render_template('user/register.html')


#
# # 用户登入
# @user_bps.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'GET':
#         # tips:新增cookie预读取
#         username = request.cookies.get('remember_username', '')  # 从cookie中拿数据,拿不到就默认设置为空
#         return render_template('user/login.html', username=username)
#     username = request.form.get('username')
#     password_raw = request.form.get('password')
#     # password_enc = hashlib.sha256(password_raw.encode('utf-8')).hexdigest()
#     phone = request.form.get('phone')
#
#     user = User.query.filter_by(username=username, isdelete=0, phone=phone).first()
#     if user and check_password_hash(user.password, password_raw):
#         session['uname'] = username
#
#         # important:新增设置cookie,因为cookie需要设置到response对象上,所以就需要构造一个response对象
#         resp = make_response(render_template('user/index.html', users=user))
#         resp.set_cookie('remember_username', username, max_age=604800)
#         # 可选：设置安全 cookie（仅 HTTPS）
#         # resp.set_cookie('remember_username', username, max_age=604800, httponly=True, secure=True)
#         return resp  # 其实这个resp就是 render_template('user/index.html',users=user)
#         # return render_template('user/index.html',users=user)
#     else:
#         return render_template('user/login.html', errorinfo='信息错误,请重试')
#
#
# # important:新增之用手机验证码登录
# @user_bps.route('/login_verifycode', endpoint='login_verifycode')
# def login_verifycode_route():
#     if request.method == 'POST':
#         phonenum = request.form.get('phonenum')
#         if not phonenum:
#             return jsonify(code=400, msg='手机号不能为空')
#         elif not phonenum.isdigit() or len(phonenum) != 11:
#             return jsonify(code=400, msg='手机格式错误')
#
#         user = User.query.filter_by(phone=phonenum, isdelete=0).first()
#         if user:
#             return jsonify(code=200, msg='该手机号已被注册')
#         else:
#             return jsonify(code=200, msg='该手机号未被注册请先注册')
#     return render_template('user/loginwithvc.html')


# view.py

@user_bps.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # # 从 cookie 获取记住的用户名
        # username = request.cookies.get('remember_username')
        # # print('拿到的cookie'+username)
        # if username == None:
        #     return render_template('user/login.html', username=username)
        # else:
        #     return render_template('user/login.html')
        # articletype = request.args.get('articletype', default='')
        # article_types = Article_type.query.all()
        # g.article_types = article_types
        return render_template('user/login.html')

    # POST 请求：判断是哪种登录方式
    username = request.form.get('username')
    password = request.form.get('password')
    # crypto_pwd = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
    print(username, password)
    phone = request.form.get('phone')
    vcode = request.form.get('vcode')  # 验证码登录用
    # 👇 加在这里！
    print("👉 Form 数据:", request.form.to_dict())
    print("👉 username:", repr(username))
    print("👉 password:", repr(password))
    print("👉 phone:", repr(phone))
    print("👉 vcode:", repr(vcode))
    # 场景1：用户名密码登录
    if username and password:
        user = User.query.filter_by(username=username, isdelete=0).first()
        if user:
            print("✅ 找到用户:", user.username)
            print("✅ 数据库存储的密码哈希:", user.password)
            print("✅ check_password_hash 结果:", check_password_hash(user.password, password))
        else:
            print("❌ 未找到用户或已删除")
        if user and check_password_hash(user.password, password):
            session['uname'] = username
            # resp = make_response(redirect('/'))
            resp = make_response(redirect('/index'))
            resp.set_cookie('remember_username', username, max_age=604800)
            return resp
        else:
            return render_template('user/login.html', errorinfo='用户名或密码错误')

    # 场景2：手机号 + 验证码登录（这里模拟验证码正确为 "123456"，实际应对接短信服务）
    elif phone and vcode:
        # 可在此处验证验证码是否正确（比如从 Redis 中比对）
        if vcode != "123456":  # 示例验证码
            return render_template('user/login.html', errorinfo='验证码错误')
        user = User.query.filter_by(phone=phone, isdelete=0).first()
        if not user:
            return render_template('user/login.html', errorinfo='该手机号未注册')
        session['uname'] = user.username
        resp = make_response(redirect(url_for('user.index')))
        resp.set_cookie('remember_username', user.username, max_age=604800)
        return resp

    # 其他情况
    return render_template('user/login.html', errorinfo='请输入完整信息')


# 短信息发送部分,实现验证码登录
@user_bps.route('/sendMSG', endpoint='sendmsg')
def sendmsg_route():
    pass


@user_bps.route('/logout', endpoint='logout')
def logout_route():
    session.clear()
    resp = make_response(redirect('/login'))
    # important:新增之退出后删除cookie
    resp.delete_cookie('remember_username')
    return resp
    # return redirect('/login')


# 手机号码验证
# @user_bps.route('/checkphone',endpoint='checkphone')
# def check_phone():
#     phonenum = request.args.get('phone')
#     res = User.query.filter_by(phone=phonenum).all()
#     if len(res)>0:
#         return jsonify(
#            code=400,msg='不可用'
#         )
#     else:
#         return jsonify(
#             code=200,
#             msg='可用'
#         )


@user_bps.route('/checkphone', endpoint='checkphone')
def check_phone():
    phonenum = request.args.get('phone', '').strip()
    if not phonenum:
        return jsonify(code=400, msg='手机号不能为空')
    if not phonenum.isdigit() or len(phonenum) != 11:
        return jsonify(code=400, msg='手机格式错误')

    user = User.query.filter_by(phone=phonenum, isdelete=0).first()
    if user:
        return jsonify(code=400, msg='该手机号已被注册')
    else:
        return jsonify(code=200, msg='可用')


# 用户登入新写法之使用wtform
# from forms import LoginForm
# @user_bps.route('/login',methods=['GET','post'])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         username = form.username.data
#         password_raw = form.password_raw.data
#         password_enc = hashlib.sha256(password_raw.encode('utf-8')).hexdigest()
#         phone = form.phone.data
#         user = User.query.filter_by(username=username, password=password_enc, phone=phone).first()
#         if user:
#             session['uname']=username
#             return redirect('/')
#         else:
#             return render_template('user/login.html', errorinfo='信息错误,请重试')
#     return render_template('user/login.html', form=form)

# start_cb:实现搜索功能

@user_bps.route('/search', methods=['POST', 'GET'])
def search():
    kw = request.args.get('search')
    print(kw)
    if not kw:
        users = User.query.filter_by(isdelete=0).all()
    else:
        users = User.query.filter(
            and_(
                or_(User.username.contains(kw), User.phone.startswith(kw)),
                User.isdelete == 0
            )
        ).all()
    return render_template('user/usercenter.html', users=users)


# end_cb:搜索功能完成


# 仅作为测试
"""
@user_bps.route('/select', methods=['GET', 'POST'], endpoint='select')
def select_route():
    user = User.query.get(1)  # 按主键查询用户(主键值),返回的是一个用户对象
    user1 = User.query.filter(User.username == 'nikofox')
    user2 = User.query.filter(User.username == 'nikofox').first()
    user3 = User.query.filter(User.username == 'nikofox').all()  # 这里返回的是User对象
    user4 = User.query.filter_by(username='nikofox').first()
    user5 = User.query.filter(User.username.startswith('z')).all()
    user_lst = User.query.filter(User.username.contains('i')).all()

    user_lst2 = User.query.filter(and_(User.username.contains('z'), User.regi_date.__lt__('2025-08-24 18:06:50'))).all()

    # 离散查询
    phoneuser = User.query.filter(User.phone.in_(['12289776578', '11897890987'])).all()
    return render_template('user/select.html', user=user, user1=user1, user2=user2, user3=user3, user4=user4,
                           user5=user5, user_lst=user_lst, user_lst2=user_lst2, phoneuser=phoneuser)

    '''
    模型类.query.filter()里面的是布尔的条件   模型类.query.filter(模型类.字段名=='值')
    模型类.query.filter_by()里面的是等值  模型类.query.filter_by(字段名=='值'[可以写多个])
    '''
"""
# 新测试路由,用于查看基础模板是否被调用
'''
@user_bps.route('/test2', endpoint='test2')
def test2_route():
    return render_template('base.html')
'''


# tips:定义上传照片的操作,利用七牛云对象存储
@user_bps.route('/upload_photo', endpoint='upphoto', methods=['POST', 'GET'])
def upload_photo_route():
    if request.method == 'GET':
        page_num = int(request.args.get('page', 1))  # important:一定要记得转整形
        pagination = Photo.query.filter(Photo.user_id == g.userme.id).order_by(desc(Photo.photo_datatime)).paginate(
            page=page_num, per_page=6)

        # for p in photos:
        #     print('---------------------------图片查询', p.photo_name)
        return render_template('user/yourphoto.html', pagination=pagination)

    # username = session.get('uname')
    photos = request.files.get('pics')  # important:这样获得的是一个filestorage对象,可以进行存储
    # user = User.query.filter_by(username=username).first()
    if photos:
        photos_name = photos.filename
        secure_name = check_img(photos_name)
        if secure_name:
            # file_path = os.path.join(Config.UPLOAD_PHOTO_FOLDER, secure_name)
            # photos.save(file_path)
            raw_pic_name = secure_name.split('.')[0]
            pic_suffix = secure_name.split('.')[-1]
            info, ret = upload_qiniu(photos, raw_pic_name, pic_suffix)
            if info.status_code == 200:
                photo = Photo()
                photo.photo_name = ret['key']
                photo.user_id = g.userme.id  # 拿到当前全局用户的id
                db.session.add(photo)
                db.session.commit()
                return redirect('/upload_photo')
                # user.photo = os.path.join('upload/photo', secure_name).replace('\\', '/')
            else:
                return render_template(
                    'user/yourphoto.html', errorinfo="上传失败"
                )
    else:
        return render_template('user/yourphoto.html', errorinfo='不支持此格式')


# important:设置一个删除图片的路由,不但要删除数据库的,也要删除云存储的!!!
@user_bps.route('/photo_del', endpoint='delphoto')
def photodel_route():
    pid = request.args.get('pid')
    photo = Photo.query.get(pid)
    result = del_qiniu(photo.photo_name)  # important:删除七牛云存储的照片
    if result == 200:
        db.session.delete(photo)  # tips:注意先后顺序,先删云存储的,再删本地的,不然本地的先删除后就没信息了，就删不了云存储的了
        db.session.commit()
        return redirect('/upload_photo')
    else:
        prev_href = request.headers.get('referer', None)  # 拿到上一页的链接
        print(prev_href)
        return render_template('user/error.html', err_msg="删除失败,请检查网络设置", prev_href=prev_href)


# 定义一个路由来展示所有的图片
@user_bps.route('/all_photo', endpoint='allphoto', methods=['POST', 'GET'])
def upload_photo_route():
    if request.method == 'GET':
        page_num = int(request.args.get('page', 1))  # important:一定要记得转整形
        pagination = Photo.query.filter().order_by(desc(Photo.photo_datatime)).paginate(
            page=page_num, per_page=30)
        return render_template('user/all_photo.html', pagination=pagination)


# tips:设置一个路由用来展示自己设定的相关信息
@user_bps.route('/aboutme', methods=['GET', 'POST'], endpoint='aboutme')
def aboutme_route():
    uid = g.userme.id
    print(uid)
    if request.method == 'GET':
        selfintro = Aboutme.query.filter(Aboutme.user_id == uid).first()
        # print(selfintro)
        if selfintro != None:
            return render_template('user/aboutme.html', selfintro=selfintro)
        else:
            return render_template('user/aboutme.html', selfintro=None)
    if request.method == 'POST':
        selfintro = request.form.get('selfintro_')
        uid = request.form.get('uid')
        intro = Aboutme()
        intro.user_id = uid
        intro.selfintro = selfintro
        db.session.add(intro)
        db.session.commit()
        return redirect('/aboutme')


# 新增一个用于处理修改简介mo(di)fyab(out)me
#tips:这部分遇到了一些问题,是因为自己对sqlalchemy的一些类型处理的方式不够清楚
@user_bps.route('/mofyabme', methods=['GET', 'POST'], endpoint='mofyme')
def mofyme_route():
    if request.method == 'POST':
        uid = request.form.get('uid',int) #tips:还有就是这里理解不深,其实get的源码定义里有这个get(self, key, default=None, type=None),最后一个type是可以指定类型的强制转化的
        abme = Aboutme.query.filter_by(user_id=uid).first() #important:这次主要就是卡在这里了,因为自己的查询语句写的有问题
        new_intro = request.form.get('new_intro')
        print('-------------------------------------------=======------', new_intro)
        abme.selfintro = new_intro
        db.session.commit()

        return redirect('/aboutme')

# #tips:新增文章管理
# @user_bps.route('/articlemanage',methods=['GET','POST'],endpoint='artm')
# def artm_route():
#     if request.method == 'POST':
#         pass
