const aiAgentService = require('../services/aiAgent.service');

exports.suggestRewardFrame = async (req, res) => {
    try {
        const result = await aiAgentService.suggestRewardFrame(req.body.projectData);
        res.json({ suggestion: result });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
};

exports.applyRewardPolicy = async (req, res) => {
    try {
        const result = await aiAgentService.applyRewardPolicy(req.body);
        res.json(result);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
};

exports.cleanAndDetectMappingErrors = (req, res) => {
    const result = aiAgentService.cleanAndDetectMappingErrors(req.body.inputData);
    res.json(result);
};

exports.analyzeComplaint = async (req, res) => {
    try {
        const result = await aiAgentService.analyzeComplaint(req.body.complaintText);
        res.json({ analysis: result });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
};
