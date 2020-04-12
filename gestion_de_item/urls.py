from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_items, name='listar_items'),
    path('<int:item_id>/', views.visualizar_item, name='visualizar_item'),
    path('<int:item_id>/eliminar/', views.eliminar_item_view, name='eliminar_item'),
    path('<int:item_id>/historial/', views.ver_historial_item_view, name='historial_item'),
    path('<int:item_id>/solicitar_aprobacion/', views.solicitar_aprobacion_view, name='solicitar_aprobacion_item'),
    path('nuevo/', views.nuevo_item_view, name='nuevo_item'),
    path('nuevo/<int:tipo_de_item_id>/', views.nuevo_item_view, name='nuevo_item_tipo'),

]
