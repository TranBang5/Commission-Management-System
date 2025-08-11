const Sequelize = require('sequelize');
module.exports = function(sequelize, DataTypes) {
  return sequelize.define('ai_analysis_logs', {
    id: {
      autoIncrement: true,
      type: DataTypes.BIGINT,
      allowNull: false,
      primaryKey: true
    },
    source_table: {
      type: DataTypes.STRING(255),
      allowNull: true
    },
    source_id: {
      type: DataTypes.INTEGER,
      allowNull: true
    },
    analysis_type: {
      type: DataTypes.ENUM('SENTIMENT_ANALYSIS','BIAS_DETECTION','KPI_SUGGESTION','POLICY_SIMULATION','PERFORMANCE_FORECAST'),
      allowNull: false
    },
    result: {
      type: DataTypes.JSON,
      allowNull: true,
      comment: "Kết quả phân tích của AI"
    }
  }, {
    sequelize,
    tableName: 'ai_analysis_logs',
    indexes: [
      {
        name: "PRIMARY",
        unique: true,
        using: "BTREE",
        fields: [
          { name: "id" },
        ]
      },
    ]
  });
};
