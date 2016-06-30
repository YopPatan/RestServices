from models import Comuna, Participacion, Resultado, Poblacion, Pacto, Partido, Candidato, EleccionFecha
from serializers import ComunaSerial, ParticipacionSerial, ResultadoSerial, PactoSerial, CandidatoSerial, PartidoSerial, EleccionSerial, TotalesSerial

#from django.db import connection
from django.db import connections

from django.db.models import Q, Count, Sum, Case, When
from rest_framework.views import APIView
from rest_framework.response import Response

class ParticipacionList(APIView):

    def get(self, request, format=None):
        elecciones = EleccionFecha.objects.all();
        eleccionesSer = EleccionSerial(elecciones, many=True).data
        
        for eleccion in eleccionesSer:
            eleccion['adultos_cnt'] = Poblacion.objects.filter(anno=eleccion['anno']).aggregate(total=Sum('poblacion_adultos_cnt'))['total'];
            participacion = Participacion.objects.filter(anno=eleccion['anno'],
                                eleccion_tipo_id=eleccion['eleccion_tipo']['id'],
                                vuelta=eleccion['vuelta']).values().annotate(emitidos_cnt=Sum('emitidos_cnt'),
                                    validos_cnt=Sum('validos_cnt'),
                                    blancos_cnt=Sum('blancos_cnt'),
                                    nulos_cnt=Sum('nulos_cnt')).order_by('-anno')

            if participacion.count() > 0:
                eleccion['participacion'] = ParticipacionSerial(participacion, many=True).data[0]
        
        return Response(eleccionesSer)
    

class PactoList(APIView):

    def get(self, request, format=None):
        pactos = Pacto.objects.all();
        pactosSer = PactoSerial(pactos, many=True).data
        
        for pacto in pactosSer:
            partidos = Partido.objects.filter(resultado__pacto_id=pacto['id']).distinct()
            partidosSer = PartidoSerial(partidos, many=True).data
            
            elecciones = EleccionFecha.objects.filter(anno=pacto['anno'])
            
            eleccionesSer = EleccionSerial(elecciones, many=True).data
            for eleccion in eleccionesSer:
                resultado = Resultado.objects.filter(pacto_id=pacto['id'], 
                                                     anno=eleccion['anno'], 
                                                     eleccion_tipo_id=eleccion['eleccion_tipo']['id']
                                                     ).values('pacto_id', 'anno', 'eleccion_tipo_id').annotate(votos_cnt=Sum('votos_cnt'),
                                                                                  electos_cnt=Count(Case(When(electo=1, then=1))))
                if resultado.count() > 0:
                    eleccion['resultado'] = TotalesSerial(resultado, many=True).data[0]

            pacto['elecciones'] = eleccionesSer
            
            for partido in partidosSer:
                eleccionesSer = EleccionSerial(elecciones, many=True).data
                for eleccion in eleccionesSer:
                    resultado = Resultado.objects.filter(partido_id=partido['id'], 
                                                         anno=eleccion['anno'], 
                                                         eleccion_tipo_id=eleccion['eleccion_tipo']['id']
                                                         ).values('partido_id', 'anno', 'eleccion_tipo_id').annotate(votos_cnt=Sum('votos_cnt'),
                                                                                        electos_cnt=Count(Case(When(electo=1, then=1))))
                    if resultado.count() > 0:
                        eleccion['resultado'] = TotalesSerial(resultado, many=True).data[0]

                partido['elecciones'] = eleccionesSer
            
            pacto['partidos'] = partidosSer
        
        return Response(pactosSer)

class ComunaDetail(APIView):
    
    def get(self, request, id, format=None):
        comuna = Comuna.objects.get(pk=id)
        comunaSer = ComunaSerial(comuna, many=False).data
        
        elecciones = EleccionFecha.objects.all();
        eleccionesSer = EleccionSerial(elecciones, many=True).data
        
        for eleccion in eleccionesSer:
            eleccion['adultos_cnt'] = Poblacion.objects.filter(anno=eleccion['anno'], comuna_id=comunaSer['id']).aggregate(total=Sum('poblacion_adultos_cnt'))['total'];
            participacion = Participacion.objects.filter(anno=eleccion['anno'],
                                eleccion_tipo_id=eleccion['eleccion_tipo']['id'],
                                vuelta=eleccion['vuelta'],
                                comuna_id=comunaSer['id']).values().annotate(emitidos_cnt=Sum('emitidos_cnt'),
                                    validos_cnt=Sum('validos_cnt'),
                                    blancos_cnt=Sum('blancos_cnt'),
                                    nulos_cnt=Sum('nulos_cnt')).order_by('-anno')

            if participacion.count() > 0:
                eleccion['participacion'] = ParticipacionSerial(participacion, many=True).data[0]
            
            candidatos = Resultado.objects.filter(eleccion_tipo_id=eleccion['eleccion_tipo']['id'], comuna_id=id, anno=eleccion['anno']).order_by('-votos_cnt')
            eleccion['candidatos'] = ResultadoSerial(candidatos, many=True).data

        comunaSer['elecciones'] = eleccionesSer;
        return Response(comunaSer)
    
class ComunaList(APIView):
    def get(self, request, format=None):
        comunas = Comuna.objects.all()
        comunasSer = ComunaSerial(comunas, many=True)
        
        return Response(comunasSer.data)

class CandidatoDetail(APIView):
    def get(self, request, id, format=None):
        candidato = Candidato.objects.get(pk=id)
        candidatoSer = CandidatoSerial(candidato, many=False).data
        
        resultados = Resultado.objects.filter(candidato_id=id).order_by('-anno')
        resultadosSer = ResultadoSerial(resultados, many=True).data
        
        candidatoSer['elecciones'] = resultadosSer
        
        return Response(candidatoSer)

class CandidatoList(APIView):
    def get(self, request, format=None):
        candidatos = Candidato.objects.filter(~Q(nombres=None))
        candidatosSer = CandidatoSerial(candidatos, many=True)
        
        return Response(candidatosSer.data)

class ComunaRanking(APIView):
    def get(self, request, format=None):
        list = []
        
        cursor = connections['vote_db'].cursor()
        cursor.execute("SELECT r1.anno, r1.comuna_id, r1.id as id1, r2.id as id2, r2.votos_cnt/r1.votos_cnt as diff FROM resultado r1, resultado r2 WHERE r1.eleccion_tipo_id=5 AND r1.eleccion_tipo_id=r2.eleccion_tipo_id and r1.anno=r2.anno and r1.comuna_id=r2.comuna_id and r1.posicion=1 and r2.posicion=2 ORDER BY diff DESC LIMIT 20")
        rows = cursor.fetchall()
        for row in rows:
            anno = row[0]
            comuna = Comuna.objects.get(pk=row[1])
            resultado1 = Resultado.objects.get(pk=row[2])
            resultado2 = Resultado.objects.get(pk=row[3])
            poblacion = Poblacion.objects.filter(anno=anno, comuna_id=row[1]).aggregate(total=Sum('poblacion_adultos_cnt'))['total'];
            
            comunaSer = ComunaSerial(comuna, many=False).data
            resultadosSer1 = ResultadoSerial(resultado1, many=False).data
            resultadosSer2 = ResultadoSerial(resultado2, many=False).data
            resultado = [resultadosSer1, resultadosSer2]
            list.append({'poblacion': poblacion, 'comuna': comunaSer, 'resultados': resultado})
            
        
        elecciones = EleccionFecha.objects.filter(eleccion_tipo_id=5)
        eleccionesSer = EleccionSerial(elecciones, many=True).data
        
        for eleccion in eleccionesSer:
            comunas = []
            cursor.execute("SELECT c.comuna_id, emitidos_cnt, poblacion_adultos_cnt, emitidos_cnt / poblacion_adultos_cnt as diff from participacion p, poblacion c where p.anno=%s and p.anno=c.anno AND p.comuna_id=c.comuna_id and p.eleccion_tipo_id=5 ORDER BY diff LIMIT 10", [eleccion['anno']])
            rows = cursor.fetchall()
            for row in rows:
                comuna = Comuna.objects.get(pk=row[0])
                comunaSer = ComunaSerial(comuna, many=False).data
                comunaSer['emitidos_cnt'] = row[1]
                comunaSer['poblacion_adultos_cnt'] = row[2]
                comunaSer['participacion'] = row[3]
                comunas.append(comunaSer)
            
            eleccion['participaciones'] = comunas;
        
        return Response({'ranking_diferencia_votos': list, 'ranking_participacion': eleccionesSer})


