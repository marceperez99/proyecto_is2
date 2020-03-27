from django.urls import path
from . import views
urlpatterns = [
    path('usuarios/', views.usuarios_view, name='usuarios'),
    path('usuarios/<int:id_usuario>', views.usuario_view, name='usuario'),
]
