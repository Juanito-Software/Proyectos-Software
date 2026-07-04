import { Component, inject } from '@angular/core';
import { NgFor } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { TaskPriority } from '../../core/models';

export interface CreateTaskDialogResult {
  title: string;
  description?: string;
  priority: TaskPriority;
}

@Component({
  selector: 'app-create-task-dialog',
  standalone: true,
  imports: [NgFor, FormsModule, MatDialogModule, MatFormFieldModule, MatInputModule, MatSelectModule, MatButtonModule],
  template: `
    <h2 mat-dialog-title>Nueva tarea</h2>
    <div mat-dialog-content class="dialog-content">
      <mat-form-field appearance="outline">
        <mat-label>Título</mat-label>
        <input matInput [(ngModel)]="title" name="title" />
      </mat-form-field>
      <mat-form-field appearance="outline">
        <mat-label>Descripción</mat-label>
        <textarea matInput [(ngModel)]="description" name="description" rows="3"></textarea>
      </mat-form-field>
      <mat-form-field appearance="outline">
        <mat-label>Prioridad</mat-label>
        <mat-select [(ngModel)]="priority" name="priority">
          <mat-option *ngFor="let p of priorities" [value]="p">{{ p }}</mat-option>
        </mat-select>
      </mat-form-field>
    </div>
    <div mat-dialog-actions align="end">
      <button mat-button (click)="dialogRef.close()">Cancelar</button>
      <button mat-flat-button color="primary" [disabled]="!title.trim()" (click)="submit()">Crear</button>
    </div>
  `,
  styles: [`
    .dialog-content {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
      min-width: min(90vw, 360px);
      padding-top: 0.5rem;
    }
  `]
})
export class CreateTaskDialogComponent {
  dialogRef = inject(MatDialogRef<CreateTaskDialogComponent>);
  priorities: TaskPriority[] = ['LOW', 'MEDIUM', 'HIGH', 'URGENT'];

  title = '';
  description = '';
  priority: TaskPriority = 'MEDIUM';

  submit() {
    const result: CreateTaskDialogResult = { title: this.title.trim(), priority: this.priority };
    if (this.description.trim()) {
      result.description = this.description.trim();
    }
    this.dialogRef.close(result);
  }
}
