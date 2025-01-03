from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SysErrorViewSet, UserViewSet, LoginView, SettingsViewSet, last_check_status


router = DefaultRouter()
router.register(r'syserrors', SysErrorViewSet)
router.register(r'users', UserViewSet)
router.register(r'Settings', SettingsViewSet)
router.register(r'LastCheck', last_check_status)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view(), name='login'),  
]
