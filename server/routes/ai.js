const express = require('express');
const { body, param, query, validationResult } = require('express-validator');
const { User, Project, Bonus, PerformanceEvaluation, ProjectMember, AuditLog } = require('../models');
const { authorize } = require('../middleware/auth');
const logger = require('../utils/logger');

const router = express.Router();

// POST /api/ai/team-recommendation - Gợi ý nhóm nhân sự cho dự án
router.post('/team-recommendation', [
  body('projectId').isUUID().withMessage('ID dự án không hợp lệ'),
  body('requiredRoles').isArray().withMessage('Vai trò yêu cầu phải là array'),
  body('teamSize').optional().isInt({ min: 1, max: 20 }).withMessage('Kích thước team phải từ 1-20'),
  body('budget').optional().isFloat({ min: 0 }).withMessage('Ngân sách phải >= 0'),
  body('priority').optional().isIn(['low', 'medium', 'high', 'critical']).withMessage('Độ ưu tiên không hợp lệ'),
  authorize('admin', 'manager', 'business')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ success: false, message: 'Dữ liệu không hợp lệ', errors: errors.array() });
    }

    const { projectId, requiredRoles, teamSize = 5, budget, priority = 'medium' } = req.body;

    // Kiểm tra dự án
    const project = await Project.findByPk(projectId);
    if (!project) {
      return res.status(404).json({ success: false, message: 'Không tìm thấy dự án' });
    }

    // Lấy tất cả nhân viên có sẵn
    const availableUsers = await User.findAll({
      where: { isActive: true },
      include: [
        {
          model: PerformanceEvaluation,
          as: 'receivedEvaluations',
          where: {
            status: 'approved',
            evaluationDate: { [require('sequelize').Op.gte]: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000) }
          },
          required: false
        },
        {
          model: Bonus,
          as: 'bonuses',
          where: {
            status: { [require('sequelize').Op.in]: ['approved', 'paid'] }
          },
          required: false
        },
        {
          model: ProjectMember,
          as: 'projects',
          where: { isActive: true },
          required: false
        }
      ]
    });

    // Phân tích năng lực từng nhân viên
    const userCapabilities = availableUsers.map(user => {
      const evaluations = user.receivedEvaluations || [];
      const bonuses = user.bonuses || [];
      const currentProjects = user.projects || [];

      // Tính điểm trung bình các kỹ năng
      const avgTechnicalSkills = evaluations.length > 0 
        ? evaluations.reduce((sum, eval) => sum + (eval.technicalSkills || 0), 0) / evaluations.length 
        : 6.0;
      
      const avgProblemSolving = evaluations.length > 0 
        ? evaluations.reduce((sum, eval) => sum + (eval.problemSolving || 0), 0) / evaluations.length 
        : 6.0;
      
      const avgCommunication = evaluations.length > 0 
        ? evaluations.reduce((sum, eval) => sum + (eval.communication || 0), 0) / evaluations.length 
        : 6.0;
      
      const avgTeamwork = evaluations.length > 0 
        ? evaluations.reduce((sum, eval) => sum + (eval.teamwork || 0), 0) / evaluations.length 
        : 6.0;
      
      const avgLeadership = evaluations.length > 0 
        ? evaluations.reduce((sum, eval) => sum + (eval.leadership || 0), 0) / evaluations.length 
        : 6.0;
      
      const avgInnovation = evaluations.length > 0 
        ? evaluations.reduce((sum, eval) => sum + (eval.innovation || 0), 0) / evaluations.length 
        : 6.0;

      // Tính điểm hiệu suất trung bình
      const avgPerformanceScore = evaluations.length > 0 
        ? evaluations.reduce((sum, eval) => sum + (eval.overallScore || 0), 0) / evaluations.length 
        : 6.0;

      // Tính thưởng trung bình
      const avgBonus = bonuses.length > 0 
        ? bonuses.reduce((sum, bonus) => sum + bonus.totalBonus, 0) / bonuses.length 
        : 0;

      // Phân tích workload hiện tại
      const currentWorkload = currentProjects.length;
      const isAvailable = currentWorkload < 3; // Tối đa 3 dự án cùng lúc

      // Tính điểm phù hợp với từng vai trò
      const roleScores = {};
      requiredRoles.forEach(role => {
        let score = 0;
        
        switch (role.toLowerCase()) {
          case 'developer':
          case 'dev':
            score = (avgTechnicalSkills * 0.4 + avgProblemSolving * 0.3 + (evaluations.length > 0 ? evaluations.reduce((sum, eval) => sum + (eval.qualityOfWork || 0), 0) / evaluations.length : 6.0) * 0.3) * 0.8;
            break;
          case 'team_lead':
          case 'leader':
            score = (avgLeadership * 0.4 + avgCommunication * 0.3 + avgTeamwork * 0.3) * 0.9;
            break;
          case 'project_manager':
          case 'manager':
            score = (avgLeadership * 0.4 + avgCommunication * 0.3 + avgProblemSolving * 0.3) * 0.9;
            break;
          case 'designer':
            score = (avgInnovation * 0.4 + avgTechnicalSkills * 0.3 + (evaluations.length > 0 ? evaluations.reduce((sum, eval) => sum + (eval.qualityOfWork || 0), 0) / evaluations.length : 6.0) * 0.3) * 0.8;
            break;
          case 'tester':
          case 'qa':
            score = ((evaluations.length > 0 ? evaluations.reduce((sum, eval) => sum + (eval.qualityOfWork || 0), 0) / evaluations.length : 6.0) * 0.4 + avgProblemSolving * 0.3 + (evaluations.length > 0 ? evaluations.reduce((sum, eval) => sum + (eval.reliability || 0), 0) / evaluations.length : 6.0) * 0.3) * 0.8;
            break;
          case 'analyst':
            score = (avgProblemSolving * 0.4 + avgCommunication * 0.3 + avgTechnicalSkills * 0.3) * 0.8;
            break;
          default:
            score = (avgPerformanceScore * 0.4 + avgBonus * 0.3 + avgTeamwork * 0.3) * 0.7;
        }

        // Điều chỉnh theo workload
        if (!isAvailable) score *= 0.5;
        
        roleScores[role] = score;
      });

      return {
        user: {
          id: user.id,
          fullName: user.fullName,
          email: user.email,
          department: user.department,
          position: user.position
        },
        capabilities: {
          technicalSkills: avgTechnicalSkills,
          problemSolving: avgProblemSolving,
          communication: avgCommunication,
          teamwork: avgTeamwork,
          leadership: avgLeadership,
          innovation: avgInnovation,
          reliability: evaluations.length > 0 ? evaluations.reduce((sum, eval) => sum + (eval.reliability || 0), 0) / evaluations.length : 6.0,
          qualityOfWork: evaluations.length > 0 ? evaluations.reduce((sum, eval) => sum + (eval.qualityOfWork || 0), 0) / evaluations.length : 6.0,
          meetingDeadlines: evaluations.length > 0 ? evaluations.reduce((sum, eval) => sum + (eval.meetingDeadlines || 0), 0) / evaluations.length : 6.0
        },
        performance: {
          averageScore: avgPerformanceScore,
          averageBonus: avgBonus,
          evaluationCount: evaluations.length,
          bonusCount: bonuses.length
        },
        availability: {
          currentWorkload,
          isAvailable,
          maxProjects: 3
        },
        roleScores,
        receivedEvaluations: evaluations,
        bonuses: bonuses
      };
    });

    // Thuật toán gợi ý team tối ưu
    const teamRecommendations = [];
    
    // Chiến lược 1: Team cân bằng (có leader, senior, junior)
    const balancedTeam = selectBalancedTeam(userCapabilities, requiredRoles, teamSize);
    
    // Chiến lược 2: Team hiệu suất cao (chọn người giỏi nhất)
    const highPerformanceTeam = selectHighPerformanceTeam(userCapabilities, requiredRoles, teamSize);
    
    // Chiến lược 3: Team tiết kiệm chi phí (cân bằng giữa năng lực và chi phí)
    const costEffectiveTeam = selectCostEffectiveTeam(userCapabilities, requiredRoles, teamSize, budget);

    teamRecommendations.push(
      { strategy: 'balanced', team: balancedTeam, score: calculateTeamScore(balancedTeam) },
      { strategy: 'high_performance', team: highPerformanceTeam, score: calculateTeamScore(highPerformanceTeam) },
      { strategy: 'cost_effective', team: costEffectiveTeam, score: calculateTeamScore(costEffectiveTeam) }
    );

    // Sắp xếp theo điểm số
    teamRecommendations.sort((a, b) => b.score - a.score);

    // Gợi ý KPI cho từng thành viên
    const kpiRecommendations = teamRecommendations[0].team.map(member => {
      return generateKPIsForMember(member, project, priority);
    });

    const recommendation = {
      project: {
        id: project.id,
        name: project.name,
        code: project.code,
        priority,
        budget: budget || project.budget
      },
      requirements: {
        roles: requiredRoles,
        teamSize,
        budget
      },
      teamRecommendations,
      recommendedTeam: teamRecommendations[0],
      kpiRecommendations,
      analysis: {
        totalCandidates: userCapabilities.length,
        availableCandidates: userCapabilities.filter(u => u.availability.isAvailable).length,
        averagePerformanceScore: userCapabilities.length > 0 ? userCapabilities.reduce((sum, u) => {
          const evaluations = u.receivedEvaluations || [];
          const score = evaluations.length > 0 
            ? evaluations.reduce((sum, eval) => sum + (eval.overallScore || 0), 0) / evaluations.length 
            : 6.0;
          return sum + score;
        }, 0) / userCapabilities.length : 0,
        skillGaps: analyzeSkillGaps(userCapabilities, requiredRoles)
      }
    };

    // Ghi log
    await AuditLog.createLog({
      userId: req.user.id,
      action: 'TEAM_RECOMMENDATION',
      resource: 'AI',
      status: 'success',
      metadata: { 
        projectId, 
        requiredRoles, 
        teamSize,
        recommendationsCount: teamRecommendations.length 
      }
    });

    logger.info(`Team recommendation generated for project ${project.code} by user ${req.user.id}`);

    res.json({
      success: true,
      message: 'Gợi ý nhóm nhân sự thành công',
      data: recommendation
    });

  } catch (error) {
    logger.error('Error generating team recommendation:', error);
    res.status(500).json({ success: false, message: 'Lỗi server khi gợi ý nhóm nhân sự' });
  }
});

// POST /api/ai/kpi-suggestion - Gợi ý KPI cho dự án
router.post('/kpi-suggestion', [
  body('projectId').isUUID().withMessage('ID dự án không hợp lệ'),
  body('teamMembers').isArray().withMessage('Thành viên team phải là array'),
  body('projectType').optional().isIn(['development', 'design', 'marketing', 'research', 'consulting']).withMessage('Loại dự án không hợp lệ'),
  body('complexity').optional().isIn(['simple', 'moderate', 'complex', 'very_complex']).withMessage('Độ phức tạp không hợp lệ'),
  authorize('admin', 'manager', 'business')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ success: false, message: 'Dữ liệu không hợp lệ', errors: errors.array() });
    }

    const { projectId, teamMembers, projectType = 'development', complexity = 'moderate' } = req.body;

    // Kiểm tra dự án
    const project = await Project.findByPk(projectId);
    if (!project) {
      return res.status(404).json({ success: false, message: 'Không tìm thấy dự án' });
    }

    // Lấy thông tin chi tiết team members
    const detailedMembers = await Promise.all(
      teamMembers.map(async (memberId) => {
        const user = await User.findByPk(memberId, {
          include: [
            {
              model: PerformanceEvaluation,
              as: 'receivedEvaluations',
              where: { status: 'approved' },
              required: false
            },
            {
              model: Bonus,
              as: 'bonuses',
              where: { status: { [require('sequelize').Op.in]: ['approved', 'paid'] } },
              required: false
            }
          ]
        });
        return user;
      })
    );

    // Tạo KPI template theo loại dự án
    const kpiTemplates = generateKPITemplates(projectType, complexity);
    
    // Điều chỉnh KPI theo năng lực từng thành viên
    const personalizedKPIs = detailedMembers.map(member => {
      const evaluations = member.receivedEvaluations || [];
      const bonuses = member.bonuses || [];
      
      // Tính điểm trung bình
      const avgScore = evaluations.length > 0 
        ? evaluations.reduce((sum, eval) => sum + (eval.overallScore || 0), 0) / evaluations.length 
        : 6.0;
      
      const avgBonus = bonuses.length > 0 
        ? bonuses.reduce((sum, bonus) => sum + bonus.totalBonus, 0) / bonuses.length 
        : 0;

      // Điều chỉnh KPI theo năng lực
      const adjustedKPIs = adjustKPIsByCapability(kpiTemplates, member, avgScore, avgBonus);
      
      return {
        userId: member.id,
        userName: member.fullName,
        position: member.position,
        department: member.department,
        capabilityLevel: getCapabilityLevel(avgScore),
        kpis: adjustedKPIs,
        recommendations: generatePersonalizedRecommendations(member, avgScore, avgBonus)
      };
    });

    // Tạo KPI tổng thể cho dự án
    const projectKPIs = generateProjectKPIs(project, teamMembers.length, projectType, complexity);

    const kpiSuggestion = {
      project: {
        id: project.id,
        name: project.name,
        code: project.code,
        type: projectType,
        complexity
      },
      teamKPIs: personalizedKPIs,
      projectKPIs,
      summary: {
        totalMembers: detailedMembers.length,
        averageCapabilityLevel: detailedMembers.length > 0 ? detailedMembers.reduce((sum, m) => sum + getCapabilityLevelScore(m), 0) / detailedMembers.length : 0,
        estimatedSuccessRate: calculateSuccessRate(detailedMembers, projectType, complexity),
        riskFactors: identifyRiskFactors(detailedMembers, projectType, complexity)
      }
    };

    // Ghi log
    await AuditLog.createLog({
      userId: req.user.id,
      action: 'KPI_SUGGESTION',
      resource: 'AI',
      status: 'success',
      metadata: { 
        projectId, 
        teamSize: teamMembers.length,
        projectType,
        complexity 
      }
    });

    logger.info(`KPI suggestion generated for project ${project.code} by user ${req.user.id}`);

    res.json({
      success: true,
      message: 'Gợi ý KPI thành công',
      data: kpiSuggestion
    });

  } catch (error) {
    logger.error('Error generating KPI suggestion:', error);
    res.status(500).json({ success: false, message: 'Lỗi server khi gợi ý KPI' });
  }
});

// Helper functions
function selectBalancedTeam(userCapabilities, requiredRoles, teamSize) {
  const team = [];
  const selectedUsers = new Set();
  
  // Chọn leader trước
  const leaders = userCapabilities
    .filter(u => u.availability.isAvailable && u.capabilities.leadership >= 7.0)
    .sort((a, b) => b.capabilities.leadership - a.capabilities.leadership);
  
  if (leaders.length > 0) {
    team.push(leaders[0]);
    selectedUsers.add(leaders[0].user.id);
  }
  
  // Chọn senior members
  const seniors = userCapabilities
    .filter(u => u.availability.isAvailable && !selectedUsers.has(u.user.id))
    .filter(u => {
      const evaluations = u.receivedEvaluations || [];
      const score = evaluations.length > 0 
        ? evaluations.reduce((sum, eval) => sum + (eval.overallScore || 0), 0) / evaluations.length 
        : 6.0;
      return score >= 7.5;
    })
    .sort((a, b) => {
      const aEvaluations = a.receivedEvaluations || [];
      const bEvaluations = b.receivedEvaluations || [];
      
      const aScore = aEvaluations.length > 0 
        ? aEvaluations.reduce((sum, eval) => sum + (eval.overallScore || 0), 0) / aEvaluations.length 
        : 6.0;
      
      const bScore = bEvaluations.length > 0 
        ? bEvaluations.reduce((sum, eval) => sum + (eval.overallScore || 0), 0) / bEvaluations.length 
        : 6.0;
      
      return bScore - aScore;
    });
  
  const seniorCount = Math.min(2, Math.floor(teamSize / 3));
  for (let i = 0; i < seniorCount && i < seniors.length; i++) {
    team.push(seniors[i]);
    selectedUsers.add(seniors[i].user.id);
  }
  
  // Chọn junior members
  const juniors = userCapabilities
    .filter(u => u.availability.isAvailable && !selectedUsers.has(u.user.id))
    .sort((a, b) => {
      const aEvaluations = a.receivedEvaluations || [];
      const bEvaluations = b.receivedEvaluations || [];
      
      const aScore = aEvaluations.length > 0 
        ? aEvaluations.reduce((sum, eval) => sum + (eval.overallScore || 0), 0) / aEvaluations.length 
        : 6.0;
      
      const bScore = bEvaluations.length > 0 
        ? bEvaluations.reduce((sum, eval) => sum + (eval.overallScore || 0), 0) / bEvaluations.length 
        : 6.0;
      
      return bScore - aScore;
    });
  
  const remainingSlots = teamSize - team.length;
  for (let i = 0; i < remainingSlots && i < juniors.length; i++) {
    team.push(juniors[i]);
  }
  
  return team;
}

function selectHighPerformanceTeam(userCapabilities, requiredRoles, teamSize) {
  return userCapabilities
    .filter(u => u.availability.isAvailable)
    .sort((a, b) => {
      const aEvaluations = a.receivedEvaluations || [];
      const bEvaluations = b.receivedEvaluations || [];
      
      const aScore = aEvaluations.length > 0 
        ? aEvaluations.reduce((sum, eval) => sum + (eval.overallScore || 0), 0) / aEvaluations.length 
        : 6.0;
      
      const bScore = bEvaluations.length > 0 
        ? bEvaluations.reduce((sum, eval) => sum + (eval.overallScore || 0), 0) / bEvaluations.length 
        : 6.0;
      
      return bScore - aScore;
    })
    .slice(0, teamSize);
}

function selectCostEffectiveTeam(userCapabilities, requiredRoles, teamSize, budget) {
  // Ưu tiên người có hiệu suất tốt nhưng không quá đắt
  return userCapabilities
    .filter(u => u.availability.isAvailable)
    .sort((a, b) => {
      const aEvaluations = a.receivedEvaluations || [];
      const bEvaluations = b.receivedEvaluations || [];
      const aBonuses = a.bonuses || [];
      const bBonuses = b.bonuses || [];
      
      const aScore = aEvaluations.length > 0 
        ? aEvaluations.reduce((sum, eval) => sum + (eval.overallScore || 0), 0) / aEvaluations.length 
        : 6.0;
      
      const bScore = bEvaluations.length > 0 
        ? bEvaluations.reduce((sum, eval) => sum + (eval.overallScore || 0), 0) / bEvaluations.length 
        : 6.0;
      
      const aBonus = aBonuses.length > 0 
        ? aBonuses.reduce((sum, b) => sum + b.totalBonus, 0) / aBonuses.length 
        : 0;
      
      const bBonus = bBonuses.length > 0 
        ? bBonuses.reduce((sum, b) => sum + b.totalBonus, 0) / bBonuses.length 
        : 0;
      
      const bPerformanceRatio = bScore / (bBonus + 1);
      const aPerformanceRatio = aScore / (aBonus + 1);
      return bPerformanceRatio - aPerformanceRatio;
    })
    .slice(0, teamSize);
}

function calculateTeamScore(team) {
  if (team.length === 0) return 0;
  
  const avgPerformance = team.length > 0 ? team.reduce((sum, member) => {
    const evaluations = member.receivedEvaluations || [];
    const score = evaluations.length > 0 
      ? evaluations.reduce((sum, eval) => sum + (eval.overallScore || 0), 0) / evaluations.length 
      : 6.0;
    return sum + score;
  }, 0) / team.length : 0;
  
  const avgBonus = team.length > 0 ? team.reduce((sum, member) => {
    const bonuses = member.bonuses || [];
    const bonus = bonuses.length > 0 
      ? bonuses.reduce((sum, b) => sum + b.totalBonus, 0) / bonuses.length 
      : 0;
    return sum + bonus;
  }, 0) / team.length : 0;
  
  const diversityScore = calculateDiversityScore(team);
  
  return (avgPerformance * 0.5 + avgBonus * 0.3 + diversityScore * 0.2);
}

function calculateDiversityScore(team) {
  if (team.length === 0) return 0;
  
  const departments = new Set(team.map(m => m.user.department));
  const positions = new Set(team.map(m => m.user.position));
  
  return (departments.size / team.length) * 0.6 + (positions.size / team.length) * 0.4;
}

function generateKPIsForMember(member, project, priority) {
  const baseKPIs = {
    technical: {
      codeQuality: { target: 8.5, weight: 0.3 },
      bugRate: { target: 0.05, weight: 0.2 },
      deliveryTime: { target: 0.9, weight: 0.25 },
      documentation: { target: 8.0, weight: 0.15 },
      testing: { target: 8.0, weight: 0.1 }
    },
    soft: {
      communication: { target: 8.0, weight: 0.3 },
      teamwork: { target: 8.0, weight: 0.3 },
      problemSolving: { target: 8.0, weight: 0.4 }
    },
    project: {
      milestoneCompletion: { target: 0.95, weight: 0.4 },
      stakeholderSatisfaction: { target: 8.5, weight: 0.3 },
      budgetAdherence: { target: 0.9, weight: 0.3 }
    }
  };

  // Điều chỉnh theo năng lực
  const evaluations = member.receivedEvaluations || [];
  const bonuses = member.bonuses || [];
  
  const avgScore = evaluations.length > 0 
    ? evaluations.reduce((sum, eval) => sum + (eval.overallScore || 0), 0) / evaluations.length 
    : 6.0;
  
  const avgBonus = bonuses.length > 0 
    ? bonuses.reduce((sum, bonus) => sum + bonus.totalBonus, 0) / bonuses.length 
    : 0;
  
  const capabilityLevel = getCapabilityLevel(avgScore);
  const adjustedKPIs = adjustKPIsByLevel(baseKPIs, capabilityLevel, priority);
  
  return {
    userId: member.user.id,
    userName: member.user.fullName,
    capabilityLevel,
    kpis: adjustedKPIs,
    recommendations: generatePersonalizedRecommendations(member, avgScore, avgBonus)
  };
}

function getCapabilityLevel(score) {
  if (score >= 8.5) return 'expert';
  if (score >= 7.5) return 'senior';
  if (score >= 6.5) return 'intermediate';
  return 'junior';
}

function adjustKPIsByLevel(baseKPIs, level, priority) {
  const multipliers = {
    expert: { easy: 1.1, medium: 1.0, hard: 0.9 },
    senior: { easy: 1.0, medium: 0.95, hard: 0.85 },
    intermediate: { easy: 0.9, medium: 0.85, hard: 0.75 },
    junior: { easy: 0.8, medium: 0.75, hard: 0.65 }
  };

  const priorityMultipliers = {
    low: 0.9,
    medium: 1.0,
    high: 1.1,
    critical: 1.2
  };

  const levelMultiplier = multipliers[level] ? multipliers[level][priority] || multipliers[level]['medium'] : 1.0;
  const priorityMultiplier = priorityMultipliers[priority] || 1.0;
  const multiplier = levelMultiplier * priorityMultiplier;
  
  const adjusted = JSON.parse(JSON.stringify(baseKPIs));
  
  // Điều chỉnh tất cả targets
  Object.keys(adjusted).forEach(category => {
    Object.keys(adjusted[category]).forEach(kpi => {
      adjusted[category][kpi].target *= multiplier;
    });
  });
  
  return adjusted;
}

function generatePersonalizedRecommendations(member, avgScore, avgBonus) {
  const recommendations = [];
  
  if (avgScore < 7.0) {
    recommendations.push('Cần cải thiện hiệu suất tổng thể');
  }
  
  const evaluations = member.receivedEvaluations || [];
  if (evaluations.length > 0) {
    const avgTechnicalSkills = evaluations.reduce((sum, eval) => sum + (eval.technicalSkills || 0), 0) / evaluations.length;
    const avgCommunication = evaluations.reduce((sum, eval) => sum + (eval.communication || 0), 0) / evaluations.length;
    const avgTeamwork = evaluations.reduce((sum, eval) => sum + (eval.teamwork || 0), 0) / evaluations.length;
    
    if (avgTechnicalSkills < 7.0) {
      recommendations.push('Đề xuất đào tạo kỹ năng kỹ thuật');
    }
    
    if (avgCommunication < 7.0) {
      recommendations.push('Cần cải thiện kỹ năng giao tiếp');
    }
    
    if (avgTeamwork < 7.0) {
      recommendations.push('Tăng cường kỹ năng làm việc nhóm');
    }
  }
  
  if (avgBonus < 1000) {
    recommendations.push('Cần tăng cường động lực và hiệu suất');
  }
  
  return recommendations;
}

function generateKPITemplates(projectType, complexity) {
  const templates = {
    development: {
      technical: {
        codeQuality: { target: 8.5, weight: 0.3 },
        bugRate: { target: 0.05, weight: 0.2 },
        deliveryTime: { target: 0.9, weight: 0.25 },
        documentation: { target: 8.0, weight: 0.15 },
        testing: { target: 8.0, weight: 0.1 }
      },
      soft: {
        communication: { target: 8.0, weight: 0.3 },
        teamwork: { target: 8.0, weight: 0.3 },
        problemSolving: { target: 8.0, weight: 0.4 }
      }
    },
    design: {
      technical: {
        designQuality: { target: 8.5, weight: 0.4 },
        creativity: { target: 8.0, weight: 0.3 },
        userExperience: { target: 8.5, weight: 0.3 }
      },
      soft: {
        communication: { target: 8.0, weight: 0.4 },
        creativity: { target: 8.5, weight: 0.3 },
        collaboration: { target: 8.0, weight: 0.3 }
      }
    },
    marketing: {
      technical: {
        campaignEffectiveness: { target: 8.0, weight: 0.4 },
        reachTarget: { target: 0.9, weight: 0.3 },
        conversionRate: { target: 0.05, weight: 0.3 }
      },
      soft: {
        communication: { target: 8.5, weight: 0.4 },
        creativity: { target: 8.0, weight: 0.3 },
        analytical: { target: 7.5, weight: 0.3 }
      }
    }
  };

  return templates[projectType] || templates.development;
}

function adjustKPIsByCapability(templates, member, avgScore, avgBonus) {
  const capabilityLevel = getCapabilityLevel(avgScore);
  const adjusted = JSON.parse(JSON.stringify(templates));
  
  const levelMultipliers = {
    expert: 1.1,
    senior: 1.0,
    intermediate: 0.9,
    junior: 0.8
  };
  
  const multiplier = levelMultipliers[capabilityLevel] || 1.0;
  
  Object.keys(adjusted).forEach(category => {
    Object.keys(adjusted[category]).forEach(kpi => {
      adjusted[category][kpi].target *= multiplier;
    });
  });
  
  return adjusted;
}

function generateProjectKPIs(project, teamSize, projectType, complexity) {
  const complexityMultipliers = {
    simple: 0.9,
    moderate: 1.0,
    complex: 1.1,
    very_complex: 1.2
  };
  
  const multiplier = complexityMultipliers[complexity] || 1.0;
  
  return {
    timeline: {
      onTimeDelivery: { target: 0.95 * multiplier, weight: 0.3 },
      milestoneCompletion: { target: 0.9 * multiplier, weight: 0.3 },
      qualityGates: { target: 0.95 * multiplier, weight: 0.4 }
    },
    quality: {
      defectRate: { target: 0.05 / multiplier, weight: 0.3 },
      customerSatisfaction: { target: 8.5 * multiplier, weight: 0.4 },
      codeReview: { target: 0.9 * multiplier, weight: 0.3 }
    },
    efficiency: {
      budgetAdherence: { target: 0.95 * multiplier, weight: 0.4 },
      resourceUtilization: { target: 0.85 * multiplier, weight: 0.3 },
      teamProductivity: { target: 0.9 * multiplier, weight: 0.3 }
    }
  };
}

function getCapabilityLevelScore(member) {
  const levels = { expert: 4, senior: 3, intermediate: 2, junior: 1 };
  const evaluations = member.receivedEvaluations || [];
  const avgScore = evaluations.length > 0 
    ? evaluations.reduce((sum, eval) => sum + (eval.overallScore || 0), 0) / evaluations.length 
    : 6.0;
  const level = getCapabilityLevel(avgScore);
  return levels[level] || 1;
}

function calculateSuccessRate(members, projectType, complexity) {
  if (members.length === 0) return 0;
  
  const avgScore = members.reduce((sum, m) => {
    const evaluations = m.receivedEvaluations || [];
    const score = evaluations.length > 0 
      ? evaluations.reduce((sum, eval) => sum + (eval.overallScore || 0), 0) / evaluations.length 
      : 6.0;
    return sum + score;
  }, 0) / members.length;
  
  const complexityFactors = { simple: 1.1, moderate: 1.0, complex: 0.9, very_complex: 0.8 };
  
  return Math.min(0.95, avgScore / 10 * (complexityFactors[complexity] || 1.0));
}

function identifyRiskFactors(members, projectType, complexity) {
  const risks = [];
  
  if (members.length === 0) return risks;
  
  const avgScore = members.reduce((sum, m) => {
    const evaluations = m.receivedEvaluations || [];
    const score = evaluations.length > 0 
      ? evaluations.reduce((sum, eval) => sum + (eval.overallScore || 0), 0) / evaluations.length 
      : 6.0;
    return sum + score;
  }, 0) / members.length;
  
  if (avgScore < 7.0) {
    risks.push('Hiệu suất team thấp');
  }
  
  const juniorCount = members.filter(m => {
    const evaluations = m.receivedEvaluations || [];
    const score = evaluations.length > 0 
      ? evaluations.reduce((sum, eval) => sum + (eval.overallScore || 0), 0) / evaluations.length 
      : 6.0;
    return getCapabilityLevel(score) === 'junior';
  }).length;
  
  if (members.length > 0 && juniorCount > members.length * 0.5) {
    risks.push('Quá nhiều junior trong team');
  }
  
  if (complexity === 'very_complex' && avgScore < 8.0) {
    risks.push('Dự án phức tạp với team chưa đủ kinh nghiệm');
  }
  
  return risks;
}

function analyzeSkillGaps(userCapabilities, requiredRoles) {
  const gaps = [];
  
  requiredRoles.forEach(role => {
    const roleUsers = userCapabilities.filter(u => 
      u.user.position.toLowerCase().includes(role.toLowerCase()) ||
      u.user.department.toLowerCase().includes(role.toLowerCase())
    );
    
    if (roleUsers.length === 0) {
      gaps.push(`Thiếu nhân sự cho vai trò: ${role}`);
    } else {
      const avgScore = roleUsers.length > 0 ? roleUsers.reduce((sum, u) => {
        const evaluations = u.receivedEvaluations || [];
        const score = evaluations.length > 0 
          ? evaluations.reduce((sum, eval) => sum + (eval.overallScore || 0), 0) / evaluations.length 
          : 6.0;
        return sum + score;
      }, 0) / roleUsers.length : 0;
      
      if (avgScore < 7.0) {
        gaps.push(`Năng lực ${role} cần cải thiện (điểm trung bình: ${avgScore.toFixed(1)})`);
      }
    }
  });
  
  return gaps;
}

module.exports = router; 