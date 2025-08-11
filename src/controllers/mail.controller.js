const mailService = require('../services/mail.service');
const { models } = require('../db');

exports.verifyEmail = async (req, res) => {
  const { token } = req.query;
  const payload = mailService.verifyToken(token);
  if (!payload) return res.status(400).json({ message: 'Token không hợp lệ hoặc đã hết hạn!' });
  await models.users.update({ is_verified: true }, { where: { id: payload.userId } });
  res.json({ message: 'Xác thực email thành công!' });
};
