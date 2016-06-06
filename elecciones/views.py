from models import Comuna, Voto, Resultado, Poblacion, Pacto
from serializers import ComunaSerial, VotoSerial, ResultadoSerial, PactoSerial

from django.db.models import Q, Count, Sum, Case, When
from rest_framework.views import APIView
from rest_framework.response import Response

class AlcaldesResumenPorPacto(APIView):

    def get(self, request, format=None):
        result = Pacto.objects.all().annotate(votos_cnt=Sum('resultado__votos_cnt'), 
                                              electos_cnt=Count(Case(When(resultado__electo=1, then=1))),
                                              independientes_cnt=Count(Case(When(resultado__partido_id=2, resultado__electo=1, then=1))),
                                              pacto_cnt=Count(Case(When(~Q(resultado__partido_id = 2) & Q(resultado__electo=1), then=1))))
      
        serializer = PactoSerial(result, many=True)
        return Response(serializer.data)

class AlcaldesResumenPorVotos(APIView):

    def get(self, request, format=None):
        result = Voto.objects.all().values('anno').annotate(emitidos_cnt=Sum('emitidos_cnt'), 
                                                            validos_cnt=Sum('validos_cnt'), 
                                                            blancos_cnt=Sum('blancos_cnt'), 
                                                            nulos_cnt=Sum('nulos_cnt'))
        serializer = VotoSerial(result, many=True)
        
        for voto in serializer.data:
            voto['poblacion_adultos_cnt'] = Poblacion.objects.filter(anno=2012).aggregate(total=Sum('poblacion_adultos_cnt'))['total'];

        return Response(serializer.data)

class AlcaldesDetallePorComuna(APIView):
    
    def get(self, request, pk, format=None):
        votos = Voto.objects.filter(eleccion_tipo_id=5, comuna_id=pk)
        votosSer = VotoSerial(votos, many=True)
        
        for voto in votosSer.data:
            poblaciones = Poblacion.objects.filter(comuna_id=pk, anno=voto['anno']).values('poblacion_adultos_cnt');
            
            if poblaciones.count() == 0:
                voto['poblacion_cnt'] = None;
            else:
                voto['poblacion_cnt'] = poblaciones[0]['poblacion_adultos_cnt'];
            
            resultados = Resultado.objects.filter(eleccion_tipo_id=5, comuna_id=pk, anno=voto['anno'])
            resultadosSer = ResultadoSerial(resultados, many=True)
            voto['candidato'] = resultadosSer.data

        return Response(votosSer.data)
    
    
    