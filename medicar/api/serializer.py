from rest_framework import exceptions
from rest_framework import serializers

from .models import Especialidade, Medico, Agenda, Consulta


class SpecialtySerializer(serializers.ModelSerializer):

    class Meta:
        model = Especialidade
        fields = '__all__'


class MedicSerializer(serializers.ModelSerializer):
    especialidade = SpecialtySerializer()
    
    class Meta:
        model = Medico
        fields = ["id", "crm", "nome", "especialidade"]


class AgendaSerializer(serializers.ModelSerializer):
    medico = MedicSerializer()

    class Meta:
        model = Agenda
        fields = '__all__'


class AppointmentSerializer(serializers.ModelSerializer):
    dia = serializers.DateField(source="agenda.dia")
    medico = MedicSerializer(source="agenda.medico")
    
    class Meta:
        model = Consulta
        fields = ["id", "dia", "horario", "data_agendamento", "medico"]


class AppointmentSerializer(serializers.ModelSerializer):
    dia = serializers.DateField(source="agenda.dia")
    medico = MedicSerializer(source="agenda.medico")
    
    class Meta:
        model = Consulta
        fields = ["id", "medico", "dia", "horario"]
        read_only_fields = ["dia", "medico"]


class CreateAppointmentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Consulta
        fields = "__all__"
