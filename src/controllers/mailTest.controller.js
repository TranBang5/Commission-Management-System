// Controller for testing email verification send
const mailService = require('../services/mail.service');
const { models } = require('../db');

exports.testSendVerification = async (req, res) => {
  try {
const { email } = req.body;
const user = await models.users.findOne({ where: { email } });
if (!user) return res.status(404).json({ message: 'User not found' });
await mailService.sendVerificationEmail({ id: user.id, email: user.email });
    res.json({ message: 'Verification email sent' });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};
