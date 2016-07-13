from __future__ import unicode_literals

from django.db import models
from boto.dynamodb.condition import NULL

class Region(models.Model):
    nombre = models.CharField(max_length=255)
    numero = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'region'


class Comuna(models.Model):
    nombre = models.CharField(max_length=45, blank=True, null=True)
    region = models.ForeignKey('Region', models.DO_NOTHING, blank=True, null=True)
#    region_id = models.IntegerField(blank=True, null=True)
    distrito = models.IntegerField(blank=True, null=True)
    circunscripcion = models.IntegerField(blank=True, null=True)
#    external_id = models.CharField(max_length=45)

    class Meta:
        managed = False
        db_table = 'comuna'

class Candidato(models.Model):
    @property
    def fullname(self):
        if self.nombres == None:
            return None
        else:
            return (self.nombres.split(' ')[0] + ' ' + self.apellido_paterno).lower()
    
    nombres = models.CharField(max_length=45, blank=True, null=True)
    apellido_paterno = models.CharField(max_length=45, blank=True, null=True)
    apellido_materno = models.CharField(max_length=45, blank=True, null=True)
    #external_id = models.CharField(max_length=45, blank=True, null=True)
    #sexo = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'candidato'

class EleccionGrupo(models.Model):
    nombre = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'eleccion_grupo'

class EleccionTipo(models.Model):
    eleccion_grupo = models.ForeignKey(EleccionGrupo, models.DO_NOTHING)
    nombre = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'eleccion_tipo'

class EleccionFecha(models.Model):
    anno = models.IntegerField()
    eleccion_tipo = models.ForeignKey('EleccionTipo', models.DO_NOTHING)
    vuelta = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'eleccion_fecha'

class Pacto(models.Model):
    eleccion_grupo = models.ForeignKey(EleccionGrupo, models.DO_NOTHING)
    anno = models.IntegerField()
    nombre = models.CharField(max_length=45, blank=True, null=True)
    lista = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pacto'

class Partido(models.Model):
    nombre = models.CharField(max_length=45, blank=True, null=True)
    siglas = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'partido'

class Padron(models.Model):
    comuna = models.ForeignKey(Comuna, models.DO_NOTHING)
    anno = models.IntegerField()
    votantes_cnt = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'padron'

class Poblacion(models.Model):
    comuna = models.ForeignKey(Comuna, models.DO_NOTHING)
    anno = models.IntegerField(blank=True, null=True)
    poblacion_cnt = models.IntegerField(blank=True, null=True)
    poblacion_adultos_cnt = models.IntegerField(blank=True, null=True)
    hombres_cnt = models.IntegerField(blank=True, null=True)
    mujeres_cnt = models.IntegerField(blank=True, null=True)
    hombres_adultos_cnt = models.IntegerField(blank=True, null=True)
    mujeres_adultos_cnt = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'poblacion'


class Resultado(models.Model):
    comuna = models.ForeignKey(Comuna, models.DO_NOTHING, blank=True, null=True)
    eleccion_tipo = models.ForeignKey(EleccionTipo, models.DO_NOTHING, blank=True, null=True)
    anno = models.IntegerField(blank=True, null=True)
    candidato = models.ForeignKey(Candidato, models.DO_NOTHING, blank=True, null=True)
    partido = models.ForeignKey(Partido, models.DO_NOTHING, blank=True, null=True)
    pacto = models.ForeignKey(Pacto, models.DO_NOTHING, blank=True, null=True)
    pacto_txt = models.CharField(max_length=45, blank=True, null=True)
    electo = models.IntegerField(blank=True, null=True)
    votos_cnt = models.IntegerField(blank=True, null=True)
    posicion = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'resultado'


class Participacion(models.Model):
    eleccion_tipo = models.ForeignKey(EleccionTipo, models.DO_NOTHING)
    comuna = models.ForeignKey(Comuna, models.DO_NOTHING)
    anno = models.IntegerField()
    vuelta = models.IntegerField()
    validos_cnt = models.IntegerField(blank=True, null=True)
    emitidos_cnt = models.IntegerField(blank=True, null=True)
    nulos_cnt = models.IntegerField(blank=True, null=True)
    blancos_cnt = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'participacion'

