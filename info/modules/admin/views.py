from . import admin_blue
from info.utils.commons import is_login
from flask import g, redirect, session, render_template, request, jsonify, current_app, url_for
from info.utils.response_code import RET
from datetime import datetime,timedelta
from info.models import User, News, Category
from info import db, constants
from info.utils import image_storage


@admin_blue.route("/index")
@is_login
def admin_index():
    user = g.user
    user = user.to_dict()
    return render_template("admin/index.html", user =user)


@admin_blue.route('/login', methods = ["GET", "POST"])
def admin_login():
    if request.method == "GET":
        return render_template("admin/login.html")

    username = request.form.get('username')
    password = request.form.get('password')

    if not all([username, password]):
        return redirect("/admin/login")

    try:
        user = User.query.filter_by(mobile= username).first()
    except Exception as e:
        user = None
        current_app.logger.error(e)

    if not user:
        return redirect("/admin/login")
    # 同时判断用户名和密码
    if not user.check_password(password) or not user:
        return redirect("/admin/login")

    session['nick_name']= user.nick_name
    session['user_id']= user.id
    session['is_admin'] = user.is_admin

    user.last_login = datetime.now()
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()

    return redirect(url_for("admin_blue.admin_index"))


@admin_blue.route("/user_count")
def admin_user_count():
    """
    查询用户总数
    查询月新增人数
    查询日新增人数
    :return:
    """

    total_count = User.query.filter_by(is_admin=False).count()

    # 统计月新增人数， 需要获取当前月第一天的时间对象  2018.10.01
    from datetime import datetime

    import time
    # 获取当前月时间对象， 格式化当前月第一天时间字符串
    t = time.localtime()
    mon_begin_date_str = "%d-%02d-01" %(t.tm_year, t.tm_mon)
    mon_begin_data = datetime.strptime(mon_begin_date_str, "%Y-%m-%d")

    mon_count = 0
    try:
        mon_count = User.query.filter(User.is_admin==False, User.create_time>mon_begin_data).count()
    except Exception as e:
        current_app.logger.error(e)


    now_time_str = "%d-%02d-%02d" %(t.tm_year, t.tm_mon, t.tm_mday)
    now_time = datetime.strptime(now_time_str, "%Y-%m-%d")

    # 日新增人数

    today_str = "%d-%02d-%02d" %(t.tm_year, t.tm_mon, t.tm_mday)
    today_date = datetime.strptime(today_str, "%Y-%m-%d")

    today_count = 0
    try:
        today_count = User.query.filter(User.is_admin==False, User.last_login>today_date).count()
    except Exception as e:
        current_app.logger.error(e)


    # 统计每日新增人数
    count_list = []
    active_list = []
    for i in range(30):
        # 获取前1～ 30 天时间对象
        day_time_start = now_time - timedelta(days = i)
        day_time_end = now_time - timedelta(days = (i-1))

        day_count = 0
        try:
            day_count = User.query.filter(User.is_admin == False, User.last_login > day_time_start, User.last_login< day_time_end).count()
        except Exception as e:
            current_app.logger.error(e)

        count_list.append(day_count)

        #  把日期对象转化为字符串保存到日期列表
        day_time_str = datetime.strftime(day_time_start, "%m-%d")
        active_list.append(day_time_str)

    count_list.reverse()
    active_list.reverse()
    data = {
        "today_count": today_count,
        "active_list":active_list,
        "count_list":count_list,
        "total":total_count,
        "mon_count": mon_count

    }

    return render_template('admin/user_count.html', data = data)


@admin_blue.route("/user_list")
@is_login
def admin_user_list():
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

    coll_news = User.query.filter_by(is_admin=False).paginate(page, 10, False)
    users = coll_news.items
    pages = coll_news.pages
    page = coll_news.page
    user_list = []

    if users:
        for u in users:
            user_list.append(u.to_admin_dict())
    data = {
        "user_list": user_list,
        "user": user,
        "pages": pages,
        "current_page": page
    }

    return render_template('admin/user_list.html', data =data)


@admin_blue.route("/news_review")
def admin_news_review():
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
        "pages": pages,
        "current_page": current_page
    }

    return render_template("admin/news_review.html", data=data)


@admin_blue.route("/news_review_detail", methods=["post", "get"])
def admin_news_review_detail():
    # 获取请求新闻id

    if request.method == "GET":
        news_id = request.args.get('id')
        if not news_id:
            return jsonify(errno=RET.PARAMERR, errmsg="获取新闻id错误")


        # 查询新闻分类
        try:
            detail_news_obj = News.query.get(news_id)
            detail_news = detail_news_obj.to_dict()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DATAERR, errmsg="获取新闻详情错误")


        data = {
            "new" : detail_news
        }

        return render_template("admin/news_review_detail.html", data=data)

    if request.method == "POST":
        status = request.form.get('action')
        reason = request.form.get('reason')
        news_id = request.form.get('news_id')

        print(status, news_id)

        if not all([news_id, status]):
            return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

        try:
            status, news_id = int(status), int(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg="转换类型错误")


        try:
            new_review = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="查询新闻id失败")

        new_review.status = status
        new_review.reason = reason if reason else ""

        try:
            db.session.add(new_review)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="保存新闻失败")

        return jsonify(errno=RET.OK, errmsg="OK")


@admin_blue.route("/news_edit")
def admin_news_edit():
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
        "pages": pages,
        "current_page": current_page
    }

    return render_template("admin/news_edit.html", data=data)


@admin_blue.route("/news_edit_detail", methods=["post", "get"])
@is_login
def admin_news_edit_detail():
    user = g.user

    if request.method == 'GET':

        news_id = request.args.get('id')

        if not news_id:
            return jsonify(errno=RET.PARAMERR, errmsg="获取新闻id错误")


        # 获取新闻分类
        try:
            cates = Category.query.filter(Category.id != 1).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="查询新闻分类错误")

        categary_list = []
        if cates:
            for cate in cates:
                categary_list.append(cate.to_dict())


        # 查询新闻分类
        try:
            detail_news_obj = News.query.get(news_id)
            detail_news = detail_news_obj.to_dict()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DATAERR, errmsg="获取新闻详情错误")

        data = {
            "new": detail_news,
            "category_list": categary_list
        }
        return render_template('admin/news_edit_detail.html', data=data)

    if request.method == "POST":
        news_id = request.form.get("news_id")
        title = request.form.get('title')
        categery = request.form.get('category')
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
        try:
            new_release = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="获取新闻对象失败")


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


@admin_blue.route("/news_type", methods=["post",'get'])
def admin_news_type():
    if request.method == "GET":
        try:
            cates = Category.query.filter(Category.id != 1).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="查询新闻分类错误")

        categary_list = []
        if cates:
            for cate in cates:
                categary_list.append(cate.to_dict())

        data = {
            "categary_list" : categary_list
        }

        return render_template("admin/news_type.html", data=data)

    if request.method == "POST":

        if not request.json:
            return jsonify(errno=RET.PARAMERR, errmsg="不是json类型参数")
        name = request.json.get("name", None)
        id = request.json.get("id", None)

        if not name:
            return jsonify(errno=RET.PARAMERR, errmsg="没有分类名参数")

        if id:
            try:
                id = int(id)
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(errno=RET.PARAMERR, errmsg="id参数类型不对")

            try:
                cate = Category.query.get(id)
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(errno=RET.DBERR, errmsg="没有查到分类id")

        else:
            cate = Category()

        cate.name = name

        try:

            db.session.add(cate)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(errno=RET.DBERR, errmsg="保存分类错误")

        return jsonify(errno=RET.OK, errmsg="OK")
