# 文章参考
# https://juejin.im/post/5b588b8c6fb9a04f834655a6
import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saleor.settings')

app = Celery('saleor')

CELERY_TIMEZONE = 'UTC'

app.config_from_object('django.conf:settings', namespace='CELERY')

# namespace='CELERY'表示， 去寻找 CELERY_xxxxxx 这样的配置

# CELERY_BROKER_URL = os.environ.get( 'CELERY_BROKER_URL', os.environ.get('CLOUDAMQP_URL')) or ''
# CELERY_TASK_ALWAYS_EAGER = not CELERY_BROKER_URL
# CELERY_ACCEPT_CONTENT = ['json']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULT_SERIALIZER = 'json'
# CELERY_RESULT_BACKEND = 'django-db'
###############################################################################################################################################


# 在flask中，需要在config指定使用celery任务的文件，这里可以不用指定，主动导入任务。
# 从所有已注册的Django app配置中加载任务模块。
app.autodiscover_tasks()
