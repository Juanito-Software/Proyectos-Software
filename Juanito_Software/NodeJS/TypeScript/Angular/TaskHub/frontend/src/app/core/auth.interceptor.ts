import { Injectable, inject } from '@angular/core';
import {
  HttpErrorResponse,
  HttpEvent,
  HttpHandler,
  HttpInterceptor,
  HttpRequest,
} from '@angular/common/http';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable, catchError, filter, switchMap, take, throwError } from 'rxjs';
import { AuthService } from './auth.service';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  private authService = inject(AuthService);
  private router = inject(Router);

  private isRefreshing = false;
  private refreshedToken$ = new BehaviorSubject<string | null>(null);

  intercept(req: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    const authReq = this.addToken(req, this.authService.getAccessToken());

    return next.handle(authReq).pipe(
      catchError((error: unknown) => {
        if (error instanceof HttpErrorResponse && error.status === 401 && !this.isAuthEndpoint(req.url)) {
          return this.handle401(req, next);
        }
        return throwError(() => error);
      }),
    );
  }

  private isAuthEndpoint(url: string): boolean {
    return (
      url.includes('/api/auth/login') ||
      url.includes('/api/auth/register') ||
      url.includes('/api/auth/refresh')
    );
  }

  private handle401(req: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    if (!this.isRefreshing) {
      this.isRefreshing = true;
      this.refreshedToken$.next(null);

      return this.authService.refresh().pipe(
        switchMap((response) => {
          this.isRefreshing = false;
          this.refreshedToken$.next(response.accessToken);
          return next.handle(this.addToken(req, response.accessToken));
        }),
        catchError((err) => {
          this.isRefreshing = false;
          this.authService.clearSession();
          this.router.navigate(['/login']);
          return throwError(() => err);
        }),
      );
    }

    // Ya hay una renovación en curso: esperamos su resultado en vez de disparar
    // otra petición de refresh en paralelo, y reintentamos con el token nuevo.
    return this.refreshedToken$.pipe(
      filter((token): token is string => token !== null),
      take(1),
      switchMap((token) => next.handle(this.addToken(req, token))),
    );
  }

  private addToken(req: HttpRequest<unknown>, token: string | null): HttpRequest<unknown> {
    return token ? req.clone({ setHeaders: { Authorization: `Bearer ${token}` } }) : req;
  }
}
