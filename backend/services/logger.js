const winston = require('winston');
const path = require('path');

// Setup logger
const setupLogger = () => {
  const logFormat = winston.format.combine(
    winston.format.timestamp({
      format: 'YYYY-MM-DD HH:mm:ss'
    }),
    winston.format.errors({ stack: true }),
    winston.format.json()
  );

  const consoleFormat = winston.format.combine(
    winston.format.colorize(),
    winston.format.timestamp({
      format: 'YYYY-MM-DD HH:mm:ss'
    }),
    winston.format.printf(({ timestamp, level, message, ...meta }) => {
      let msg = `${timestamp} [${level}]: ${message}`;
      if (Object.keys(meta).length > 0) {
        msg += ` ${JSON.stringify(meta)}`;
      }
      return msg;
    })
  );

  const logger = winston.createLogger({
    level: process.env.LOG_LEVEL || 'info',
    format: logFormat,
    transports: [
      // Error logs
      new winston.transports.File({
        filename: path.join('logs', 'error.log'),
        level: 'error',
        maxsize: 5242880, // 5MB
        maxFiles: 5
      }),
      // Combined logs
      new winston.transports.File({
        filename: path.join('logs', 'combined.log'),
        maxsize: 5242880, // 5MB
        maxFiles: 5
      }),
      // Application logs
      new winston.transports.File({
        filename: path.join('logs', 'app.log'),
        maxsize: 5242880, // 5MB
        maxFiles: 5
      })
    ]
  });

  // Add console transport in development
  if (process.env.NODE_ENV !== 'production') {
    logger.add(new winston.transports.Console({
      format: consoleFormat
    }));
  }

  return logger;
};

// Create specific loggers
const createLogger = (category) => {
  const logger = setupLogger();
  
  return {
    info: (message, meta = {}) => {
      logger.info(message, { category, ...meta });
    },
    error: (message, meta = {}) => {
      logger.error(message, { category, ...meta });
    },
    warn: (message, meta = {}) => {
      logger.warn(message, { category, ...meta });
    },
    debug: (message, meta = {}) => {
      logger.debug(message, { category, ...meta });
    },
    verbose: (message, meta = {}) => {
      logger.verbose(message, { category, ...meta });
    }
  };
};

// Audit logger for sensitive operations
const createAuditLogger = () => {
  const logger = winston.createLogger({
    level: 'info',
    format: winston.format.combine(
      winston.format.timestamp(),
      winston.format.json()
    ),
    transports: [
      new winston.transports.File({
        filename: path.join('logs', 'audit.log'),
        maxsize: 5242880, // 5MB
        maxFiles: 10
      })
    ]
  });

  return {
    logAction: (action, userId, details = {}) => {
      logger.info('Audit Action', {
        action,
        userId,
        timestamp: new Date().toISOString(),
        ip: details.ip,
        userAgent: details.userAgent,
        resource: details.resource,
        changes: details.changes,
        metadata: details.metadata
      });
    },
    
    logLogin: (userId, success, details = {}) => {
      logger.info('Login Attempt', {
        action: 'login',
        userId,
        success,
        timestamp: new Date().toISOString(),
        ip: details.ip,
        userAgent: details.userAgent,
        reason: details.reason
      });
    },
    
    logCommissionChange: (commissionId, userId, changes, details = {}) => {
      logger.info('Commission Change', {
        action: 'commission_change',
        commissionId,
        userId,
        changes,
        timestamp: new Date().toISOString(),
        ip: details.ip,
        userAgent: details.userAgent,
        reason: details.reason
      });
    },
    
    logAIAction: (action, userId, aiResponse, details = {}) => {
      logger.info('AI Action', {
        action: 'ai_action',
        userId,
        aiAction: action,
        aiConfidence: aiResponse.confidence,
        aiFactors: aiResponse.factors,
        timestamp: new Date().toISOString(),
        ip: details.ip,
        userAgent: details.userAgent,
        metadata: details.metadata
      });
    }
  };
};

// Performance logger
const createPerformanceLogger = () => {
  const logger = winston.createLogger({
    level: 'info',
    format: winston.format.combine(
      winston.format.timestamp(),
      winston.format.json()
    ),
    transports: [
      new winston.transports.File({
        filename: path.join('logs', 'performance.log'),
        maxsize: 5242880, // 5MB
        maxFiles: 5
      })
    ]
  });

  return {
    logAPICall: (endpoint, method, duration, statusCode, userId = null) => {
      logger.info('API Performance', {
        endpoint,
        method,
        duration,
        statusCode,
        userId,
        timestamp: new Date().toISOString()
      });
    },
    
    logAICalculation: (calculationType, duration, accuracy, userId = null) => {
      logger.info('AI Performance', {
        calculationType,
        duration,
        accuracy,
        userId,
        timestamp: new Date().toISOString()
      });
    },
    
    logDatabaseQuery: (collection, operation, duration, userId = null) => {
      logger.info('Database Performance', {
        collection,
        operation,
        duration,
        userId,
        timestamp: new Date().toISOString()
      });
    }
  };
};

// Error logger with context
const createErrorLogger = () => {
  const logger = winston.createLogger({
    level: 'error',
    format: winston.format.combine(
      winston.format.timestamp(),
      winston.format.errors({ stack: true }),
      winston.format.json()
    ),
    transports: [
      new winston.transports.File({
        filename: path.join('logs', 'errors.log'),
        maxsize: 5242880, // 5MB
        maxFiles: 10
      })
    ]
  });

  return {
    logError: (error, context = {}) => {
      logger.error('Application Error', {
        message: error.message,
        stack: error.stack,
        name: error.name,
        code: error.code,
        context,
        timestamp: new Date().toISOString()
      });
    },
    
    logValidationError: (errors, context = {}) => {
      logger.error('Validation Error', {
        errors,
        context,
        timestamp: new Date().toISOString()
      });
    },
    
    logSecurityError: (error, context = {}) => {
      logger.error('Security Error', {
        message: error.message,
        type: error.type,
        context,
        timestamp: new Date().toISOString()
      });
    }
  };
};

module.exports = {
  setupLogger,
  createLogger,
  createAuditLogger,
  createPerformanceLogger,
  createErrorLogger
}; 