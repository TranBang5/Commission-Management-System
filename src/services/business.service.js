const { models } = require('../db');
const axios = require('axios');

exports.getLinkedProjects = async (user) => {
    // Lấy các dự án mà doanh nghiệp này là business_partner
    return await models.projects.findAll({ where: { business_partner_id: user.id } });
};

exports.getProjectProgress = async (projectId) => {
    // Lấy tiến độ dự án (có thể lấy từ milestones, status, v.v.)
    const project = await models.projects.findByPk(projectId);
    // Giả lập tiến độ
    return { id: project.id, name: project.name, status: project.status };
};

exports.getProjectTeam = async (projectId) => {
    // Lấy danh sách thành viên dự án
    return await models.project_members.findAll({ where: { project_id: projectId }, include: [{ model: models.users, as: 'user' }] });
};

exports.getProjectPerformance = async (projectId) => {
    // Lấy đánh giá hiệu suất dự án
    return await models.performance_reviews.findAll({ where: { project_id: projectId } });
};

exports.submitProjectReview = async (projectId, data) => {
    // Nhận xét định tính, đánh giá sau dự án
    return await models.performance_reviews.create({ project_id: projectId, ...data });
};

exports.nlpAnalyzeReview = async (text) => {
    // Gọi AI để loại bỏ cảm tính, phân loại phản hồi
    const response = await axios.post('https://api.openai.com/v1/chat/completions', {
        model: "gpt-4",
        messages: [
            { role: "system", content: "Bạn là AI phân tích nhận xét dự án, loại bỏ cảm tính, phân loại phản hồi." },
            { role: "user", content: text }
        ]
    }, {
        headers: { 'Authorization': `Bearer ${process.env.OPENAI_API_KEY}` }
    });
    return response.data.choices[0].message.content;
};
