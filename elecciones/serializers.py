from rest_framework import serializers
from models import Comuna, Voto, Resultado, Pacto

class ComunaSerial(serializers.ModelSerializer):
    class Meta:
        model = Comuna
        fields = ('id', 'external_id')

class PactoSerial(serializers.ModelSerializer):
    votos_cnt = serializers.IntegerField(required=False)
    electos_cnt = serializers.IntegerField(required=False)
    independientes_cnt = serializers.IntegerField(required=False)
    pacto_cnt = serializers.IntegerField(required=False)
    
    class Meta:
        model = Pacto
        fields = ('id', 'nombre', 'anno', 'votos_cnt', 'electos_cnt', 'independientes_cnt', 'pacto_cnt')

class VotoSerial(serializers.ModelSerializer):
#    comuna = serializers.SlugRelatedField(many=False, read_only=True, slug_field='external_id', allow_null=True)
    
    class Meta:
        model = Voto
        fields = ('id', 'anno', 'validos_cnt', 'emitidos_cnt', 'nulos_cnt', 'blancos_cnt')

class ResultadoSerial(serializers.ModelSerializer):
    candidato = serializers.SlugRelatedField(many=False, read_only=True, slug_field='external_id', allow_null=True)
    partido = serializers.SlugRelatedField(many=False, read_only=True, slug_field='siglas', allow_null=True)
    pacto = serializers.SlugRelatedField(many=False, read_only=True, slug_field='nombre', allow_null=True)
    
    class Meta:
        model = Resultado
        fields = ('id', 'candidato', 'partido', 'pacto', 'electo', 'votos_cnt')



