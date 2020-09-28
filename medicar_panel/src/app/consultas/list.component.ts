import { Component, OnInit } from '@angular/core';
import { first } from 'rxjs/operators';

import { AccountService } from '@app/_services';

@Component({ templateUrl: 'list.component.html' })
export class ListComponent implements OnInit {
    consultas = null;
    user = null;

    constructor(private accountService: AccountService) {
      this.user = this.accountService.userValue
    }

    ngOnInit() {
        this.accountService.getAll(this.user)
            .pipe(first())
            .subscribe(consultas => this.consultas = consultas);
    }

    deleteAppointment(id) {
        this.accountService.delete(id)
            .pipe(first())
            .subscribe(() => {
                this.consultas = this.consultas.filter(x => x.id !== id)
            });
    }
}
