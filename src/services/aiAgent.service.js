
const axios = require('axios');
const { models } = require('../db');

async function callOpenAI(messages) {
    const response = await axios.post(
        'https://api.openai.com/v1/chat/completions',
        {
            model: "gpt-4",
            messages
        },
        {
            headers: { 'Authorization': `Bearer ${process.env.OPENAI_API_KEY}` }
        }
    );
    return response.data.choices[0].message.content;
}

// Đề xuất khung thưởng cho nhóm nhân sự dựa theo phân công dự án
exports.suggestRewardFrame = async (projectData) => {
    // Lấy thông tin dự án và thành viên từ DB nếu có id
    let project = projectData;
    if (projectData.id) {
        project = await models.projects.findByPk(projectData.id, {
            include: [{ model: models.project_members, as: 'project_members' }]
        });
    }
    const messages = [
        { role: "system", content: "Bạn là chuyên gia nhân sự." },
        { role: "user", content: `Dự án: ${JSON.stringify(project)}. Đề xuất khung thưởng phù hợp cho nhóm nhân sự.` }
    ];
    const suggestion = await callOpenAI(messages);
    // Lưu log AI
    await models.ai_analysis_logs.create({
        source_table: 'projects',
        source_id: projectData.id || null,
        analysis_type: 'KPI_SUGGESTION',
        result: { suggestion }
    });
    return suggestion;
};

// Tự động áp dụng các chính sách và khung thưởng để phân chia doanh thu
exports.applyRewardPolicy = async (data) => {
    // data: { project_id, reward_policy_id, total_reward_pool }
    const project = await models.projects.findByPk(data.project_id, {
        include: [{ model: models.project_members, as: 'project_members' }]
    });
    const policy = await models.reward_policies.findByPk(data.reward_policy_id);
    const messages = [
        { role: "system", content: "Bạn là AI chuyên tự động phân chia doanh thu theo chính sách thưởng." },
        { role: "user", content: `Dự án: ${JSON.stringify(project)}, Chính sách: ${JSON.stringify(policy)}, Tổng thưởng: ${data.total_reward_pool}. Hãy tự động áp dụng chính sách và trả về kết quả chia thưởng chi tiết cho từng thành viên.` }
    ];
    const result = await callOpenAI(messages);
    await models.ai_analysis_logs.create({
        source_table: 'reward_calculations',
        source_id: null,
        analysis_type: 'POLICY_SIMULATION',
        result: { result }
    });
    return result;
};

// Tự động ánh xạ dữ liệu, làm sạch, phát hiện lỗi mapping
exports.cleanAndDetectMappingErrors = (inputData) => {
    const errors = [];
    inputData.forEach((item, idx) => {
        if (!item.name || !item.value) errors.push({ idx, error: 'Thiếu trường bắt buộc' });
    });
    return { cleaned: inputData.filter(i => i.name && i.value), errors };
};

// NLP phân tích nội dung khiếu nại, gợi ý phản hồi và ưu tiên xử lý
exports.analyzeComplaint = async (complaintText) => {
    const messages = [
        { role: "system", content: "Bạn là chuyên gia chăm sóc khách hàng." },
        { role: "user", content: `Phân tích khiếu nại: "${complaintText}". Gợi ý phản hồi và mức độ ưu tiên xử lý.` }
    ];
    const analysis = await callOpenAI(messages);
    await models.ai_analysis_logs.create({
        source_table: 'complaints',
        source_id: null,
        analysis_type: 'SENTIMENT_ANALYSIS',
        result: { analysis }
    });
    return analysis;
};
