const { Sequelize } = require('sequelize');
const initModels = require('../models/init-models');

const sequelize = new Sequelize(process.env.DB_NAME, process.env.DB_USER, process.env.DB_PASS, {
  host: process.env.DB_HOST,
  dialect: 'mysql', // hoặc 'postgres', 'mssql' tùy hệ quản trị
  logging: false,
  define: {          // <--- THÊM KHỐI NÀY
    underscored: true  // <--- VÀ DÒNG QUAN TRỌNG NÀY
  }
});

const models = initModels(sequelize);

module.exports = { sequelize, models };
