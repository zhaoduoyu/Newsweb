from info.modules.passport import passport_blue
from flask import current_app, jsonify, session
from flask import make_response
from flask import request
from info import constants,redis_store,db
from info.utils.captcha.captcha import captcha
from info.utils.response_code import RET
import re
import random
from info.models import User
from datetime import datetime

@passport_blue.route('/image_code')
def get_image_code():
    """
    获取图片验证码
    :return:
    """
    # 1. 获取到当前的图片编号id
    code_id = request.args.get('code_id')
    # 2. 生成验证码
    name, text, image = captcha.generate_captcha()
    print("图片验证码：", text)
    try:
        # 保存当前生成的图片验证码内容
        redis_store.setex('ImageCode_' + code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        return make_response(jsonify(errno=RET.DATAERR, errmsg='保存图片验证码失败'))

    # 返回响应内容
    resp = make_response(image)
    # 设置内容类型
    resp.headers['Content-Type'] = 'image/jpg'
    return resp


@passport_blue.route('/smscode', methods=["GET","POST"])
def send_sms():
    '''
    校验图片验证码， 生成手机验证码， 保存到服务端redis数据库中， 用第三方yuntongxun,发送手机验证码
    :return:
    '''
    # 获取请求参数, post方法获取data里面的参数
    req_args = request.json
    mobile = req_args.get('mobile')
    image_code = req_args.get('image_code')
    image_code_id = req_args.get('image_code_id')
    print(mobile, image_code_id, image_code)
    # 1. 校验参数是否齐全
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 2. 校验手机号格式正确
    if not re.match("^1[3578][0-9]{9}$", mobile):
        # 提示手机号不正确
        return jsonify(errno=RET.DATAERR, errmsg="手机号不正确")

    # 3. 获取请求的图片验证码和本地redis数据库中的验证码进行对比
    try:
        real_image_code = redis_store.get('ImageCode_'+image_code_id)
        if real_image_code:
            # real_image_code = real_image_code.decode()
            redis_store.delete('ImageCode_'+image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        # 获取图片验证码失败
        return jsonify(errno=RET.DBERR, errmsg="获取图片验证码失败")

    if not real_image_code:
        return jsonify(errno=RET.PARAMERR, errmsg="验证码已过期")

    if real_image_code.lower() != image_code.lower():
        return jsonify(errno=RET.PARAMERR, errmsg="验证码输入错误")


    # 4.1 校验该手机是否已经注册
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        user = None  # 如果查询时出现错误，也需要给user初始化，如果不初始化，会报未定义的异常
        current_app.logger.error(e)
    if user:
        # 该手机已被注册
        return jsonify(errno=RET.DATAEXIST, errmsg="该手机已被注册")


    # 6. 生成发送短信的内容并发送短信
    from info.libs.yuntongxun.sms import CCP
    result = random.randint(0, 999999)
    sms_code = "%06d" % result

    # 5. redis中保存短信验证码内容
    try:
        redis_store.set("SMS_" + mobile, sms_code, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        # 保存短信验证码失败
        return jsonify(errno=RET.DBERR, errmsg="保存短信验证码失败")

    current_app.logger.debug("短信验证码的内容：%s" % sms_code)
    result = CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES / 60], 1)
    print(result)
    if result != 0:
        # 发送短信失败
        return jsonify(errno=RET.THIRDERR, errmsg="发送短信失败")



    # 7. 返回发送成功的响应
    return jsonify(errno=RET.OK, errmsg="发送成功")


@passport_blue.route('/register', methods=['post', 'get'])
def register():
    """
    1 获取用户提交参数
    2 验证参数完整性 mobile, smscode, password
    3 验证手机号码合法性
    4 提取redis数据库中的smscode
    5 服务端smscode与用户提交的数据对比
    6 验证手机号是否已经注册过账号
    7 完成验证程序， 将用户提交的信息保存在mysql数据库中
    8 完成注册， 返回成功状态吗
    :return:
    """

    # 1 获取用户提交参数
    req_args = request.json
    mobile = req_args.get('mobile')
    smscode = req_args.get('smscode')
    password = req_args.get('password')

    # 2 验证参数完整性 mobile, smscode, password
    if not all([mobile, smscode, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='提交的参数不完整')


    # 3 验证手机号码合法性
    if not re.match(r"1[3456789]\d{9}$", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg = '手机号码不合法')

    # 4.提取redis数据库中的smscode
    # from info import redis_store
    try:
        real_smscode = redis_store.get('SMS_'+mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='提取手机验证吗失败')

    # 5 判断数据库中提取的验证码是否存在
    if not real_smscode:
        return jsonify(errno=RET.DATAEXIST, errmsg='手机验证码已过期')

    # 6 预前端提交的验证码进行对比
    if real_smscode.lower() != smscode.lower():
        return jsonify(errno=RET.PARAMERR, errmsg = '手机验证码输入错误')


    # 对比完成后删除手机验证码
    try:
        redis_store.delete('SMS_'+mobile)
    except Exception as e:
        current_app.logger.error(e)

    # 7 检查该手机号是否已经注册过


    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        user = None   # 提取数据异常给user初始化None， 不然会报未定义错误
        current_app.logger.error(e)

    if user:
        return jsonify(errno=RET.DATAEXIST, errmsg='该手机号码已经注册')

    # 8 保存用户提交信息到mysql数据库中， 完成注册
    user = User()
    user.mobile = mobile
    user.nick_name = mobile
    user.password = password

    # from info import db

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存用户数据失败')

    # 9 缓存用户信息到redis数据库中

    session['nick_name'] = user.mobile
    session['user_id'] = user.id

    # 10 返回结果

    return jsonify(errno=RET.OK, errmsg='OK')


@passport_blue.route('/login', methods=['post'])
def login():
    '''
    1 获取请求参数
    2 查找用户名
    3 对比密码
    4 保存用户登陆session信息
    5 返回状态码
    :return:
    '''

    req_data = request.json
    mobile = req_data.get('mobile')
    password = req_data.get('password')

    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='登陆参数不完整')

    # 2 查找用户
    # from info.models import User
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        user = None
        current_app.logger.error(e)

    # 同时判断用户名和密码
    if not user.check_password(password) or not user:
        return jsonify(errno=RET.LOGINERR, errmsg='用户名或密码不正确')

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

    return jsonify(errno=RET.OK, errmsg='OK')


@passport_blue.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('nick_name', None)
    session.pop('mobile', None)

    return jsonify(errno=RET.OK, errmsg='OK')
