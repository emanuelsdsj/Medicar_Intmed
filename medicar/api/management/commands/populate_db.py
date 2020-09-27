import decimal

from django.core.management.base import BaseCommand

from api.models import Agenda, Especialidade, Medico, Consulta
from datetime import datetime


specialties = [
    {
        'nome': 'Cancerologia'
    },
    {
        'nome': 'Angiologia'
    },
    {
        'nome': 'Clínica Médica'
    },
    {
        'nome': 'Dermatologia'
    },
    {
        'nome': 'Pediatria'
    }
]

medics = [
    {
        'nome': 'Kefka Palazzo',
        'crm': 1234,
        'email': 'kefka@finalfantasy.com',
        'telefone': '71983667011'
    },
    {
        'nome': 'Vivi Ornitier',
        'crm': 1235,
        'email': 'vivi@finalfantasy.com',
        'telefone': '71983667012'
    },
    {
        'nome': 'Yuffie Kisaragi',
        'crm': 1236,
        'email': 'yuffie@finalfantasy.com',
        'telefone': '71983667013'
    },
    {
        'nome': 'Oerba Dia Vanille',
        'crm': 1237,
        'email': 'oerba@finalfantasy.com',
        'telefone': '71983667014'
    },
    {
        'nome': 'Rikku',
        'crm': 1238,
        'email': 'rikku@finalfantasy.com',
        'telefone': '71983667015'
    }
]

agendas = [
    {
        'dia': datetime.now(),
        'horarios': ["09:00", "10:00", "12:00"]
    },
    {
        'dia': datetime.now(),
        'horarios': ["15:00", "16:00", "17:00"]
    },
    {
        'dia': datetime.now(),
        'horarios': ["18:00", "18:30", "19:00"]
    },
    {
        'dia': datetime.now(),
        'horarios': ["20:00", "20:30", "21:00"]
    },
    {
        'dia': datetime.now(),
        'horarios': ["22:00", "23:00", "23:30"]
    }
]


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Especialidade
        Especialidade.objects.all().delete()
        specialty_list = [Especialidade(**specialty) for specialty in specialties]
        Especialidade.objects.bulk_create(specialty_list)
        specialty_list = Especialidade.objects.all()
        for pos, medic in enumerate(medics):
            medic["especialidade"] = specialty_list[pos]
        
        # Médico
        Medico.objects.all().delete()
        medic_list = [Medico(**medic) for medic in medics]
        Medico.objects.bulk_create(medic_list)
        medic_list = Medico.objects.all()
        for pos, agenda in enumerate(agendas):
            agenda["medico"] = medic_list[pos]

        # Agenda
        Agenda.objects.all().delete()
        agenda_list = [Agenda(**agenda) for agenda in agendas]
        Agenda.objects.bulk_create(agenda_list)

        # Consulta
        Consulta.objects.all().delete()
