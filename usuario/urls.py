from django.urls import path
from . import views
urlpatterns = [
    path('usuarios/<int:id_usuario>',views.usuario_view,name='usuario'),
]
