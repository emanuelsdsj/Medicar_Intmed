def values_gte_than(agendas, value):
    for agenda in agendas:
        if agenda.dia == value.today():
            agenda.horarios = [time for time in agenda.horarios if time >= value.time()]
    return agendas