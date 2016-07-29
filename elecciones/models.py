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
    def nombre_corto(self):
        if self.nombres == None:
            return None
        else:
            return (self.nombres.split(' ')[0] + ' ' + self.apellido_paterno)

    @property
    def nombre_completo(self):
        if self.nombres == None:
            return None
        else:
            return (self.nombres + ' ' + self.apellido_paterno + ' ' + self.apellido_materno)
    
    nombres = models.CharField(max_length=45, blank=True, null=True)
    apellido_paterno = models.CharField(max_length=45, blank=True, null=True)
    apellido_materno = models.CharField(max_length=45, blank=True, null=True)
    #external_id = models.CharField(max_length=45, blank=True, null=True)
    sexo = models.CharField(max_length=45, blank=True, null=True)

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
    @property
    def nombre_corto(self):
        if len(self.nombre) > 30:
            return self.nombre[:26] + "..."
        else:
            return self.nombre
    
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

class Poblacion(models.Model):
    comuna = models.ForeignKey(Comuna, models.DO_NOTHING)
    anno = models.IntegerField(blank=True, null=True)
#    poblacion_cnt = models.IntegerField(blank=True, null=True)
    poblacion_adultos_cnt = models.IntegerField(blank=True, null=True)
    padron_cnt = models.IntegerField(blank=True, null=True)
#    hombres_cnt = models.IntegerField(blank=True, null=True)
#    mujeres_cnt = models.IntegerField(blank=True, null=True)
#    hombres_adultos_cnt = models.IntegerField(blank=True, null=True)
#    mujeres_adultos_cnt = models.IntegerField(blank=True, null=True)

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

class Pobreza(models.Model):
#    id = models.AutoField(unique=True)
    comuna = models.ForeignKey(Comuna, models.DO_NOTHING)
    poblacion_cnt = models.IntegerField()
    poblacion_idx = models.FloatField()
    anno = models.IntegerField()
    limite_inferior_idx = models.FloatField()
    limite_superior_idx = models.FloatField()

    class Meta:
        managed = False
        db_table = 'pobreza'

class Educacion(models.Model):
#    id = models.AutoField(unique=True)
    comuna = models.ForeignKey(Comuna, models.DO_NOTHING)
    establecimiento_id = models.IntegerField()
    establecimiento_txt = models.CharField(max_length=45, blank=True, null=True)
    anno = models.IntegerField()
    colegios_cnt = models.IntegerField()
    psu_promedio = models.FloatField()
    alumnos_cnt = models.IntegerField()
    psu_desviacion = models.FloatField()

    class Meta:
        managed = False
        db_table = 'educacion'

class Delincuencia(models.Model):
#    id = models.AutoField(unique=True)
    comuna = models.ForeignKey(Comuna, models.DO_NOTHING)
    anno = models.IntegerField()
    dmcs_denuncias = models.IntegerField()
    dmcs_detenciones = models.IntegerField()
    vif_denuncias = models.IntegerField()
    vif_detenciones = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'delincuencia'
        
class Salud(models.Model):
#    comuna_txt = models.TextField(blank=True, null=True)
    comuna_id = models.IntegerField(blank=True, null=True)
    anno = models.IntegerField(blank=True, null=True)
    emp_hombres_20_44 = models.FloatField(blank=True, null=True)
    emp_mujeres_45_64 = models.FloatField(blank=True, null=True)
    emp_adulto_mayor = models.FloatField(blank=True, null=True)
    control_embarazo_hasta_14_semanas = models.FloatField(blank=True, null=True)
    odontologia_hasta_20 = models.FloatField(blank=True, null=True)
    ap_gestion_reclamos = models.FloatField(blank=True, null=True)
    cobertura_diabetes_sobre_15 = models.FloatField(blank=True, null=True)
    cobertura_hta_sobre_15 = models.FloatField(blank=True, null=True)
    cobertura_desarrollo_psicomotor_12_23_meses = models.FloatField(blank=True, null=True)
    visita_domiciliaria = models.FloatField(blank=True, null=True)
    cobertura_asma_y_epoc = models.FloatField(blank=True, null=True)
    cobertura_psiquiatrica_sobre_5 = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'salud'




