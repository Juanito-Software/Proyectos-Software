import { Component, OnInit, inject } from '@angular/core';
import { NgFor, NgIf } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { CdkDragDrop, DragDropModule, moveItemInArray, transferArrayItem } from '@angular/cdk/drag-drop';
import { ProjectService } from '../../core/project.service';
import { TaskService } from '../../core/task.service';
import { Project, Task, TaskStatus } from '../../core/models';
import { CreateTaskDialogComponent } from './create-task-dialog.component';
import { ConfirmDialogComponent } from '../../shared/confirm-dialog.component';

interface Column {
  status: TaskStatus;
  label: string;
  tasks: Task[];
}

@Component({
  selector: 'app-project-detail',
  standalone: true,
  imports: [
    NgFor,
    NgIf,
    RouterLink,
    MatCardModule,
    MatButtonModule,
    MatChipsModule,
    MatDialogModule,
    MatSnackBarModule,
    DragDropModule,
  ],
  template: `
    <div class="project-detail">
      <div class="project-header">
        <a mat-button routerLink="/">← Volver</a>
        <div class="project-title">
          <h2>{{ project?.name }}</h2>
          <p *ngIf="project?.description">{{ project?.description }}</p>
        </div>
        <button mat-flat-button color="primary" (click)="openCreateTaskDialog()">Nueva tarea</button>
      </div>

      <div class="board">
        <div class="column" *ngFor="let column of columns">
          <h3>{{ column.label }} ({{ column.tasks.length }})</h3>
          <div
            class="column-body"
            cdkDropList
            [id]="column.status"
            [cdkDropListData]="column.tasks"
            [cdkDropListConnectedTo]="connectedLists"
            (cdkDropListDropped)="drop($event, column.status)"
          >
            <mat-card class="task-card" *ngFor="let task of column.tasks" cdkDrag>
              <div class="task-card-handle" cdkDragHandle>
                <strong>{{ task.title }}</strong>
              </div>
              <p *ngIf="task.description">{{ task.description }}</p>
              <div class="task-card-footer">
                <mat-chip-set>
                  <mat-chip>{{ task.priority }}</mat-chip>
                </mat-chip-set>
                <button mat-button color="warn" (click)="deleteTask(task, column)">Eliminar</button>
              </div>
            </mat-card>
            <p class="empty-hint" *ngIf="!column.tasks.length">Sin tareas</p>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .project-detail { padding: 1rem; display: flex; flex-direction: column; gap: 1rem; }
    .project-header { display: flex; align-items: center; gap: 1rem; }
    .project-title { flex: 1 1 auto; }
    .project-title h2 { margin: 0; }
    .project-title p { margin: 0.25rem 0 0; color: rgba(0,0,0,0.6); }
    .board { display: flex; gap: 1rem; overflow-x: auto; }
    .column {
      flex: 1 0 260px;
      min-width: 260px;
      background: #f1f3f9;
      border-radius: 8px;
      padding: 0.75rem;
    }
    .column h3 { margin: 0 0 0.75rem; font-size: 0.95rem; }
    .column-body { display: flex; flex-direction: column; gap: 0.5rem; min-height: 120px; }
    .task-card { padding: 0.75rem; display: flex; flex-direction: column; gap: 0.4rem; }
    .task-card-handle { cursor: grab; }
    .task-card p { margin: 0; font-size: 0.85rem; color: rgba(0,0,0,0.6); }
    .task-card-footer { display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; }
    .empty-hint { color: rgba(0,0,0,0.4); font-size: 0.85rem; text-align: center; margin: 1rem 0; }
    .cdk-drag-preview { box-shadow: 0 4px 12px rgba(0,0,0,0.2); }
    .cdk-drag-placeholder { opacity: 0.3; }
  `]
})
export class ProjectDetailComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private projectService = inject(ProjectService);
  private taskService = inject(TaskService);
  private dialog = inject(MatDialog);
  private snackBar = inject(MatSnackBar);

  project: Project | null = null;
  projectId = '';

  columns: Column[] = [
    { status: 'TODO', label: 'Por hacer', tasks: [] },
    { status: 'IN_PROGRESS', label: 'En progreso', tasks: [] },
    { status: 'IN_REVIEW', label: 'En revisión', tasks: [] },
    { status: 'DONE', label: 'Hecho', tasks: [] },
  ];

  get connectedLists(): string[] {
    return this.columns.map((c) => c.status);
  }

  ngOnInit(): void {
    this.projectId = this.route.snapshot.paramMap.get('id') ?? '';
    this.projectService.getProject(this.projectId).subscribe({
      next: (project) => (this.project = project),
      error: () => this.snackBar.open('No se pudo cargar el proyecto', 'Cerrar', { duration: 3000 }),
    });
    this.loadTasks();
  }

  loadTasks(): void {
    this.taskService.listByProject(this.projectId).subscribe({
      next: (tasks) => {
        for (const column of this.columns) {
          column.tasks = tasks.filter((task) => task.status === column.status);
        }
      },
      error: () => this.snackBar.open('No se pudieron cargar las tareas', 'Cerrar', { duration: 3000 }),
    });
  }

  drop(event: CdkDragDrop<Task[]>, targetStatus: TaskStatus): void {
    if (event.previousContainer === event.container) {
      moveItemInArray(event.container.data, event.previousIndex, event.currentIndex);
      return;
    }

    const task = event.previousContainer.data[event.previousIndex];
    transferArrayItem(event.previousContainer.data, event.container.data, event.previousIndex, event.currentIndex);

    this.taskService.updateTask(task.id, { status: targetStatus }).subscribe({
      next: (updated) => {
        task.status = updated.status;
      },
      error: () => {
        this.snackBar.open('No se pudo mover la tarea', 'Cerrar', { duration: 3000 });
        this.loadTasks();
      },
    });
  }

  openCreateTaskDialog(): void {
    const dialogRef = this.dialog.open(CreateTaskDialogComponent);
    dialogRef.afterClosed().subscribe((payload) => {
      if (!payload) return;
      this.taskService.createTask({ ...payload, projectId: this.projectId }).subscribe({
        next: () => {
          this.snackBar.open('Tarea creada', 'Cerrar', { duration: 3000 });
          this.loadTasks();
        },
        error: () => this.snackBar.open('No se pudo crear la tarea', 'Cerrar', { duration: 3000 }),
      });
    });
  }

  deleteTask(task: Task, column: Column): void {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      data: {
        title: 'Eliminar tarea',
        message: `¿Seguro que querés eliminar "${task.title}"? Esta acción no se puede deshacer.`,
      },
    });

    dialogRef.afterClosed().subscribe((confirmed) => {
      if (!confirmed) return;
      this.taskService.deleteTask(task.id).subscribe({
        next: () => {
          column.tasks = column.tasks.filter((t) => t.id !== task.id);
          this.snackBar.open('Tarea eliminada', 'Cerrar', { duration: 3000 });
        },
        error: () => {
          this.snackBar.open('No se pudo eliminar la tarea', 'Cerrar', { duration: 3000 });
        },
      });
    });
  }
}
