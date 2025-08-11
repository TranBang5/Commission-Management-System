const express = require('express');
const router = express.Router();
const aiAgentController = require('../controllers/aiAgent.controller');

router.post('/suggest-reward-frame', aiAgentController.suggestRewardFrame);
router.post('/apply-reward-policy', aiAgentController.applyRewardPolicy);
router.post('/clean-mapping', aiAgentController.cleanAndDetectMappingErrors);
router.post('/analyze-complaint', aiAgentController.analyzeComplaint);

module.exports = router;
