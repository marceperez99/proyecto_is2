from django.urls import path
from . import views
from django.urls import path, include
from django.urls import path, include # <--
from django.views.generic import TemplateView # <--

urlpatterns = [
    path('', views.index_view, name='index'),
    path('accounts/', include('allauth.urls')),
    path('login/', TemplateView.as_view(template_name="sso/login.html"), name='login'),  # <--
]
