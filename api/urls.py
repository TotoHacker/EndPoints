from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SysErrorViewSet, UserViewSet, LoginView

router = DefaultRouter()
router.register(r'syserrors', SysErrorViewSet)

router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view(), name='login'),  
]
