from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
import views

urlpatterns = [
    url(r'^participacion$', views.ParticipacionList.as_view()),
    url(r'^comuna/$', views.ComunaList.as_view()),
    url(r'^comuna/(?P<id>[0-9]+)$', views.ComunaDetail.as_view()),
    url(r'^comuna/ranking$', views.ComunaRanking.as_view()),
    url(r'^candidato/$', views.CandidatoList.as_view()),
    url(r'^candidato/(?P<id>[0-9]+)$', views.CandidatoDetail.as_view()),
    url(r'^pacto$', views.PactoList.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)