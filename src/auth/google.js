console.log(process.env);
const passport = require('passport');
const GoogleStrategy = require('passport-google-oauth20').Strategy;
const { models } = require('../db');

passport.use(new GoogleStrategy({
    clientID: process.env.GOOGLE_CLIENT_ID,
    clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    callbackURL: process.env.GOOGLE_CALLBACK_URL
  },
  async (accessToken, refreshToken, profile, done) => {
    try {
      // Tìm hoặc tạo user
      let user = await models.users.findOne({ where: { email: profile.emails[0].value } });
      if (!user) {
        user = await models.users.create({
          full_name: profile.displayName,
          email: profile.emails[0].value,
          password_hash: '', // Không cần mật khẩu
          system_role: 'EMPLOYEE' // hoặc BUSINESS_PARTNER, tùy logic
        });
      }
      return done(null, user);
    } catch (err) {
      return done(err, null);
    }
  }
));

passport.serializeUser((user, done) => {
  done(null, user.id);
});

passport.deserializeUser(async (id, done) => {
  try {
    const user = await models.users.findByPk(id);
    done(null, user);
  } catch (err) {
    done(err, null);
  }
});

module.exports = passport;
