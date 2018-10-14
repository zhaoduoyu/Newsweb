from flask import Blueprint

# 创建蓝图对象
news_blue = Blueprint("news_blue", __name__)

from . import views