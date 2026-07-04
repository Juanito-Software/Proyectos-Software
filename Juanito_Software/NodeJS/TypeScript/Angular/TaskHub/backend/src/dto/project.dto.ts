export interface CreateProjectInput {
  name: string;
  description?: string;
}

export interface UpdateProjectInput {
  name?: string;
  description?: string;
}

export interface AddMemberInput {
  userId: string;
  role?: 'OWNER' | 'EDITOR' | 'VIEWER';
}
