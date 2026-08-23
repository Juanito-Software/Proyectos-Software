import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { HttpErrorResponse } from '@angular/common/http';
import { AuthService } from '../../core/auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [FormsModule, RouterLink, MatCardModule, MatFormFieldModule, MatInputModule, MatButtonModule, MatSnackBarModule],
  template: `
    <div class="auth-shell">
      <mat-card class="auth-card">
        <h2>Crear cuenta</h2>
        <p>Regístrate en TaskHub</p>
        <mat-form-field appearance="outline">
          <mat-label>Nombre</mat-label>
          <input matInput placeholder="Tu nombre" [(ngModel)]="name" name="name" />
        </mat-form-field>
        <mat-form-field appearance="outline">
          <mat-label>Email</mat-label>
          <input matInput placeholder="tu@email.com" [(ngModel)]="email" name="email" />
        </mat-form-field>
        <mat-form-field appearance="outline">
          <mat-label>Contraseña</mat-label>
          <input matInput type="password" [(ngModel)]="password" name="password" />
          <mat-hint>Mínimo 8 caracteres, con una mayúscula y un número</mat-hint>
        </mat-form-field>
        <button mat-flat-button color="primary" (click)="register()">Crear cuenta</button>
        <a routerLink="/login">¿Ya tienes cuenta? Inicia sesión</a>
      </mat-card>
    </div>
  `,
  styles: [`
    .auth-shell {
      min-height: 100vh;
      display: grid;
      place-items: center;
      background: linear-gradient(135deg, #2563eb, #7c3aed);
      padding: 1rem;
    }
    .auth-card {
      width: min(100%, 420px);
      padding: 1.5rem;
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }
  `]
})
export class RegisterComponent {
  private authService = inject(AuthService);
  private router = inject(Router);
  private snackBar = inject(MatSnackBar);

  name = '';
  email = '';
  password = '';

  register() {
    this.authService.register({ name: this.name, email: this.email, password: this.password }).subscribe({
      next: () => {
        this.router.navigate(['/']);
      },
      error: (err: HttpErrorResponse) => {
        this.snackBar.open(this.extractErrorMessage(err), 'Cerrar', { duration: 5000 });
      },
    });
  }

  private extractErrorMessage(err: HttpErrorResponse): string {
    const body = err.error;
    if (body?.errors) {
      const firstField = Object.values<string[]>(body.errors)[0];
      if (firstField?.length) return firstField[0];
    }
    return body?.message ?? 'No se pudo crear la cuenta';
  }
}
