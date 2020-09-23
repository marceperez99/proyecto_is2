from django.urls import path

from gestion_de_notificaciones import views

urlpatterns = [
    path('', views.ver_notificaciones_view, name='notificaciones'),
    path('<int:notificacion_id>/', views.visualizar_notificacion_view, name='ver_notificacion'),
]
