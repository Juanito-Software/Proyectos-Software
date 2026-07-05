import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { AuthService } from '../../core/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule, RouterLink, MatCardModule, MatFormFieldModule, MatInputModule, MatButtonModule, MatSnackBarModule],
  template: `
    <div class="auth-shell">
      <mat-card class="auth-card">
        <h2>Iniciar sesión</h2>
        <p>Accede a TaskHub</p>
        <mat-form-field appearance="outline">
          <mat-label>Email</mat-label>
          <input matInput placeholder="tu@email.com" [(ngModel)]="email" name="email" />
        </mat-form-field>
        <mat-form-field appearance="outline">
          <mat-label>Contraseña</mat-label>
          <input matInput type="password" [(ngModel)]="password" name="password" />
        </mat-form-field>
        <button mat-flat-button color="primary" (click)="login()">Entrar</button>
        <a routerLink="/register">¿No tienes cuenta? Regístrate</a>
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
export class LoginComponent {
  private authService = inject(AuthService);
  private router = inject(Router);
  private snackBar = inject(MatSnackBar);

  email = '';
  password = '';

  login() {
    this.authService.login({ email: this.email, password: this.password }).subscribe({
      next: () => {
        this.router.navigate(['/']);
      },
      error: () => {
        this.snackBar.open('Credenciales inválidas', 'Cerrar', { duration: 3000 });
      },
    });
  }
}
