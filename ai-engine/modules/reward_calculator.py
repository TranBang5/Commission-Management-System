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
            'developer': {
                'kpi_score': 0.25,
                'quality_score': 0.20,
                'efficiency_score': 0.20,
                'teamwork_score': 0.15,
                'innovation_score': 0.10,
                'project_progress': 0.10
            },
            'designer': {
                'kpi_score': 0.20,
                'quality_score': 0.30,
                'efficiency_score': 0.15,
                'teamwork_score': 0.15,
                'innovation_score': 0.20,
                'project_progress': 0.10
            },
            'tester': {
                'kpi_score': 0.30,
                'quality_score': 0.25,
                'efficiency_score': 0.20,
                'teamwork_score': 0.15,
                'innovation_score': 0.05,
                'project_progress': 0.05
            },
            'analyst': {
                'kpi_score': 0.25,
                'quality_score': 0.20,
                'efficiency_score': 0.20,
                'teamwork_score': 0.20,
                'innovation_score': 0.10,
                'project_progress': 0.05
            },
            'lead': {
                'kpi_score': 0.20,
                'quality_score': 0.15,
                'efficiency_score': 0.15,
                'teamwork_score': 0.25,
                'innovation_score': 0.15,
                'project_progress': 0.10
            },
            'consultant': {
                'kpi_score': 0.20,
                'quality_score': 0.20,
                'efficiency_score': 0.15,
                'teamwork_score': 0.20,
                'innovation_score': 0.15,
                'project_progress': 0.10
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
            'developer': 0.02,  # 2% of project profit
            'designer': 0.02,
            'tester': 0.015,
            'analyst': 0.015,
            'lead': 0.03,
            'consultant': 0.025
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
                        project_profit: float, role: str) -> Dict[str, float]:
        """Calculate various bonus components"""
        multiplier = self.bonus_multipliers.get(performance_level, 1.0)
        profit_sharing_rate = self.profit_sharing_rates.get(role, 0.02)
        
        # Performance bonus
        performance_bonus = base_salary * (multiplier - 1.0)
        
        # Project profit sharing
        profit_bonus = project_profit * profit_sharing_rate
        
        # Quality bonus (if quality score is high)
        quality_score = performance_data.get('quality_score', 0)
        quality_bonus = base_salary * 0.1 if quality_score >= 90 else 0
        
        # Innovation bonus (if innovation score is high)
        innovation_score = performance_data.get('innovation_score', 0)
        innovation_bonus = base_salary * 0.05 if innovation_score >= 85 else 0
        
        return {
            'performance_bonus': performance_bonus,
            'project_bonus': profit_bonus,
            'quality_bonus': quality_bonus,
            'innovation_bonus': innovation_bonus,
            'total_bonus': performance_bonus + profit_bonus + quality_bonus + innovation_bonus
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

    async def calculate(self, period: Dict[str, int], project_id: str, 
                       employee_id: str, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate commission using AI and rule-based approach"""
        try:
            logger.info(f"Calculating commission for employee {employee_id}")
            
            role = performance_data.get('role', 'developer')
            base_salary = performance_data.get('base_salary', 0)
            project_profit = performance_data.get('project_profit', 0)
            
            # Calculate weighted performance score
            weighted_score = self._calculate_weighted_score(performance_data, role)
            
            # Determine performance level
            performance_level = self._determine_performance_level(weighted_score)
            
            # Calculate bonuses
            bonuses = self._calculate_bonus(base_salary, performance_level, project_profit, role)
            
            # Calculate AI confidence
            ai_confidence = self._calculate_ai_confidence(performance_data)
            
            # Prepare AI factors for transparency
            ai_factors = [
                {
                    'factor': 'weighted_performance_score',
                    'weight': 0.4,
                    'score': weighted_score,
                    'impact': weighted_score * 0.4
                },
                {
                    'factor': 'performance_level',
                    'weight': 0.3,
                    'score': 100 if performance_level == 'excellent' else 80 if performance_level == 'good' else 60,
                    'impact': bonuses['performance_bonus']
                },
                {
                    'factor': 'project_profit_sharing',
                    'weight': 0.2,
                    'score': min(100, (project_profit / base_salary) * 100) if base_salary > 0 else 0,
                    'impact': bonuses['project_bonus']
                },
                {
                    'factor': 'quality_innovation_bonus',
                    'weight': 0.1,
                    'score': 100 if bonuses['quality_bonus'] > 0 or bonuses['innovation_bonus'] > 0 else 0,
                    'impact': bonuses['quality_bonus'] + bonuses['innovation_bonus']
                }
            ]
            
            # Calculate total amount
            total_amount = base_salary + bonuses['total_bonus']
            
            result = {
                'period': period,
                'project_id': project_id,
                'employee_id': employee_id,
                'role': role,
                'base_salary': base_salary,
                'performance_metrics': {
                    'kpi_score': performance_data.get('kpi_score', 0),
                    'quality_score': performance_data.get('quality_score', 0),
                    'efficiency_score': performance_data.get('efficiency_score', 0),
                    'teamwork_score': performance_data.get('teamwork_score', 0),
                    'innovation_score': performance_data.get('innovation_score', 0),
                    'project_progress': performance_data.get('project_progress', 0),
                    'client_satisfaction': performance_data.get('client_satisfaction', 0),
                    'deadline_adherence': performance_data.get('deadline_adherence', 0)
                },
                'ai_calculations': {
                    'overall_score': weighted_score,
                    'performance_level': performance_level,
                    'performance_bonus': bonuses['performance_bonus'],
                    'project_bonus': bonuses['project_bonus'],
                    'quality_bonus': bonuses['quality_bonus'],
                    'innovation_bonus': bonuses['innovation_bonus'],
                    'total_bonus': bonuses['total_bonus'],
                    'ai_confidence': ai_confidence,
                    'ai_factors': ai_factors
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