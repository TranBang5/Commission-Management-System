const Sequelize = require('sequelize');
module.exports = function(sequelize, DataTypes) {
  return sequelize.define('rewards', {
    id: {
      autoIncrement: true,
      type: DataTypes.INTEGER,
      allowNull: false,
      primaryKey: true
    },
    calculation_id: {
      type: DataTypes.INTEGER,
      allowNull: false,
      references: {
        model: 'reward_calculations',
        key: 'id'
      }
    },
    user_id: {
      type: DataTypes.INTEGER,
      allowNull: false,
      references: {
        model: 'users',
        key: 'id'
      }
    },
    amount: {
      type: DataTypes.DECIMAL(15,2),
      allowNull: false
    },
    explanation: {
      type: DataTypes.TEXT,
      allowNull: true,
      comment: "Nội dung giải thích do AI tạo để minh bạch hóa"
    }
  }, {
    sequelize,
    tableName: 'rewards',
    indexes: [
      {
        name: "PRIMARY",
        unique: true,
        using: "BTREE",
        fields: [
          { name: "id" },
        ]
      },
      {
        name: "calculation_id",
        using: "BTREE",
        fields: [
          { name: "calculation_id" },
        ]
      },
      {
        name: "user_id",
        using: "BTREE",
        fields: [
          { name: "user_id" },
        ]
      },
    ]
  });
};
