const express = require('express');
const router = express.Router();
const mailController = require('../controllers/mail.controller');

// Route xác thực email
router.get('/verify-email', mailController.verifyEmail);

module.exports = router;
