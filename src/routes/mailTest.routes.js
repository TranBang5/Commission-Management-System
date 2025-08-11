// Router for testing email verification send
const express = require('express');
const router = express.Router();
const mailTestController = require('../controllers/mailTest.controller');

// POST /test/send-verification
router.post('/send-verification', mailTestController.testSendVerification);

module.exports = router;
