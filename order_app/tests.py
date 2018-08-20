from django.test import TestCase

from processflow.runner.object_compare import deep_copy


from .models import Order, OrderItem, Picker

class TestModels(TestCase):

    def setUp(self):
        Picker.objects.create(name="picker")

        o = Order.objects.create(order_id="O-001", channel_order_id="xxx-yyy", address="Buxdehude")

        OrderItem.objects.create(
            order=o, sku="SKU-1", title="Dolle Wurst",
            channel_item_id="01234", channel_order_item_id="41298532614738",
            price="12.95", amount=1)

        OrderItem.objects.create(
            order=o, sku="SKU-2", title="Hundewurst",
            channel_item_id="01235", channel_order_item_id="41298532614739",
            price="16.99", amount=2)

    def test_content(self):

        picker = Picker.objects.get(name="picker")
        order = Order.objects.get(order_id="O-001")
        i1, i2 = order.orderitem_set.all()

    def test_deep_copy(self):
        order = Order.objects.get(order_id="O-001")
        values = deep_copy(order)
        self.assertEqual(values["id"], values["pk"])

        fields = Order.objects.filter(order_id="O-001").values()[0]
        fields["pk"] = fields["id"]
        fields["orderitem_set"] = set(i.id for i in order.orderitem_set.all())

        self.assertEqual(values, fields)


