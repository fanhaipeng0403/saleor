from django.conf.urls import url

from . import views
from .views.discount import remove_voucher_view

checkout_urlpatterns = [
    url(r'^$', views.checkout_index, name='index'),
    url(r'^shipping-address/', views.checkout_shipping_address,
        name='shipping-address'),
    url(r'^shipping-method/', views.checkout_shipping_method,
        name='shipping-method'),
    url(r'^summary/', views.checkout_summary, name='summary'),
    url(r'^remove_voucher/', remove_voucher_view,
        name='remove-voucher'),
    url(r'^login/', views.checkout_login, name='login')]


cart_urlpatterns = [
    url(r'^$', views.cart_index, name='index'),




    # (?P<name>pattern), 获取参数, 注意是，关键字参数，捕获的值作为关键字参数而不是位置参数传递给视图函数, variant_id=‘1’ , 且永远为字符串类型
    url(r'^update/(?P<variant_id>\d+)/$', views.update_cart_line, name='update-line'),

    url(r'^clear-cart/$', views.clear_cart, name='clear-cart'),
    url(r'^summary/$', views.cart_summary, name='summary'),
    url(r'^shipping-options/$', views.cart_shipping_options, name='shipping-options')]
