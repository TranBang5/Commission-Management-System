const express = require('express');
const router = express.Router();
const businessController = require('../controllers/business.controller');

router.get('/projects', businessController.getLinkedProjects);
router.get('/projects/:id/progress', businessController.getProjectProgress);
router.get('/projects/:id/team', businessController.getProjectTeam);
router.get('/projects/:id/performance', businessController.getProjectPerformance);
router.post('/projects/:id/review', businessController.submitProjectReview);
router.post('/nlp/review', businessController.nlpAnalyzeReview);

module.exports = router;
