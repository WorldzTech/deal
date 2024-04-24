"""
URL configuration for deal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static

from . import admin_api, admin_api_urls
from .views import *
from .users_views import *
from .admin_api import *
from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views
from deal import settings

urlpatterns = [
    path('post/get/', GetBlogPost.as_view(), name='api_post_get'),
    path('product/get/', GetProduct.as_view(), name='api_product_get'),
    path('product/search/', SearchProductByMask.as_view(), name='api_product_search'),
    path('product/cart/', AddProductToCart.as_view(), name='api_product_cart'),
    path('users/signup/', UserRegister.as_view(), name='api_user_signup'),
    path('users/signin/', LoginUser.as_view(), name='api_user_signin'),
    path('users/logout/', LogoutUser.as_view(), name='api_user_logout'),
    path('users/get/', GetUser.as_view(), name='api_user_get'),
    path('users/cart/', GetUserCart.as_view(), name='api_user_cart'),
    path('users/cart/order/', MakeOrder.as_view(), name='api_user_cart_order'),
    path('users/orders/', GetUserOrders.as_view(), name='api_user_orders'),
    path('users/favorites/', UserFavorites.as_view(), name='api_user_favorites'),
    path('users/support/', UserSupportRequests.as_view(), name='api_user_support_requests'),
    path('users/order/', GetUserOrder.as_view(), name='api_user_order'),
    path('catalog/', GetCatalog.as_view(), name='api_catalog'),
    path('tags/groups', TagGroupsEndpoint.as_view(), name='api_tags_groups'),
    path('tags/', TagsEndpoint.as_view(), name='api_tags'),
    path('token/',
         jwt_views.TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('token/refresh/',
         jwt_views.TokenRefreshView.as_view(),
         name='token_refresh'),
    path('', include('chats.chat_api_urls')),
    path('admin/', include('api.admin_api_urls'), name='admin_api'),
]
