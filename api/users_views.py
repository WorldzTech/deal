from django.contrib.auth import login
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from core.models import Product, Order
from core.serializer import ProductSerializer
from storage.models import StorageUnit
from users.serializers import UserSignupSerializer, UserSigninSerializer, UserSerializer

from storage.serializers import StorageSerializer


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
    permission_classes = (AllowAny,)
    authentication_classes = (SessionAuthentication,)

    def post(self, request):
        data = request.data
        serializer = UserSigninSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.check_user(data)
            login(request, user)
            return Response(serializer.data, status=status.HTTP_200_OK)


class GetUser(APIView):
    permission_classes = (IsAuthenticated, )

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
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        cart = dict(request.user.cart)

        print(cart)

        resp = []

        for item in cart:
            itemData = {
                'item': item
            }
            for size in cart[item]:
                print(item)
                print(size)
                itemData['size'] = size
                itemData['amount'] = cart[item][size]['amount']

                product = Product.objects.get(item=item)

                unit = StorageUnit.objects.get(product=product, size=size)
                itemData['available'] = unit.amount
                itemData['price'] = product.price

                resp.append(itemData)

                itemData = {
                    'item': item
                }

        return Response(resp, status=status.HTTP_200_OK)


class MakeOrder(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        user = request.user
        cartData = request.data

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

        for item in cart:
            product = Product.objects.get(item=item)
            for size in cart[item]:
                storageUnit = StorageUnit.objects.get(product=product, size=size)
                storageUnit.amount -= cart[item][size]['amount']
                storageUnit.save()

        Order.objects.create(user=user, status=Order.OrderStatus.created, products=cart)

        user.cart = {}
        user.save()

        return Response(status=status.HTTP_200_OK)
