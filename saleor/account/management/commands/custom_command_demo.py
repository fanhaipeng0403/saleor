from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "这是个测试命令"

    def add_arguments(self, parser):
        parser.add_argument('--url1', dest='url1', required=True, help='the url to process', )
        parser.add_argument('--url2', dest='url2', required=True, help='the url to process', )
        parser.add_argument('--url3', dest='url3', required=True, help='the url to process', )

    def handle(self, *args, **options):
        url1 = options['url1']
        url2 = options['url2']
        url3 = options['url3']
        print(url1 + url2 + url3)

# >>> (saleor-master) C:\Users\User\Desktop\saleor>python manage.py custom_command_demo --url1 1  --url2 2 --url3 3
# >>>
# >>>> 123
