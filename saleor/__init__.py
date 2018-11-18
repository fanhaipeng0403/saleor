

# 引入到Project的__init__.py,确保CELERY可以在最初就被初始化

from .celeryconf import app as celery_app # 一个import会执行文件下的所有内容

__all__ = ['celery_app']
__version__ = 'dev'
