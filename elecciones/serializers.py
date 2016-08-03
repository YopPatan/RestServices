from rest_framework import serializers
from models import Comuna, Participacion, Resultado, Pacto, Candidato, EleccionFecha, EleccionTipo, Region, Partido, Pobreza, Delincuencia, Educacion, Poblacion, Salud, Desempleo, Ambiente

class RegionSerial(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ('id', 'nombre', 'numero')

class ComunaSerial(serializers.ModelSerializer):
    class Meta:
        model = Comuna
        fields = ('id', 'nombre')

class AmbienteSerial(serializers.ModelSerializer):
    comuna = ComunaSerial(many=False, read_only=True, required=False)
    
    class Meta:
        model = Ambiente
        fields = ('comuna', 'anno', 'metros_idx', 'imagen')


class CandidatoSerial(serializers.ModelSerializer):
    class Meta:
        model = Candidato
        fields = ('id', 'nombre_corto', 'nombre_completo', 'sexo')
        
class EleccionTipoSerial(serializers.ModelSerializer):
    class Meta:
        model = EleccionTipo
        fields = ('id', 'nombre') 

class EleccionSerial(serializers.ModelSerializer):
    eleccion_tipo = EleccionTipoSerial(many=False, read_only=True)
    
    class Meta:
        model = EleccionFecha
        fields = ('id', 'anno', 'vuelta', 'eleccion_tipo')       

class PactoSerial(serializers.ModelSerializer):
    class Meta:
        model = Pacto
        fields = ('id', 'nombre', 'anno', 'nombre_corto')
        
class PartidoSerial(serializers.ModelSerializer):
    class Meta:
        model = Partido
        fields = ('id', 'nombre', 'siglas')

class PobrezaSerial(serializers.ModelSerializer):
    comuna = ComunaSerial(many=False, read_only=True, required=False)
    class Meta:
        model = Pobreza
        fields = ('comuna', 'anno', 'poblacion_cnt', 'poblacion_idx')
        
class DesempleoSerial(serializers.ModelSerializer):
#    region = RegionSerial(many=False, read_only=True, required=False)
    class Meta:
        model = Desempleo
        fields = ('anno', 'poblacion_idx')

class EducacionSerial(serializers.ModelSerializer):
    comuna = ComunaSerial(many=False, read_only=True, required=False)
    
    class Meta:
        model = Educacion
        fields = ('comuna', 'establecimiento_id', 'establecimiento_txt', 'anno', 'colegios_cnt', 'psu_promedio', 'alumnos_cnt')

class SaludSerial(serializers.ModelSerializer):
#    comuna = ComunaSerial(many=False, read_only=True, required=False)
    
    class Meta:
        model = Salud
        fields = ('anno', 'emp_hombres_20_44', 'emp_mujeres_45_64', 'emp_adulto_mayor', 'control_embarazo_hasta_14_semanas', 'odontologia_hasta_20', 'ap_gestion_reclamos', 'cobertura_diabetes_sobre_15', 'cobertura_hta_sobre_15', 'cobertura_desarrollo_psicomotor_12_23_meses', 'visita_domiciliaria', 'cobertura_asma_y_epoc', 'cobertura_psiquiatrica_sobre_5')

class DelincuenciaSerial(serializers.ModelSerializer):
    class Meta:
        model = Delincuencia
        fields = ('anno', 'dmcs_denuncias', 'dmcs_detenciones' ,'vif_denuncias', 'vif_detenciones')
        
class PoblacionSerial(serializers.ModelSerializer):
    class Meta:
        model = Poblacion
        fields = ('anno', 'padron_cnt')


class ParticipacionSerial(serializers.ModelSerializer):
    class Meta:
        model = Participacion
        fields = ('validos_cnt', 'emitidos_cnt', 'nulos_cnt', 'blancos_cnt')

class ResultadoSerial(serializers.ModelSerializer):
    comuna = ComunaSerial(many=False, read_only=True, required=False)
    candidato = CandidatoSerial(many=False, read_only=True, required=False)
    pacto = PactoSerial(many=False, read_only=True, required=False)
    partido = PartidoSerial(many=False, read_only=True, required=False)
    eleccion_tipo = EleccionTipoSerial(many=False, read_only=True, required=False)
    
    class Meta:
        model = Resultado
        fields = ('anno', 'comuna', 'eleccion_tipo', 'candidato', 'partido', 'pacto', 'electo', 'votos_cnt', 'posicion')