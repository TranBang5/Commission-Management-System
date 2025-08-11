require('dotenv').config();
const express = require('express');
const bodyParser = require('body-parser');
const session = require('express-session');
const passport = require('./auth/google');

require('./db');

const adminRoutes = require('./routes/admin.routes');
const aiAgentRoutes = require('./routes/aiAgent.routes');
const businessRoutes = require('./routes/business.routes');
const googleRoutes = require('./routes/google.routes');
const mailRoutes = require('./routes/mail.routes');

const mailTestRoutes = require('./routes/mailTest.routes');

const app = express();
app.use(bodyParser.json());
app.use(session({
	secret: process.env.SESSION_SECRET || 'secret',
	resave: false,
	saveUninitialized: false
}));
app.use(passport.initialize());
app.use(passport.session());



app.use('/api/admin', adminRoutes);
app.use('/api/ai-agent', aiAgentRoutes);
app.use('/api/business', businessRoutes);
app.use('/', googleRoutes);
app.use('/', mailRoutes);

app.use('/api/test', mailTestRoutes);

// ...existing code...

app.get('/', (req, res) => res.send('N-Tier NodeJS Project with AI is running!'));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
