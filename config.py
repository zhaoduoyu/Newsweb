from redis import StrictRedis


class Config(object):
    DEBUG = True
    SECRET_KEY = "EjpNVSNQTyGi1VvWECj9TvC/+kq3oujee2kTfQUs8yCM6xX9Yjq52v54g+HVoknA"

    # 配置数据库基本信息
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@localhost/information"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # 配置Redis数据库基本信息
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # SESSION 信息配置
    SESSION_TYPE = "redis"  # 指定 session 保存到 redis 中
    SESSION_USE_SIGNER = True  # 让 cookie 中的 session_id 被加密签名处理
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 使用 redis 的实例
    PERMANENT_SESSION_LIFETIME = 86400  # session 的有效期，单位是秒

    # 说明：主账号，登陆云通讯网站后，可在"控制台-应用"中看到开发者主账号ACCOUNT SID
    _accountSid = '8a216da8662360a401662560d450035e'

    # 说明：主账号Token，登陆云通讯网站后，可在控制台-应用中看到开发者主账号AUTH TOKEN
    _accountToken = '9bfc2fc86715450db2c8e8f884949cc2'

    # 请使用管理控制台首页的APPID或自己创建应用的APPID
    _appId = '8a216da8662360a401662560d4ad0365'


class DevelopementConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    pass


config = {
    'developement':DevelopementConfig,
    'production':ProductionConfig
}