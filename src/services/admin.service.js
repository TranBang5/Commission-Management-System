const { models } = require('../db');

// Dự án
exports.getProjects = async () => {
    return await models.projects.findAll();
};
exports.createProject = async (data) => {
    return await models.projects.create(data);
};

// Khung thưởng (Reward Policy)
exports.getRewardFrames = async () => {
    return await models.reward_policies.findAll();
};
exports.createRewardFrame = async (data) => {
    return await models.reward_policies.create(data);
};

// Tính thưởng tự động (Reward Calculation)
exports.calculateReward = async (data) => {
    // data: { project_id, reward_policy_id, total_reward_pool }
    const project = await models.projects.findByPk(data.project_id, {
        include: [{ model: models.project_members, as: 'project_members' }]
    });
    if (!project) return { error: 'Project not found' };
    const members = project.project_members || [];
    const perMember = data.total_reward_pool / (members.length || 1);
    // Lưu kết quả vào reward_calculations
    const calculation = await models.reward_calculations.create({
        project_id: data.project_id,
        reward_policy_id: data.reward_policy_id,
        total_reward_pool: data.total_reward_pool,
        status: 'PRELIMINARY'
    });
    // Tạo bản ghi rewards cho từng thành viên
    for (const m of members) {
        await models.rewards.create({
            calculation_id: calculation.id,
            user_id: m.user_id,
            amount: perMember
        });
    }
    return { calculation_id: calculation.id, perMember };
};

// Quản lý dữ liệu đầu vào (project_members)
exports.getInputData = async () => {
    return await models.project_members.findAll();
};
exports.createInputData = async (data) => {
    return await models.project_members.create(data);
};

// Khiếu nại
exports.getComplaints = async () => {
    return await models.complaints.findAll();
};
exports.createComplaint = async (data) => {
    return await models.complaints.create(data);
};
