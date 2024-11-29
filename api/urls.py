from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SysErrorViewSet, UserViewSet, LoginView, SettingsViewSet
from django.contrib.auth.decorators import login_required


router = DefaultRouter()
router.register(r'syserrors', SysErrorViewSet)
router.register(r'users', UserViewSet)
router.register(r'Settings', SettingsViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view(), name='login'),  
]
