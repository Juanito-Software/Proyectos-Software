import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { CreateProjectRequest, Project } from './models';

@Injectable({ providedIn: 'root' })
export class ProjectService {
  private http = inject(HttpClient);
  private readonly apiUrl = 'http://localhost:3000/api/projects';

  listProjects(page = 1, limit = 10, search?: string): Observable<Project[]> {
    let params: Record<string, string | number> = { page, limit };
    if (search) {
      params = { ...params, search };
    }

    return this.http.get<Project[]>(this.apiUrl, { params });
  }

  createProject(payload: CreateProjectRequest): Observable<Project> {
    return this.http.post<Project>(this.apiUrl, payload);
  }

  getProject(id: string): Observable<Project> {
    return this.http.get<Project>(`${this.apiUrl}/${id}`);
  }

  deleteProject(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }
}
