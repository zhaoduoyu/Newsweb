from . import profile_blue
from flask import render_template,request, current_app, redirect,g, jsonify,session
from info.models import User, Category, News
from info.utils.commons import is_login
from info.utils.response_code import RET
from info import db, constants
from info.utils import image_storage
from datetime import datetime

@profile_blue.route('/info')
@is_login
def user_admin_info():
    '''
    1 检查参数
    2 提取用户信息
    3 模版渲染
    :return:
    '''
    user = g.user

    if not user:
        return redirect('/')

    user.to_dict()

    return render_template('news/user.html', user=user)


@profile_blue.route('/base_info', methods=["POST", "GET"])
@is_login
def user_base_info():
    '''
    1 检查参数
    2 提取用户信息
    3 模版渲染
    :return:
    '''
    user = g.user

    if not user:
        return redirect('/')

    user.to_dict()

    if request.method == "GET":

        return render_template('news/user_base_info.html', user=user)

    if request.method == "POST":
        signature = request.json.get("signature")
        nick_name = request.json.get("nick_name")
        gender = request.json.get("gender")
        # print(gender)

        if not all([signature, nick_name, gender]) or gender.upper() not in ['MAN', 'WOMAN']:
            return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

        user.gender = gender
        user.nick_name = nick_name
        user.signature = signature

        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()

        session['nick_name'] = nick_name
        session['signature'] = signature
        return jsonify(errno=RET.OK, errmsg="OK")


@profile_blue.route('/pic_info', methods=["POST", "GET"])
@is_login
def user_pic_info():
    '''
    1 检查参数
    2 提取用户信息
    3 模版渲染
    :return:
    '''
    user = g.user

    if not user:
        return redirect('/')

    user.to_dict()

    if request.method == "GET":
        return render_template('news/user_pic_info.html', user=user)

    if request.method == "POST":
        avatar = request.files.get('avatar')
        if not avatar:
            return jsonify(errno=RET.PARAMERR, errmsg="没有头像参数")
        image_data = avatar.read()

        try:
            image_name = image_storage.storage(image_data)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.THIRDERR, errmsg="上传到七牛云错误")

        user.avatar_url = constants.QINIU_DOMIN_PREFIX + image_name

        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()

        return jsonify(errno=RET.OK, errmsg="OK")


@profile_blue.route('/user_follow')
@is_login
def user_follow_info():
    '''
    1 检查参数
    2 提取用户信息
    3 模版渲染
    :return:
    '''
    page = 1
    user = g.user

    page_req = request.args
    page_date = None
    if page_req:
        page_date = page_req.get('page')

    if page_date:
        page = page_date

        try:
            page = int(page)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg="参数类型错误")


    if not user:
        return redirect('/')

    user.to_dict()

    try:
        follow_obj = User.query.paginate(page, 4, False)
        follow_list = follow_obj.items
        follow_pages = follow_obj.pages

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="查询用户信息错误")
    if not follow_list:
        return jsonify(errno=RET.DATAERR, errmsg="没查到用户列表")

    followers_list = []

    for foll in follow_list:
        if foll in user.followers:
            # print(user.followers.all, foll, "true")
            foll = foll.to_dict()
            foll['is_followed'] = True
        else:
            # print(user.followers.all, foll, "false")
            foll = foll.to_dict()
            foll['is_followed'] = False


        followers_list.append(foll)

    data = {
        "current_page":page,
        "totalpages": follow_pages,
        "followers_list" :followers_list,
        'user' : user
    }

    return render_template('news/user_follow.html', data=data)


@profile_blue.route('/user_pass_info', methods=['post', 'get'])
@is_login
def user_pass_info():

    user = g.user

    if not user:
        return redirect('/')

    user.to_dict()
    if request.method == 'GET':
        return render_template('news/user_pass_info.html')

    if request.method == "POST":

        oldpass = request.form.get("old_pass")
        newpass = request.form.get("new_pass")
        newpass_check = request.form.get("new_pass2")

        if not all([oldpass, newpass, newpass_check]):
            return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

        if not user.check_password(oldpass):
            return jsonify(errno=RET.PWDERR, errmsg="原密码不正确")

        if newpass != newpass_check:
            return jsonify(errno=RET.PARAMERR, errmsg="确认密码与新密码不一致")

        user.password = newpass

        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(errno=RET.DBERR, errmsg="保存信息失败")

        return jsonify(errno=RET.OK, errmsg="OK")


@profile_blue.route('/user_collection', methods=['get'])
@is_login
def user_collection():

    user = g.user

    if not user:
        return redirect('/')

    page = 1

    if request.args:
        page = request.args.get('page', 1)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数类型转换失败")


    coll_news = user.collection_news.paginate(page, 10, False)
    collection_news = coll_news.items
    pages = coll_news.pages
    current_page = coll_news.page
    news_list = []

    if collection_news:
        for news in collection_news:
            news_list.append(news.to_dict())
    data = {
        "news_list" : news_list,
        "user" : user,
        "pages": pages,
        "current_page":page
    }
    if request.method == 'GET':
        return render_template('news/user_collection.html', data=data)


@profile_blue.route('/user_news_release', methods=['get', 'post'])
@is_login
def user_news_release():
    user = g.user

    if not user:
        return redirect('/')

    try:
        cates = Category.query.filter(Category.id != 1).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询新闻分类错误")

    categary_list = []
    if cates:
        for cate in cates:
            categary_list.append(cate.to_dict())


    if request.method == 'GET':
        return render_template('news/user_news_release.html', categary_list=categary_list)

    if request.method == "POST":

        title = request.form.get('title')
        categery = request.form.get('categary')
        digest = request.form.get('digest')
        image_file = request.files.get('image')
        content = request.form.get('content')
        print(content)
        if not all([title, categery, digest, image_file, content]):
            return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

        image_data = image_file.read()
        try:
            image_name = image_storage.storage(image_data)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.THIRDERR, errmsg="上传图片到期牛云错误")

        new_release = News()
        new_release.title = title
        new_release.digest = digest
        new_release.index_image_url = constants.QINIU_DOMIN_PREFIX + image_name
        new_release.content = content
        new_release.category_id = categery
        new_release.status = 1
        new_release.user_id = user.id
        new_release.source = user.nick_name
        new_release.create_time = datetime.now()


        try:
            db.session.add(new_release)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="保存新闻失败")


        return jsonify(errno=RET.OK, errmsg="OK")

@profile_blue.route('/user_news_list', methods=['get', 'post'])
@is_login
def user_news_list():
    user = g.user

    if not user:
        return redirect('/')

    page = 1

    if request.args:
        page = request.args.get('page', 1)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数类型转换失败")

    coll_news = News.query.order_by(News.create_time.desc()).paginate(page, 10, False)
    collection_news = coll_news.items
    pages = coll_news.pages
    current_page = coll_news.page
    news_list = []

    if collection_news:
        for news in collection_news:
            news_list.append(news.to_dict())
    data = {
        "news_list": news_list,
        "user": user,
        "pages": pages,
        "current_page": page
    }
    if request.method == 'GET':
        return render_template('news/user_news_list.html', data=data)
        pass
