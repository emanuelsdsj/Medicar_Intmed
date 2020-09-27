from .models import Agenda

def values_gte_than(object_list, value):
    available_objects = []
    if object_list:
        if isinstance(object_list[0], Agenda):
            for agenda in object_list:
                if agenda.dia == value.today().date():
                    agenda.horarios = [time for time in agenda.horarios if time >= value.time()]
                if agenda.horarios:
                    available_objects.append(agenda)
        else:
            for consulta in object_list:
                if consulta.agenda.dia == value.today().date():
                    if consulta.horario > value.time():
                        available_objects.append(consulta)
                else:
                    available_objects.append(consulta)
    return available_objects
