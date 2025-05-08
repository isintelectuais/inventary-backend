"""
URL configuration for sistema_sia project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from apps.usuarios.api import router as usuarios_router
from apps.armazens.api import router as armazens_router
from apps.imagens.api import router as imagens_router
from apps.inventario.api import router as inventario_router
from apps.robos.api import router as robos_router
from apps.trajetorias.api import router as trajetorias_router
api = NinjaAPI(title="Sistema de Inventário de Armazém")
api.add_router("/armazens/", armazens_router)
api.add_router("/usuarios", usuarios_router)
api.add_router("/imagens/", imagens_router)
api.add_router("/inventario/", inventario_router)
api.add_router("/robos/", robos_router)
api.add_router("/trajetorias/", trajetorias_router)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
]