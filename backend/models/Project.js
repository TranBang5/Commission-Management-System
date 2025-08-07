const mongoose = require('mongoose');

const projectSchema = new mongoose.Schema({
  name: {
    type: String,
    required: [true, 'Project name is required'],
    trim: true,
    maxlength: [200, 'Project name cannot exceed 200 characters']
  },
  code: {
    type: String,
    required: [true, 'Project code is required'],
    unique: true,
    trim: true,
    uppercase: true,
    match: [/^[A-Z0-9]{3,10}$/, 'Project code must be 3-10 uppercase letters/numbers']
  },
  description: {
    type: String,
    trim: true,
    maxlength: [1000, 'Description cannot exceed 1000 characters']
  },
  client: {
    name: {
      type: String,
      required: [true, 'Client name is required'],
      trim: true,
      maxlength: [200, 'Client name cannot exceed 200 characters']
    },
    email: {
      type: String,
      trim: true,
      lowercase: true,
      match: [/^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/, 'Please enter a valid email']
    },
    phone: {
      type: String,
      trim: true
    },
    company: {
      type: String,
      trim: true,
      maxlength: [200, 'Company name cannot exceed 200 characters']
    }
  },
  manager: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: [true, 'Project manager is required']
  },
  team: [{
    user: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: true
    },
    role: {
      type: String,
      enum: ['developer', 'designer', 'tester', 'analyst', 'lead', 'consultant'],
      required: true
    },
    startDate: {
      type: Date,
      required: true
    },
    endDate: {
      type: Date,
      default: null
    },
    allocation: {
      type: Number,
      min: 0,
      max: 100,
      default: 100,
      required: true
    },
    hourlyRate: {
      type: Number,
      min: 0,
      default: 0
    }
  }],
  status: {
    type: String,
    enum: ['planning', 'active', 'on-hold', 'completed', 'cancelled'],
    default: 'planning',
    required: true
  },
  priority: {
    type: String,
    enum: ['low', 'medium', 'high', 'critical'],
    default: 'medium'
  },
  category: {
    type: String,
    enum: ['web', 'mobile', 'desktop', 'api', 'consulting', 'training', 'maintenance'],
    required: true
  },
  startDate: {
    type: Date,
    required: [true, 'Start date is required']
  },
  endDate: {
    type: Date,
    required: [true, 'End date is required']
  },
  actualStartDate: {
    type: Date,
    default: null
  },
  actualEndDate: {
    type: Date,
    default: null
  },
  budget: {
    planned: {
      type: Number,
      min: 0,
      required: [true, 'Planned budget is required']
    },
    actual: {
      type: Number,
      min: 0,
      default: 0
    },
    currency: {
      type: String,
      default: 'VND',
      enum: ['VND', 'USD', 'EUR']
    }
  },
  revenue: {
    planned: {
      type: Number,
      min: 0,
      required: [true, 'Planned revenue is required']
    },
    actual: {
      type: Number,
      min: 0,
      default: 0
    },
    received: {
      type: Number,
      min: 0,
      default: 0
    },
    currency: {
      type: String,
      default: 'VND',
      enum: ['VND', 'USD', 'EUR']
    }
  },
  progress: {
    planned: {
      type: Number,
      min: 0,
      max: 100,
      default: 0
    },
    actual: {
      type: Number,
      min: 0,
      max: 100,
      default: 0
    }
  },
  kpis: [{
    name: {
      type: String,
      required: true,
      trim: true
    },
    description: {
      type: String,
      trim: true
    },
    type: {
      type: String,
      enum: ['percentage', 'number', 'boolean', 'text'],
      required: true
    },
    target: {
      type: mongoose.Schema.Types.Mixed,
      required: true
    },
    actual: {
      type: mongoose.Schema.Types.Mixed,
      default: null
    },
    weight: {
      type: Number,
      min: 0,
      max: 100,
      default: 10
    },
    isCompleted: {
      type: Boolean,
      default: false
    }
  }],
  milestones: [{
    name: {
      type: String,
      required: true,
      trim: true
    },
    description: {
      type: String,
      trim: true
    },
    dueDate: {
      type: Date,
      required: true
    },
    completedDate: {
      type: Date,
      default: null
    },
    isCompleted: {
      type: Boolean,
      default: false
    },
    deliverables: [{
      name: String,
      description: String,
      isCompleted: { type: Boolean, default: false }
    }]
  }],
  risks: [{
    description: {
      type: String,
      required: true,
      trim: true
    },
    probability: {
      type: String,
      enum: ['low', 'medium', 'high'],
      required: true
    },
    impact: {
      type: String,
      enum: ['low', 'medium', 'high'],
      required: true
    },
    mitigation: {
      type: String,
      trim: true
    },
    status: {
      type: String,
      enum: ['open', 'mitigated', 'closed'],
      default: 'open'
    }
  }],
  documents: [{
    name: {
      type: String,
      required: true,
      trim: true
    },
    type: {
      type: String,
      enum: ['contract', 'specification', 'design', 'test', 'delivery', 'other'],
      required: true
    },
    url: {
      type: String,
      required: true
    },
    uploadedBy: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: true
    },
    uploadedAt: {
      type: Date,
      default: Date.now
    }
  }],
  tags: [{
    type: String,
    trim: true
  }],
  notes: {
    type: String,
    trim: true,
    maxlength: [2000, 'Notes cannot exceed 2000 characters']
  },
  metadata: {
    type: Map,
    of: mongoose.Schema.Types.Mixed,
    default: {}
  }
}, {
  timestamps: true,
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// Virtual for project duration
projectSchema.virtual('duration').get(function() {
  if (this.actualStartDate && this.actualEndDate) {
    return Math.ceil((this.actualEndDate - this.actualStartDate) / (1000 * 60 * 60 * 24));
  }
  return Math.ceil((this.endDate - this.startDate) / (1000 * 60 * 60 * 24));
});

// Virtual for profit margin
projectSchema.virtual('profitMargin').get(function() {
  if (this.revenue.actual > 0) {
    return ((this.revenue.actual - this.budget.actual) / this.revenue.actual) * 100;
  }
  return 0;
});

// Virtual for completion status
projectSchema.virtual('isCompleted').get(function() {
  return this.status === 'completed';
});

// Virtual for overdue status
projectSchema.virtual('isOverdue').get(function() {
  return this.status === 'active' && new Date() > this.endDate;
});

// Indexes
projectSchema.index({ code: 1 });
projectSchema.index({ status: 1 });
projectSchema.index({ manager: 1 });
projectSchema.index({ 'client.name': 1 });
projectSchema.index({ startDate: 1 });
projectSchema.index({ endDate: 1 });
projectSchema.index({ category: 1 });
projectSchema.index({ tags: 1 });

// Pre-save middleware
projectSchema.pre('save', function(next) {
  // Auto-calculate progress based on completed milestones
  if (this.milestones && this.milestones.length > 0) {
    const completedMilestones = this.milestones.filter(m => m.isCompleted).length;
    this.progress.actual = Math.round((completedMilestones / this.milestones.length) * 100);
  }
  next();
});

// Static method to find active projects
projectSchema.statics.findActive = function() {
  return this.find({ status: 'active' });
};

// Static method to find overdue projects
projectSchema.statics.findOverdue = function() {
  return this.find({
    status: 'active',
    endDate: { $lt: new Date() }
  });
};

// Static method to find projects by manager
projectSchema.statics.findByManager = function(managerId) {
  return this.find({ manager: managerId });
};

// Static method to find projects by team member
projectSchema.statics.findByTeamMember = function(userId) {
  return this.find({
    'team.user': userId,
    'team.endDate': { $exists: false }
  });
};

module.exports = mongoose.model('Project', projectSchema); 