import json

from datetime import datetime
from django.http.response import JsonResponse
from rest_framework import viewsets, status
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated 
from django.core import serializers

from .models import Especialidade, Medico, Agenda, Consulta
from .serializers import (
    SpecialtySerializer, 
    MedicSerializer,
    AgendaSerializer,
    AppointmentSerializer,
    CreateAppointmentSerializer
)
from .utils import values_gte_than


class SpecialtyViewSet(viewsets.ModelViewSet):
    serializer_class = SpecialtySerializer
    permission_classes = (IsAuthenticated,)
    
    def list(self, request):
        name_requested = request.query_params.get("search", "")
        specialties = Especialidade.objects.filter(nome__contains=name_requested).all()
        specialties_serialized = self.serializer_class(specialties, many=True)
        return JsonResponse(specialties_serialized.data, safe=False)

class MedicViewSet(viewsets.ModelViewSet):
    serializer_class = MedicSerializer
    permission_classes = (IsAuthenticated,)
    
    def list(self, request):
        name_requested = request.query_params.get("search", "")
        specialties = request.query_params.getlist("especialidade", None)
        if specialties:
            medics = Medico.objects.filter(nome__contains=name_requested, 
                                          especialidade__in=specialties).all()
        else:
            medics = Medico.objects.filter(nome__contains=name_requested).all()
        medics_serialized = self.serializer_class(medics, many=True)
        return JsonResponse(medics_serialized.data, safe=False)


class AgendaViewSet(viewsets.ModelViewSet):
    serializer_class = AgendaSerializer
    permission_classes = (IsAuthenticated,)
    
    def list(self, request):
        today = datetime.now()
        agendas = Agenda.objects.select_related('medico').filter(dia__gte=today.date()).all()
        agendas = values_gte_than(agendas, today.time())
        agenda_serialized = self.serializer_class(agendas, many=True)
        return JsonResponse(agenda_serialized.data, safe=False)


class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    create_serializer_class = CreateAppointmentSerializer
    agenda_serializer_class = AgendaSerializer
    permission_classes = (IsAuthenticated,)
    
    def list(self, request):
        today = datetime.now()
        appointment = Consulta.objects.filter(horario__gte=today.time(), 
                                              agenda__dia__gte=today.date()).all()
        appointment_serialized = self.serializer_class(appointment, many=True)
        return JsonResponse(appointment_serialized.data, safe=False)

    def create(self, request):
        today = datetime.now()
        data = JSONParser().parse(request)
        time = datetime.strptime(data.get("horario"), "%H:%M").time()
        appointment = Consulta.objects.filter(agenda=data.get("agenda_id"), horario=time).first()
        if appointment:
            return JsonResponse({
                "Status": "Failed",
                "Error": "Consulta já foi marcada"}, 
                status=status.HTTP_400_BAD_REQUEST, safe=False
            )
        agenda = Agenda.objects.filter(id=data.get("agenda_id"), dia__gte=today.date()).first()
        agenda = values_gte_than([agenda], today.time())[0]
        if not agenda and not agenda.horarios:
            return JsonResponse({
                "Status": "Failed",
                "Error": "A agenda do médico não foi encontrada"}, 
                status=status.HTTP_404_NOT_FOUND, safe=False
            )
        if time not in agenda.horarios:
            return JsonResponse({
                "Status": "Failed",
                "Error": "Horário escolhido já está reservado ou não pode ser mais marcado"}, 
                status=status.HTTP_400_BAD_REQUEST, safe=False
            )
        appointment_data = {
            "agenda": data.get("agenda_id"),
            "horario": time,
            "usuario": request.user.id
        }
        appointment_serialized = self.create_serializer_class(data=appointment_data)
        if appointment_serialized.is_valid():
            agenda.horarios.remove(time)
            agenda.save()
            appointment_serialized = self.serializer_class(appointment_serialized.save())
        return JsonResponse(appointment_serialized.data, safe=False)

    def destroy(self, request, pk):
        today = datetime.now()
        appointment = Consulta.objects.filter(id=pk, usuario=request.user.id, 
                                              horario__gte=today.time(), 
                                              agenda__dia__gte=today.date()).first()
        if not appointment:
            return JsonResponse({
                "Status": "Failed",
                "Error": "A consulta não foi encontrada"}, 
                status=status.HTTP_404_NOT_FOUND, safe=False
            )
        agenda = Agenda.objects.filter(id=appointment.agenda.id, dia__gte=today.date()).first()
        agenda.horarios.append(appointment.horario)
        agenda.save()
        appointment.delete()
        return JsonResponse("", safe=False)