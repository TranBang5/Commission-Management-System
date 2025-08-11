const express = require('express');
const router = express.Router();
const adminController = require('../controllers/admin.controller');

router.get('/projects', adminController.getProjects);
router.post('/projects', adminController.createProject);

router.get('/reward-frames', adminController.getRewardFrames);
router.post('/reward-frames', adminController.createRewardFrame);

router.post('/calculate-reward', adminController.calculateReward);

router.get('/input-data', adminController.getInputData);
router.post('/input-data', adminController.createInputData);

router.get('/complaints', adminController.getComplaints);
router.post('/complaints', adminController.createComplaint);

module.exports = router;
