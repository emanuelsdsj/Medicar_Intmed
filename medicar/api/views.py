import json
import requests

from datetime import datetime
from django.http.response import JsonResponse
from rest_framework import viewsets, status
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated 
from django.core import serializers
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

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
        kwargs = {
            '{0}__{1}'.format('nome', 'contains'): name_requested
        }
        if specialties:
            kwargs['{0}__{1}'.format('especialidade', 'in')] = specialties
        medics = Medico.objects.filter(**kwargs).all()
        medics_serialized = self.serializer_class(medics, many=True)
        return JsonResponse(medics_serialized.data, safe=False)


class AgendaViewSet(viewsets.ModelViewSet):
    serializer_class = AgendaSerializer
    permission_classes = (IsAuthenticated,)
    
    def list(self, request):
        today = datetime.now()
        medics = request.query_params.getlist("medico", None)
        specialties = request.query_params.getlist("especialidade", None)
        initial_date = request.query_params.get("data_inicio", None)
        final_date = request.query_params.get("data_final", None)
        kwargs = {
            '{0}__{1}'.format('dia', 'gte'): today.date()
        }
        if specialties:
            kwargs['{0}__{1}__{2}'.format('medico', 'especialidade', 'in')] = specialties
        if medics:
            kwargs['{0}__{1}'.format('medico', 'in')] = medics
        if initial_date and final_date:
            kwargs['{0}__{1}'.format('dia', 'range')] = (initial_date, final_date)
        
        agendas = Agenda.objects.select_related('medico').filter(**kwargs).order_by("dia").all()
        agendas = values_gte_than(agendas, today)
        agenda_serialized = self.serializer_class(agendas, many=True)
        return JsonResponse(agenda_serialized.data, safe=False)


class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    create_serializer_class = CreateAppointmentSerializer
    agenda_serializer_class = AgendaSerializer
    permission_classes = (IsAuthenticated,)
    
    def list(self, request):
        today = datetime.now()
        appointment = Consulta.objects.filter(usuario=request.user.id,
                                              agenda__dia__gte=today.date()).all()
        appointment = values_gte_than(appointment, today)
        appointment_serialized = self.serializer_class(appointment, many=True)
        return JsonResponse(appointment_serialized.data, safe=False)

    def create(self, request):
        today = datetime.now()
        data = JSONParser().parse(request)
        print(data)
        time = datetime.strptime(data.get("horario"), "%H:%M:%S").time()
        appointment = Consulta.objects.filter(agenda=data.get("agenda_id"), horario=time).first()
        if appointment:
            return JsonResponse({
                "Status": "Failed",
                "Error": "Consulta já foi marcada"}, 
                status=status.HTTP_400_BAD_REQUEST, safe=False
            )
        agenda = Agenda.objects.filter(id=data.get("agenda_id"), dia__gte=today.date()).first()
        agenda = values_gte_than([agenda], today)[0]
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
        print(appointment_data)
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


@csrf_exempt
def signup(request):
    if request.method != "POST":
        return JsonResponse("", 
                status=status.HTTP_405_METHOD_NOT_ALLOWED, safe=False
            )
    data = JSONParser().parse(request)
    user = User.objects.create_user(username=data.get("username"), password=data.get("password"))
    user.first_name = data.get("first_name", "")
    user.last_name = data.get("last_name", "")
    user.save()
    return JsonResponse("", 
                status=status.HTTP_200_OK, safe=False
            )


@csrf_exempt
def signin(request):
    if request.method != "POST":
        return JsonResponse("", 
                status=status.HTTP_405_METHOD_NOT_ALLOWED, safe=False
            )
    data = JSONParser().parse(request)
    user = authenticate(username=data.get("username"), password=data.get("password"))
    if not user:
        return JsonResponse({
                "Status": "Failed",
                "Error": "Usuário inválido"}, 
                status=status.HTTP_400_BAD_REQUEST, safe=False
            )
    login(request, user)
    body = {
        "username": data.get("username"),
        "password": data.get("password")
    } 
    data = requests.post("http://127.0.0.1:8000/api-token-auth/", json=body)
    data = data.json()
    body["id"] = user.id
    body["first_name"] = user.first_name
    body["last_name"] = user.last_name
    body["token"] = data["token"]
    return JsonResponse(body, 
                status=status.HTTP_200_OK, safe=False
            )


@csrf_exempt
@login_required
def signout(request):
    if request.method != "POST":
        return JsonResponse("", 
                status=status.HTTP_405_METHOD_NOT_ALLOWED, safe=False
            )
    logout(request)
    return JsonResponse({
                "Status": "Success"}, 
                status=status.HTTP_200_OK, safe=False
            )
