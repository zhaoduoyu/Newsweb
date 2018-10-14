from flask import session, g
from info import constants, db
from info.utils.response_code import RET
from . import news_blue
from flask import render_template, jsonify
from flask import current_app
from flask import request
import json
from info.models import News,User,Category
from info.utils.commons import is_login


@news_blue.route('/')
@is_login
def index():
    user = g.user
    # 查询新闻分类
    cata_list = Category.query.all()

    # 查询点击排行
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
        news_list = None

    # 判断是否取到数据
    if not news_list:
        return jsonify(errno=RET.NODATA, errmsg='查询排行新闻错误')

    # 奖新闻对象转化为字典添加到列表中
    click_news = []
    for new in news_list:
        news = new.to_dict()
        click_news.append(news)

    data = {
        'user':user,
        'cata_list':cata_list,
        'click_list':click_news
    }
    return render_template('news/index.html', data=data)


@news_blue.route('/update_news', methods=['post'])
def update_news():
    # 获取请求页参数
    # from info.models import News
    page = request.json.get("page")
    ccid = request.json.get('curentCid')


    if not all([page, ccid]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    try:
        page, ccid = int(page), int(ccid)
    except Exception as e:
        return jsonify(errno=RET.PARAMERR, errmsg="转换分页类型错误")

    if ccid == 1:
        news = News.query.order_by(News.create_time.desc()).paginate(page, 5).items
    else:
        news = News.query.filter_by(category_id=ccid).paginate(page, 5).items
    res_list = []
    for new in news:
        n = new.to_dict()

        res_list.append(n)
    data = {
        'res_list':res_list
    }
    return json.dumps(res_list)


@news_blue.route("/favicon.ico")
def favicon():

    return current_app.send_static_file('news/favicon.ico')


@news_blue.route("/detail")
@is_login
def details():

    user = g.user

    # 获取请求新闻id
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

    # 查询当前新闻作者
    author_id = detail_news_obj.user_id
    try:
        author = User.query.get(author_id)
        author_dict = author.to_dict()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="查询作者失败")

    is_collect = False
    is_follow = False
    if user:
        print(author)
        if detail_news_obj in user.collection_news:
            is_collect = True
        if author in user.followers.all():
            is_follow = True
    # 查询点击排行
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
        news_list = None

    # 判断是否取到数据
    if not news_list:
        return jsonify(errno=RET.NODATA, errmsg='查询排行新闻错误')

    # 奖新闻对象转化为字典添加到列表中
    click_news = []
    for new in news_list:
        news = new.to_dict()
        click_news.append(news)

    data = {
        'author_obj': author,
        'author':author_dict,
        'is_follow':is_follow,
        "is_collect": is_collect,
        'user': user,
        'detail_news': detail_news,
        'click_list': click_news
    }
    return render_template('news/detail.html', data=data)


@news_blue.route('/news_collect', methods=['post'])
@is_login
def news_collect():

    '''
    1 获取参数
    2 检查参数完整性
    3 检查用户登陆状态， 获取用户id
    3 查看用户操作  ？ 收藏/取消收藏
    4 查看用户是否已经收藏
    5 保存用户收藏/取消收藏
    6 返回状态吗
    :return:
    '''

    # 获取参数
    news_id = request.json.get('news_id')
    action = request.json.get('action')
    # 检查参数完整
    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 检查用户是否登陆， 获取用户id
    user = g.user
    if not user:
        return jsonify(errno=RET.LOGINERR, errmsg="用户未登录")

    # 获取新闻对象
    new = News.query.get(news_id)

    # 查看用户收藏状态
    coll_list = user.collection_news

    if new not in coll_list and action == "collect":
        user.collection_news.append(new)

    if new in coll_list and action == 'cancel_collect':
        user.collection_news.remove(new)

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存数据错误")

    return jsonify(errno=RET.OK, errmsg="OK")


@news_blue.route('/followed_user', methods=["post"])
@is_login
def followed_user():

    user = g.user
    if not user:
        return jsonify(errno=RET.LOGINERR, errmsg="用户未登录")

    # 接受检查参数
    user_id = request.json.get('user_id')
    action = request.json.get('action')
    if not all([user_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 获取要关注的用户信息
    try:
        author = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询作者信息失败")

    if author not in user.followers.all() and action == 'follow':
        user.followers.append(author)
    if author in user.followers.all() and action == "unfollow":
        user.followers.remove(author)


    try:
        db.session.add(author)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")

    return jsonify(errno=RET.OK, errmsg="OK")


