from flask import session, g
from info.models import User


def click_news_filter(index):
    if index==1:
        return 'first'
    elif index == 2:
        return "second"
    elif index ==3:
        return "third"
    else:
        return ""


# 定义验证是否登陆的装饰器
def is_login(f):
    def wrapper(*args, **kwargs):
        # 验证用户登陆
        user = None
        user_id = session.get('user_id')
        if user_id:
            user = User.query.get(user_id)
        g.user = user
        return f(*args, **kwargs)

    wrapper.__name__ = f.__name__
    return wrapper
