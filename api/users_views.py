import logging

from django.contrib.auth import login, get_user_model
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from core.models import Product, Order, SupportRequest
from core.serializer import ProductSerializer, OrderSerializer, SupportRequestSerializer
from storage.models import StorageUnit
from users.serializers import UserSignupSerializer, UserSigninSerializer, UserSerializer

from storage.serializers import StorageSerializer

user_model = get_user_model()


class UserRegister(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        clean_data = request.data
        print(clean_data)
        serializer = UserSignupSerializer(data=clean_data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.create(clean_data)
            if user:
                return Response(serializer.data)
            else:
                return Response({'failed': 'no user'})
        return Response(status=status.HTTP_400_BAD_REQUEST)


class LoginUser(APIView):
    def post(self, request):
        username = request.data['username']
        password = request.data['password']

        user = user_model.objects.filter(mobilePhone=username).first()
        print(f"LOGIN AS {user}")

        if user is None:
            return Response({'message': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)

        if not user.check_password(password):
            return Response({'message': 'Неверный пароль'}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)
        token = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'isAdmin': user.is_staff
        }
        return Response(token)


class GetUser(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response({'user': serializer.data}, status=status.HTTP_200_OK)


class LogoutUser(APIView):
    # permission_classes = (IsAuthenticated,)

    def post(self, request):
        print(request.headers)
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class GetUserCart(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        cart = request.user.cart

        if not cart:
            request.user.cart = {}
            request.user.save()

        cart = request.user.cart

        print(cart)

        resp = []
        old_items = []

        renew_cart = {}

        for item in cart:
            if Product.objects.filter(item=item).exists():
                renew_cart[item] = cart[item]

        request.user.cart = renew_cart
        request.user.save()

        for item in renew_cart:
            itemData = {
                'item': item
            }
            for size in cart[item]:
                print(item)
                print(size)
                itemData['size'] = size
                itemData['amount'] = cart[item][size]['amount']

                product = Product.objects.filter(item=item).first()

                unit = StorageUnit.objects.get(product=product, size=size)
                itemData['available'] = unit.amount
                itemData['price'] = product.price

                resp.append(itemData)

                itemData = {
                    'item': item
                }

        return Response(resp, status=status.HTTP_200_OK)


class MakeOrder(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        logger = logging.getLogger(__name__)
        logger.debug(request.data)
        user = request.user
        cartData = request.data['cart']
        address = request.data['address']
        mobilePhone = request.data['mobilePhone']
        fullname = request.data['fullname']
        email = request.data['email']

        cart = {}

        for position in cartData:
            if position['item'] not in cart.keys():
                cart[position['item']] = {}
            if position['size'] not in cart[position['item']].keys():
                cart[position['item']][position['size']] = {}

            cart[position['item']][position['size']]['amount'] = position['amount']
            cart[position['item']][position['size']]['available'] = position['available']

        print(cart)

        for item in cart:
            product = Product.objects.get(item=item)
            for size in cart[item]:
                storageUnit = StorageUnit.objects.get(product=product, size=size)
                if storageUnit.amount < cart[item][size]['amount']:
                    print(storageUnit.amount, cart[item][size]['amount'])
                    cart[item][size]['amount'] = cart[item][size]['available']

        totalPrice = 0

        try:
            for item in cart:
                product = Product.objects.get(item=item)
                for size in cart[item]:
                    totalPrice += product.price * cart[item][size]['amount']
                    storageUnit = StorageUnit.objects.get(product=product, size=size)
                    storageUnit.amount -= cart[item][size]['amount']
                    storageUnit.save()
        except:
            return Response({"point": 156}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(user=user, status=Order.OrderStatus.created, products=cart,
                                     totalPrice=totalPrice, address=address, phoneNumber=mobilePhone, email=email,
                                     receiverFullname=fullname)

        try:
            order.generate_inner_id()
        except Exception:
            return Response({"point": 172}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order.create_support_chat()
        except:
            return Response({"point": 177}, status=status.HTTP_400_BAD_REQUEST)

        user.cart = {}
        user.save()

        return Response({"id": order.innerId}, status=status.HTTP_200_OK)


class GetUserOrders(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        orders = Order.objects.filter(user=user).order_by('creation_date')[::-1]

        data = []
        for order in orders:
            data.append(OrderSerializer(order).data)

        return Response(data, status=status.HTTP_200_OK)


class UserFavorites(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        productItem = request.data.get('item')
        user = request.user

        product = Product.objects.get(item=productItem)

        if product in user.favorites.all():
            user.favorites.remove(product)
        else:
            user.favorites.add(product)

        user.save()

        return Response(status=status.HTTP_200_OK)

    def get(self, request):
        user = request.user

        data = []

        for item in user.favorites.all():
            data.append(ProductSerializer(item).data)

        return Response(data, status=status.HTTP_200_OK)


class UserSupportRequests(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user

        requests = SupportRequest.objects.filter(user=user).order_by('-date')

        data = []

        for r in requests.all():
            rd = SupportRequestSerializer(r).data
            if r.chat:
                rd['chatId'] = r.chat.id
            data.append(rd)

        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        topic = request.data.get('topic')
        body = request.data.get('body')

        req = SupportRequest.objects.create(user=user, topic=topic, description=body)

        req.startChat()

        return Response(status=status.HTTP_201_CREATED)


class GetUserOrder(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        orderId = request.GET.get('orderId')

        order = Order.objects.filter(id=orderId).first()

        if order and order.user == user:
            data = OrderSerializer(order).data
            productsDetails = []

            for item in dict(order.products).keys():
                print(dict(order.products))
                productData = {
                    'item': item
                }
                product = Product.objects.get(item=item)
                for size in dict(order.products[item]).keys():
                    print(dict(order.products[item]))
                    print(size)
                    productData['size'] = size
                    productData['amount'] = order.products[item][size]['amount']
                    productData['available'] = order.products[item][size]['amount']
                    productData['price'] = product.price

                    print(productData)
                    productsDetails.append(productData)
                    productData = {
                        'item': item
                    }

            data['details'] = productsDetails

            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
