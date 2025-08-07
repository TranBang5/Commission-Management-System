const redis = require('redis');
const winston = require('winston');

// Setup logger
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: 'logs/redis.log', level: 'error' }),
    new winston.transports.File({ filename: 'logs/combined.log' })
  ]
});

// Add console transport in development
if (process.env.NODE_ENV !== 'production') {
  logger.add(new winston.transports.Console({
    format: winston.format.simple()
  }));
}

let redisClient = null;

// Connect to Redis
const connectRedis = async () => {
  try {
    redisClient = redis.createClient({
      url: process.env.REDIS_URL || `redis://${process.env.REDIS_HOST || 'localhost'}:${process.env.REDIS_PORT || 6379}`,
      password: process.env.REDIS_PASSWORD || undefined,
      retry_strategy: (options) => {
        if (options.error && options.error.code === 'ECONNREFUSED') {
          logger.error('Redis server refused connection');
          return new Error('Redis server refused connection');
        }
        if (options.total_retry_time > 1000 * 60 * 60) {
          logger.error('Redis retry time exhausted');
          return new Error('Retry time exhausted');
        }
        if (options.attempt > 10) {
          logger.error('Redis max retry attempts reached');
          return undefined;
        }
        return Math.min(options.attempt * 100, 3000);
      }
    });

    redisClient.on('error', (err) => {
      logger.error('Redis Client Error:', err);
    });

    redisClient.on('connect', () => {
      logger.info('Redis Client Connected');
    });

    redisClient.on('ready', () => {
      logger.info('Redis Client Ready');
    });

    redisClient.on('end', () => {
      logger.warn('Redis Client Disconnected');
    });

    await redisClient.connect();
    logger.info('Redis connected successfully');

  } catch (error) {
    logger.error('Error connecting to Redis:', error);
    // Don't exit process, Redis is optional for some features
  }
};

// Get Redis client
const getRedisClient = () => {
  return redisClient;
};

// Set key-value pair
const setKey = async (key, value, expireTime = null) => {
  try {
    if (!redisClient) {
      throw new Error('Redis client not connected');
    }

    const serializedValue = typeof value === 'object' ? JSON.stringify(value) : value;
    
    if (expireTime) {
      await redisClient.setEx(key, expireTime, serializedValue);
    } else {
      await redisClient.set(key, serializedValue);
    }

    logger.debug(`Redis SET: ${key}`);
    return true;
  } catch (error) {
    logger.error('Redis SET error:', error);
    return false;
  }
};

// Get value by key
const getKey = async (key) => {
  try {
    if (!redisClient) {
      throw new Error('Redis client not connected');
    }

    const value = await redisClient.get(key);
    
    if (value === null) {
      return null;
    }

    // Try to parse as JSON, if fails return as string
    try {
      return JSON.parse(value);
    } catch {
      return value;
    }
  } catch (error) {
    logger.error('Redis GET error:', error);
    return null;
  }
};

// Delete key
const deleteKey = async (key) => {
  try {
    if (!redisClient) {
      throw new Error('Redis client not connected');
    }

    const result = await redisClient.del(key);
    logger.debug(`Redis DEL: ${key}`);
    return result > 0;
  } catch (error) {
    logger.error('Redis DEL error:', error);
    return false;
  }
};

// Check if key exists
const keyExists = async (key) => {
  try {
    if (!redisClient) {
      throw new Error('Redis client not connected');
    }

    const result = await redisClient.exists(key);
    return result === 1;
  } catch (error) {
    logger.error('Redis EXISTS error:', error);
    return false;
  }
};

// Set hash field
const setHashField = async (key, field, value) => {
  try {
    if (!redisClient) {
      throw new Error('Redis client not connected');
    }

    const serializedValue = typeof value === 'object' ? JSON.stringify(value) : value;
    await redisClient.hSet(key, field, serializedValue);
    logger.debug(`Redis HSET: ${key}.${field}`);
    return true;
  } catch (error) {
    logger.error('Redis HSET error:', error);
    return false;
  }
};

// Get hash field
const getHashField = async (key, field) => {
  try {
    if (!redisClient) {
      throw new Error('Redis client not connected');
    }

    const value = await redisClient.hGet(key, field);
    
    if (value === null) {
      return null;
    }

    // Try to parse as JSON, if fails return as string
    try {
      return JSON.parse(value);
    } catch {
      return value;
    }
  } catch (error) {
    logger.error('Redis HGET error:', error);
    return null;
  }
};

// Get all hash fields
const getHashAll = async (key) => {
  try {
    if (!redisClient) {
      throw new Error('Redis client not connected');
    }

    const hash = await redisClient.hGetAll(key);
    
    // Try to parse values as JSON
    const result = {};
    for (const [field, value] of Object.entries(hash)) {
      try {
        result[field] = JSON.parse(value);
      } catch {
        result[field] = value;
      }
    }

    return result;
  } catch (error) {
    logger.error('Redis HGETALL error:', error);
    return {};
  }
};

// Add to sorted set
const addToSortedSet = async (key, member, score) => {
  try {
    if (!redisClient) {
      throw new Error('Redis client not connected');
    }

    await redisClient.zAdd(key, { score, value: member });
    logger.debug(`Redis ZADD: ${key} ${score} ${member}`);
    return true;
  } catch (error) {
    logger.error('Redis ZADD error:', error);
    return false;
  }
};

// Get sorted set range
const getSortedSetRange = async (key, start = 0, stop = -1, withScores = false) => {
  try {
    if (!redisClient) {
      throw new Error('Redis client not connected');
    }

    if (withScores) {
      return await redisClient.zRangeWithScores(key, start, stop);
    } else {
      return await redisClient.zRange(key, start, stop);
    }
  } catch (error) {
    logger.error('Redis ZRANGE error:', error);
    return [];
  }
};

// Health check for Redis
const checkRedisHealth = async () => {
  try {
    if (!redisClient) {
      return {
        status: 'disconnected',
        error: 'Redis client not initialized',
        timestamp: new Date().toISOString()
      };
    }

    await redisClient.ping();
    return {
      status: 'healthy',
      timestamp: new Date().toISOString()
    };
  } catch (error) {
    logger.error('Redis health check failed:', error);
    return {
      status: 'unhealthy',
      error: error.message,
      timestamp: new Date().toISOString()
    };
  }
};

// Close Redis connection
const closeRedis = async () => {
  try {
    if (redisClient) {
      await redisClient.quit();
      logger.info('Redis connection closed');
    }
  } catch (error) {
    logger.error('Error closing Redis connection:', error);
  }
};

module.exports = {
  connectRedis,
  getRedisClient,
  setKey,
  getKey,
  deleteKey,
  keyExists,
  setHashField,
  getHashField,
  getHashAll,
  addToSortedSet,
  getSortedSetRange,
  checkRedisHealth,
  closeRedis,
  logger
}; 