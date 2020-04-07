from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_items, name='listar_items'),
    path('<int:item_id>/', views.visualizar_item, name='visualizar_item'),
]
