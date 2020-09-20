def values_gte_than(agendas, value):
    for agenda in agendas:
        agenda.horarios = [time for time in agenda.horarios if time >= value]
    return agendas