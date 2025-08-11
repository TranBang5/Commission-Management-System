const express = require('express');
const router = express.Router();
const passport = require('../auth/google');
const googleService = require('../services/google.service');

// Đăng nhập/đăng ký Google
router.get('/auth/google', passport.authenticate('google', { scope: ['profile', 'email'] }));

router.get('/auth/google/callback',
  passport.authenticate('google', { failureRedirect: '/login-failed' }),
  (req, res) => {
    // Đăng nhập thành công, trả về thông tin user hoặc redirect
    res.json({ user: req.user, message: 'Đăng nhập Google thành công!' });
  }
);

// Đăng xuất
router.get('/logout', (req, res) => {
  req.logout(() => {
    res.json({ message: 'Đã đăng xuất!' });
  });
});

// Lấy thông tin user hiện tại
router.get('/me', googleService.ensureAuthenticated, (req, res) => {
  res.json({ user: req.user });
});

module.exports = router;
