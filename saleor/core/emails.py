from django.contrib.sites.models import Site
from django.templatetags.static import static

from ..core.utils import build_absolute_uri


def get_email_base_context():

    # 内置功能:获取当前网站相关信息

    site = Site.objects.get_current()


    # static 输入相对路径，输出绝对路径

     # build_absolute_uri, 域名路径+资源路径， 并且
    logo_url = build_absolute_uri(static('images/logo-document.svg'))

    return {
        'domain': site.domain,
        'logo_url': logo_url,
        'site_name': site.name}
