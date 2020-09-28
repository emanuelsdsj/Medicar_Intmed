import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { first } from 'rxjs/operators';

import { AccountService, AlertService } from '@app/_services';
import { Especialidade, Medico, Agenda } from '@app/_models';
import { callbackify } from 'util';


@Component({ templateUrl: 'add-edit.component.html' })
export class AddEditComponent implements OnInit {
    form: FormGroup;
    id: string;
    isAddMode: boolean;
    loading = false;
    submitted = false;
    user = null;
    especialidades = null;
    especialidade: FormGroup;
    medicos = null
    medico: FormGroup;
    agendas = null;
    horarios = [];
    agenda = null;
    horario = null

    constructor(
        private formBuilder: FormBuilder,
        private route: ActivatedRoute,
        private router: Router,
        private accountService: AccountService,
        private alertService: AlertService
    ) {
      this.user = accountService.userValue
    }

    ngOnInit() {
        this.accountService.getAllEspecialidades(this.user)
          .pipe(first())
          .subscribe(especialidades => this.especialidades = especialidades);

        this.form = this.formBuilder.group({
            nome: ['', Validators.required],
            agenda: ['', Validators.required],
            especialidade: ['', Validators.required],
            dia: ['', Validators.required],
            horario: ['', Validators.required]
        });
    }

    // convenience getter for easy access to form fields
    get f() { return this.form.controls; }

    onSubmit() {
        this.submitted = true;

        // reset alerts on submit
        this.alertService.clear();

        // stop here if form is invalid
        if (!this.agenda && !this.horario) {
            return;
        }

        this.loading = true;
        this.createAppoitment();
    }

    onEspecialidadeSelected(id){
      this.accountService.getAllMedicos(this.user, id)
        .pipe(first())
        .subscribe(medicos => this.medicos = medicos);
    }

    onMedicoSelected(id){
      this.accountService.getAllAgendas(this.user, id)
        .pipe(first())
        .subscribe(agendas => this.agendas = agendas);
    }

    onAgendasSelected(agenda){
      this.horarios = []
      agenda = agenda.toString().split(',');
      for(let i=0; i<agenda.length; i++) {
        if(i == 0) {
          this.agenda = agenda[i]
        }
        else {
          this.horarios.push(agenda[i])
        }
      }
    }

    onHorariosSelected(horario) {
      this.horario = horario
    }

    private createAppoitment() {
        this.accountService.createAppointment(this.agenda, this.horario)
            .pipe(first())
            .subscribe(
                data => {
                    this.alertService.success('Consulta marcada com sucesso', { keepAfterRouteChange: true });
                    this.router.navigate(['.', { relativeTo: this.route }]);
                },
                error => {
                    this.alertService.error(error);
                    this.loading = false;
                });
    }
}
