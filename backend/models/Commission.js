const mongoose = require('mongoose');

const commissionSchema = new mongoose.Schema({
  period: {
    year: {
      type: Number,
      required: [true, 'Year is required'],
      min: [2020, 'Year must be 2020 or later']
    },
    month: {
      type: Number,
      required: [true, 'Month is required'],
      min: [1, 'Month must be between 1 and 12'],
      max: [12, 'Month must be between 1 and 12']
    }
  },
  project: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Project',
    required: [true, 'Project is required']
  },
  employee: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: [true, 'Employee is required']
  },
  role: {
    type: String,
    enum: ['developer', 'designer', 'tester', 'analyst', 'lead', 'consultant'],
    required: true
  },
  baseSalary: {
    type: Number,
    min: 0,
    required: [true, 'Base salary is required']
  },
  performanceMetrics: {
    kpiScore: {
      type: Number,
      min: 0,
      max: 100,
      default: 0
    },
    qualityScore: {
      type: Number,
      min: 0,
      max: 100,
      default: 0
    },
    efficiencyScore: {
      type: Number,
      min: 0,
      max: 100,
      default: 0
    },
    teamworkScore: {
      type: Number,
      min: 0,
      max: 100,
      default: 0
    },
    innovationScore: {
      type: Number,
      min: 0,
      max: 100,
      default: 0
    }
  },
  projectMetrics: {
    projectProgress: {
      type: Number,
      min: 0,
      max: 100,
      default: 0
    },
    projectProfit: {
      type: Number,
      default: 0
    },
    clientSatisfaction: {
      type: Number,
      min: 0,
      max: 100,
      default: 0
    },
    deadlineAdherence: {
      type: Number,
      min: 0,
      max: 100,
      default: 0
    }
  },
  aiCalculations: {
    overallScore: {
      type: Number,
      min: 0,
      max: 100,
      default: 0
    },
    performanceBonus: {
      type: Number,
      min: 0,
      default: 0
    },
    projectBonus: {
      type: Number,
      min: 0,
      default: 0
    },
    qualityBonus: {
      type: Number,
      min: 0,
      default: 0
    },
    innovationBonus: {
      type: Number,
      min: 0,
      default: 0
    },
    totalBonus: {
      type: Number,
      min: 0,
      default: 0
    },
    aiConfidence: {
      type: Number,
      min: 0,
      max: 100,
      default: 0
    },
    aiFactors: [{
      factor: String,
      weight: Number,
      score: Number,
      impact: Number
    }]
  },
  manualAdjustments: {
    approvedBy: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User'
    },
    approvedAt: {
      type: Date
    },
    adjustmentAmount: {
      type: Number,
      default: 0
    },
    adjustmentReason: {
      type: String,
      trim: true,
      maxlength: [500, 'Adjustment reason cannot exceed 500 characters']
    },
    adjustmentType: {
      type: String,
      enum: ['bonus', 'penalty', 'correction'],
      default: 'correction'
    }
  },
  finalAmount: {
    type: Number,
    min: 0,
    required: [true, 'Final amount is required']
  },
  currency: {
    type: String,
    default: 'VND',
    enum: ['VND', 'USD', 'EUR']
  },
  status: {
    type: String,
    enum: ['draft', 'calculated', 'pending_approval', 'approved', 'paid', 'disputed'],
    default: 'draft'
  },
  paymentDetails: {
    paymentDate: {
      type: Date
    },
    paymentMethod: {
      type: String,
      enum: ['bank_transfer', 'cash', 'check', 'other']
    },
    transactionId: {
      type: String,
      trim: true
    },
    notes: {
      type: String,
      trim: true,
      maxlength: [500, 'Payment notes cannot exceed 500 characters']
    }
  },
  disputes: [{
    raisedBy: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: true
    },
    raisedAt: {
      type: Date,
      default: Date.now
    },
    reason: {
      type: String,
      required: true,
      trim: true,
      maxlength: [1000, 'Dispute reason cannot exceed 1000 characters']
    },
    evidence: [{
      type: String,
      trim: true
    }],
    status: {
      type: String,
      enum: ['open', 'under_review', 'resolved', 'rejected'],
      default: 'open'
    },
    resolvedBy: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User'
    },
    resolvedAt: {
      type: Date
    },
    resolution: {
      type: String,
      trim: true,
      maxlength: [1000, 'Resolution cannot exceed 1000 characters']
    },
    aiAnalysis: {
      sentiment: {
        type: String,
        enum: ['positive', 'negative', 'neutral']
      },
      confidence: {
        type: Number,
        min: 0,
        max: 100
      },
      keyPoints: [String],
      recommendation: {
        type: String,
        enum: ['uphold', 'modify', 'reject']
      }
    }
  }],
  auditTrail: [{
    action: {
      type: String,
      required: true,
      enum: ['created', 'calculated', 'adjusted', 'approved', 'paid', 'disputed', 'resolved']
    },
    performedBy: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: true
    },
    performedAt: {
      type: Date,
      default: Date.now
    },
    details: {
      type: String,
      trim: true
    },
    previousAmount: {
      type: Number
    },
    newAmount: {
      type: Number
    }
  }],
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

// Virtual for total score
commissionSchema.virtual('totalScore').get(function() {
  const performance = this.performanceMetrics;
  const project = this.projectMetrics;
  
  return (
    (performance.kpiScore * 0.3) +
    (performance.qualityScore * 0.2) +
    (performance.efficiencyScore * 0.2) +
    (performance.teamworkScore * 0.15) +
    (performance.innovationScore * 0.15)
  );
});

// Virtual for project score
commissionSchema.virtual('projectScore').get(function() {
  const project = this.projectMetrics;
  
  return (
    (project.projectProgress * 0.3) +
    (project.clientSatisfaction * 0.3) +
    (project.deadlineAdherence * 0.4)
  );
});

// Virtual for total bonus percentage
commissionSchema.virtual('totalBonusPercentage').get(function() {
  if (this.baseSalary > 0) {
    return (this.aiCalculations.totalBonus / this.baseSalary) * 100;
  }
  return 0;
});

// Virtual for period string
commissionSchema.virtual('periodString').get(function() {
  return `${this.period.year}-${this.period.month.toString().padStart(2, '0')}`;
});

// Indexes
commissionSchema.index({ 'period.year': 1, 'period.month': 1 });
commissionSchema.index({ project: 1 });
commissionSchema.index({ employee: 1 });
commissionSchema.index({ status: 1 });
commissionSchema.index({ 'period.year': 1, 'period.month': 1, employee: 1 }, { unique: true });

// Pre-save middleware
commissionSchema.pre('save', function(next) {
  // Auto-calculate final amount
  this.finalAmount = this.baseSalary + this.aiCalculations.totalBonus + this.manualAdjustments.adjustmentAmount;
  
  // Auto-calculate total bonus
  this.aiCalculations.totalBonus = 
    this.aiCalculations.performanceBonus +
    this.aiCalculations.projectBonus +
    this.aiCalculations.qualityBonus +
    this.aiCalculations.innovationBonus;
  
  next();
});

// Static method to find by period
commissionSchema.statics.findByPeriod = function(year, month) {
  return this.find({
    'period.year': year,
    'period.month': month
  });
};

// Static method to find by employee
commissionSchema.statics.findByEmployee = function(employeeId) {
  return this.find({ employee: employeeId }).sort({ 'period.year': -1, 'period.month': -1 });
};

// Static method to find by project
commissionSchema.statics.findByProject = function(projectId) {
  return this.find({ project: projectId });
};

// Static method to find pending approvals
commissionSchema.statics.findPendingApproval = function() {
  return this.find({ status: 'pending_approval' });
};

// Static method to find disputes
commissionSchema.statics.findDisputes = function() {
  return this.find({
    'disputes.status': { $in: ['open', 'under_review'] }
  });
};

module.exports = mongoose.model('Commission', commissionSchema); 