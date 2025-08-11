const businessService = require('../services/business.service');

exports.getLinkedProjects = async (req, res) => {
    try {
        const projects = await businessService.getLinkedProjects(req.user); // user là doanh nghiệp
        res.json(projects);
    } catch (err) {
        res.status(500).json({ message: 'Lỗi khi lấy danh sách dự án liên kết', error: err.message });
    }
};

exports.getProjectProgress = async (req, res) => {
    try {
        const progress = await businessService.getProjectProgress(req.params.id);
        res.json(progress);
    } catch (err) {
        res.status(500).json({ message: 'Lỗi khi lấy tiến độ dự án', error: err.message });
    }
};

exports.getProjectTeam = async (req, res) => {
    try {
        const team = await businessService.getProjectTeam(req.params.id);
        res.json(team);
    } catch (err) {
        res.status(500).json({ message: 'Lỗi khi lấy hồ sơ nhóm nhân sự', error: err.message });
    }
};

exports.getProjectPerformance = async (req, res) => {
    try {
        const perf = await businessService.getProjectPerformance(req.params.id);
        res.json(perf);
    } catch (err) {
        res.status(500).json({ message: 'Lỗi khi lấy hiệu suất dự án', error: err.message });
    }
};

exports.submitProjectReview = async (req, res) => {
    try {
        const review = await businessService.submitProjectReview(req.params.id, req.body);
        res.json(review);
    } catch (err) {
        res.status(500).json({ message: 'Lỗi khi gửi nhận xét', error: err.message });
    }
};

exports.nlpAnalyzeReview = async (req, res) => {
    try {
        const result = await businessService.nlpAnalyzeReview(req.body.text);
        res.json(result);
    } catch (err) {
        res.status(500).json({ message: 'Lỗi NLP', error: err.message });
    }
};
