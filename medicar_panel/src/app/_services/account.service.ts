import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { map } from 'rxjs/operators';

import { environment } from '@environments/environment';
import { User, Consulta, Especialidade, Agenda } from '@app/_models';


@Injectable({ providedIn: 'root' })
export class AccountService {
    private userSubject: BehaviorSubject<User>;
    public user: Observable<User>;
    private headers = {
      headers: new HttpHeaders({'Content-Type': 'application/json'})
    };

    constructor(
        private router: Router,
        private http: HttpClient,
    ) {
        this.userSubject = new BehaviorSubject<User>(JSON.parse(localStorage.getItem('user')));
        this.user = this.userSubject.asObservable();
    }

    public get userValue(): User {
        return this.userSubject.value;
    }

    login(username, password) {
        return this.http.post<User>(`${environment.apiUrl}/signin/`, { username, password })
              .pipe(map(user => {
                  // store user details and jwt token in local storage to keep user logged in between page refreshes
                  localStorage.setItem('user', JSON.stringify(user));
                  this.userSubject.next(user);
                  return user;
              }));
    }

    logout() {
        // remove user from local storage and set current user to null
        localStorage.removeItem('user');
        this.userSubject.next(null);
        this.router.navigate(['/account/login']);
    }

    register(user: User) {
        return this.http.post(
          `${environment.apiUrl}/signup/`,
          JSON.stringify({
            "username": user.username,
            "password": user.password,
            "first_name": user.first_name,
            "last_name": user.last_name
          }),
          this.headers
        )
    }

    createAppointment(agenda_id, horario) {
        return this.http.post(
          `${environment.apiUrl}/consultas/`,
          JSON.stringify({
            "agenda_id": Number(agenda_id),
            "horario": horario
          }),
          this.headers
        )
    }

    getAll(user: User) {
        const headers_authorization = {
          headers: new HttpHeaders({'Authorization': user.token})
        }
        return this.http.get<Consulta[]>(
          `${environment.apiUrl}/consultas`,
          headers_authorization);
    }

    getAllEspecialidades(user: User) {
      const headers_authorization = {
        headers: new HttpHeaders({'Authorization': user.token})
      }
      return this.http.get<Especialidade[]>(
        `${environment.apiUrl}/especialidades`,
        headers_authorization);
    }

    getAllMedicos(user: User, id) {
      const headers_authorization = {
        headers: new HttpHeaders({'Authorization': user.token})
      }
      return this.http.get<Especialidade[]>(
        `${environment.apiUrl}/medicos?especialidade=`+id,
        headers_authorization);
    }

    getAllAgendas(user: User, id) {
      const headers_authorization = {
        headers: new HttpHeaders({'Authorization': user.token})
      }
      return this.http.get<Especialidade[]>(
        `${environment.apiUrl}/agendas?medico=`+id,
        headers_authorization);
    }

    update(id, params) {
        return this.http.put(`${environment.apiUrl}/users/${id}`, params)
            .pipe(map(x => {
                // update stored user if the logged in user updated their own record
                if (id == this.userValue.id) {
                    // update local storage
                    const user = { ...this.userValue, ...params };
                    localStorage.setItem('user', JSON.stringify(user));

                    // publish updated user to subscribers
                    this.userSubject.next(user);
                }
                return x;
            }));
    }

    delete(id: string) {
        return this.http.delete(`${environment.apiUrl}/users/${id}`)
            .pipe(map(x => {
                // auto logout if the logged in user deleted their own record
                if (id == this.userValue.id) {
                    this.logout();
                }
                return x;
            }));
    }
}
