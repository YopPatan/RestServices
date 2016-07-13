from models import Region, Comuna, Participacion, Resultado, Poblacion, Pacto, Partido, Candidato, EleccionFecha, EleccionTipo, EleccionGrupo
from serializers import ComunaSerial, ParticipacionSerial, ResultadoSerial, PactoSerial, CandidatoSerial, PartidoSerial, EleccionSerial, RegionSerial, EleccionTipoSerial

#from django.db import connection
from django.db import connections

from django.db.models import Q, Count, Sum, Case, When
from rest_framework.views import APIView
from rest_framework.response import Response

class EleccionList(APIView):

    def get(self, request, format=None):
        cursor = connections['vote_db'].cursor()
        
        elecciones = EleccionFecha.objects.all()
        eleccionesSer = EleccionSerial(elecciones, many=True).data
        
        for eleccion in eleccionesSer:
            participacion = Participacion.objects.filter(anno=eleccion['anno'],
                                eleccion_tipo_id=eleccion['eleccion_tipo']['id'],
                                vuelta=eleccion['vuelta']).values('anno').annotate(emitidos_cnt=Sum('emitidos_cnt'),
                                    validos_cnt=Sum('validos_cnt'),
                                    blancos_cnt=Sum('blancos_cnt'),
                                    nulos_cnt=Sum('nulos_cnt')).order_by('-anno')

            if participacion.count() > 0:
                eleccion['participacion'] = ParticipacionSerial(participacion, many=True).data[0]

            eleccion['adultos_cnt'] = Poblacion.objects.filter(anno=eleccion['anno']).aggregate(total=Sum('poblacion_adultos_cnt'))['total'];
        
            cursor.execute("SELECT COUNT(CASE WHEN elecciones=1 THEN 1 END) as nuevos, COUNT(CASE WHEN elecciones>1 THEN 1 END) as historicos FROM (SELECT r.candidato_id, count(DISTINCT anno) as elecciones FROM resultado r, (SELECT candidato_id from resultado WHERE anno=%s AND eleccion_tipo_id=%s GROUP by candidato_id) as foo WHERE r.candidato_id=foo.candidato_id AND r.anno<=%s GROUP BY candidato_id) foo", [eleccion['anno'], eleccion['eleccion_tipo']['id'], eleccion['anno']])
            row = cursor.fetchone()
            eleccion['candidatos_nuevos_cnt'] = row[0]
            eleccion['candidatos_historicos_cnt'] = row[1]
            
        return Response(eleccionesSer)
    

class EleccionTipoDetail(APIView):
    def get(self, request, id, format=None):
        cursor = connections['vote_db'].cursor()
        
        tipo = EleccionTipo.objects.get(pk=id)
        tipoSer = EleccionTipoSerial(tipo, many=False).data
        
        elecciones = EleccionFecha.objects.filter(eleccion_tipo_id=id).order_by('-anno')
        eleccionesSer = EleccionSerial(elecciones, many=True).data
        for eleccion in eleccionesSer:
            pactos = Pacto.objects.filter(anno=eleccion['anno'])
            pactosSer = PactoSerial(pactos, many=True).data
            
            partidos = Partido.objects.filter(resultado__anno=eleccion['anno']).distinct()
            partidosSer = PartidoSerial(partidos, many=True).data
            
            for pacto in pactosSer:
                cursor.execute("SELECT count(DISTINCT candidato_id) as candidatos_cnt, count(DISTINCT candidato_id, CASE WHEN electo=1 THEN 1 END) AS electos_cnt, SUM(votos_cnt) as votos_cnt FROM resultado WHERE eleccion_tipo_id=%s AND pacto_id=%s", [id, pacto['id']])
                row = cursor.fetchone()
                pacto['candidatos_cnt'] = row[0]
                pacto['electos_cnt'] = row[1]
                pacto['votos_cnt'] = row[2]
            
            for partido in partidosSer:
                cursor.execute("SELECT count(DISTINCT candidato_id) as candidatos_cnt, count(DISTINCT candidato_id, CASE WHEN electo=1 THEN 1 END) AS electos_cnt, SUM(votos_cnt) as votos_cnt FROM resultado WHERE eleccion_tipo_id=%s AND partido_id=%s", [id, partido['id']])
                row = cursor.fetchone()
                partido['candidatos_cnt'] = row[0]
                partido['electos_cnt'] = row[1]
                partido['votos_cnt'] = row[2]
            
            eleccion['pactos'] = pactosSer
            eleccion['partidos'] = partidosSer
        
        tipoSer['elecciones'] = eleccionesSer
        
        return Response(tipoSer)

class ComunaDetail(APIView):
    
    def get(self, request, id, tipo_id, format=None):
        comuna = Comuna.objects.get(pk=id)
        comunaSer = ComunaSerial(comuna, many=False).data

        tipos = EleccionTipo.objects.filter(eleccion_grupo_id=tipo_id)

        for tipo in tipos:

            elecciones = EleccionFecha.objects.filter(eleccion_tipo_id=tipo.id).order_by('-anno');
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
    
            comunaSer[tipo.nombre.lower()] = eleccionesSer;
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
        
        municipales = Resultado.objects.filter(Q(candidato_id=id) & (Q(eleccion_tipo_id=4) | Q(eleccion_tipo_id=5))).order_by('-anno')
        municipalesSer = ResultadoSerial(municipales, many=True).data
        
        senadores = Resultado.objects.filter(candidato_id=id, eleccion_tipo_id=3).values('anno', 'eleccion_tipo_id', 'comuna__region_id', 'comuna__circunscripcion', 'posicion', 'electo', 'pacto_id', 'partido_id').annotate(comunas_cnt=Count(1), votos_cnt=Sum('votos_cnt'))
        senadoresSer= list(senadores)

        diputados = Resultado.objects.filter(candidato_id=id, eleccion_tipo_id=2).values('anno', 'eleccion_tipo_id', 'comuna__region_id', 'comuna__distrito', 'posicion', 'electo', 'pacto_id', 'partido_id').annotate(comunas_cnt=Count(1), votos_cnt=Sum('votos_cnt'))
        diputadosSer= list(diputados)
        
        parlamentarias = senadoresSer + diputadosSer
        
        for eleccion in parlamentarias:
            if eleccion['pacto_id'] != None:
                pacto = Pacto.objects.get(pk=eleccion['pacto_id'])
                eleccion['pacto'] = PactoSerial(pacto, many=False).data
            
            partido = Partido.objects.get(pk=eleccion['partido_id'])
            eleccion['partido'] = PartidoSerial(partido, many=False).data
            
            region = Region.objects.get(pk=eleccion['comuna__region_id'])
            eleccion['region'] = RegionSerial(region, many=False).data
        
        candidatoSer['elecciones'] = municipalesSer + parlamentarias
        
        return Response(candidatoSer)

#class CandidatoList(APIView):
#    def get(self, request, format=None):
#        candidatos = Candidato.objects.filter(~Q(nombres=None))
#        candidatosSer = CandidatoSerial(candidatos, many=True)
#        
#        return Response(candidatosSer.data)

class ComunaRanking(APIView):
    def get(self, request, format=None):
        cursor = connections['vote_db'].cursor()
        elecciones = EleccionFecha.objects.filter(eleccion_tipo_id=5)
        eleccionesSer = EleccionSerial(elecciones, many=True).data
        
        for eleccion in eleccionesSer:
            ranking_participacion = []
            ranking_diff_votos = []
            
            cursor.execute("SELECT c.comuna_id, emitidos_cnt, poblacion_adultos_cnt, emitidos_cnt / poblacion_adultos_cnt as diff from participacion p, poblacion c where p.anno=%s and p.anno=c.anno AND p.comuna_id=c.comuna_id and p.eleccion_tipo_id=5 ORDER BY diff LIMIT 10", [eleccion['anno']])
            rows = cursor.fetchall()
            for row in rows:
                comuna = Comuna.objects.get(pk=row[0])
                comunaSer = ComunaSerial(comuna, many=False).data
                comunaSer['emitidos_cnt'] = row[1]
                comunaSer['poblacion_adultos_cnt'] = row[2]
                comunaSer['participacion'] = row[3]
                ranking_participacion.append(comunaSer)
        
            cursor.execute("SELECT r1.comuna_id, r1.id as id1, r2.id as id2, r2.votos_cnt/r1.votos_cnt as diff FROM resultado r1, resultado r2 WHERE r1.anno=%s AND r1.eleccion_tipo_id=5 AND r1.eleccion_tipo_id=r2.eleccion_tipo_id and r1.anno=r2.anno and r1.comuna_id=r2.comuna_id and r1.posicion=1 and r2.posicion=2 ORDER BY diff DESC LIMIT 5", [eleccion['anno']])
            rows = cursor.fetchall()
            for row in rows:
                comuna = Comuna.objects.get(pk=row[0])
                resultado1 = Resultado.objects.get(pk=row[1])
                resultado2 = Resultado.objects.get(pk=row[2])
                poblacion = Poblacion.objects.filter(anno=eleccion['anno'], comuna_id=row[0]).aggregate(total=Sum('poblacion_adultos_cnt'))['total'];
                
                comunaSer = ComunaSerial(comuna, many=False).data
                resultadosSer1 = ResultadoSerial(resultado1, many=False).data
                resultadosSer2 = ResultadoSerial(resultado2, many=False).data
                resultado = [resultadosSer1, resultadosSer2]
                ranking_diff_votos.append({'poblacion': poblacion, 'comuna': comunaSer, 'resultados': resultado})
            
            eleccion['ranking_participacion'] = ranking_participacion;
            eleccion['ranking_diff_votos'] = ranking_diff_votos;
            
        return Response(eleccionesSer)


