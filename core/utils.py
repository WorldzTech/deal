import core.models as core_models
from storage.models import StorageUnit


def create_order(invoice):
    cart = {}

    for position in invoice.order_data:
        if position['item'] not in cart.keys():
            cart[position['item']] = {}
        if position['size'] not in cart[position['item']].keys():
            cart[position['item']][position['size']] = {}

        cart[position['item']][position['size']]['amount'] = position['amount']
        cart[position['item']][position['size']]['available'] = position['available']

    for item in cart:
        product = core_models.Product.objects.get(item=item)
        for size in cart[item]:
            storageUnit = StorageUnit.objects.get(product=product, size=size)
            if storageUnit.amount < cart[item][size]['amount']:
                print(storageUnit.amount, cart[item][size]['amount'])
                cart[item][size]['amount'] = cart[item][size]['available']

    totalPrice = 0

    try:
        for item in cart:
            product = core_models.Product.objects.get(item=item)
            for size in cart[item]:
                totalPrice += product.price * cart[item][size]['amount']
                storageUnit = StorageUnit.objects.get(product=product, size=size)
                storageUnit.amount -= cart[item][size]['amount']
                storageUnit.save()
    except:
        return {"point": 156}

    order = core_models.Order.objects.create(user=invoice.client, status=core_models.Order.OrderStatus.created, products=cart,
                                 totalPrice=totalPrice, address=invoice.address, phoneNumber=invoice.mobile_phone,
                                 email=invoice.email,
                                 receiverFullname=invoice.fullname)

    return order
