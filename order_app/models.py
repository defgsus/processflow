import collections
from enum import Enum

from django.db import models
from django.db.models.base import ValidationError
from django.utils.translation import ugettext_lazy as _


class OrderStatus(Enum):
    NEW = _("new")
    INVALID = _("invalud")
    CREATED = _("created")
    FULFILLMENT = _("fulfillment")
    FULFILLMENT_NOTIFIED = _("fulfillment(n)")
    SENT = _("sent")
    SENT_NOTIFIED = _("sent(n)")


class Order(models.Model):

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    order_id = models.CharField(verbose_name=_("Own Order ID"), max_length=32, null=True, default=None)
    status = models.CharField(verbose_name=_("Own Status"), max_length=32, default=OrderStatus.NEW,
                              choices=[(tag.name, tag.value) for tag in OrderStatus])

    channel = models.CharField(verbose_name=_("Channel"), max_length=32, null=True, default=None)
    channel_order_id = models.CharField(verbose_name=_("Channel's Order ID"), max_length=64, null=True, default=None)
    channel_status = models.CharField(verbose_name=_("Channel"), max_length=32, null=True, default=None)

    address = models.CharField(verbose_name=_("Address"), max_length=1024)

    def clean(self):
        data = super().clean()
        if not data.get("order_id") and not data.get("channel_order_id"):
            raise ValidationError(_("Must either specify order_id or channel_order_id"))


class OrderItem(models.Model):

    class Meta:
        verbose_name = _("Order Item")
        verbose_name_plural = _("Order Items")

    order = models.ForeignKey(verbose_name=_("Order"), to=Order, on_delete=models.PROTECT)

    sku = models.CharField(verbose_name=_("Stock Keeping Unit"), max_length=64)
    title = models.CharField(verbose_name=_("Title"), max_length=512)
    channel_item_id = models.CharField(verbose_name=_("Channel's Item ID"), max_length=64, null=True, default=None)
    channel_order_item_id = models.CharField(verbose_name=_("Channel's Order-item ID"), max_length=64, null=True, default=None)

    channel_status = models.CharField(verbose_name=_("Channel's Order-item Status"), max_length=64)

    price = models.DecimalField(verbose_name=_("Price of item"), max_digits=12, decimal_places=2)
    amount = models.IntegerField(verbose_name=_("Number of items"))


class Picker(models.Model):

    class Meta:
        verbose_name = _("Picker")
        verbose_name_plural = _("Pickers")

    name = models.CharField(verbose_name=_("Picker's name"), max_length=32)
    items_collected = models.IntegerField(verbose_name=_("Number of items collected"), default=0)

