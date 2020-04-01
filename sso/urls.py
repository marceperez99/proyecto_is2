from django.urls import path
from . import views
from django.urls import path, include
from django.urls import path, include # <--
from django.views.generic import TemplateView # <--

urlpatterns = [
    path('', views.index_view, name='index'),
    path('accounts/', include('allauth.urls')),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('sin_permiso/', views.sin_permiso, name='sin_permiso'),
]
