import { Task, CreateTaskDTO, UpdateTaskDTO, TaskFilters } from './tasks.types';

export class TasksRepository {
  private tasks: Task[] = [];
  private static instance: TasksRepository;

  private constructor() {
    // Seed initial data
    this.seedTasks();
  }

  public static getInstance(): TasksRepository {
    if (!TasksRepository.instance) {
      TasksRepository.instance = new TasksRepository();
    }
    return TasksRepository.instance;
  }

  private seedTasks(): void {
    const now = new Date();
    this.tasks = [
      {
        id: 'task-1',
        title: 'Learn TypeScript and clean coding',
        description: 'Understand strict type checking, interface contracts, and modular codebase structure.',
        status: 'completed',
        priority: 'high',
        createdAt: new Date(now.getTime() - 24 * 60 * 60 * 1000 * 3), // 3 days ago
        updatedAt: new Date(now.getTime() - 24 * 60 * 60 * 1000 * 3),
      },
      {
        id: 'task-2',
        title: 'Build Express CRUD API',
        description: 'Implement a highly-typed layered backend using Express router, controller, service, and repository architecture.',
        status: 'in-progress',
        priority: 'high',
        createdAt: new Date(now.getTime() - 24 * 60 * 60 * 1000), // 1 day ago
        updatedAt: now,
      },
      {
        id: 'task-3',
        title: 'Design high-end developer dashboard UI',
        description: 'Build a glassmorphic front-end interface featuring dynamic request counters, logs, and a live testing panel.',
        status: 'pending',
        priority: 'medium',
        createdAt: now,
        updatedAt: now,
      },
    ];
  }

  // Simulate database latency (e.g., 50ms)
  private async delay(ms: number = 50): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  public async findAll(filters?: TaskFilters): Promise<Task[]> {
    await this.delay();
    let result = [...this.tasks];

    if (filters) {
      if (filters.status) {
        result = result.filter((t) => t.status === filters.status);
      }
      if (filters.priority) {
        result = result.filter((t) => t.priority === filters.priority);
      }
      if (filters.search) {
        const query = filters.search.toLowerCase();
        result = result.filter(
          (t) =>
            t.title.toLowerCase().includes(query) ||
            t.description.toLowerCase().includes(query)
        );
      }
    }

    // Sort by createdAt descending by default
    return result.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
  }

  public async findById(id: string): Promise<Task | null> {
    await this.delay();
    const task = this.tasks.find((t) => t.id === id);
    return task ? { ...task } : null;
  }

  public async findByTitle(title: string): Promise<Task | null> {
    await this.delay();
    const task = this.tasks.find(
      (t) => t.title.toLowerCase() === title.toLowerCase()
    );
    return task ? { ...task } : null;
  }

  public async create(dto: CreateTaskDTO): Promise<Task> {
    await this.delay();
    const now = new Date();
    const newTask: Task = {
      id: `task-${Math.random().toString(36).substring(2, 11)}`,
      title: dto.title,
      description: dto.description,
      status: dto.status || 'pending',
      priority: dto.priority || 'medium',
      createdAt: now,
      updatedAt: now,
    };

    this.tasks.push(newTask);
    return { ...newTask };
  }

  public async update(id: string, dto: UpdateTaskDTO): Promise<Task | null> {
    await this.delay();
    const index = this.tasks.findIndex((t) => t.id === id);
    if (index === -1) return null;

    const currentTask = this.tasks[index];
    const updatedTask: Task = {
      ...currentTask,
      ...dto,
      id: currentTask.id, // Ensure ID cannot be changed
      createdAt: currentTask.createdAt, // Ensure creation date remains constant
      updatedAt: new Date(),
    };

    this.tasks[index] = updatedTask;
    return { ...updatedTask };
  }

  public async delete(id: string): Promise<boolean> {
    await this.delay();
    const index = this.tasks.findIndex((t) => t.id === id);
    if (index === -1) return false;

    this.tasks.splice(index, 1);
    return true;
  }
}
