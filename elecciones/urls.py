from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
import views

urlpatterns = [
    url(r'^alcaldes/resumen/porpacto$', views.AlcaldesResumenPorPacto.as_view()),
    url(r'^alcaldes/resumen/poranno$', views.AlcaldesResumenPorVotos.as_view()),
    url(r'^alcaldes/detalle/comuna/(?P<pk>[0-9]+)/$', views.AlcaldesDetallePorComuna.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)