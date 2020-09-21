from .validator import validate_past_date
from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField

class Especialidade(models.Model):
    nome = models.CharField(max_length=30, null=False, blank=False)

    def __str__(self):
        return self.nome


class Medico(models.Model):
    nome = models.CharField(max_length=30, null=False, blank=False)
    crm = models.IntegerField(null=False, blank=False)
    email = models.EmailField(max_length=75)
    telefone = models.CharField(max_length=11, null=True, blank=True)
    especialidade = models.ForeignKey(Especialidade, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome


class Agenda(models.Model):
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE, null=False, blank=False)
    dia = models.DateField(null=False, blank=False, 
                           validators=[validate_past_date])
    horarios = ArrayField(models.TimeField(blank=False, null=False), 
                          blank=False, null=False)

    class Meta:
        unique_together = (("medico", "dia"),)

    def __str__(self):
        return f"{self.medico} - {str(self.dia)}"


class Consulta(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    agenda = models.ForeignKey(Agenda, on_delete=models.CASCADE)
    horario = models.TimeField(blank=False, null=False)
    data_agendamento = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("agenda", "horario"),)

    def __str__(self):
        return f"{self.agenda.medico} - {str(self.agenda.dia)}-{str(self.horario)}"
