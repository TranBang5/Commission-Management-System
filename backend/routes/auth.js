const express = require('express');
const Joi = require('joi');
const User = require('../models/User');
const { generateToken, hashPassword, comparePassword } = require('../middleware/auth');
const { authLimiter } = require('../middleware/rateLimiter');
const { asyncHandler } = require('../middleware/errorHandler');
const { createAuditLogger } = require('../services/logger');

const router = express.Router();
const auditLogger = createAuditLogger();

// Validation schemas
const registerSchema = Joi.object({
  username: Joi.string().min(3).max(30).required(),
  email: Joi.string().email().required(),
  password: Joi.string().min(6).required(),
  firstName: Joi.string().max(50).required(),
  lastName: Joi.string().max(50).required(),
  role: Joi.string().valid('admin', 'manager', 'staff', 'partner').default('staff'),
  department: Joi.string().max(100).optional(),
  position: Joi.string().max(100).optional(),
  employeeId: Joi.string().optional(),
  phone: Joi.string().pattern(/^[\+]?[1-9][\d]{0,15}$/).optional()
});

const loginSchema = Joi.object({
  email: Joi.string().email().required(),
  password: Joi.string().required()
});

const changePasswordSchema = Joi.object({
  currentPassword: Joi.string().required(),
  newPassword: Joi.string().min(6).required(),
  confirmPassword: Joi.string().valid(Joi.ref('newPassword')).required()
});

// @route   POST /api/auth/register
// @desc    Register new user
// @access  Public (Admin only in production)
router.post('/register', authLimiter, asyncHandler(async (req, res) => {
  const { error, value } = registerSchema.validate(req.body);
  if (error) {
    return res.status(400).json({
      success: false,
      message: 'Validation error',
      errors: error.details.map(detail => ({
        field: detail.path.join('.'),
        message: detail.message
      }))
    });
  }

  // Check if user already exists
  const existingUser = await User.findOne({
    $or: [{ email: value.email }, { username: value.username }]
  });

  if (existingUser) {
    return res.status(400).json({
      success: false,
      message: 'User already exists with this email or username'
    });
  }

  // Create new user
  const user = new User(value);
  await user.save();

  // Generate token
  const token = generateToken(user._id);

  // Log audit
  auditLogger.logAction('user_registered', user._id, {
    ip: req.ip,
    userAgent: req.get('User-Agent'),
    resource: 'user',
    changes: { action: 'created', userId: user._id }
  });

  res.status(201).json({
    success: true,
    message: 'User registered successfully',
    data: {
      user: {
        id: user._id,
        username: user.username,
        email: user.email,
        firstName: user.firstName,
        lastName: user.lastName,
        role: user.role,
        department: user.department,
        position: user.position
      },
      token
    }
  });
}));

// @route   POST /api/auth/login
// @desc    Login user
// @access  Public
router.post('/login', authLimiter, asyncHandler(async (req, res) => {
  const { error, value } = loginSchema.validate(req.body);
  if (error) {
    return res.status(400).json({
      success: false,
      message: 'Validation error',
      errors: error.details.map(detail => ({
        field: detail.path.join('.'),
        message: detail.message
      }))
    });
  }

  // Find user by email
  const user = await User.findOne({ email: value.email.toLowerCase() });
  if (!user) {
    auditLogger.logLogin(null, false, {
      ip: req.ip,
      userAgent: req.get('User-Agent'),
      reason: 'User not found'
    });
    return res.status(401).json({
      success: false,
      message: 'Invalid credentials'
    });
  }

  // Check if account is locked
  if (user.isLocked) {
    auditLogger.logLogin(user._id, false, {
      ip: req.ip,
      userAgent: req.get('User-Agent'),
      reason: 'Account locked'
    });
    return res.status(401).json({
      success: false,
      message: 'Account is locked. Please try again later.'
    });
  }

  // Check if user is active
  if (!user.isActive) {
    auditLogger.logLogin(user._id, false, {
      ip: req.ip,
      userAgent: req.get('User-Agent'),
      reason: 'Account inactive'
    });
    return res.status(401).json({
      success: false,
      message: 'Account is inactive'
    });
  }

  // Verify password
  const isPasswordValid = await user.comparePassword(value.password);
  if (!isPasswordValid) {
    await user.incLoginAttempts();
    auditLogger.logLogin(user._id, false, {
      ip: req.ip,
      userAgent: req.get('User-Agent'),
      reason: 'Invalid password'
    });
    return res.status(401).json({
      success: false,
      message: 'Invalid credentials'
    });
  }

  // Reset login attempts on successful login
  await user.resetLoginAttempts();

  // Generate token
  const token = generateToken(user._id);

  // Log successful login
  auditLogger.logLogin(user._id, true, {
    ip: req.ip,
    userAgent: req.get('User-Agent')
  });

  res.json({
    success: true,
    message: 'Login successful',
    data: {
      user: {
        id: user._id,
        username: user.username,
        email: user.email,
        firstName: user.firstName,
        lastName: user.lastName,
        role: user.role,
        department: user.department,
        position: user.position,
        preferences: user.preferences
      },
      token
    }
  });
}));

// @route   POST /api/auth/refresh
// @desc    Refresh token
// @access  Private
router.post('/refresh', asyncHandler(async (req, res) => {
  const { token } = req.body;
  
  if (!token) {
    return res.status(400).json({
      success: false,
      message: 'Token is required'
    });
  }

  try {
    const jwt = require('jsonwebtoken');
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    
    const user = await User.findById(decoded.userId).select('-password');
    if (!user || !user.isActive) {
      return res.status(401).json({
        success: false,
        message: 'Invalid token'
      });
    }

    // Generate new token
    const newToken = generateToken(user._id);

    res.json({
      success: true,
      message: 'Token refreshed successfully',
      data: {
        token: newToken,
        user: {
          id: user._id,
          username: user.username,
          email: user.email,
          firstName: user.firstName,
          lastName: user.lastName,
          role: user.role,
          department: user.department,
          position: user.position,
          preferences: user.preferences
        }
      }
    });
  } catch (error) {
    return res.status(401).json({
      success: false,
      message: 'Invalid token'
    });
  }
}));

// @route   POST /api/auth/logout
// @desc    Logout user
// @access  Private
router.post('/logout', asyncHandler(async (req, res) => {
  // In a stateless JWT system, logout is handled client-side
  // But we can log the action for audit purposes
  auditLogger.logAction('user_logout', req.user.id, {
    ip: req.ip,
    userAgent: req.get('User-Agent'),
    resource: 'auth'
  });

  res.json({
    success: true,
    message: 'Logout successful'
  });
}));

// @route   GET /api/auth/me
// @desc    Get current user
// @access  Private
router.get('/me', asyncHandler(async (req, res) => {
  const user = await User.findById(req.user.id).select('-password');
  
  res.json({
    success: true,
    data: {
      user: {
        id: user._id,
        username: user.username,
        email: user.email,
        firstName: user.firstName,
        lastName: user.lastName,
        role: user.role,
        department: user.department,
        position: user.position,
        employeeId: user.employeeId,
        phone: user.phone,
        avatar: user.avatar,
        preferences: user.preferences,
        permissions: user.permissions,
        lastLogin: user.lastLogin,
        createdAt: user.createdAt
      }
    }
  });
}));

// @route   PUT /api/auth/change-password
// @desc    Change password
// @access  Private
router.put('/change-password', asyncHandler(async (req, res) => {
  const { error, value } = changePasswordSchema.validate(req.body);
  if (error) {
    return res.status(400).json({
      success: false,
      message: 'Validation error',
      errors: error.details.map(detail => ({
        field: detail.path.join('.'),
        message: detail.message
      }))
    });
  }

  const user = await User.findById(req.user.id);
  
  // Verify current password
  const isCurrentPasswordValid = await user.comparePassword(value.currentPassword);
  if (!isCurrentPasswordValid) {
    return res.status(400).json({
      success: false,
      message: 'Current password is incorrect'
    });
  }

  // Update password
  user.password = value.newPassword;
  await user.save();

  // Log audit
  auditLogger.logAction('password_changed', user._id, {
    ip: req.ip,
    userAgent: req.get('User-Agent'),
    resource: 'user',
    changes: { action: 'password_changed' }
  });

  res.json({
    success: true,
    message: 'Password changed successfully'
  });
}));

// @route   PUT /api/auth/profile
// @desc    Update profile
// @access  Private
router.put('/profile', asyncHandler(async (req, res) => {
  const updateSchema = Joi.object({
    firstName: Joi.string().max(50).optional(),
    lastName: Joi.string().max(50).optional(),
    phone: Joi.string().pattern(/^[\+]?[1-9][\d]{0,15}$/).optional(),
    preferences: Joi.object({
      theme: Joi.string().valid('light', 'dark').optional(),
      language: Joi.string().optional(),
      notifications: Joi.object({
        email: Joi.boolean().optional(),
        push: Joi.boolean().optional(),
        sms: Joi.boolean().optional()
      }).optional()
    }).optional()
  });

  const { error, value } = updateSchema.validate(req.body);
  if (error) {
    return res.status(400).json({
      success: false,
      message: 'Validation error',
      errors: error.details.map(detail => ({
        field: detail.path.join('.'),
        message: detail.message
      }))
    });
  }

  const user = await User.findById(req.user.id);
  
  // Update fields
  Object.keys(value).forEach(key => {
    if (key === 'preferences') {
      user.preferences = { ...user.preferences, ...value.preferences };
    } else {
      user[key] = value[key];
    }
  });

  await user.save();

  // Log audit
  auditLogger.logAction('profile_updated', user._id, {
    ip: req.ip,
    userAgent: req.get('User-Agent'),
    resource: 'user',
    changes: { updatedFields: Object.keys(value) }
  });

  res.json({
    success: true,
    message: 'Profile updated successfully',
    data: {
      user: {
        id: user._id,
        username: user.username,
        email: user.email,
        firstName: user.firstName,
        lastName: user.lastName,
        role: user.role,
        department: user.department,
        position: user.position,
        phone: user.phone,
        preferences: user.preferences
      }
    }
  });
}));

module.exports = router; 