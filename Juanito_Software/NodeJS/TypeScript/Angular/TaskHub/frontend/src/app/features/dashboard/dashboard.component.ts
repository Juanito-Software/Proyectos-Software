import { Component, inject, OnInit } from '@angular/core';
import { NgFor, NgIf } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatListModule } from '@angular/material/list';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { ProjectService } from '../../core/project.service';
import { Project } from '../../core/models';
import { CreateProjectDialogComponent } from './create-project-dialog.component';
import { ConfirmDialogComponent } from '../../shared/confirm-dialog.component';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [NgFor, NgIf, RouterLink, MatCardModule, MatButtonModule, MatListModule, MatDialogModule, MatSnackBarModule],
  template: `
    <div class="dashboard-shell">
      <mat-card>
        <h2>Panel de TaskHub</h2>
        <p>Gestiona tus proyectos y tareas desde aquí.</p>
        <button mat-raised-button color="primary" (click)="openCreateDialog()">Crear proyecto</button>
      </mat-card>

      <mat-card class="projects-card">
        <h3>Mis proyectos</h3>
        <mat-list>
          <mat-list-item *ngFor="let project of projects" [routerLink]="['/projects', project.id]" class="clickable">
            <div matListItemTitle>{{ project.name }}</div>
            <div matListItemLine>{{ project.description || 'Sin descripción' }}</div>
            <button mat-button color="warn" matListItemMeta (click)="deleteProject($event, project)">Eliminar</button>
          </mat-list-item>
          <mat-list-item *ngIf="!projects.length">
            <div matListItemTitle>No tienes proyectos aún</div>
          </mat-list-item>
        </mat-list>
      </mat-card>
    </div>
  `,
  styles: [`
    .dashboard-shell { display: grid; gap: 1rem; padding: 2rem; }
    .projects-card { padding: 1rem; }
    .clickable { cursor: pointer; }
    .clickable:hover { background: rgba(0,0,0,0.04); }
  `]
})
export class DashboardComponent implements OnInit {
  private projectService = inject(ProjectService);
  private dialog = inject(MatDialog);
  private snackBar = inject(MatSnackBar);
  projects: Project[] = [];

  ngOnInit(): void {
    this.loadProjects();
  }

  loadProjects(): void {
    this.projectService.listProjects().subscribe({
      next: (projects) => (this.projects = projects),
      error: () => (this.projects = []),
    });
  }

  openCreateDialog(): void {
    const dialogRef = this.dialog.open(CreateProjectDialogComponent);
    dialogRef.afterClosed().subscribe((payload) => {
      if (!payload) return;
      this.projectService.createProject(payload).subscribe({
        next: () => {
          this.snackBar.open('Proyecto creado', 'Cerrar', { duration: 3000 });
          this.loadProjects();
        },
        error: () => {
          this.snackBar.open('No se pudo crear el proyecto', 'Cerrar', { duration: 3000 });
        },
      });
    });
  }

  deleteProject(event: Event, project: Project): void {
    event.stopPropagation();
    event.preventDefault();

    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      data: {
        title: 'Eliminar proyecto',
        message: `¿Seguro que querés eliminar "${project.name}"? Esta acción no se puede deshacer.`,
      },
    });

    dialogRef.afterClosed().subscribe((confirmed) => {
      if (!confirmed) return;
      this.projectService.deleteProject(project.id).subscribe({
        next: () => {
          this.snackBar.open('Proyecto eliminado', 'Cerrar', { duration: 3000 });
          this.loadProjects();
        },
        error: () => {
          this.snackBar.open('No se pudo eliminar el proyecto', 'Cerrar', { duration: 3000 });
        },
      });
    });
  }
}
