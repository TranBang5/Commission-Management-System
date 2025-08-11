const Sequelize = require('sequelize');
module.exports = function(sequelize, DataTypes) {
  return sequelize.define('complaints', {
    id: {
      autoIncrement: true,
      type: DataTypes.INTEGER,
      allowNull: false,
      primaryKey: true
    },
    user_id: {
      type: DataTypes.INTEGER,
      allowNull: false,
      references: {
        model: 'users',
        key: 'id'
      }
    },
    reward_id: {
      type: DataTypes.INTEGER,
      allowNull: false,
      references: {
        model: 'rewards',
        key: 'id'
      }
    },
    content: {
      type: DataTypes.TEXT,
      allowNull: false
    },
    status: {
      type: DataTypes.ENUM('OPEN','AI_RESPONDED','PENDING_MANAGER','RESOLVED','CLOSED'),
      allowNull: false,
      defaultValue: "OPEN"
    },
    handler_user_id: {
      type: DataTypes.INTEGER,
      allowNull: true,
      references: {
        model: 'users',
        key: 'id'
      }
    },
    resolution: {
      type: DataTypes.TEXT,
      allowNull: true
    }
  }, {
    sequelize,
    tableName: 'complaints',
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
        name: "user_id",
        using: "BTREE",
        fields: [
          { name: "user_id" },
        ]
      },
      {
        name: "reward_id",
        using: "BTREE",
        fields: [
          { name: "reward_id" },
        ]
      },
      {
        name: "handler_user_id",
        using: "BTREE",
        fields: [
          { name: "handler_user_id" },
        ]
      },
    ]
  });
};
