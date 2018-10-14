from flask import Flask
from config import config,Config
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
import logging         # 标准模块中的logging
from logging.handlers import RotatingFileHandler
import redis



logging.basicConfig(level=logging.DEBUG) # 调试debug级
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
# 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flask app使用的）添加日志记录器
logging.getLogger().addHandler(file_log_handler)



db = SQLAlchemy()
redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, decode_responses=True)

def create_app(config_modul):

    from info.modules.news import news_blue
    from info.modules.passport import passport_blue
    from info.modules.users import profile_blue
    from info.modules.admin import admin_blue
    app = Flask(__name__)
    app.config.from_object(config[config_modul])
    app.register_blueprint(news_blue)
    app.register_blueprint(passport_blue)
    app.register_blueprint(profile_blue)
    app.register_blueprint(admin_blue)
    Session(app)
    db.init_app(app)

    # 使用自定义的过滤器
    from info.utils.commons import click_news_filter
    app.add_template_filter(click_news_filter, "click_news_filter")

    '''开启csrf防护
    1 生成csrf_token 值
    2 返回给前段浏览器，
    3 ajax请求头添加x-CSRFTocken， 浏览器每次请求时携带csrf_token
    '''

    from flask_wtf import csrf,CSRFProtect
    # 注册app开启csrf防护
    CSRFProtect(app)


    # 2 将生成的csrf——token返还到浏览器cookie中
    @app.after_request
    def after_requst(response):

        # 1 生成csrf_token
        csrf_token = csrf.generate_csrf()
        response.set_cookie('csrf_token', csrf_token)
        return response
    return app

