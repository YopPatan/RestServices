from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
import views

urlpatterns = [
   url(r'^gif$', views.Gif.as_view()),
#    url(r'^show$', views.ShowList.as_view()),
#    url(r'^programming/normal$', views.ProgrammingNormalList.as_view()),
#    url(r'^programming/extend$', views.ProgrammingExtendList.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)