const express = require('express');
const bodyParser = require('body-parser');
require('dotenv').config();
require('./db'); // Thêm dòng này ngay sau require('dotenv').config();

const adminRoutes = require('./routes/admin.routes');
const aiAgentRoutes = require('./routes/aiAgent.routes');
const businessRoutes = require('./routes/business.routes');

const app = express();
app.use(bodyParser.json());


app.use('/api/admin', adminRoutes);
app.use('/api/ai-agent', aiAgentRoutes);
app.use('/api/business', businessRoutes);

app.get('/', (req, res) => res.send('N-Tier NodeJS Project with AI is running!'));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
