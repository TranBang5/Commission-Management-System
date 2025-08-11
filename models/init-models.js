var DataTypes = require("sequelize").DataTypes;
var _ai_analysis_logs = require("./ai_analysis_logs");
var _audit_trails = require("./audit_trails");
var _complaints = require("./complaints");
var _performance_reviews = require("./performance_reviews");
var _project_members = require("./project_members");
var _projects = require("./projects");
var _reward_calculations = require("./reward_calculations");
var _reward_policies = require("./reward_policies");
var _rewards = require("./rewards");
var _users = require("./users");

function initModels(sequelize) {
  var ai_analysis_logs = _ai_analysis_logs(sequelize, DataTypes);
  var audit_trails = _audit_trails(sequelize, DataTypes);
  var complaints = _complaints(sequelize, DataTypes);
  var performance_reviews = _performance_reviews(sequelize, DataTypes);
  var project_members = _project_members(sequelize, DataTypes);
  var projects = _projects(sequelize, DataTypes);
  var reward_calculations = _reward_calculations(sequelize, DataTypes);
  var reward_policies = _reward_policies(sequelize, DataTypes);
  var rewards = _rewards(sequelize, DataTypes);
  var users = _users(sequelize, DataTypes);

  performance_reviews.belongsTo(projects, { as: "project", foreignKey: "project_id"});
  projects.hasMany(performance_reviews, { as: "performance_reviews", foreignKey: "project_id"});
  project_members.belongsTo(projects, { as: "project", foreignKey: "project_id"});
  projects.hasMany(project_members, { as: "project_members", foreignKey: "project_id"});
  reward_calculations.belongsTo(projects, { as: "project", foreignKey: "project_id"});
  projects.hasMany(reward_calculations, { as: "reward_calculations", foreignKey: "project_id"});
  rewards.belongsTo(reward_calculations, { as: "calculation", foreignKey: "calculation_id"});
  reward_calculations.hasMany(rewards, { as: "rewards", foreignKey: "calculation_id"});
  reward_calculations.belongsTo(reward_policies, { as: "reward_policy", foreignKey: "reward_policy_id"});
  reward_policies.hasMany(reward_calculations, { as: "reward_calculations", foreignKey: "reward_policy_id"});
  complaints.belongsTo(rewards, { as: "reward", foreignKey: "reward_id"});
  rewards.hasMany(complaints, { as: "complaints", foreignKey: "reward_id"});
  audit_trails.belongsTo(users, { as: "user", foreignKey: "user_id"});
  users.hasMany(audit_trails, { as: "audit_trails", foreignKey: "user_id"});
  complaints.belongsTo(users, { as: "user", foreignKey: "user_id"});
  users.hasMany(complaints, { as: "complaints", foreignKey: "user_id"});
  complaints.belongsTo(users, { as: "handler_user", foreignKey: "handler_user_id"});
  users.hasMany(complaints, { as: "handler_user_complaints", foreignKey: "handler_user_id"});
  performance_reviews.belongsTo(users, { as: "reviewee_user", foreignKey: "reviewee_user_id"});
  users.hasMany(performance_reviews, { as: "performance_reviews", foreignKey: "reviewee_user_id"});
  performance_reviews.belongsTo(users, { as: "reviewer_user", foreignKey: "reviewer_user_id"});
  users.hasMany(performance_reviews, { as: "reviewer_user_performance_reviews", foreignKey: "reviewer_user_id"});
  project_members.belongsTo(users, { as: "user", foreignKey: "user_id"});
  users.hasMany(project_members, { as: "project_members", foreignKey: "user_id"});
  projects.belongsTo(users, { as: "business_partner", foreignKey: "business_partner_id"});
  users.hasMany(projects, { as: "projects", foreignKey: "business_partner_id"});
  reward_calculations.belongsTo(users, { as: "approved_by_user", foreignKey: "approved_by_user_id"});
  users.hasMany(reward_calculations, { as: "reward_calculations", foreignKey: "approved_by_user_id"});
  reward_policies.belongsTo(users, { as: "created_by_user", foreignKey: "created_by_user_id"});
  users.hasMany(reward_policies, { as: "reward_policies", foreignKey: "created_by_user_id"});
  rewards.belongsTo(users, { as: "user", foreignKey: "user_id"});
  users.hasMany(rewards, { as: "rewards", foreignKey: "user_id"});

  return {
    ai_analysis_logs,
    audit_trails,
    complaints,
    performance_reviews,
    project_members,
    projects,
    reward_calculations,
    reward_policies,
    rewards,
    users,
  };
}
module.exports = initModels;
module.exports.initModels = initModels;
module.exports.default = initModels;
