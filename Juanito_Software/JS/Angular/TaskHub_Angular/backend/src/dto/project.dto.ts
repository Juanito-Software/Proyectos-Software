export interface CreateProjectInput {
  name: string;
  description?: string;
}

export interface UpdateProjectInput {
  name?: string;
  description?: string;
}

export interface AddMemberInput {
  email: string;
  role?: 'EDITOR' | 'VIEWER';
}
