import express, { Request, Response, NextFunction } from 'express';
import cors from 'cors';
import path from 'path';
import { tasksRouter } from './modules/tasks/tasks.router';
import { errorHandler } from './middleware/error.middleware';
import { requestLogger } from './middleware/logging.middleware';
import { ApiError } from './utils/api-error';
import { ApiResponse } from './utils/api-response';

const app = express();

// System stats trackers
const startTime = new Date();
let requestCount = 0;

// Enable CORS
app.use(cors());

// Parse incoming request JSON bodies
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Custom request logger
app.use(requestLogger);

// Count every incoming request for server stats dashboard
app.use((_req: Request, _res: Response, next: NextFunction) => {
  requestCount++;
  next();
});

// Serve premium interactive API playground at root
app.use(express.static(path.join(__dirname, 'public')));

// Server statistics endpoint
app.get('/api/system/stats', (_req: Request, res: Response) => {
  const uptime = Math.floor((Date.now() - startTime.getTime()) / 1000);
  res.json(
    ApiResponse.success(
      {
        uptimeSeconds: uptime,
        uptimeFormatted: `${Math.floor(uptime / 60)}m ${uptime % 60}s`,
        totalRequests: requestCount,
        startedAt: startTime.toISOString(),
        nodeVersion: process.version,
        platform: process.platform,
      },
      'System statistics retrieved successfully'
    )
  );
});

// Bind tasks resource pathways
app.use('/api/tasks', tasksRouter);

// Fallback 404 handler for invalid routes
app.use((req: Request, _res: Response, next: NextFunction) => {
  next(ApiError.notFound(`Cannot ${req.method} ${req.originalUrl} - Resource not found`));
});

// Global error handler middleware
app.use(errorHandler);

export default app;
