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
from .views import *
from .users_views import *
from .admin_api import *
from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views
from deal import settings
from .admin_api import *

urlpatterns = [
    path('models/fields/product', GetProductModelFields.as_view(), name='models_fields_product'),
    path('product', ProductEndpoint.as_view(), name='create_product'),
    path('supportrequests', SupportRequestsEndpoint.as_view(), name='admin_requests'),
    path('supportrequests/details', SupportRequestDetailsEndpoint.as_view(), name='admin_requests_details'),
    path('supportrequests/sendmessage', SendMessageViaSupportAccountEndpoint.as_view(), name='admin_requests_sendmessage'),
    path('supportrequests/close', CloseSupportRequestEndpoint.as_view(), name='admin_requests_close'),
    path('tags/groups/switch', SwitchTagGroupsEndpoint.as_view(), name='admin_tags_groups_switch'),
    path('orders/', GetOrdersEndpoint.as_view(), name='admin_orders'),
    path('orders/status', SetOrderStatusEndpoint.as_view(), name='admin_orders_status'),
    path('storage/', StorageEndpoint.as_view(), name='admin_storage'),
    path('storage/details/', StorageUnitDetailsEndpoint.as_view(), name='admin_storage_details'),
]
