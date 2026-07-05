import { Routes } from '@angular/router';
import { LayoutComponent } from './shared/layout.component';
import { LoginComponent } from './features/auth/login.component';
import { RegisterComponent } from './features/auth/register.component';
import { DashboardComponent } from './features/dashboard/dashboard.component';
import { ProjectDetailComponent } from './features/projects/project-detail.component';
import { authGuard } from './core/auth.guard';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  {
    path: '',
    component: LayoutComponent,
    canActivate: [authGuard],
    children: [
      { path: '', component: DashboardComponent },
      { path: 'projects/:id', component: ProjectDetailComponent },
    ],
  },
  { path: '**', redirectTo: '' },
];
