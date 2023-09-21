from django.urls import path, include
from rest_framework import routers
from users.views import subscribe, SubscriptionsViewSet

router_v1 = routers.DefaultRouter()
router_v1.register(r'users/subscriptions', SubscriptionsViewSet,
                   basename='subscriptions')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/<int:pk>/subscribe/', subscribe),
]
