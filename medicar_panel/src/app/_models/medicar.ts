export class User {
    id: string;
    username: string;
    password: string;
    first_name: string;
    last_name: string;
    token: string;
}

export class Consulta {
  id: string;
  medico: Medico;
  agenda: Agenda;
  dia: string;
  horario: string;
}

export class Medico {
  id: string;
  crm: string;
  nome: string;
  especialidade: Especialidade;
}

export class Especialidade {
  id: string;
  nome: string;
}

export class Agenda {
  id: string;
  medico: Medico;
  dia: string;
  horarios: string;
}
