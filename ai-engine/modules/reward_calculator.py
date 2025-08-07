import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class RewardCalculator:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.model_path = "models/reward_calculator.pkl"
        self.scaler_path = "models/reward_scaler.pkl"
        
        # Load pre-trained model if exists
        self._load_model()
        
        # Define feature weights for different roles
        self.role_weights = {
            # Đội ngũ phát triển
            'developer': {
                'kpi_score': 0.25,
                'quality_score': 0.20,
                'efficiency_score': 0.20,
                'teamwork_score': 0.15,
                'innovation_score': 0.10,
                'project_progress': 0.10
            },
            # Đội ngũ marketing
            'marketing_specialist': {
                'kpi_score': 0.30,
                'quality_score': 0.15,
                'efficiency_score': 0.20,
                'teamwork_score': 0.15,
                'innovation_score': 0.15,
                'project_progress': 0.05
            },
            # Các mentor
            'direct_mentor': {
                'kpi_score': 0.20,
                'quality_score': 0.15,
                'efficiency_score': 0.15,
                'teamwork_score': 0.30,
                'innovation_score': 0.10,
                'project_progress': 0.10
            },
            'indirect_mentor': {
                'kpi_score': 0.15,
                'quality_score': 0.15,
                'efficiency_score': 0.15,
                'teamwork_score': 0.25,
                'innovation_score': 0.15,
                'project_progress': 0.15
            },
            # Đội ngũ thu hút nhân lực
            'hr_recruiter': {
                'kpi_score': 0.35,
                'quality_score': 0.20,
                'efficiency_score': 0.25,
                'teamwork_score': 0.10,
                'innovation_score': 0.05,
                'project_progress': 0.05
            },
            # Đội ngũ liên hệ doanh nghiệp
            'business_development': {
                'kpi_score': 0.30,
                'quality_score': 0.15,
                'efficiency_score': 0.20,
                'teamwork_score': 0.20,
                'innovation_score': 0.10,
                'project_progress': 0.05
            }
        }
        
        # Bonus multipliers based on performance levels
        self.bonus_multipliers = {
            'excellent': 1.5,  # 90-100%
            'good': 1.3,       # 80-89%
            'average': 1.1,    # 70-79%
            'below_average': 0.9,  # 60-69%
            'poor': 0.7        # <60%
        }
        
        # Project profit sharing rates
        self.profit_sharing_rates = {
            # Đội ngũ phát triển
            'developer': 0.02,  # 2% of project profit
            # Đội ngũ marketing
            'marketing_specialist': 0.015,
            # Các mentor
            'direct_mentor': 0.025,
            'indirect_mentor': 0.02,
            # Đội ngũ thu hút nhân lực
            'hr_recruiter': 0.015,
            # Đội ngũ liên hệ doanh nghiệp
            'business_development': 0.025
        }

    def _load_model(self):
        """Load pre-trained model if available"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                self.is_trained = True
                logger.info("Pre-trained reward calculator model loaded")
            else:
                logger.info("No pre-trained model found, will use rule-based calculation")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")

    def _save_model(self):
        """Save trained model"""
        try:
            os.makedirs("models", exist_ok=True)
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            logger.info("Model saved successfully")
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")

    def _extract_features(self, performance_data: Dict[str, Any], role: str) -> np.ndarray:
        """Extract features from performance data"""
        features = []
        
        # Basic performance metrics
        features.extend([
            performance_data.get('kpi_score', 0),
            performance_data.get('quality_score', 0),
            performance_data.get('efficiency_score', 0),
            performance_data.get('teamwork_score', 0),
            performance_data.get('innovation_score', 0),
            performance_data.get('project_progress', 0),
            performance_data.get('client_satisfaction', 0),
            performance_data.get('deadline_adherence', 0)
        ])
        
        # Role-specific features
        role_encoding = {
            'developer': [1, 0, 0, 0, 0, 0],
            'designer': [0, 1, 0, 0, 0, 0],
            'tester': [0, 0, 1, 0, 0, 0],
            'analyst': [0, 0, 0, 1, 0, 0],
            'lead': [0, 0, 0, 0, 1, 0],
            'consultant': [0, 0, 0, 0, 0, 1]
        }
        features.extend(role_encoding.get(role, [0, 0, 0, 0, 0, 0]))
        
        # Project metrics
        features.extend([
            performance_data.get('project_profit', 0),
            performance_data.get('base_salary', 0)
        ])
        
        return np.array(features).reshape(1, -1)

    def _calculate_weighted_score(self, performance_data: Dict[str, Any], role: str) -> float:
        """Calculate weighted performance score based on role"""
        weights = self.role_weights.get(role, self.role_weights['developer'])
        
        weighted_score = 0
        for metric, weight in weights.items():
            score = performance_data.get(metric, 0)
            weighted_score += score * weight
            
        return min(100, max(0, weighted_score))

    def _determine_performance_level(self, score: float) -> str:
        """Determine performance level based on score"""
        if score >= 90:
            return 'excellent'
        elif score >= 80:
            return 'good'
        elif score >= 70:
            return 'average'
        elif score >= 60:
            return 'below_average'
        else:
            return 'poor'

    def _calculate_bonus(self, base_salary: float, performance_level: str, 
                        project_revenue: float, role: str, performance_data: Dict[str, Any] = None) -> Dict[str, float]:
        
        # Lấy tỷ lệ % của vai trò từ profit_sharing_rates
        role_percentage = self.profit_sharing_rates.get(role, 0.02) * 100
        
        # Xác định tỷ lệ hiệu suất dựa trên xếp loại
        performance_rate = self.bonus_multipliers.get(performance_level, 1.0)
        
        # Áp dụng công thức tính thưởng duy nhất
        total_bonus = project_revenue * (role_percentage / 100) * performance_rate
        
        # Trả về kết quả để sử dụng trong mô hình lai
        return {
            'personal_bonus': total_bonus, # Giờ đây personal_bonus chính là total_bonus
            'role_percentage': role_percentage,
            'performance_rate': performance_rate,
            'quality_bonus': 0, # Không còn áp dụng
            'innovation_bonus': 0, # Không còn áp dụng
            'total_bonus': total_bonus
        }
        
    def _calculate_ai_confidence(self, performance_data: Dict[str, Any], 
                                historical_data: Optional[List[Dict]] = None) -> float:
        """Calculate AI confidence in the calculation"""
        # Simple confidence calculation based on data completeness
        required_fields = ['kpi_score', 'quality_score', 'efficiency_score', 
                         'teamwork_score', 'innovation_score', 'project_progress']
        
        completeness = sum(1 for field in required_fields 
                          if performance_data.get(field, 0) > 0) / len(required_fields)
        
        # Adjust confidence based on data consistency
        scores = [performance_data.get(field, 0) for field in required_fields]
        consistency = 1 - (np.std(scores) / 100) if scores else 0
        
        # Historical data consistency if available
        historical_consistency = 0
        if historical_data and len(historical_data) > 0:
            historical_scores = []
            for record in historical_data[-5:]:  # Last 5 records
                if 'performance_score' in record:
                    historical_scores.append(record['performance_score'])
            
            if historical_scores:
                historical_consistency = 1 - (np.std(historical_scores) / 100)
        
        # Weighted confidence calculation
        confidence = (completeness * 0.4 + consistency * 0.4 + historical_consistency * 0.2)
        return min(100, max(0, confidence * 100))

    # Thay thế hàm calculate cũ bằng hàm này

    async def calculate(self, period: Dict[str, int], project_id: str, 
                    employee_id: str, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        *** NEW SEQUENTIAL LOGIC ***
        1. AI (or Rules) determines the performance score.
        2. A simple formula calculates the final bonus from that score.
        """
        try:
            logger.info(f"Calculating commission for employee {employee_id}")
            
            role = performance_data.get('role', 'developer')
            base_salary = performance_data.get('base_salary', 0)
            project_revenue = performance_data.get('project_revenue', 0)

            # --- PHẦN 1: XÁC ĐỊNH ĐIỂM HIỆU SUẤT TỔNG HỢP ---
            final_performance_score = 0
            source_of_score = 'rule_based'

            if self.is_trained:
                # Nếu AI đã được huấn luyện, hãy dùng AI để dự đoán điểm
                try:
                    features = self._extract_features(performance_data, role)
                    scaled_features = self.scaler.transform(features)
                    predicted_score = self.model.predict(scaled_features)[0]
                    final_performance_score = max(0, min(100, predicted_score)) # Giới hạn điểm từ 0-100
                    source_of_score = 'ai_predicted'
                except Exception as e:
                    logger.warning(f"AI prediction failed: {e}. Falling back to rule-based score.")
                    # Nếu AI lỗi, quay về dùng luật
                    final_performance_score = self._calculate_weighted_score(performance_data, role)
            else:
                # Nếu AI chưa được huấn luyện, dùng hệ thống luật để tính điểm
                final_performance_score = self._calculate_weighted_score(performance_data, role)

            # --- PHẦN 2: TÍNH TOÁN THƯỞNG TỪ ĐIỂM HIỆU SUẤT ---
            
            # Chuyển đổi điểm số (0-100) sang cấp độ và tỷ lệ hiệu suất
            performance_level = self._determine_performance_level(final_performance_score)
            performance_rate = self.bonus_multipliers.get(performance_level, 1.0)
            
            # Lấy tỷ lệ % của vai trò
            role_percentage = self.profit_sharing_rates.get(role, 0.02) * 100
            
            # Áp dụng công thức tài chính cuối cùng
            total_bonus = project_revenue * (role_percentage / 100) * performance_rate
            total_amount = base_salary + total_bonus

            # --- PHẦN 3: TRẢ VỀ KẾT QUẢ MINH BẠCH ---
            result = {
                'period': period,
                'project_id': project_id,
                'employee_id': employee_id,
                'role': role,
                'base_salary': base_salary,
                'performance_metrics': performance_data, # Trả về đầy đủ để tham khảo
                'ai_calculations': {
                    'source_of_score': source_of_score, # Cho biết điểm được tính từ đâu (AI hay Luật)
                    'final_performance_score': final_performance_score,
                    'performance_level': performance_level,
                    'performance_rate': performance_rate,
                    'total_bonus': total_bonus,
                },
                'final_amount': total_amount,
                'currency': 'VND',
                'calculation_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Commission calculation completed for employee {employee_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating commission: {str(e)}")
            raise

    async def train(self, training_data: Dict[str, Any]) -> Dict[str, Any]:
        """Train the reward calculation model"""
        try:
            logger.info("Training reward calculation model")
            
            # Prepare training data
            X = []
            y = []
            
            for record in training_data.get('commissions', []):
                features = self._extract_features(record['performance_data'], record['role'])
                X.append(features.flatten())
                y.append(record['final_amount'])
            
            if len(X) < 10:
                logger.warning("Insufficient training data, using rule-based approach")
                return {
                    'success': True,
                    'message': 'Insufficient data for ML model, using rule-based calculation',
                    'model_type': 'rule_based'
                }
            
            X = np.array(X)
            y = np.array(y)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            train_score = self.model.score(X_train_scaled, y_train)
            test_score = self.model.score(X_test_scaled, y_test)
            
            self.is_trained = True
            self._save_model()
            
            logger.info(f"Model trained successfully. Train R²: {train_score:.3f}, Test R²: {test_score:.3f}")
            
            return {
                'success': True,
                'train_score': train_score,
                'test_score': test_score,
                'model_type': 'random_forest',
                'n_samples': len(X)
            }
            
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def is_ready(self) -> bool:
        """Check if the calculator is ready"""
        return True  # Always ready for rule-based calculation

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            'model_type': 'random_forest' if self.is_trained else 'rule_based',
            'is_trained': self.is_trained,
            'role_weights': self.role_weights,
            'bonus_multipliers': self.bonus_multipliers,
            'profit_sharing_rates': self.profit_sharing_rates
        } 
