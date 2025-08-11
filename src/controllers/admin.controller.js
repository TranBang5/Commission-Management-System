const adminService = require('../services/admin.service');

// Dùng async/await và try/catch cho tất cả các hàm

exports.getProjects = async (req, res) => {
    try {
        const projects = await adminService.getProjects();
        res.json(projects);
    } catch (error) {
        res.status(500).json({ message: 'Lỗi khi lấy danh sách dự án', error: error.message });
    }
};

exports.createProject = async (req, res) => {
    try {
        const project = await adminService.createProject(req.body);
        res.status(201).json(project);
    } catch (error) {
        res.status(500).json({ message: 'Lỗi khi tạo dự án', error: error.message });
    }
};

exports.getRewardFrames = async (req, res) => {
    try {
        const frames = await adminService.getRewardFrames();
        res.json(frames);
    } catch (error) {
        res.status(500).json({ message: 'Lỗi khi lấy khung thưởng', error: error.message });
    }
};

exports.createRewardFrame = async (req, res) => {
    try {
        const frame = await adminService.createRewardFrame(req.body);
        res.status(201).json(frame);
    } catch (error) {
        res.status(500).json({ message: 'Lỗi khi tạo khung thưởng', error: error.message });
    }
};

exports.calculateReward = async (req, res) => {
    try {
        const result = await adminService.calculateReward(req.body);
        res.json(result);
    } catch (error) {
        res.status(500).json({ message: 'Lỗi khi tính thưởng', error: error.message });
    }
};

exports.getInputData = async (req, res) => {
    try {
        const data = await adminService.getInputData();
        res.json(data);
    } catch (error) {
        res.status(500).json({ message: 'Lỗi khi lấy dữ liệu đầu vào', error: error.message });
    }
};

exports.createInputData = async (req, res) => {
    try {
        const data = await adminService.createInputData(req.body);
        res.status(201).json(data);
    } catch (error) {
        res.status(500).json({ message: 'Lỗi khi tạo dữ liệu đầu vào', error: error.message });
    }
};

exports.getComplaints = async (req, res) => {
    try {
        const complaints = await adminService.getComplaints();
        res.json(complaints);
    } catch (error) {
        res.status(500).json({ message: 'Lỗi khi lấy khiếu nại', error: error.message });
    }
};

exports.createComplaint = async (req, res) => {
    try {
        const complaint = await adminService.createComplaint(req.body);
        res.status(201).json(complaint);
    } catch (error) {
        res.status(500).json({ message: 'Lỗi khi tạo khiếu nại', error: error.message });
    }
};