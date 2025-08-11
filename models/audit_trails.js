const Sequelize = require('sequelize');
module.exports = function(sequelize, DataTypes) {
  return sequelize.define('audit_trails', {
    id: {
      autoIncrement: true,
      type: DataTypes.BIGINT,
      allowNull: false,
      primaryKey: true
    },
    user_id: {
      type: DataTypes.INTEGER,
      allowNull: true,
      references: {
        model: 'users',
        key: 'id'
      }
    },
    is_ai_action: {
      type: DataTypes.BOOLEAN,
      allowNull: true,
      defaultValue: 0
    },
    action_type: {
      type: DataTypes.STRING(255),
      allowNull: false
    },
    target_table: {
      type: DataTypes.STRING(255),
      allowNull: true
    },
    target_id: {
      type: DataTypes.INTEGER,
      allowNull: true
    },
    old_data: {
      type: DataTypes.JSON,
      allowNull: true
    },
    new_data: {
      type: DataTypes.JSON,
      allowNull: true
    },
    timestamp: {
      type: DataTypes.DATE,
      allowNull: true,
      defaultValue: Sequelize.Sequelize.literal('CURRENT_TIMESTAMP')
    }
  }, {
    sequelize,
    tableName: 'audit_trails',
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
    ]
  });
};
