const Sequelize = require('sequelize');
module.exports = function(sequelize, DataTypes) {
  return sequelize.define('performance_reviews', {
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
    reviewee_user_id: {
      type: DataTypes.INTEGER,
      allowNull: false,
      comment: "Người được đánh giá",
      references: {
        model: 'users',
        key: 'id'
      }
    },
    reviewer_user_id: {
      type: DataTypes.INTEGER,
      allowNull: false,
      comment: "Người đánh giá",
      references: {
        model: 'users',
        key: 'id'
      }
    },
    quantitative_score: {
      type: DataTypes.TINYINT,
      allowNull: true
    },
    qualitative_feedback: {
      type: DataTypes.TEXT,
      allowNull: true,
      comment: "Đầu vào cho xử lý ngôn ngữ tự nhiên (NLP)"
    },
    review_date: {
      type: DataTypes.DATE,
      allowNull: true,
      defaultValue: Sequelize.Sequelize.literal('CURRENT_TIMESTAMP')
    }
  }, {
    sequelize,
    tableName: 'performance_reviews',
    timestamps: false,
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
        name: "reviewee_user_id",
        using: "BTREE",
        fields: [
          { name: "reviewee_user_id" },
        ]
      },
      {
        name: "reviewer_user_id",
        using: "BTREE",
        fields: [
          { name: "reviewer_user_id" },
        ]
      },
    ]
  });
};
