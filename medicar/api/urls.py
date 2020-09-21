from django import urls
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from .views import SpecialtyViewSet, MedicViewSet, AgendaViewSet, AppointmentViewSet


router = routers.DefaultRouter()
router.register(r'especialidades', SpecialtyViewSet, basename="especialidades")
router.register(r'medicos', MedicViewSet, basename="medicos")
router.register(r'agendas', AgendaViewSet, basename="agendas")
router.register(r'consultas', AppointmentViewSet, basename="consultas")

urlpatterns = [
    urls.path('', urls.include(router.urls)),
    urls.path('{consulta_id}', urls.include(router.urls)),
    urls.path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
]
