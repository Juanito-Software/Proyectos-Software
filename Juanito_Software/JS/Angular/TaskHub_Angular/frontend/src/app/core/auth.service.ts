import { Injectable, inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, catchError, finalize, of, tap } from 'rxjs';
import { AuthResponse, LoginRequest, RegisterRequest } from './models';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private http = inject(HttpClient);
  private platformId = inject(PLATFORM_ID);
  private readonly apiUrl = 'http://localhost:3000/api/auth';
  private currentUserSubject = new BehaviorSubject<AuthResponse['user'] | null>(this.readUser());
  currentUser$ = this.currentUserSubject.asObservable();

  login(payload: LoginRequest): Observable<AuthResponse> {
    return this.http
      .post<AuthResponse>(`${this.apiUrl}/login`, payload, { withCredentials: true })
      .pipe(tap((response) => this.storeSession(response)));
  }

  register(payload: RegisterRequest): Observable<AuthResponse> {
    return this.http
      .post<AuthResponse>(`${this.apiUrl}/register`, payload, { withCredentials: true })
      .pipe(tap((response) => this.storeSession(response)));
  }

  // Renueva el access token usando el refresh token guardado en la cookie httpOnly
  // (nunca es accesible desde JS, así que no hace falta enviarlo explícitamente).
  refresh(): Observable<AuthResponse> {
    return this.http
      .post<AuthResponse>(`${this.apiUrl}/refresh`, {}, { withCredentials: true })
      .pipe(tap((response) => this.storeSession(response)));
  }

  logout(): Observable<void> {
    return this.http.post<void>(`${this.apiUrl}/logout`, {}, { withCredentials: true }).pipe(
      catchError(() => of(void 0)),
      finalize(() => this.clearSession()),
    );
  }

  isAuthenticated(): boolean {
    return !!this.currentUserSubject.value;
  }

  getAccessToken(): string | null {
    return this.isBrowser() ? localStorage.getItem('taskhub:accessToken') : null;
  }

  clearSession(): void {
    if (this.isBrowser()) {
      localStorage.removeItem('taskhub:user');
      localStorage.removeItem('taskhub:accessToken');
    }
    this.currentUserSubject.next(null);
  }

  private storeSession(response: AuthResponse) {
    if (this.isBrowser()) {
      localStorage.setItem('taskhub:user', JSON.stringify(response.user));
      localStorage.setItem('taskhub:accessToken', response.accessToken);
    }
    this.currentUserSubject.next(response.user);
  }

  private readUser(): AuthResponse['user'] | null {
    if (!this.isBrowser()) {
      return null;
    }
    const raw = localStorage.getItem('taskhub:user');
    return raw ? JSON.parse(raw) : null;
  }

  private isBrowser(): boolean {
    return isPlatformBrowser(this.platformId);
  }
}
