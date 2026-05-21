import { TasksRepository } from './tasks.repository';
import { Task, CreateTaskDTO, UpdateTaskDTO, TaskFilters } from './tasks.types';
import { ApiError } from '../../utils/api-error';

export class TasksService {
  private repository: TasksRepository;

  constructor() {
    this.repository = TasksRepository.getInstance();
  }

  public async getAllTasks(filters?: TaskFilters): Promise<Task[]> {
    return this.repository.findAll(filters);
  }

  public async getTaskById(id: string): Promise<Task> {
    const task = await this.repository.findById(id);
    if (!task) {
      throw ApiError.notFound(`Task with ID '${id}' not found`);
    }
    return task;
  }

  public async createTask(dto: CreateTaskDTO): Promise<Task> {
    // Business rule: Titles must be unique
    const existingTask = await this.repository.findByTitle(dto.title);
    if (existingTask) {
      throw ApiError.badRequest(`A task with the title '${dto.title}' already exists`);
    }

    return this.repository.create(dto);
  }

  public async updateTask(id: string, dto: UpdateTaskDTO): Promise<Task> {
    // Verify task exists
    const task = await this.repository.findById(id);
    if (!task) {
      throw ApiError.notFound(`Task with ID '${id}' not found`);
    }

    // Business rule: If title is changed, check uniqueness
    if (dto.title && dto.title.toLowerCase() !== task.title.toLowerCase()) {
      const existingTask = await this.repository.findByTitle(dto.title);
      if (existingTask) {
        throw ApiError.badRequest(`A task with the title '${dto.title}' already exists`);
      }
    }

    const updatedTask = await this.repository.update(id, dto);
    if (!updatedTask) {
      throw ApiError.internal(`Failed to update task with ID '${id}'`);
    }

    return updatedTask;
  }

  public async deleteTask(id: string): Promise<void> {
    // Verify task exists
    const exists = await this.repository.findById(id);
    if (!exists) {
      throw ApiError.notFound(`Task with ID '${id}' not found`);
    }

    const deleted = await this.repository.delete(id);
    if (!deleted) {
      throw ApiError.internal(`Failed to delete task with ID '${id}'`);
    }
  }
}
