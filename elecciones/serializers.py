from rest_framework import serializers
from models import Comuna, Participacion, Resultado, Pacto, Candidato, EleccionFecha, EleccionTipo

class ComunaSerial(serializers.ModelSerializer):
    class Meta:
        model = Comuna
        fields = ('id', 'nombre')

class CandidatoSerial(serializers.ModelSerializer):
#    fullname = serializers.SerializerMethodField('getfullname')
#    def getfullname(self, candidato):
#        return candidato.nombres
    
    class Meta:
        model = Candidato
        fields = ('id', 'fullname')
        
class EleccionTipoSerial(serializers.ModelSerializer):
    class Meta:
        model = EleccionTipo
        fields = ('id', 'nombre') 

class EleccionSerial(serializers.ModelSerializer):
#    eleccion_tipo = serializers.SlugRelatedField(many=False, read_only=True, slug_field='nombre', allow_null=True)
#    adultos_cnt = serializers.IntegerField(required=False)
    eleccion_tipo = EleccionTipoSerial(many=False, read_only=True)
    
    class Meta:
        model = EleccionFecha
        fields = ('id', 'anno', 'vuelta', 'eleccion_tipo')       

class PactoSerial(serializers.ModelSerializer):
    votos_cnt = serializers.IntegerField(required=False)
    candidatos_cnt = serializers.IntegerField(required=False)
    electos_cnt = serializers.IntegerField(required=False)
    independientes_cnt = serializers.IntegerField(required=False)
    pacto_cnt = serializers.IntegerField(required=False)
    
    class Meta:
        model = Pacto
        fields = ('id', 'nombre', 'anno', 'votos_cnt', 'candidatos_cnt', 'electos_cnt', 'independientes_cnt', 'pacto_cnt')
        
class PartidoSerial(serializers.ModelSerializer):
    votos_cnt = serializers.IntegerField(required=False)
    electos_cnt = serializers.IntegerField(required=False)
    
    class Meta:
        model = Pacto
        fields = ('id', 'nombre', 'votos_cnt', 'electos_cnt')

class ParticipacionSerial(serializers.ModelSerializer):
#    comuna = serializers.SlugRelatedField(many=False, read_only=True, slug_field='external_id', allow_null=True)
    
    class Meta:
        model = Participacion
        fields = ('validos_cnt', 'emitidos_cnt', 'nulos_cnt', 'blancos_cnt')

class ResultadoSerial(serializers.ModelSerializer):
    candidato = serializers.SlugRelatedField(many=False, read_only=True, slug_field='fullname', allow_null=True, required=False)
    partido = serializers.SlugRelatedField(many=False, read_only=True, slug_field='siglas', allow_null=True, required=False)
    pacto = serializers.SlugRelatedField(many=False, read_only=True, slug_field='nombre', allow_null=True, required=False)
    comuna = serializers.SlugRelatedField(many=False, read_only=True, slug_field='nombre', allow_null=True, required=False)
    
    class Meta:
        model = Resultado
        fields = ('anno', 'comuna', 'candidato', 'partido', 'pacto', 'electo', 'votos_cnt', 'posicion')

class TotalesSerial(serializers.ModelSerializer):
    electos_cnt = serializers.IntegerField(required=False)
    
    class Meta:
        model = Resultado
        fields = ('anno', 'votos_cnt', 'electos_cnt')

