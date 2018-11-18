https://www.ibm.com/developerworks/cn/web/1101_jinjh_djangoi18n/
https://code.ziqiangxuetang.com/django/django-internationalization.html
http://www.liujiangblog.com/course/django/180
https://wizardforcel.gitbooks.io/django-book-20-zh-cn/content/19.html
https://juejin.im/post/5b3efc36e51d45197136eb09

1. mkdir locale 
2. django-admin.py makemessages -l zh_CN,       (一定要是下划线)
3. 生成了 locale/zh_CN/LC_MESSAGES/django.po 



文件内容如下 

"""
#: saleor/account/forms.py:69

msgctxt "Form field" , # 用于语境分析，有些词是多义词

msgid "Email"
msgstr "电子邮件"


"""

msgid 是在源文件中出现的翻译字符串。msgstr 是相应语言的翻译结果。


4. 每次对其做了修改，都需要用 django-admin.py compilemessages 编译成“.mo”文件供 gettext 使用

5. 确认相关配置

首先需要确认 testsite 目录下 setting.py 的配置，主要需要核实 LANGUAGE_CODE，USE_I18N 和 MIDDLEWARE_CLASSES。

setting.py 中的国际化相关配置

LANGUAGE_CODE = 'en-us'
USE_I18N = True 
MIDDLEWARE_CLASSES = ( 
   'django.middleware.common.CommonMiddleware', 
   'django.contrib.sessions.middleware.SessionMiddleware', 
   
   
   ####################################################
   'django.middleware.locale.LocaleMiddleware', 
   ####################################################
   
   'django.contrib.auth.middleware.AuthenticationMiddleware', 
)
请注意注意 MIDDLEWARE_CLASSES 中的'django.middleware.locale.LocaleMiddleware', 需要放在'django.contrib.sessions.middleware.SessionMiddleware' 后面。

