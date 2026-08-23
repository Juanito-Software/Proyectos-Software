import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Comment, CreateTaskRequest, Task, UpdateTaskRequest } from './models';

@Injectable({ providedIn: 'root' })
export class TaskService {
  private http = inject(HttpClient);
  private readonly apiUrl = 'http://localhost:3000/api/tasks';

  listByProject(projectId: string): Observable<Task[]> {
    return this.http.get<Task[]>(this.apiUrl, { params: { projectId } });
  }

  getTask(id: string): Observable<Task> {
    return this.http.get<Task>(`${this.apiUrl}/${id}`);
  }

  createTask(payload: CreateTaskRequest): Observable<Task> {
    return this.http.post<Task>(this.apiUrl, payload);
  }

  updateTask(id: string, payload: UpdateTaskRequest): Observable<Task> {
    return this.http.put<Task>(`${this.apiUrl}/${id}`, payload);
  }

  deleteTask(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }

  addComment(taskId: string, text: string): Observable<Comment> {
    return this.http.post<Comment>(`${this.apiUrl}/${taskId}/comments`, { text });
  }
}
