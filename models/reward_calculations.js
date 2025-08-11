const Sequelize = require('sequelize');
module.exports = function(sequelize, DataTypes) {
  return sequelize.define('reward_calculations', {
    id: {
      autoIncrement: true,
      type: DataTypes.INTEGER,
      allowNull: false,
      primaryKey: true
    },
    project_id: {
      type: DataTypes.INTEGER,
      allowNull: false,
      references: {
        model: 'projects',
        key: 'id'
      }
    },
    reward_policy_id: {
      type: DataTypes.INTEGER,
      allowNull: false,
      references: {
        model: 'reward_policies',
        key: 'id'
      }
    },
    calculation_date: {
      type: DataTypes.DATE,
      allowNull: true,
      defaultValue: Sequelize.Sequelize.literal('CURRENT_TIMESTAMP')
    },
    total_reward_pool: {
      type: DataTypes.DECIMAL(15,2),
      allowNull: false
    },
    status: {
      type: DataTypes.ENUM('PRELIMINARY','PENDING_APPROVAL','APPROVED','PAID'),
      allowNull: false
    },
    approved_by_user_id: {
      type: DataTypes.INTEGER,
      allowNull: true,
      references: {
        model: 'users',
        key: 'id'
      }
    },
    approved_at: {
      type: DataTypes.DATE,
      allowNull: true
    }
  }, {
    sequelize,
    tableName: 'reward_calculations',
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
        name: "project_id",
        using: "BTREE",
        fields: [
          { name: "project_id" },
        ]
      },
      {
        name: "reward_policy_id",
        using: "BTREE",
        fields: [
          { name: "reward_policy_id" },
        ]
      },
      {
        name: "approved_by_user_id",
        using: "BTREE",
        fields: [
          { name: "approved_by_user_id" },
        ]
      },
    ]
  });
};
