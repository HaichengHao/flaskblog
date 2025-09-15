"""
@File    :view.py
@Editor  : 百年
@Date    :2025/8/10 10:04 
"""
from sqlalchemy import and_, or_
from werkzeug.security import generate_password_hash, check_password_hash

from .models import User
from exts.extensions import db
from flask import Blueprint, request, render_template, redirect, url_for, session, jsonify, make_response, g
from .models import User

user_bps = Blueprint(name='user', import_name=__name__)
import hashlib


@user_bps.route('/')
def index():
    username = session.get('uname')
    # print('当前用户名:'+username)
    # username = session.get('uname')
    if username:
        return render_template('user/index.html', username=username)
    else:
        return redirect('/login')


@user_bps.route('/usercenter', endpoint='usercenter', methods=['GET', 'POST'])
def usercenter():
    username = session.get('uname')
    userme = User.query.filter_by(username=username).first()
    if request.method == 'GET':
        return render_template('user/center.html', username=username, userme=userme)
    else:
        # POST 处理
        username = request.form.get('userme')
        newusername = request.form.get('newusername')
        password = request.form.get('password')
        repassword = request.form.get('repassword')
        phone = request.form.get('phone')

        if password != repassword:
            return render_template('user/center.html', errorinfo='两次输入的密码不一致，请重新输入')

        user = User.query.filter_by(username=username).first()
        # 更新用户名（如果提供了新用户名）
        if newusername:
            user.username = newusername
        # 更新密码（已加密）
        user.password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

        # 更新手机号
        if phone:
            user.phone = phone

        db.session.commit()
        # 修改之后应该直接退出重新登陆
        session.clear()
        return redirect('/')


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


# 更新数据
@user_bps.route('/modifydata', methods=['POST', 'GET'], endpoint='modifydata')
def modidata():
    if request.method == 'GET':
        username = session.get('uname')
        user = User.query.filter_by(username=username).first()
        if not user:
            return "用户不存在", 404
        return render_template('user/custom_data.html', user=user)

    # POST 处理
    username = request.form.get('username')
    newusername = request.form.get('newusername')
    password = request.form.get('password')
    repassword = request.form.get('repassword')
    phone = request.form.get('phone')

    if password != repassword:
        return render_template('user/custom_data.html', errorinfo='两次输入的密码不一致，请重新输入')

    user = User.query.filter_by(username=username).first()
    if not user:
        return render_template('user/custom_data.html', errorinfo="用户不存在，无法修改")

    # 更新用户名（如果提供了新用户名）
    if newusername:
        user.username = newusername

    # 更新密码（已加密）
    user.password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

    # 更新手机号
    if phone:
        user.phone = phone

    db.session.commit()
    return redirect(url_for('user.index'))


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
        username = request.cookies.get('remember_username')
        # print('拿到的cookie'+username)
        if username == None:
            return render_template('user/login.html', username=username)
        else:
            return render_template('user/login.html')
        # return render_template('user/login.html')

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
            resp = make_response(redirect('/'))
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


# 新测试路由,用于查看基础模板是否被调用
@user_bps.route('/test2', endpoint='test2')
def test2_route():
    return render_template('base.html')
