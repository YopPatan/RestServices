from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
import views

urlpatterns = [
    url(r'^generar/$', views.GenerateJson.as_view()),
    url(r'^eleccion/$', views.EleccionList.as_view()),
    url(r'^tipo/(?P<id>[0-9]+)$', views.EleccionTipoDetail.as_view()),
    url(r'^comuna/$', views.ComunaList.as_view()),
    url(r'^comuna/(?P<id>[0-9]+)/tipo/(?P<tipo_id>[0-9]+)$', views.ComunaDetail.as_view()),
    url(r'^comuna/ranking/tipo/(?P<tipo_id>[0-9]+)$', views.ComunaRanking.as_view()),
    url(r'^candidato/$', views.CandidatoList.as_view()),
    url(r'^candidato/(?P<id>[0-9]+)$', views.CandidatoDetail.as_view()),
#    url(r'^distrito/(?P<id>[0-9]+)$', views.PactoList.as_view()),
#    url(r'^circunscripcion/(?P<id>[0-9]+)$', views.PactoList.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)