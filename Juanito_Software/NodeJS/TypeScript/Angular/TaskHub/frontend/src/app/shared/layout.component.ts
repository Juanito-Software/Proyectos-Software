import { Component, inject } from '@angular/core';
import { Router, RouterLink, RouterOutlet } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { AuthService } from '../core/auth.service';

@Component({
  selector: 'app-layout',
  standalone: true,
  imports: [RouterLink, RouterOutlet, MatToolbarModule, MatButtonModule],
  template: `
    <mat-toolbar color="primary">
      <span>TaskHub</span>
      <span class="spacer"></span>
      <button mat-button routerLink="/">Dashboard</button>
      <button mat-button (click)="logout()">Cerrar sesión</button>
    </mat-toolbar>
    <main>
      <router-outlet></router-outlet>
    </main>
  `,
  styles: [`
    .spacer { flex: 1 1 auto; }
    main { padding: 1rem; }
  `]
})
export class LayoutComponent {
  private authService = inject(AuthService);
  private router = inject(Router);

  logout() {
    this.authService.logout().subscribe(() => {
      this.router.navigate(['/login']);
    });
  }
}
