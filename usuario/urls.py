from django.urls import path
from . import views
urlpatterns = [
    path('usuarios/', views.usuarios_view, name='usuarios'),
    path('usuarios/<int:usuario_id>', views.usuario_view, name='usuario'),
]
