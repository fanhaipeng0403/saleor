"""Cart-related ORM models."""
from decimal import Decimal
from uuid import uuid4

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.encoding import smart_str
from django_prices.models import MoneyField
from measurement.measures import Weight

from ..account.models import Address
from ..core.utils.taxes import ZERO_TAXED_MONEY, zero_money
from ..shipping.models import ShippingMethod

# cart 购物车
CENTS = Decimal('0.01')

# Manager
# https://www.jianshu.com/p/2bc5b7c4275d

# 关于 QuerySet的讲解
# https://www.cnblogs.com/gaoya666/p/9005753.html
class CartQueryset(models.QuerySet):
    """A specialized queryset for dealing with carts."""

    def for_display(self):
        """Annotate the queryset for display purposes.

        Prefetches additional data from the database to avoid the n+1 queries
        problem.
        """
        return self.prefetch_related(
            'lines__variant__translations',
            'lines__variant__product__translations',
            'lines__variant__product__images',
            'lines__variant__product__product_type__product_attributes__values')  # noqa


class Cart(models.Model):
    """A shopping cart."""

    created = models.DateTimeField(auto_now_add=True)
    last_change = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, related_name='carts',
        on_delete=models.CASCADE)
    email = models.EmailField(blank=True, default='')
    token = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    quantity = models.PositiveIntegerField(default=0)
    billing_address = models.ForeignKey(
        Address, related_name='+', editable=False, null=True,
        on_delete=models.SET_NULL)
    shipping_address = models.ForeignKey(
        Address, related_name='+', editable=False, null=True,
        on_delete=models.SET_NULL)
    shipping_method = models.ForeignKey(
        ShippingMethod, blank=True, null=True, related_name='carts',
        on_delete=models.SET_NULL)
    note = models.TextField(blank=True, default='')
    discount_amount = MoneyField(
        currency=settings.DEFAULT_CURRENCY,
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=zero_money)
    discount_name = models.CharField(max_length=255, blank=True, null=True)
    translated_discount_name = models.CharField(
        max_length=255, blank=True, null=True)
    voucher_code = models.CharField(max_length=12, blank=True, null=True)

    # Entry.objects.all()[:5], objects
    # objects是一个特殊的属性, 通过它来查询数据库, 它就是模型的一个Manager.
    objects = CartQueryset.as_manager()

    class Meta:
        ordering = ('-last_change',)

    def __repr__(self):
        return 'Cart(quantity=%s)' % (self.quantity,)

    def __iter__(self):
        return iter(self.lines.all())

    def __len__(self):
        return self.lines.count()

    def is_shipping_required(self):
        """Return `True` if any of the lines requires shipping."""
        return any(line.is_shipping_required() for line in self)

    def get_shipping_price(self, taxes):
        return (
            self.shipping_method.get_total(taxes)
            if self.shipping_method and self.is_shipping_required()
            else ZERO_TAXED_MONEY)

    def get_subtotal(self, discounts=None, taxes=None):
        """Return the total cost of the cart prior to shipping."""
        subtotals = (line.get_total(discounts, taxes) for line in self)
        return sum(subtotals, ZERO_TAXED_MONEY)

    def get_total(self, discounts=None, taxes=None):
        """Return the total cost of the cart."""
        return (
            self.get_subtotal(discounts, taxes)
            + self.get_shipping_price(taxes) - self.discount_amount)

    def get_total_weight(self):
        # Cannot use `sum` as it parses an empty Weight to an int
        weights = Weight(kg=0)
        for line in self:
            weights += line.variant.get_weight() * line.quantity
        return weights

    def get_line(self, variant):
        """Return a line matching the given variant and data if any."""
        matching_lines = (line for line in self if line.variant == variant)
        return next(matching_lines, None)


class CartLine(models.Model):
    """A single cart line.

    Multiple lines in the same cart can refer to the same product variant if
    their `data` field is different.

    """

    cart = models.ForeignKey( Cart, related_name='lines', on_delete=models.CASCADE)
                               # app.ModelName
    variant = models.ForeignKey('product.ProductVariant', related_name='+', on_delete=models.CASCADE)


    # 正数，验证器
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    # sqlalchemy 的实现

    # __table_args__ = (
    #     CheckConstraint(bar >= 0, name='check_bar_positive'),
    #     {})

            #postgresql 特殊的字段类型
    data = JSONField(blank=True, default=dict)

    # 模型的元数据，指的是“除了字段外的所有内容”，例如排序方式、数据库表名、人类可读的单数或者复数名等等
    # http://www.liujiangblog.com / course / django / 99
    # 类似于sqlalchemy的 __table_args__ = (db.Index('users_org_id_email', 'org_id', 'email', unique=True),)

    class Meta:

        unique_together = ('cart', 'variant', 'data')


        # flask
        # __table_args__ = (
        #     UniqueConstraint('col1', 'col2', 'number', name='uix_table_col1_col2_col3'),
        # )
        # __table_args__ = (UniqueConstraint("object_type", "object_id", "user_id", name="unique_favorite"),)


    def __str__(self):

        # 我们在需要将用户提交的数据转换为 Unicode 的时候，可以使用 smart_unicode，而在需要将程序中字符输出到非 Unicode 环境（比如 HTTP 协议数据）时可以使用 smart_str 方法

        return smart_str(self.variant)

    def __eq__(self, other):
        if not isinstance(other, CartLine):
            return NotImplemented

        return (
            self.variant == other.variant and
            self.quantity == other.quantity)

    def __ne__(self, other):
        return not self == other  # pragma: no cover


    def __repr__(self):
        return 'CartLine(variant=%r, quantity=%r)' % (
            self.variant, self.quantity)

    # 一些对象类型（譬如，文件对象）不能进行 pickle。处理这种不能 pickle 的对象的实例属性时可以使用特殊的方法（ _getstate_() 和 _setstate_() ）来修改类实例的状态。这里有一个 Foo 类的示例，我们已经对它进行了修改以处理文件对象
    def __getstate__(self):
        return self.variant, self.quantity

    def __setstate__(self, data):
        self.variant, self.quantity = data

    def get_total(self, discounts=None, taxes=None):
        """Return the total price of this line."""
        amount = self.quantity * self.variant.get_price(discounts, taxes)
        return amount.quantize(CENTS)

    def is_shipping_required(self):
        """Return `True` if the related product variant requires shipping."""
        return self.variant.is_shipping_required()
