import { Component, inject } from '@angular/core';
import { NgFor, NgIf } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { ProjectService } from '../../core/project.service';
import { AssignableProjectRole, Project, ProjectMember } from '../../core/models';

export interface MembersDialogData {
  project: Project;
}

const ROLE_LABELS: Record<ProjectMember['role'], string> = {
  OWNER: 'Propietario',
  EDITOR: 'Editor',
  VIEWER: 'Lector',
};

/**
 * Miembros de un proyecto: la lista actual y un formulario para añadir por email.
 *
 * El dialogo hace la peticion el mismo, en vez de devolver el formulario a
 * ProjectDetail como los de crear tarea, para poder enseñar el error sin
 * cerrarse: si el email no existe o ya es miembro, el propietario tiene que
 * verlo y poder corregirlo sin volver a escribir todo.
 */
@Component({
  selector: 'app-members-dialog',
  standalone: true,
  imports: [NgFor, NgIf, FormsModule, MatDialogModule, MatFormFieldModule, MatInputModule, MatSelectModule, MatButtonModule],
  template: `
    <h2 mat-dialog-title>Miembros de «{{ data.project.name }}»</h2>
    <div mat-dialog-content class="dialog-content">
      <ul class="member-list">
        <li class="member" *ngFor="let m of members">
          <div>
            <strong>{{ m.user.name }}</strong>
            <span class="member-email">{{ m.user.email }}</span>
          </div>
          <span class="member-role">{{ roleLabel(m.role) }}</span>
        </li>
      </ul>

      <form class="add-member" (ngSubmit)="add()">
        <h3>Añadir miembro</h3>
        <mat-form-field appearance="outline">
          <mat-label>Email</mat-label>
          <input matInput type="email" [(ngModel)]="email" name="email" autocomplete="off" />
        </mat-form-field>
        <mat-form-field appearance="outline">
          <mat-label>Rol</mat-label>
          <mat-select [(ngModel)]="role" name="role">
            <mat-option value="EDITOR">Editor: crea, edita y comenta tareas</mat-option>
            <mat-option value="VIEWER">Lector: solo puede verlas</mat-option>
          </mat-select>
        </mat-form-field>
        <p class="error" role="alert" *ngIf="error">{{ error }}</p>
        <button mat-flat-button color="primary" type="submit" [disabled]="!email.trim() || saving">Añadir</button>
      </form>
    </div>
    <div mat-dialog-actions align="end">
      <button mat-button type="button" (click)="dialogRef.close()">Cerrar</button>
    </div>
  `,
  styles: [`
    .dialog-content { display: flex; flex-direction: column; gap: 1rem; min-width: min(90vw, 440px); }
    .member-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.5rem; }
    .member { display: flex; justify-content: space-between; align-items: center; gap: 0.5rem;
              background: #f1f3f9; border-radius: 6px; padding: 0.5rem 0.75rem; }
    .member-email { display: block; font-size: 0.8rem; color: rgba(0,0,0,0.6); }
    .member-role { font-size: 0.85rem; }
    .add-member { display: flex; flex-direction: column; gap: 0.25rem; }
    .add-member h3 { margin: 0 0 0.5rem; font-size: 0.95rem; }
    .add-member button { align-self: flex-end; }
    .error { color: #b3261e; margin: 0; font-size: 0.85rem; }
  `],
})
export class MembersDialogComponent {
  dialogRef = inject(MatDialogRef<MembersDialogComponent>);
  data: MembersDialogData = inject(MAT_DIALOG_DATA);
  private projectService = inject(ProjectService);

  members: ProjectMember[] = [...(this.data.project.members ?? [])];
  email = '';
  // Por defecto el rol con menos permisos: equivocarse aqui debe costar poco.
  role: AssignableProjectRole = 'VIEWER';
  saving = false;
  error = '';

  roleLabel(role: ProjectMember['role']): string {
    return ROLE_LABELS[role] ?? role;
  }

  add(): void {
    const email = this.email.trim();
    if (!email || this.saving) return;

    this.saving = true;
    this.error = '';
    this.projectService.addMember(this.data.project.id, { email, role: this.role }).subscribe({
      next: (member) => {
        this.saving = false;
        this.members = [...this.members, member];
        this.email = '';
      },
      error: (err: HttpErrorResponse) => {
        this.saving = false;
        this.error = errorMessage(err);
      },
    });
  }
}

/**
 * 404 y 409 traen un mensaje pensado para el usuario («No existe ningún usuario
 * con ese email», «Ese usuario ya es miembro del proyecto») y se enseña tal
 * cual. El resto se traduce aqui, sin exponer lo que diga el servidor.
 */
function errorMessage(err: HttpErrorResponse): string {
  if ((err.status === 404 || err.status === 409) && typeof err.error?.message === 'string') {
    return err.error.message;
  }
  if (err.status === 400) {
    return err.error?.errors?.email?.[0] ?? 'Revisa el email y el rol';
  }
  if (err.status === 403) {
    return 'Solo el propietario del proyecto puede añadir miembros';
  }
  return 'No se pudo añadir el miembro. Inténtalo de nuevo.';
}
