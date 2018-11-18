import uuid

##############################################
from django.conf import settings
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.db import models
from django.db.models import Q
from django.forms.models import model_to_dict
from django.utils import timezone
from django.utils.translation import pgettext_lazy
from django_countries.fields import Country, CountryField


############ 使用了第三方的电话号码字段类型
from phonenumber_field.modelfields import PhoneNumber, PhoneNumberField

from .validators import validate_possible_number


def get_token():
    return str(uuid.uuid4())


class PossiblePhoneNumberField(PhoneNumberField):
    """Less strict field for phone numbers written to database."""

    default_validators = [validate_possible_number]


class Address(models.Model):

    # null 是针对数据库而言，如果 null = True, 表示数据库的该字段可以为空，那么在新建一个model对象的时候是不会报错的
    # blank 是针对表单的，如果 blank = True，表示你的表单填写该字段的时候可以不填，比如 admin 界面下增加 model 一条记录的时候

    first_name = models.CharField(max_length=256, blank=True)

    last_name = models.CharField(max_length=256, blank=True)

    company_name = models.CharField(max_length=256, blank=True)

    street_address_1 = models.CharField(max_length=256, blank=True)

    street_address_2 = models.CharField(max_length=256, blank=True)

    city = models.CharField(max_length=256, blank=True)

    city_area = models.CharField(max_length=128, blank=True)

    postal_code = models.CharField(max_length=20, blank=True)

    country = CountryField()

    country_area = models.CharField(max_length=128, blank=True)

    phone = PossiblePhoneNumberField(blank=True, default='')


    @property
    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    def __str__(self):
        if self.company_name:
            return '%s - %s' % (self.company_name, self.full_name)
        return self.full_name

    def __repr__(self):
        return (
            'Address(first_name=%r, last_name=%r, company_name=%r, '
            'street_address_1=%r, street_address_2=%r, city=%r, '
            'postal_code=%r, country=%r, country_area=%r, phone=%r)' % (
                self.first_name, self.last_name, self.company_name,
                self.street_address_1, self.street_address_2, self.city,
                self.postal_code, self.country, self.country_area,
                self.phone))

    def __eq__(self, other):
        return self.as_data() == other.as_data()

    def as_data(self):
        """Return the address as a dict suitable for passing as kwargs.

        Result does not contain the primary key or an associated user.
        """
        data = model_to_dict(self, exclude=['id', 'user'])
        if isinstance(data['country'], Country):
            data['country'] = data['country'].code
        if isinstance(data['phone'], PhoneNumber):
            data['phone'] = data['phone'].as_e164
        return data

    def get_copy(self):
        """Return a new instance of the same address."""
        return Address.objects.create(**self.as_data())


class UserManager(BaseUserManager):

    def create_user(
        self, email, password=None, is_staff=False, is_active=True,
        **extra_fields):
        """Create a user instance with the given email and password."""
        email = UserManager.normalize_email(email)
        # Google OAuth2 backend send unnecessary username field
        extra_fields.pop('username', None)

        user = self.model(
            email=email, is_active=is_active, is_staff=is_staff,
            **extra_fields)
        if password:
            user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        return self.create_user(
            email, password, is_staff=True, is_superuser=True, **extra_fields)

    def customers(self):
        return self.get_queryset().filter(
            Q(is_staff=False) | (Q(is_staff=True) & Q(orders__isnull=False)))

    def staff(self):
        return self.get_queryset().filter(is_staff=True)


class User(PermissionsMixin, AbstractBaseUser):

    # 邮箱，地址，员工， token， 激活，通知？？？， 加入日期？？， 收货地址，账单地址？？？？

    email = models.EmailField(unique=True)
    ################# ManyToMAnyFiled 相当于 relationShip？？？
    addresses = models.ManyToManyField( Address, blank=True, related_name='user_addresses')
    is_staff = models.BooleanField(default=False)
    token = models.UUIDField(default=get_token, editable=False, unique=True)
    is_active = models.BooleanField(default=True)
    note = models.TextField(null=True, blank=True)
    ########################################################## 不会出现在admin后台，即后台不可编辑
    date_joined = models.DateTimeField(default=timezone.now, editable=False)
    default_shipping_address = models.ForeignKey( Address, related_name='+', null=True, blank=True, on_delete=models.SET_NULL)
    default_billing_address = models.ForeignKey( Address, related_name='+', null=True, blank=True, on_delete=models.SET_NULL)

    USERNAME_FIELD = 'email'

    objects = UserManager()

    class Meta:
        permissions = (
            (
                'manage_users', pgettext_lazy(
                    'Permission description', 'Manage customers.')),
            (
                'manage_staff', pgettext_lazy(
                    'Permission description', 'Manage staff.')),
            (
                'impersonate_users', pgettext_lazy(
                    'Permission description', 'Impersonate customers.')))

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def get_ajax_label(self):
        address = self.default_billing_address
        if address:
            return '%s %s (%s)' % (
                address.first_name, address.last_name, self.email)
        return self.email


class CustomerNote(models.Model):
    user = models.ForeignKey( settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL)

    # auto_now无论是你添加还是修改对象，时间为你添加或者修改的时间。
    # auto_now_add为添加时的时间，更新对象时不会有变动

    # sqlalchemy常规的是创建create_time 和 update_time  然后 # Column(DateTime(True), default=func.now(), onupdate=func.now(), nullable=False)

    date = models.DateTimeField(db_index=True, auto_now_add=True)

    content = models.TextField()

    is_public = models.BooleanField(default=True)

    # AUTH_USER_MODEL = 'account.User'
    #####################################################使用related_name属性定义名称(related_name是关联对象反向引用描述符)。
    customer = models.ForeignKey( settings.AUTH_USER_MODEL, related_name='notes', on_delete=models.CASCADE)

    class Meta:
        ordering = ('date',)

    # sqlalchemy 中使用
    # __mapper_args__ = {
    #         "order_by": title
    #     }
