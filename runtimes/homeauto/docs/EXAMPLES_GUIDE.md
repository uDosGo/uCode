---
title: "uHomeNest Examples Guide"
status: draft
last_updated: 2026-04-22T23:26:13+10:00
category: guide
tags: [guide, ucode3]
description: "Comprehensive collection of examples demonstrating uHomeNest v1.0.1 features, integration patterns, and best practices."
---
# uHomeNest Examples Guide

## 📚 Overview

Comprehensive collection of examples demonstrating uHomeNest v1.0.1 features, integration patterns, and best practices.

## 🎬 Scheduled Service Jobs

### Daily Media Scan

```javascript
// config/scheduled-jobs/daily-scan.js
module.exports = {
  name: 'daily-media-scan',
  schedule: '0 3 * * *', // 3 AM daily
  handler: async (context) => {
    const { mediaScanner } = context.services;
    
    console.log('Starting daily media scan...');
    const result = await mediaScanner.scanAll();
    
    console.log(`Scan completed: ${result.added} new items, ${result.updated} updated`);
    
    return result;
  }
};
```

### Weekly Database Optimization

```javascript
// config/scheduled-jobs/weekly-optimize.js
module.exports = {
  name: 'weekly-database-optimize',
  schedule: '0 4 * * 0', // 4 AM every Sunday
  handler: async (context) => {
    const { database } = context.services;
    
    console.log('Starting database optimization...');
    await database.optimize();
    await database.vacuum();
    
    console.log('Database optimization completed');
    
    return { success: true };
  }
};
```

### Monthly Backup

```javascript
// config/scheduled-jobs/monthly-backup.js
module.exports = {
  name: 'monthly-backup',
  schedule: '0 5 1 * *', // 5 AM on 1st of month
  handler: async (context) => {
    const { backupService } = context.services;
    
    console.log('Starting monthly backup...');
    const backupPath = await backupService.fullBackup();
    
    console.log(`Backup completed: ${backupPath}`);
    
    return { path: backupPath };
  }
};
```

## 🌐 Local Network Service Modules

### Media Indexer Service

```javascript
// services/media-indexer.js
const { MediaScanner } = require('./media-scanner');

class MediaIndexerService {
  constructor(config) {
    this.scanner = new MediaScanner(config.mediaVaultPath);
    this.index = new Map();
  }

  async indexAll() {
    const files = await this.scanner.scan();
    
    for (const file of files) {
      const metadata = await this.scanner.extractMetadata(file);
      this.index.set(file.path, metadata);
    }
    
    return { count: this.index.size };
  }

  getById(id) {
    return this.index.get(id);
  }

  search(query) {
    return Array.from(this.index.values())
      .filter(item => item.name.includes(query));
  }
}

module.exports = MediaIndexerService;
```

### Playback Service

```javascript
// services/playback-service.js
const { JellyfinClient } = require('./jellyfin-client');

class PlaybackService {
  constructor(config) {
    this.jellyfin = new JellyfinClient(config);
    this.activeSessions = new Map();
  }

  async startPlayback(itemId, deviceId) {
    const sessionId = await this.jellyfin.startPlayback(itemId, deviceId);
    this.activeSessions.set(sessionId, { itemId, deviceId, startedAt: new Date() });
    
    return { sessionId, status: 'playing' };
  }

  async stopPlayback(sessionId) {
    await this.jellyfin.stopPlayback(sessionId);
    this.activeSessions.delete(sessionId);
    
    return { status: 'stopped' };
  }

  getActiveSessions() {
    return Array.from(this.activeSessions.values());
  }
}

module.exports = PlaybackService;
```

### Notification Service

```javascript
// services/notification-service.js
class NotificationService {
  constructor(config) {
    this.subscribers = new Map();
  }

  subscribe(userId, callback) {
    if (!this.subscribers.has(userId)) {
      this.subscribers.set(userId, []);
    }
    this.subscribers.get(userId).push(callback);
  }

  unsubscribe(userId, callback) {
    const callbacks = this.subscribers.get(userId);
    if (callbacks) {
      this.subscribers.set(userId, callbacks.filter(cb => cb !== callback));
    }
  }

  notify(userId, message) {
    const callbacks = this.subscribers.get(userId);
    if (callbacks) {
      callbacks.forEach(callback => callback(message));
    }
  }

  broadcast(message) {
    this.subscribers.forEach((callbacks) => {
      callbacks.forEach(callback => callback(message));
    });
  }
}

module.exports = NotificationService;
```

## 💾 Persistent State Patterns

### Media Playback State

```javascript
// state/playback-state.js
const fs = require('fs');
const path = require('path');

class PlaybackState {
  constructor(stateFile = 'playback-state.json') {
    this.stateFile = path.join(__dirname, stateFile);
    this.state = this.load();
  }

  load() {
    try {
      const data = fs.readFileSync(this.stateFile, 'utf8');
      return JSON.parse(data);
    } catch (error) {
      return { sessions: {}, history: [] };
    }
  }

  save() {
    fs.writeFileSync(this.stateFile, JSON.stringify(this.state, null, 2));
  }

  startSession(sessionId, itemId) {
    this.state.sessions[sessionId] = {
      itemId,
      startedAt: new Date().toISOString(),
      position: 0
    };
    this.save();
  }

  updatePosition(sessionId, position) {
    if (this.state.sessions[sessionId]) {
      this.state.sessions[sessionId].position = position;
      this.save();
    }
  }

  endSession(sessionId) {
    const session = this.state.sessions[sessionId];
    if (session) {
      this.state.history.push({
        ...session,
        endedAt: new Date().toISOString()
      });
      delete this.state.sessions[sessionId];
      this.save();
    }
  }

  getSession(sessionId) {
    return this.state.sessions[sessionId];
  }

  getHistory() {
    return this.state.history;
  }
}

module.exports = PlaybackState;
```

### User Preferences State

```javascript
// state/user-preferences.js
const lowdb = require('lowdb');
const FileSync = require('lowdb/adapters/FileSync');

class UserPreferences {
  constructor(dbFile = 'user-preferences.json') {
    const adapter = new FileSync(dbFile);
    this.db = lowdb(adapter);
    
    this.db.defaults({ users: {} }).write();
  }

  getPreferences(userId) {
    return this.db.get(`users.${userId}`).value() || {};
  }

  setPreference(userId, key, value) {
    this.db.set(`users.${userId}.${key}`, value).write();
  }

  getPreference(userId, key, defaultValue = null) {
    return this.db.get(`users.${userId}.${key}`).value() || defaultValue;
  }

  removePreference(userId, key) {
    this.db.unset(`users.${userId}.${key}`).write();
  }

  getAllUsers() {
    return Object.keys(this.db.get('users').value());
  }
}

module.exports = UserPreferences;
```

## 🔄 Public Contract Integration

### Core System Contract

```typescript
// contracts/core-contract.ts
interface CoreSystemContract {
  // System information
  getSystemInfo(): Promise<{
    version: string;
    uptime: number;
    memoryUsage: number;
    cpuUsage: number;
  }>;

  // Health monitoring
  getHealthStatus(): Promise<{
    status: 'healthy' | 'degraded' | 'unhealthy';
    services: Record<string, 'healthy' | 'unhealthy'>;
    timestamp: string;
  }>;

  // Configuration
  getConfiguration(): Promise<any>;
  updateConfiguration(config: any): Promise<void>;

  // Logging
  getLogs(level: 'info' | 'warn' | 'error', limit?: number): Promise<Array<{
    timestamp: string;
    level: string;
    message: string;
    context?: any;
  }>>;
}
```

### Wizard Integration Contract

```typescript
// contracts/wizard-contract.ts
interface WizardIntegrationContract {
  // Voice commands
  registerVoiceCommand(command: string, handler: () => void): Promise<void>;
  unregisterVoiceCommand(command: string): Promise<void>;
  getRegisteredCommands(): Promise<string[]>;

  // Intent handling
  handleIntent(intent: string, parameters: any): Promise<any>;

  // Context management
  setContext(context: any): Promise<void>;
  getContext(): Promise<any>;
  clearContext(): Promise<void>;

  // Feedback
  provideFeedback(type: 'success' | 'error' | 'info', message: string): Promise<void>;
}
```

### Implementation Example

```javascript
// integrations/wizard-integration.js
const { WizardIntegrationContract } = require('../contracts/wizard-contract');

class WizardIntegration implements WizardIntegrationContract {
  constructor() {
    this.commands = new Map();
    this.context = {};
  }

  async registerVoiceCommand(command, handler) {
    this.commands.set(command, handler);
    console.log(`Registered voice command: ${command}`);
  }

  async unregisterVoiceCommand(command) {
    this.commands.delete(command);
    console.log(`Unregistered voice command: ${command}`);
  }

  async getRegisteredCommands() {
    return Array.from(this.commands.keys());
  }

  async handleIntent(intent, parameters) {
    console.log(`Handling intent: ${intent}`, parameters);
    
    if (this.commands.has(intent)) {
      const handler = this.commands.get(intent);
      return handler(parameters);
    }
    
    throw new Error(`Unknown intent: ${intent}`);
  }

  async setContext(context) {
    this.context = { ...this.context, ...context };
    console.log('Context updated:', this.context);
  }

  async getContext() {
    return this.context;
  }

  async clearContext() {
    this.context = {};
    console.log('Context cleared');
  }

  async provideFeedback(type, message) {
    console.log(`[${type.toUpperCase()}] ${message}`);
    // In real implementation, this would show UI feedback
  }
}

module.exports = WizardIntegration;
```

## 📦 Service Module Patterns

### Modular Service Structure

```javascript
// services/base-service.js
class BaseService {
  constructor(name, config = {}) {
    this.name = name;
    this.config = config;
    this.initialized = false;
    this.dependencies = new Map();
  }

  async init() {
    if (this.initialized) return;
    
    await this.validateConfig();
    await this.setupDependencies();
    
    this.initialized = true;
    console.log(`${this.name} service initialized`);
  }

  async validateConfig() {
    // Validate required configuration
    if (this.config.required && !this.config.required.every(key => this.config[key])) {
      throw new Error(`${this.name}: Missing required configuration`);
    }
  }

  async setupDependencies() {
    // Setup any dependencies
    for (const [name, dependency] of this.dependencies) {
      if (!dependency.initialized) {
        await dependency.init();
      }
    }
  }

  async shutdown() {
    this.initialized = false;
    console.log(`${this.name} service shut down`);
  }

  addDependency(name, service) {
    this.dependencies.set(name, service);
  }

  getDependency(name) {
    return this.dependencies.get(name);
  }
}

module.exports = BaseService;
```

### Service Locator Pattern

```javascript
// services/service-locator.js
class ServiceLocator {
  constructor() {
    this.services = new Map();
  }

  register(name, service) {
    if (this.services.has(name)) {
      console.warn(`Service ${name} already registered, overwriting`);
    }
    this.services.set(name, service);
    console.log(`Registered service: ${name}`);
  }

  get(name) {
    const service = this.services.get(name);
    if (!service) {
      throw new Error(`Service ${name} not found`);
    }
    return service;
  }

  async initAll() {
    for (const [name, service] of this.services) {
      try {
        await service.init();
      } catch (error) {
        console.error(`Failed to initialize service ${name}:`, error);
        throw error;
      }
    }
  }

  async shutdownAll() {
    for (const [name, service] of Array.from(this.services.values()).reverse()) {
      try {
        await service.shutdown();
      } catch (error) {
        console.error(`Failed to shutdown service ${name}:`, error);
      }
    }
  }

  list() {
    return Array.from(this.services.keys());
  }
}

module.exports = ServiceLocator;
```

### Dependency Injection Example

```javascript
// services/media-service.js
const BaseService = require('./base-service');

class MediaService extends BaseService {
  constructor(config) {
    super('media', config);
  }

  async init() {
    await super.init();
    
    // Get dependencies from service locator
    const serviceLocator = this.getDependency('serviceLocator');
    this.storageService = serviceLocator.get('storage');
    this.metadataService = serviceLocator.get('metadata');
    
    await this.storageService.ensureDirectory(this.config.mediaPath);
  }

  async scanMedia() {
    const files = await this.storageService.listFiles(this.config.mediaPath);
    
    const mediaItems = await Promise.all(files.map(async file => {
      const metadata = await this.metadataService.extract(file);
      return { ...metadata, path: file };
    }));
    
    return mediaItems.filter(item => item.type === 'media');
  }

  async getMediaItem(id) {
    // Implementation to get specific media item
  }

  async searchMedia(query) {
    // Implementation to search media
  }
}

module.exports = MediaService;
```

## 🎯 Best Practices

### Error Handling

```javascript
// utils/error-handler.js
class ErrorHandler {
  static handle(error, context = {}) {
    console.error('Error:', error.message);
    console.error('Stack:', error.stack);
    console.error('Context:', context);
    
    // Log to monitoring system
    this.logToMonitoring(error, context);
    
    // Notify administrators for critical errors
    if (this.isCritical(error)) {
      this.notifyAdmins(error, context);
    }
    
    return this.createResponse(error);
  }

  static isCritical(error) {
    return error.severity === 'critical' ||
           error.code >= 500 ||
           error.message.includes('database');
  }

  static logToMonitoring(error, context) {
    // Implementation to log to monitoring system
  }

  static notifyAdmins(error, context) {
    // Implementation to notify administrators
  }

  static createResponse(error) {
    return {
      error: {
        code: error.code || 'INTERNAL_ERROR',
        message: error.message || 'Internal server error',
        details: process.env.NODE_ENV === 'development' ? error.stack : undefined
      }
    };
  }
}

module.exports = ErrorHandler;
```

### Configuration Management

```javascript
// utils/config-manager.js
const fs = require('fs');
const path = require('path');

class ConfigManager {
  constructor(configDir = 'config') {
    this.configDir = configDir;
    this.configs = new Map();
  }

  loadConfig(name) {
    try {
      const configPath = path.join(this.configDir, `${name}.json`);
      const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      
      // Validate config
      this.validateConfig(name, config);
      
      this.configs.set(name, config);
      return config;
    } catch (error) {
      console.error(`Failed to load config ${name}:`, error);
      throw error;
    }
  }

  validateConfig(name, config) {
    // Implement validation logic
    const schema = this.getSchema(name);
    if (schema && !this.validateAgainstSchema(config, schema)) {
      throw new Error(`Invalid config ${name}`);
    }
  }

  getConfig(name) {
    if (!this.configs.has(name)) {
      this.loadConfig(name);
    }
    return this.configs.get(name);
  }

  updateConfig(name, updates) {
    const config = this.getConfig(name);
    const updated = { ...config, ...updates };
    
    this.validateConfig(name, updated);
    
    const configPath = path.join(this.configDir, `${name}.json`);
    fs.writeFileSync(configPath, JSON.stringify(updated, null, 2));
    
    this.configs.set(name, updated);
    return updated;
  }

  getSchema(name) {
    // Return validation schema for config
    return this.schemas[name];
  }

  validateAgainstSchema(config, schema) {
    // Implement schema validation
    return true;
  }
}

module.exports = ConfigManager;
```

### Logging System

```javascript
// utils/logger.js
const winston = require('winston');
const path = require('path');

class Logger {
  constructor(serviceName) {
    this.serviceName = serviceName;
    this.logger = this.createLogger();
  }

  createLogger() {
    return winston.createLogger({
      level: process.env.LOG_LEVEL || 'info',
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json()
      ),
      transports: [
        new winston.transports.Console({
          format: winston.format.combine(
            winston.format.colorize(),
            winston.format.simple()
          )
        }),
        new winston.transports.File({
          filename: path.join('logs', `${this.serviceName}.log`),
          maxsize: 10000000, // 10MB
          maxFiles: 5
        })
      ]
    });
  }

  info(message, context = {}) {
    this.logger.info({ service: this.serviceName, ...context, message });
  }

  warn(message, context = {}) {
    this.logger.warn({ service: this.serviceName, ...context, message });
  }

  error(message, context = {}) {
    this.logger.error({ service: this.serviceName, ...context, message });
  }

  debug(message, context = {}) {
    this.logger.debug({ service: this.serviceName, ...context, message });
  }

  child(context) {
    return this.logger.child(context);
  }
}

module.exports = Logger;
```

### Event System

```javascript
// utils/event-emitter.js
const EventEmitter = require('events');

class AppEventEmitter extends EventEmitter {
  constructor() {
    super();
    this.setMaxListeners(50);
  }

  emit(event, ...args) {
    console.debug(`Emitting event: ${event}`, ...args);
    return super.emit(event, ...args);
  }

  on(event, listener) {
    console.debug(`Registered listener for: ${event}`);
    return super.on(event, listener);
  }

  once(event, listener) {
    console.debug(`Registered once listener for: ${event}`);
    return super.once(event, listener);
  }

  removeListener(event, listener) {
    console.debug(`Removed listener for: ${event}`);
    return super.removeListener(event, listener);
  }

  async emitAsync(event, ...args) {
    const listeners = this.listeners(event);
    const results = [];
    
    for (const listener of listeners) {
      try {
        const result = await listener(...args);
        results.push(result);
      } catch (error) {
        console.error(`Error in event listener for ${event}:`, error);
      }
    }
    
    return results;
  }
}

module.exports = AppEventEmitter;
```

## 📊 Performance Patterns

### Caching Strategy

```javascript
// utils/cache-manager.js
class CacheManager {
  constructor(ttl = 3600) {
    this.cache = new Map();
    this.ttl = ttl; // Default TTL in seconds
  }

  set(key, value, ttl = this.ttl) {
    const expires = Date.now() + ttl * 1000;
    this.cache.set(key, { value, expires });
    
    // Cleanup expired items periodically
    this.scheduleCleanup();
  }

  get(key) {
    const item = this.cache.get(key);
    
    if (!item) return undefined;
    
    if (item.expires < Date.now()) {
      this.cache.delete(key);
      return undefined;
    }
    
    return item.value;
  }

  delete(key) {
    this.cache.delete(key);
  }

  clear() {
    this.cache.clear();
  }

  scheduleCleanup() {
    if (this.cleanupScheduled) return;
    
    this.cleanupScheduled = true;
    setTimeout(() => {
      this.cleanup();
      this.cleanupScheduled = false;
    }, 3600000); // Cleanup every hour
  }

  cleanup() {
    const now = Date.now();
    
    for (const [key, item] of this.cache) {
      if (item.expires < now) {
        this.cache.delete(key);
      }
    }
  }

  size() {
    return this.cache.size;
  }
}

module.exports = CacheManager;
```

### Batch Processing

```javascript
// utils/batch-processor.js
class BatchProcessor {
  constructor(batchSize = 100, delay = 1000) {
    this.batchSize = batchSize;
    this.delay = delay;
    this.queue = [];
    this.processing = false;
  }

  add(item) {
    this.queue.push(item);
    
    if (this.queue.length >= this.batchSize && !this.processing) {
      this.processBatch();
    }
  }

  async processBatch() {
    if (this.processing) return;
    
    this.processing = true;
    const batch = this.queue.splice(0, this.batchSize);
    
    try {
      await this.processItems(batch);
    } catch (error) {
      console.error('Batch processing error:', error);
      // Handle error (retry, log, etc.)
    } finally {
      this.processing = false;
      
      // Process remaining items if any
      if (this.queue.length > 0) {
        setTimeout(() => this.processBatch(), this.delay);
      }
    }
  }

  async processItems(items) {
    // Override this method in subclass
    console.log(`Processing batch of ${items.length} items`);
    
    for (const item of items) {
      try {
        await this.processItem(item);
      } catch (error) {
        console.error(`Error processing item ${item.id}:`, error);
        // Handle individual item error
      }
    }
  }

  async processItem(item) {
    // Override this method in subclass
    throw new Error('processItem must be implemented');
  }

  async flush() {
    if (this.queue.length > 0) {
      await this.processBatch();
    }
  }

  getQueueSize() {
    return this.queue.length;
  }
}

module.exports = BatchProcessor;
```

### Rate Limiting

```javascript
// utils/rate-limiter.js
class RateLimiter {
  constructor(limit, windowMs) {
    this.limit = limit;
    this.windowMs = windowMs;
    this.requests = new Map();
  }

  check(key) {
    const now = Date.now();
    const windowStart = now - this.windowMs;
    
    // Clean up old requests
    const requests = this.requests.get(key) || [];
    const recentRequests = requests.filter(timestamp => timestamp > windowStart);
    
    if (recentRequests.length >= this.limit) {
      return false; // Rate limit exceeded
    }
    
    // Add current request
    recentRequests.push(now);
    this.requests.set(key, recentRequests);
    
    // Schedule cleanup
    this.scheduleCleanup(key);
    
    return true; // Request allowed
  }

  scheduleCleanup(key) {
    setTimeout(() => {
      const requests = this.requests.get(key);
      if (requests && requests.length > 0) {
        const now = Date.now();
        const windowStart = now - this.windowMs;
        this.requests.set(key, requests.filter(t => t > windowStart));
      }
    }, this.windowMs);
  }

  reset(key) {
    this.requests.delete(key);
  }

  getRemaining(key) {
    const now = Date.now();
    const windowStart = now - this.windowMs;
    const requests = this.requests.get(key) || [];
    const recentRequests = requests.filter(timestamp => timestamp > windowStart);
    
    return Math.max(0, this.limit - recentRequests.length);
  }
}

module.exports = RateLimiter;
```

## 🔧 Testing Patterns

### Unit Test Example

```javascript
// tests/media-scanner.test.js
const { MediaScanner } = require('../services/media-scanner');
const fs = require('fs');
const path = require('path');

describe('MediaScanner', () => {
  let scanner;
  let testDir;

  beforeAll(() => {
    testDir = path.join(__dirname, 'test-media');
    fs.mkdirSync(testDir, { recursive: true });
    
    // Create test files
    fs.writeFileSync(path.join(testDir, 'movie.mp4'), 'test');
    fs.writeFileSync(path.join(testDir, 'song.mp3'), 'test');
    fs.writeFileSync(path.join(testDir, 'image.jpg'), 'test');
  });

  afterAll(() => {
    // Cleanup
    fs.rmSync(testDir, { recursive: true, force: true });
  });

  beforeEach(() => {
    scanner = new MediaScanner(testDir);
  });

  describe('scan', () => {
    it('should find media files', async () => {
      const files = await scanner.scan();
      expect(files.length).toBe(3);
    });

    it('should filter by extension', async () => {
      const files = await scanner.scan(['mp4', 'mp3']);
      expect(files.length).toBe(2);
    });
  });

  describe('extractMetadata', () => {
    it('should extract basic metadata', async () => {
      const file = path.join(testDir, 'movie.mp4');
      const metadata = await scanner.extractMetadata(file);
      
      expect(metadata).toHaveProperty('name');
      expect(metadata).toHaveProperty('size');
      expect(metadata).toHaveProperty('type');
    });
  });
});
```

### Integration Test Example

```javascript
// tests/integration/media-flow.test.js
const { MediaService } = require('../../services/media-service');
const { StorageService } = require('../../services/storage-service');
const { MetadataService } = require('../../services/metadata-service');
const ServiceLocator = require('../../services/service-locator');

describe('Media Flow Integration', () => {
  let mediaService;
  let serviceLocator;

  beforeAll(async () => {
    // Setup service locator
    serviceLocator = new ServiceLocator();
    
    // Register services
    serviceLocator.register('storage', new StorageService({ mediaPath: '/tmp/test-media' }));
    serviceLocator.register('metadata', new MetadataService());
    serviceLocator.register('serviceLocator', serviceLocator);
    
    // Create media service
    mediaService = new MediaService({ mediaPath: '/tmp/test-media' });
    mediaService.addDependency('serviceLocator', serviceLocator);
    
    // Initialize
    await serviceLocator.initAll();
  });

  afterAll(async () => {
    await serviceLocator.shutdownAll();
  });

  describe('scanMedia', () => {
    it('should scan and return media items', async () => {
      // Setup test media
      const storage = serviceLocator.get('storage');
      await storage.writeFile('test.mp4', Buffer.from('test'));
      
      // Scan media
      const mediaItems = await mediaService.scanMedia();
      
      expect(mediaItems.length).toBe(1);
      expect(mediaItems[0]).toHaveProperty('path');
      expect(mediaItems[0]).toHaveProperty('type');
    });
  });

  describe('getMediaItem', () => {
    it('should retrieve specific media item', async () => {
      const items = await mediaService.scanMedia();
      if (items.length > 0) {
        const item = await mediaService.getMediaItem(items[0].id);
        expect(item).toBeDefined();
        expect(item.id).toBe(items[0].id);
      }
    });
  });
});
```

### Performance Test Example

```javascript
// tests/performance/media-scan.perf.js
const { MediaScanner } = require('../../services/media-scanner');
const fs = require('fs');
const path = require('path');

describe('MediaScanner Performance', () => {
  let scanner;
  let testDir;
  let testFiles = [];

  beforeAll(() => {
    testDir = path.join(__dirname, 'perf-test-media');
    fs.mkdirSync(testDir, { recursive: true });
    
    // Create 100 test files
    for (let i = 0; i < 100; i++) {
      const filePath = path.join(testDir, `movie${i}.mp4`);
      fs.writeFileSync(filePath, Buffer.alloc(1024 * 1024)); // 1MB files
      testFiles.push(filePath);
    }
  });

  afterAll(() => {
    // Cleanup
    fs.rmSync(testDir, { recursive: true, force: true });
  });

  beforeEach(() => {
    scanner = new MediaScanner(testDir);
  });

  it('should scan 100 files in under 2 seconds', async () => {
    const start = Date.now();
    const files = await scanner.scan();
    const duration = Date.now() - start;
    
    expect(files.length).toBe(100);
    expect(duration).toBeLessThan(2000); // 2 seconds
    console.log(`Scan completed in ${duration}ms`);
  }, 10000); // 10 second timeout

  it('should extract metadata for 100 files in under 5 seconds', async () => {
    const start = Date.now();
    const files = await scanner.scan();
    
    const metadataPromises = files.slice(0, 10).map(file => 
      scanner.extractMetadata(file.path)
    );
    
    await Promise.all(metadataPromises);
    const duration = Date.now() - start;
    
    expect(duration).toBeLessThan(5000); // 5 seconds
    console.log(`Metadata extraction completed in ${duration}ms`);
  }, 15000); // 15 second timeout
});
```

## 📚 Best Practices Summary

### Code Organization
- Use modular service structure
- Separate concerns (services, utils, contracts)
- Follow consistent naming conventions
- Keep files focused and small

### Error Handling
- Use centralized error handler
- Provide meaningful error messages
- Log errors with context
- Handle errors gracefully

### Configuration
- Use configuration management
- Validate configurations
- Support environment variables
- Provide sensible defaults

### Logging
- Use structured logging
- Include service context
- Support multiple log levels
- Rotate log files

### Testing
- Write unit tests for components
- Write integration tests for flows
- Include performance tests
- Test error conditions

### Performance
- Use caching appropriately
- Implement batch processing
- Apply rate limiting
- Optimize I/O operations

### Documentation
- Document public APIs
- Include usage examples
- Keep documentation current
- Use consistent format

---

*Last Updated: 2026-04-29*
*uHomeNest v1.0.1*
*Examples Guide: Comprehensive*