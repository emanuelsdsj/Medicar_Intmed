import { Injectable } from '@angular/core';
import { HttpRequest, HttpHandler, HttpEvent, HttpInterceptor } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AccountService } from '@app/_services';

@Injectable()
export class JwtInterceptor implements HttpInterceptor {
    constructor(private accountService: AccountService) { }

    intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
        const user = this.accountService.userValue;
        const isLoggedIn = user && user.token;
        if (isLoggedIn) {
            request = request.clone({
                setHeaders: {
                    Authorization: `Token ${user.token}`
                }
            });
        }

        return next.handle(request);
    }
}
