import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { CreateProjectRequest } from '../../core/models';

@Component({
  selector: 'app-create-project-dialog',
  standalone: true,
  imports: [FormsModule, MatDialogModule, MatFormFieldModule, MatInputModule, MatButtonModule],
  template: `
    <h2 mat-dialog-title>Nuevo proyecto</h2>
    <div mat-dialog-content class="dialog-content">
      <mat-form-field appearance="outline">
        <mat-label>Nombre</mat-label>
        <input matInput [(ngModel)]="name" name="name" />
      </mat-form-field>
      <mat-form-field appearance="outline">
        <mat-label>Descripción</mat-label>
        <textarea matInput [(ngModel)]="description" name="description" rows="3"></textarea>
      </mat-form-field>
    </div>
    <div mat-dialog-actions align="end">
      <button mat-button (click)="dialogRef.close()">Cancelar</button>
      <button mat-flat-button color="primary" [disabled]="!name.trim()" (click)="submit()">Crear</button>
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
export class CreateProjectDialogComponent {
  dialogRef = inject(MatDialogRef<CreateProjectDialogComponent>);

  name = '';
  description = '';

  submit() {
    const payload: CreateProjectRequest = { name: this.name.trim() };
    if (this.description.trim()) {
      payload.description = this.description.trim();
    }
    this.dialogRef.close(payload);
  }
}
