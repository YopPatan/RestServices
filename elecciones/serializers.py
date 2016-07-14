from rest_framework import serializers
from models import Comuna, Participacion, Resultado, Pacto, Candidato, EleccionFecha, EleccionTipo, Region, Partido

class RegionSerial(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ('id', 'nombre', 'numero')

class ComunaSerial(serializers.ModelSerializer):
    class Meta:
        model = Comuna
        fields = ('id', 'nombre', 'region')

class CandidatoSerial(serializers.ModelSerializer):
#    fullname = serializers.SerializerMethodField('getfullname')
#    def getfullname(self, candidato):
#        return candidato.nombres
    
    class Meta:
        model = Candidato
        fields = ('id', 'nombre_corto', 'nombre_completo')
        
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
    class Meta:
        model = Pacto
        fields = ('id', 'nombre', 'anno')
        
class PartidoSerial(serializers.ModelSerializer):
    class Meta:
        model = Partido
        fields = ('id', 'nombre', 'siglas')

class ParticipacionSerial(serializers.ModelSerializer):
#    comuna = serializers.SlugRelatedField(many=False, read_only=True, slug_field='external_id', allow_null=True)
    
    class Meta:
        model = Participacion
        fields = ('validos_cnt', 'emitidos_cnt', 'nulos_cnt', 'blancos_cnt')

class ResultadoSerial(serializers.ModelSerializer):
    #candidato = serializers.SlugRelatedField(many=False, read_only=True, slug_field='fullname', allow_null=True, required=False)
    #partido = serializers.SlugRelatedField(many=False, read_only=True, slug_field='siglas', allow_null=True, required=False)
    #pacto = serializers.SlugRelatedField(many=False, read_only=True, slug_field='nombre', allow_null=True, required=False)
    #comuna = serializers.SlugRelatedField(many=False, read_only=True, slug_field='nombre', allow_null=True, required=False)
    comuna = ComunaSerial(many=False, read_only=True, required=False)
    candidato = CandidatoSerial(many=False, read_only=True, required=False)
    pacto = PactoSerial(many=False, read_only=True, required=False)
    partido = PartidoSerial(many=False, read_only=True, required=False)
    
    class Meta:
        model = Resultado
        fields = ('anno', 'comuna', 'candidato', 'partido', 'pacto', 'electo', 'votos_cnt', 'posicion')

#class TotalesSerial(serializers.ModelSerializer):
#    electos_cnt = serializers.IntegerField(required=False)
#    
#    class Meta:
#        model = Resultado
#        fields = ('anno', 'votos_cnt', 'electos_cnt')

