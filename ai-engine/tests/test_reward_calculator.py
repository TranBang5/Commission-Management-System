import pytest
import pytest_asyncio
import numpy as np
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.reward_calculator import RewardCalculator

@pytest.fixture
def calculator():
    """Fixture để tạo instance của RewardCalculator"""
    return RewardCalculator()

@pytest.fixture
def sample_performance_data():
    """Dữ liệu hiệu suất mẫu cho testing"""
    return {
        'kpi_score': 85,
        'quality_score': 90,
        'efficiency_score': 88,
        'teamwork_score': 92,
        'innovation_score': 85,
        'project_progress': 95,
        'client_satisfaction': 88,
        'deadline_adherence': 90,
        'base_salary': 20000000,  # 20 triệu VND
        'project_revenue': 500000000,  # 500 triệu VND
        'role': 'developer'
    }

class TestRewardCalculator:
    """Test class cho RewardCalculator"""
    
    def test_calculate_weighted_score(self, calculator, sample_performance_data):
        """Test tính toán điểm hiệu suất tổng hợp"""
        # Test cho developer
        score = calculator._calculate_weighted_score(sample_performance_data, 'developer')
        assert 0 <= score <= 100
        assert score > 0
        
        # Test cho marketing specialist
        sample_performance_data['role'] = 'marketing_specialist'
        score = calculator._calculate_weighted_score(sample_performance_data, 'marketing_specialist')
        assert 0 <= score <= 100
        
        # Test cho direct mentor
        sample_performance_data['role'] = 'direct_mentor'
        score = calculator._calculate_weighted_score(sample_performance_data, 'direct_mentor')
        assert 0 <= score <= 100
        
        # Test cho indirect mentor
        sample_performance_data['role'] = 'indirect_mentor'
        score = calculator._calculate_weighted_score(sample_performance_data, 'indirect_mentor')
        assert 0 <= score <= 100

    def test_determine_performance_level(self, calculator):
        """Test phân loại mức độ hiệu suất"""
        assert calculator._determine_performance_level(95) == 'excellent'
        assert calculator._determine_performance_level(85) == 'good'
        assert calculator._determine_performance_level(75) == 'average'
        assert calculator._determine_performance_level(65) == 'below_average'
        assert calculator._determine_performance_level(55) == 'poor'

    def test_calculate_bonus(self, calculator, sample_performance_data):
        """Test tính toán các khoản thưởng"""
        base_salary = 20000000
        project_revenue = 500000000
        
        # Test cho developer
        bonuses = calculator._calculate_bonus(base_salary, 'good', project_revenue, 'developer', sample_performance_data)
        assert 'personal_bonus' in bonuses  # Changed from 'performance_bonus'
        assert 'role_percentage' in bonuses
        assert 'performance_rate' in bonuses
        assert 'quality_bonus' in bonuses
        assert 'innovation_bonus' in bonuses
        assert 'total_bonus' in bonuses
        assert bonuses['total_bonus'] >= 0
        
        # Test cho marketing specialist
        bonuses = calculator._calculate_bonus(base_salary, 'excellent', project_revenue, 'marketing_specialist', sample_performance_data)
        assert bonuses['total_bonus'] >= 0
        
        # Test cho direct mentor
        bonuses = calculator._calculate_bonus(base_salary, 'good', project_revenue, 'direct_mentor', sample_performance_data)
        assert bonuses['total_bonus'] >= 0
        
        # Test cho indirect mentor
        bonuses = calculator._calculate_bonus(base_salary, 'good', project_revenue, 'indirect_mentor', sample_performance_data)
        assert bonuses['total_bonus'] >= 0

    @pytest.mark.asyncio
    async def test_calculate_commission(self, calculator, sample_performance_data):
        """Test tính toán commission hoàn chỉnh"""
        period = {'year': 2024, 'month': 8}
        project_id = 'proj_001'
        employee_id = 'emp_001'
        
        # Test cho developer
        result = await calculator.calculate(period, project_id, employee_id, sample_performance_data)
        
        assert 'period' in result
        assert 'project_id' in result
        assert 'employee_id' in result
        assert 'role' in result
        assert 'base_salary' in result
        assert 'performance_metrics' in result
        assert 'ai_calculations' in result
        assert 'final_amount' in result
        assert 'currency' in result
        assert 'calculation_timestamp' in result
        
        # Kiểm tra các thành phần AI
        ai_calc = result['ai_calculations']
        assert 'source_of_score' in ai_calc
        assert 'final_performance_score' in ai_calc
        assert 'performance_level' in ai_calc
        assert 'performance_rate' in ai_calc
        assert 'total_bonus' in ai_calc
        # Các trường cũ không còn:
        # assert 'overall_score' in ai_calc
        # assert 'performance_level' in ai_calc
        # assert 'ai_confidence' in ai_calc
        # assert 'ai_factors' in ai_calc
        
        # Test cho các vai trò khác
        roles_to_test = [
            'marketing_specialist',
            'direct_mentor',
            'indirect_mentor',
            'hr_recruiter',
            'business_development'
        ]
        
        for role in roles_to_test:
            sample_performance_data['role'] = role
            result = await calculator.calculate(period, project_id, employee_id, sample_performance_data)
            assert result['role'] == role
            assert result['final_amount'] > 0

    def test_role_weights_coverage(self, calculator):
        """Test đảm bảo tất cả vai trò đều có trọng số"""
        expected_roles = [
            'developer',
            'marketing_specialist',
            'direct_mentor',
            'indirect_mentor',
            'hr_recruiter',
            'business_development'
        ]
        
        for role in expected_roles:
            assert role in calculator.role_weights
            weights = calculator.role_weights[role]
            assert 'kpi_score' in weights
            assert 'quality_score' in weights
            assert 'efficiency_score' in weights
            assert 'teamwork_score' in weights
            assert 'innovation_score' in weights
            assert 'project_progress' in weights
            
            # Kiểm tra tổng trọng số = 1.0
            total_weight = sum(weights.values())
            assert abs(total_weight - 1.0) < 0.001

    def test_profit_sharing_rates_coverage(self, calculator):
        """Test đảm bảo tất cả vai trò đều có tỷ lệ chia lợi nhuận"""
        expected_roles = [
            'developer',
            'marketing_specialist',
            'direct_mentor',
            'indirect_mentor',
            'hr_recruiter',
            'business_development'
        ]
        
        for role in expected_roles:
            assert role in calculator.profit_sharing_rates
            rate = calculator.profit_sharing_rates[role]
            assert 0 <= rate <= 0.1  # Tỷ lệ hợp lý từ 0-10%

    def test_extract_features(self, calculator, sample_performance_data):
        """Test trích xuất đặc trưng cho ML"""
        features = calculator._extract_features(sample_performance_data, 'developer')
        assert isinstance(features, np.ndarray)
        assert features.shape[1] == 16  # 8 metrics + 6 role encodings + 2 project metrics
        
        # Test cho vai trò khác
        features = calculator._extract_features(sample_performance_data, 'marketing_specialist')
        assert features.shape[1] == 16

    def test_calculate_ai_confidence(self, calculator, sample_performance_data):
        """Test tính toán độ tin cậy AI"""
        confidence = calculator._calculate_ai_confidence(sample_performance_data)
        assert 0 <= confidence <= 100
        
        # Test với dữ liệu không đầy đủ
        incomplete_data = {'kpi_score': 85}
        confidence = calculator._calculate_ai_confidence(incomplete_data)
        assert 0 <= confidence <= 100

    def test_is_ready(self, calculator):
        """Test kiểm tra sẵn sàng của calculator"""
        assert calculator.is_ready() == True

    def test_get_model_info(self, calculator):
        """Test lấy thông tin model"""
        info = calculator.get_model_info()
        assert 'model_type' in info
        assert 'is_trained' in info
        assert 'role_weights' in info
        assert 'bonus_multipliers' in info
        assert 'profit_sharing_rates' in info

    @pytest.mark.asyncio
    async def test_edge_cases(self, calculator):
        """Test các trường hợp đặc biệt"""
        period = {'year': 2024, 'month': 8}
        project_id = 'proj_001'
        employee_id = 'emp_001'
        
        # Test với dữ liệu tối thiểu
        min_data = {
            'role': 'developer',
            'base_salary': 10000000,
            'project_revenue': 0
        }
        result = await calculator.calculate(period, project_id, employee_id, min_data)
        assert result['final_amount'] >= min_data['base_salary']
        
        # Test với dữ liệu cao
        high_data = {
            'kpi_score': 100,
            'quality_score': 100,
            'efficiency_score': 100,
            'teamwork_score': 100,
            'innovation_score': 100,
            'project_progress': 100,
            'role': 'developer',
            'base_salary': 50000000,
            'project_revenue': 1000000000
        }
        result = await calculator.calculate(period, project_id, employee_id, high_data)
        assert result['ai_calculations']['performance_level'] == 'excellent'

    def test_bonus_calculation_accuracy(self, calculator):
        """Test độ chính xác của hàm _calculate_bonus với giá trị mong đợi"""
        # Test case 1: developer, good
        base_salary = 20_000_000
        project_revenue = 500_000_000
        role = 'developer'
        performance_level = 'good'  # bonus_multipliers = 1.3, profit_sharing_rates = 0.02
        expected_bonus = project_revenue * 0.02 * 1.3
        bonuses = calculator._calculate_bonus(base_salary, performance_level, project_revenue, role)
        assert abs(bonuses['total_bonus'] - expected_bonus) < 1e-3

        # Test case 2: marketing_specialist, excellent
        role2 = 'marketing_specialist'
        performance_level2 = 'excellent'  # bonus_multipliers = 1.5, profit_sharing_rates = 0.015
        expected_bonus2 = project_revenue * 0.015 * 1.5
        bonuses2 = calculator._calculate_bonus(base_salary, performance_level2, project_revenue, role2)
        assert abs(bonuses2['total_bonus'] - expected_bonus2) < 1e-3

        # Test case 3: direct_mentor, below_average
        role3 = 'direct_mentor'
        performance_level3 = 'below_average'  # bonus_multipliers = 0.9, profit_sharing_rates = 0.025
        expected_bonus3 = project_revenue * 0.025 * 0.9
        bonuses3 = calculator._calculate_bonus(base_salary, performance_level3, project_revenue, role3)
        assert abs(bonuses3['total_bonus'] - expected_bonus3) < 1e-3

if __name__ == "__main__":
    pytest.main([__file__])
