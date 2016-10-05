from models import Region, Comuna, Participacion, Resultado, Poblacion, Pacto, Partido, Candidato, EleccionFecha, EleccionTipo, EleccionGrupo, Educacion, Delincuencia, Pobreza, Salud, Desempleo, Ambiente, Representante
from serializers import ComunaSerial, ParticipacionSerial, ResultadoSerial, PactoSerial, CandidatoSerial, PartidoSerial, EleccionSerial, RegionSerial, EleccionTipoSerial, EducacionSerial, DelincuenciaSerial, PobrezaSerial, PoblacionSerial, SaludSerial, DesempleoSerial, AmbienteSerial, EleccionGrupoSerial, RepresentanteSerial, ComunaFullSerial
#from django.db import connection
from django.db import connections

from django.db.models import Q, Count, Sum, Case, When, Max, Min
from rest_framework.views import APIView
from rest_framework.response import Response
import numpy as np

import json
import requests
import os

class GenerateJson(APIView):
    def get(self, request, format=None):

        elecciones_rest = requests.get('http://127.0.0.1:8000/elecciones/eleccion/?format=json')
        elecciones_json = elecciones_rest.json()
        elecciones_str = json.dumps(elecciones_json)
        f = open('elecciones/json/elecciones.json', 'w')
        f.write(elecciones_str)
        f.close()
        
        municipales_rest = requests.get('http://127.0.0.1:8000/elecciones/tipo/5?format=json')
        municipales_json = municipales_rest.json()
        municipales_str = json.dumps(municipales_json)
        f = open('elecciones/json/municipales.json', 'w')
        f.write(municipales_str)
        f.close()
        
        ranking_rest = requests.get('http://127.0.0.1:8000/elecciones/comuna/ranking/tipo/5?format=json')
        ranking_json = ranking_rest.json()
        ranking_str = json.dumps(ranking_json)
        f = open('elecciones/json/ranking.json', 'w')
        f.write(ranking_str)
        f.close()
        
        candidatos_rest = requests.get('http://127.0.0.1:8000/elecciones/candidato/?format=json')
        candidatos_json = candidatos_rest.json()
        candidatos_str = json.dumps(candidatos_json)
        f = open('elecciones/json/candidatos.json', 'w')
        f.write(candidatos_str)
        f.close()
        
        for candidato in candidatos_json:
            candidato_rest = requests.get('http://127.0.0.1:8000/elecciones/candidato/' + str(candidato['candidato']['id']) + '?format=json')
            candidato_json = candidato_rest.json()
            candidato_str = json.dumps(candidato_json)
            fc = open('elecciones/json/candidato_' + str(candidato['candidato']['id']) + '.json', 'w')
            fc.write(candidato_str)
            fc.close()

        
        comunas_rest = requests.get('http://127.0.0.1:8000/elecciones/comuna/?format=json')
        comunas_json = comunas_rest.json()
        comunas_str = json.dumps(comunas_json)
        f = open('elecciones/json/comunas.json', 'w')
        f.write(comunas_str)
        f.close()
        
        for comuna in comunas_json:
            if comuna['id'] == 0:
                continue
            #print 'http://127.0.0.1:8000/elecciones/comuna/' + str(comuna['id']) + '/tipo/3?format=json'
            comuna_rest = requests.get('http://127.0.0.1:8000/elecciones/comuna/' + str(comuna['id']) + '/tipo/3?format=json')
            comuna_json = comuna_rest.json()
            comuna_str = json.dumps(comuna_json)
            fc = open('elecciones/json/comuna_' + str(comuna['id']) + '.json', 'w')
            fc.write(comuna_str)
            fc.close()
        
        return Response(os.getcwd())

class EleccionList(APIView):

    def get(self, request, format=None):
        cursor = connections['vote_db'].cursor()
        
        elecciones = EleccionFecha.objects.all()
        eleccionesSer = EleccionSerial(elecciones, many=True).data
        
        for eleccion in eleccionesSer:
            grupo = EleccionTipo.objects.get(pk=eleccion['eleccion_tipo']['id']).eleccion_grupo
            eleccion['eleccion_grupo'] = EleccionGrupoSerial(grupo, many=False).data
            
            participacion = Participacion.objects.filter(anno=eleccion['anno'],
                                eleccion_tipo_id=eleccion['eleccion_tipo']['id'],
                                vuelta=eleccion['vuelta']).values('anno').annotate(emitidos_cnt=Sum('emitidos_cnt'),
                                    validos_cnt=Sum('validos_cnt'),
                                    blancos_cnt=Sum('blancos_cnt'),
                                    nulos_cnt=Sum('nulos_cnt')).order_by('-anno')

            if participacion.count() > 0:
                eleccion['participacion'] = ParticipacionSerial(participacion, many=True).data[0]

            eleccion['poblacion_adultos_cnt'] = Poblacion.objects.filter(anno=eleccion['anno']).aggregate(total=Sum('padron_cnt'))['total'];
        
            cursor.execute("SELECT COUNT(CASE WHEN elecciones=1 THEN 1 END) as nuevos, COUNT(CASE WHEN elecciones>1 THEN 1 END) as historicos FROM (SELECT r.candidato_id, count(DISTINCT anno) as elecciones FROM resultado r, (SELECT candidato_id from resultado WHERE anno=%s AND eleccion_tipo_id=%s GROUP by candidato_id) as foo WHERE r.candidato_id=foo.candidato_id AND r.anno<=%s GROUP BY candidato_id) foo", [eleccion['anno'], eleccion['eleccion_tipo']['id'], eleccion['anno']])
            row = cursor.fetchone()
            eleccion['candidatos_nuevos_cnt'] = row[0]
            eleccion['candidatos_historicos_cnt'] = row[1]
            
            cursor.execute("SELECT COUNT(DISTINCT c.id, CASE WHEN sexo='HOMBRE' THEN 1 END) AS candidatos_hombres_cnt, COUNT(DISTINCT c.id, CASE WHEN sexo='MUJER' THEN 1 END) AS candidatos_mujeres_cnt FROM resultado r, candidato c WHERE r.candidato_id=c.id AND r.anno=%s AND r.eleccion_tipo_id=%s", [eleccion['anno'], eleccion['eleccion_tipo']['id']])
            row = cursor.fetchone()
            eleccion['candidatos_hombres_cnt'] = row[0]
            eleccion['candidatos_mujeres_cnt'] = row[1]
            
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
                cursor.execute("SELECT count(DISTINCT candidato_id) as candidatos_cnt, count(DISTINCT candidato_id, CASE WHEN electo=1 THEN 1 END) AS electos_cnt, SUM(votos_cnt) as votos_cnt FROM resultado WHERE eleccion_tipo_id=%s AND partido_id=%s AND anno=%s", [id, partido['id'], eleccion['anno']])
                row = cursor.fetchone()
                partido['candidatos_cnt'] = row[0]
                partido['electos_cnt'] = row[1]
                partido['votos_cnt'] = row[2]
            
            eleccion['pactos'] = pactosSer
            eleccion['partidos'] = partidosSer
            
            cursor.execute("SELECT COUNT(CASE WHEN elecciones=1 THEN 1 END) as nuevos, COUNT(CASE WHEN elecciones>1 THEN 1 END) as historicos FROM (SELECT r.candidato_id, count(DISTINCT anno) as elecciones FROM resultado r, (SELECT candidato_id from resultado WHERE anno=%s AND eleccion_tipo_id=%s GROUP by candidato_id) as foo WHERE r.candidato_id=foo.candidato_id AND r.anno<=%s GROUP BY candidato_id) foo", [eleccion['anno'], eleccion['eleccion_tipo']['id'], eleccion['anno']])
            row = cursor.fetchone()
            eleccion['candidatos_nuevos_cnt'] = row[0]
            eleccion['candidatos_historicos_cnt'] = row[1]

            cursor.execute("SELECT COUNT(DISTINCT c.id, CASE WHEN sexo='HOMBRE' THEN 1 END) AS candidatos_hombres_cnt, COUNT(DISTINCT c.id, CASE WHEN sexo='MUJER' THEN 1 END) AS candidatos_mujeres_cnt FROM resultado r, candidato c WHERE r.candidato_id=c.id AND r.anno=%s AND r.eleccion_tipo_id=%s", [eleccion['anno'], eleccion['eleccion_tipo']['id']])
            row = cursor.fetchone()
            eleccion['candidatos_hombres_cnt'] = row[0]
            eleccion['candidatos_mujeres_cnt'] = row[1]

        
        tipoSer['elecciones'] = eleccionesSer
        
        return Response(tipoSer)

class ComunaDetail(APIView):
    
    def get(self, request, id, tipo_id, format=None):
        cursor = connections['vote_db'].cursor()
        
        comuna = Comuna.objects.get(pk=id)
        comunaSer = ComunaFullSerial(comuna, many=False).data
        
#        region = Region.objects.get(pk=comuna.region.id)
#        regionSer = RegionSerial(region, many=False).data
#        comunaSer['region'] = regionSer

        delincuencia = Delincuencia.objects.filter(comuna_id=id)
        delincuenciaSer = DelincuenciaSerial(delincuencia, many=True).data
        comunaSer['delincuencia'] = delincuenciaSer

        educacion = Educacion.objects.filter(comuna_id=id)
        educacionSer = EducacionSerial(educacion, many=True).data
        comunaSer['educacion'] = educacionSer
               
        pobreza = Pobreza.objects.filter(comuna_id=id)
        pobrezaSer = PobrezaSerial(pobreza, many=True).data
        comunaSer['pobreza'] = pobrezaSer

        salud = Salud.objects.filter(comuna_id=id)
        saludSer = SaludSerial(salud, many=True).data
        comunaSer['salud'] = saludSer
        
        ambiente = Ambiente.objects.filter(comuna_id=id)
        ambienteSer = AmbienteSerial(ambiente, many=True).data
        comunaSer['ambiente'] = ambienteSer
        
        educacionLimit = Educacion.objects.filter(establecimiento_id=1).aggregate(Min('psu_promedio'), Max('psu_promedio'));
        educacionExt = Educacion.objects.filter(Q(psu_promedio=educacionLimit['psu_promedio__min']) | Q(psu_promedio=educacionLimit['psu_promedio__max'])).order_by('psu_promedio')
        educacionExtSer = EducacionSerial(educacionExt, many=True).data

        pobrezaLimit = Pobreza.objects.aggregate(Min('poblacion_idx'), Max('poblacion_idx'));
        pobrezaExt = Pobreza.objects.filter(Q(poblacion_idx=pobrezaLimit['poblacion_idx__min']) | Q(poblacion_idx=pobrezaLimit['poblacion_idx__max'])).order_by('poblacion_idx')
        pobrezaExtSer = PobrezaSerial(pobrezaExt, many=True).data

        ambienteLimit = Ambiente.objects.aggregate(Min('metros_idx'), Max('metros_idx'));
        ambienteExt = Ambiente.objects.filter(Q(metros_idx=ambienteLimit['metros_idx__min']) | Q(metros_idx=ambienteLimit['metros_idx__max'])).order_by('metros_idx')
        ambienteExtSer = AmbienteSerial(ambienteExt, many=True).data

        comunaSer['extremos'] = {}
        comunaSer['extremos']['educacion'] = educacionExtSer
        comunaSer['extremos']['pobreza'] = pobrezaExtSer
        comunaSer['extremos']['ambiente'] = ambienteExtSer

        desempleo = Desempleo.objects.filter(region_id=comuna.region.id)
        desempleoSer = DesempleoSerial(desempleo, many=True).data
        comunaSer['desempleo'] = desempleoSer
        
#        poblacion = Poblacion.objects.filter(comuna_id=id)
#        poblacionSer = PoblacionSerial(poblacion, many=True).data
#        comunaSer['poblacion'] = poblacionSer

        comunaSer['poblacion_adultos_cnt'] = Poblacion.objects.filter(anno=2016, comuna_id=comunaSer['id']).aggregate(total=Sum('padron_cnt'))['total'];
        comunaSer['poblacion_adultos_idx'] = (comunaSer['poblacion_adultos_cnt'] * 100.0) / Poblacion.objects.filter(anno=2016).aggregate(total=Sum('padron_cnt'))['total'];
        
        representantes = Representante.objects.filter(comuna_id=id)
        representantesSer = RepresentanteSerial(representantes, many=True).data
        comunaSer['candidatos_alcalde'] = representantesSer

        votos_concejales = []
        cursor.execute("SELECT pacto_id, p.nombre, SUM(votos_cnt) as votos_total FROM resultado r, pacto p WHERE p.id=r.pacto_id and r.comuna_id=%s and r.anno=2012 and r.eleccion_tipo_id=4 group by r.pacto_id ORDER BY votos_total DESC", [id])
        rows = cursor.fetchall()
        for row in rows:
#            comuna = Comuna.objects.get(pk=row[0])
#            comunaSer = ComunaSerial(comuna, many=False).data
            pacto = {"pacto_id": row[0], "nombre": row[1], "votos_cnt": row[2]}
#            comunaSer['emitidos_cnt'] = row[1]
#            comunaSer['poblacion_adultos_cnt'] = row[2]
#            comunaSer['participacion'] = row[3]
            votos_concejales.append(pacto)
        comunaSer['votos_pacto'] = votos_concejales

        tipos = EleccionTipo.objects.filter(eleccion_grupo_id=tipo_id)
        
        for tipo in tipos:
            
            min_anno = Participacion.objects.filter(comuna_id=id, eleccion_tipo_id=tipo.id).aggregate(Min('anno'))
            print min_anno

            if min_anno['anno__min'] == None:
                continue
            
            elecciones = EleccionFecha.objects.filter(eleccion_tipo_id=tipo.id, anno__gte=min_anno['anno__min']).order_by('-anno');
            eleccionesSer = EleccionSerial(elecciones, many=True).data
            
            for eleccion in eleccionesSer:
                eleccion['poblacion_adultos_cnt'] = Poblacion.objects.filter(anno=eleccion['anno'], comuna_id=comunaSer['id']).aggregate(total=Sum('padron_cnt'))['total'];
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
        comunas = Comuna.objects.filter(~Q(id = 0) & ~Q(id = 512))
        comunasSer = ComunaFullSerial(comunas, many=True)
        
        return Response(comunasSer.data)

class CandidatoDetail(APIView):
    def get(self, request, id, format=None):
        candidato = Candidato.objects.get(pk=id)
        candidatoSer = CandidatoSerial(candidato, many=False).data
        
        representantes = Representante.objects.filter(candidato_id=id)
        representantesSer = RepresentanteSerial(representantes[0], many=False).data
        candidatoSer['actual'] = representantesSer
        
        municipales = Resultado.objects.filter(Q(candidato_id=id) & (Q(eleccion_tipo_id=4) | Q(eleccion_tipo_id=5))).order_by('-anno')
        municipalesSer = ResultadoSerial(municipales, many=True).data
        
        senadores = Resultado.objects.filter(candidato_id=id, eleccion_tipo_id=3).values('anno', 'eleccion_tipo_id', 'comuna__region_id', 'comuna__circunscripcion', 'posicion', 'electo', 'pacto_id', 'partido_id').annotate(comunas_cnt=Count(1), votos_cnt=Sum('votos_cnt'))
        senadoresSer= list(senadores)

        diputados = Resultado.objects.filter(candidato_id=id, eleccion_tipo_id=2).values('anno', 'eleccion_tipo_id', 'comuna__region_id', 'comuna__distrito', 'posicion', 'electo', 'pacto_id', 'partido_id').annotate(comunas_cnt=Count(1), votos_cnt=Sum('votos_cnt'))
        diputadosSer= list(diputados)

        presidentes = Resultado.objects.filter(candidato_id=id, eleccion_tipo_id=1).values('anno', 'eleccion_tipo_id', 'posicion', 'electo', 'pacto_id', 'partido_id').annotate(comunas_cnt=Count(1), votos_cnt=Sum('votos_cnt'))
        presidentesSer= list(presidentes)
        
        parlamentarias = senadoresSer + diputadosSer + presidentesSer
        
        grupo = EleccionGrupo.objects.get(pk=3)
        #print grupo.id
        
        for eleccion in municipalesSer:
            #grupo = EleccionGrupo.objects.get(pk=tipo.grupo.id)
            eleccion['eleccion_grupo'] = EleccionGrupoSerial(grupo, many=False).data
        
        for eleccion in parlamentarias:
            if eleccion['pacto_id'] != None:
                pacto = Pacto.objects.get(pk=eleccion['pacto_id'])
                eleccion['pacto'] = PactoSerial(pacto, many=False).data
            
            partido = Partido.objects.get(pk=eleccion['partido_id'])
            eleccion['partido'] = PartidoSerial(partido, many=False).data
            
            if eleccion['eleccion_tipo_id'] == 1:
                eleccion['region'] = {}
                eleccion['region']['nombre'] = "Nacional";
            else:
                region = Region.objects.get(pk=eleccion['comuna__region_id'])
                eleccion['region'] = RegionSerial(region, many=False).data
            
            tipo = EleccionTipo.objects.get(pk=eleccion['eleccion_tipo_id'])
            eleccion['eleccion_tipo'] = EleccionTipoSerial(tipo, many=False).data
            
            #print tipo.eleccion_grupo_id

            grupo = EleccionGrupo.objects.get(pk=tipo.eleccion_grupo_id)
            eleccion['eleccion_grupo'] = EleccionGrupoSerial(grupo, many=False).data
        
        candidatoSer['elecciones'] = municipalesSer + parlamentarias
        
        return Response(candidatoSer)

class CandidatoList(APIView):
    def get(self, request, format=None):
        representantes = Representante.objects.all()
        representantesSer = RepresentanteSerial(representantes, many=True).data
        #candidatos = Candidato.objects.filter(resultado__eleccion_tipo_id=5, resultado__anno=2012)
        #candidatos = Candidato.objects.all()
        #candidatosSer = CandidatoSerial(candidatos, many=True)
        
        return Response(representantesSer)

class ComunaRanking(APIView):
    def get(self, request, tipo_id, format=None):
        cursor = connections['vote_db'].cursor()
        elecciones = EleccionFecha.objects.filter(eleccion_tipo_id=tipo_id)
        eleccionesSer = EleccionSerial(elecciones, many=True).data
        
        for eleccion in eleccionesSer:
            ranking_menor_participacion_regiones = []
            ranking_menor_participacion_rm = []
            ranking_mayor_participacion_regiones = []
            ranking_mayor_participacion_rm = []
            ranking_diff_votos = []
            
            cursor.execute("SELECT po.comuna_id, emitidos_cnt, padron_cnt, emitidos_cnt / padron_cnt as diff from participacion p, poblacion po, comuna c where c.id=p.comuna_id AND p.anno=%s and p.anno=po.anno AND p.comuna_id=po.comuna_id AND c.region_id!=13 AND p.eleccion_tipo_id=5 AND padron_cnt>100000 ORDER BY diff LIMIT 5", [eleccion['anno']])
            rows = cursor.fetchall()
            for row in rows:
                comuna = Comuna.objects.get(pk=row[0])
                comunaSer = ComunaSerial(comuna, many=False).data
                comunaSer['emitidos_cnt'] = row[1]
                comunaSer['poblacion_adultos_cnt'] = row[2]
                comunaSer['participacion'] = row[3]
                ranking_menor_participacion_regiones.append(comunaSer)

            cursor.execute("SELECT po.comuna_id, emitidos_cnt, padron_cnt, emitidos_cnt / padron_cnt as diff from participacion p, poblacion po, comuna c where c.id=p.comuna_id AND p.anno=%s and p.anno=po.anno AND p.comuna_id=po.comuna_id AND c.region_id=13 AND p.eleccion_tipo_id=5 AND padron_cnt>100000 ORDER BY diff LIMIT 5", [eleccion['anno']])
            rows = cursor.fetchall()
            for row in rows:
                comuna = Comuna.objects.get(pk=row[0])
                comunaSer = ComunaSerial(comuna, many=False).data
                comunaSer['emitidos_cnt'] = row[1]
                comunaSer['poblacion_adultos_cnt'] = row[2]
                comunaSer['participacion'] = row[3]
                ranking_menor_participacion_rm.append(comunaSer)

            cursor.execute("SELECT po.comuna_id, emitidos_cnt, padron_cnt, emitidos_cnt / padron_cnt as diff from participacion p, poblacion po, comuna c where c.id=p.comuna_id AND p.anno=%s and p.anno=po.anno AND p.comuna_id=po.comuna_id AND c.region_id!=13 AND p.eleccion_tipo_id=5 AND padron_cnt>100000 ORDER BY diff DESC LIMIT 5", [eleccion['anno']])
            rows = cursor.fetchall()
            for row in rows:
                comuna = Comuna.objects.get(pk=row[0])
                comunaSer = ComunaSerial(comuna, many=False).data
                comunaSer['emitidos_cnt'] = row[1]
                comunaSer['poblacion_adultos_cnt'] = row[2]
                comunaSer['participacion'] = row[3]
                ranking_mayor_participacion_regiones.append(comunaSer)

            cursor.execute("SELECT po.comuna_id, emitidos_cnt, padron_cnt, emitidos_cnt / padron_cnt as diff from participacion p, poblacion po, comuna c where c.id=p.comuna_id AND p.anno=%s and p.anno=po.anno AND p.comuna_id=po.comuna_id AND c.region_id=13 AND p.eleccion_tipo_id=5 AND padron_cnt>100000 ORDER BY diff DESC LIMIT 5", [eleccion['anno']])
            rows = cursor.fetchall()
            for row in rows:
                comuna = Comuna.objects.get(pk=row[0])
                comunaSer = ComunaSerial(comuna, many=False).data
                comunaSer['emitidos_cnt'] = row[1]
                comunaSer['poblacion_adultos_cnt'] = row[2]
                comunaSer['participacion'] = row[3]
                ranking_mayor_participacion_rm.append(comunaSer)
        
            cursor.execute("SELECT r1.comuna_id, r1.id as id1, r2.id as id2, r2.votos_cnt/r1.votos_cnt as diff, r1.votos_cnt * 100 / p.validos_cnt as votos_idx1, r2.votos_cnt * 100 / p.validos_cnt as votos_idx1 FROM resultado r1, resultado r2, participacion p WHERE p.anno=r1.anno and p.comuna_id=r1.comuna_id and p.eleccion_tipo_id=r1.eleccion_tipo_id and r1.anno=%s AND r1.eleccion_tipo_id=5 AND r1.eleccion_tipo_id=r2.eleccion_tipo_id and r1.anno=r2.anno and r1.comuna_id=r2.comuna_id and r1.posicion=1 and r2.posicion=2 ORDER BY diff DESC LIMIT 5", [eleccion['anno']])
            rows = cursor.fetchall()
            for row in rows:
                comuna = Comuna.objects.get(pk=row[0])
                resultado1 = Resultado.objects.get(pk=row[1])
                resultado2 = Resultado.objects.get(pk=row[2])
                poblacion = Poblacion.objects.filter(anno=eleccion['anno'], comuna_id=row[0]).aggregate(total=Sum('padron_cnt'))['total'];
                
                comunaSer = ComunaSerial(comuna, many=False).data
                resultadosSer1 = ResultadoSerial(resultado1, many=False).data
                resultadosSer1['votos_idx'] = row[4]
                resultadosSer2 = ResultadoSerial(resultado2, many=False).data
                resultadosSer2['votos_idx'] = row[5]
                resultado = [resultadosSer1, resultadosSer2]
                ranking_diff_votos.append({'poblacion': poblacion, 'comuna': comunaSer, 'resultados': resultado})
            
            eleccion['ranking_menor_participacion'] = {}
            eleccion['ranking_menor_participacion']['regiones'] = ranking_menor_participacion_regiones;
            eleccion['ranking_menor_participacion']['rm'] = ranking_menor_participacion_rm;
            
            eleccion['ranking_mayor_participacion'] = {}
            eleccion['ranking_mayor_participacion']['regiones'] = ranking_mayor_participacion_regiones;
            eleccion['ranking_mayor_participacion']['rm'] = ranking_mayor_participacion_rm;
            
            eleccion['ranking_diff_votos'] = ranking_diff_votos;
            
        return Response(eleccionesSer)


