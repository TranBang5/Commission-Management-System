// Service for sending verification email (reuse mail.service.js)
const mailService = require('./mail.service');

exports.sendVerificationEmail = async (email) => {
  // Call the existing mailService logic
  return mailService.sendVerificationEmail({ email });
};
