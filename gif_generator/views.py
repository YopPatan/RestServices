from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class Gif(APIView):

#    def get(self, request, format=None):
#        genres = Genre.objects.all()
#        serializer = GenreSerializer(genres, many=True)
#        return Response(serializer.data)

    def post(self, request, format=None):
        return Response({}, status=status.HTTP_201_CREATED);

class Url(APIView):
    
    def post(self, request, format=None):
        return Response({}, status=status.HTTP_201_CREATED);