import { Component, OnInit, inject } from '@angular/core';
import { DatePipe, NgFor, NgIf } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { TaskService } from '../../core/task.service';
import { Comment, ProjectMember, Task, TaskPriority, TaskStatus, UpdateTaskRequest } from '../../core/models';

export interface TaskDetailDialogData {
  task: Task;
  members: ProjectMember[];
}

@Component({
  selector: 'app-task-detail-dialog',
  standalone: true,
  imports: [
    NgFor,
    NgIf,
    DatePipe,
    FormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatSnackBarModule,
    MatProgressSpinnerModule,
  ],
  template: `
    <h2 mat-dialog-title>Editar tarea</h2>
    <div mat-dialog-content class="dialog-content">
      <mat-form-field appearance="outline">
        <mat-label>Título</mat-label>
        <input matInput [(ngModel)]="title" name="title" />
      </mat-form-field>

      <mat-form-field appearance="outline">
        <mat-label>Descripción</mat-label>
        <textarea matInput [(ngModel)]="description" name="description" rows="3"></textarea>
      </mat-form-field>

      <div class="row">
        <mat-form-field appearance="outline">
          <mat-label>Estado</mat-label>
          <mat-select [(ngModel)]="status" name="status">
            <mat-option *ngFor="let s of statuses" [value]="s">{{ s }}</mat-option>
          </mat-select>
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>Prioridad</mat-label>
          <mat-select [(ngModel)]="priority" name="priority">
            <mat-option *ngFor="let p of priorities" [value]="p">{{ p }}</mat-option>
          </mat-select>
        </mat-form-field>
      </div>

      <div class="row">
        <mat-form-field appearance="outline">
          <mat-label>Responsable</mat-label>
          <mat-select [(ngModel)]="assigneeId" name="assigneeId">
            <mat-option [value]="null">Sin asignar</mat-option>
            <mat-option *ngFor="let m of data.members" [value]="m.userId">{{ m.user.name }}</mat-option>
          </mat-select>
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>Fecha límite</mat-label>
          <input matInput type="date" [(ngModel)]="deadline" name="deadline" />
        </mat-form-field>
      </div>

      <div class="comments">
        <h3>Comentarios</h3>
        <div class="comment-list" *ngIf="!loadingComments; else loading">
          <p class="empty-hint" *ngIf="!comments.length">Todavía no hay comentarios</p>
          <div class="comment" *ngFor="let c of comments">
            <div class="comment-header">
              <strong>{{ c.author.name }}</strong>
              <span>{{ c.createdAt | date: 'short' }}</span>
            </div>
            <p>{{ c.text }}</p>
          </div>
        </div>
        <ng-template #loading>
          <mat-spinner diameter="24"></mat-spinner>
        </ng-template>

        <div class="new-comment">
          <mat-form-field appearance="outline">
            <mat-label>Agregar comentario</mat-label>
            <textarea matInput [(ngModel)]="newComment" name="newComment" rows="2"></textarea>
          </mat-form-field>
          <button mat-button [disabled]="!newComment.trim()" (click)="addComment()">Enviar</button>
        </div>
      </div>
    </div>
    <div mat-dialog-actions align="end">
      <button mat-button (click)="dialogRef.close()">Cancelar</button>
      <button mat-flat-button color="primary" [disabled]="!title.trim() || saving" (click)="save()">Guardar</button>
    </div>
  `,
  styles: [`
    .dialog-content {
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
      min-width: min(90vw, 480px);
      max-height: 70vh;
      padding-top: 0.5rem;
    }
    .row { display: flex; gap: 0.75rem; }
    .row mat-form-field { flex: 1 1 0; }
    .comments { display: flex; flex-direction: column; gap: 0.5rem; }
    .comments h3 { margin: 0; font-size: 0.95rem; }
    .comment-list { display: flex; flex-direction: column; gap: 0.5rem; max-height: 220px; overflow-y: auto; }
    .comment { background: #f1f3f9; border-radius: 6px; padding: 0.5rem 0.75rem; }
    .comment-header { display: flex; justify-content: space-between; font-size: 0.8rem; color: rgba(0,0,0,0.6); }
    .comment p { margin: 0.25rem 0 0; font-size: 0.9rem; }
    .empty-hint { color: rgba(0,0,0,0.4); font-size: 0.85rem; }
    .new-comment { display: flex; flex-direction: column; align-items: flex-end; gap: 0.25rem; }
    .new-comment mat-form-field { width: 100%; }
  `]
})
export class TaskDetailDialogComponent implements OnInit {
  dialogRef = inject(MatDialogRef<TaskDetailDialogComponent>);
  data: TaskDetailDialogData = inject(MAT_DIALOG_DATA);
  private taskService = inject(TaskService);
  private snackBar = inject(MatSnackBar);

  statuses: TaskStatus[] = ['TODO', 'IN_PROGRESS', 'IN_REVIEW', 'DONE'];
  priorities: TaskPriority[] = ['LOW', 'MEDIUM', 'HIGH', 'URGENT'];

  title = '';
  description = '';
  status: TaskStatus = 'TODO';
  priority: TaskPriority = 'MEDIUM';
  assigneeId: string | null = null;
  deadline = '';

  comments: Comment[] = [];
  newComment = '';
  saving = false;
  loadingComments = true;

  ngOnInit(): void {
    const task = this.data.task;
    this.title = task.title;
    this.description = task.description ?? '';
    this.status = task.status;
    this.priority = task.priority;
    this.assigneeId = task.assigneeId;
    this.deadline = task.deadline ? task.deadline.slice(0, 10) : '';
    this.comments = task.comments ?? [];

    this.taskService.getTask(task.id).subscribe({
      next: (full) => {
        this.comments = full.comments ?? [];
        this.loadingComments = false;
      },
      error: () => {
        this.loadingComments = false;
      },
    });
  }

  save(): void {
    if (!this.title.trim() || this.saving) return;

    const payload: UpdateTaskRequest = {
      title: this.title.trim(),
      description: this.description.trim(),
      status: this.status,
      priority: this.priority,
      assigneeId: this.assigneeId,
      deadline: this.deadline ? new Date(this.deadline).toISOString() : null,
    };

    this.saving = true;
    this.taskService.updateTask(this.data.task.id, payload).subscribe({
      next: (updated) => {
        this.saving = false;
        this.dialogRef.close({ ...updated, comments: this.comments });
      },
      error: () => {
        this.saving = false;
        this.snackBar.open('No se pudo guardar la tarea', 'Cerrar', { duration: 3000 });
      },
    });
  }

  addComment(): void {
    const text = this.newComment.trim();
    if (!text) return;

    this.taskService.addComment(this.data.task.id, text).subscribe({
      next: (comment) => {
        this.comments = [...this.comments, comment];
        this.newComment = '';
      },
      error: () => this.snackBar.open('No se pudo enviar el comentario', 'Cerrar', { duration: 3000 }),
    });
  }
}
