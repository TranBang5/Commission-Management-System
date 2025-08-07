#!/usr/bin/env python3
"""
Simple test script for RewardCalculator
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.reward_calculator import RewardCalculator

def test_basic_functionality():
    """Test basic functionality of RewardCalculator"""
    print("Testing RewardCalculator...")
    
    # Create calculator instance
    calculator = RewardCalculator()
    
    # Test data
    performance_data = {
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
    
    # Test weighted score calculation
    print("\n1. Testing weighted score calculation...")
    score = calculator._calculate_weighted_score(performance_data, 'developer')
    print(f"Developer score: {score:.2f}")
    assert 0 <= score <= 100, f"Score {score} is out of range"
    
    # Test different roles
    roles = ['developer', 'marketing_specialist', 'direct_mentor', 'indirect_mentor', 'hr_recruiter', 'business_development']
    for role in roles:
        performance_data['role'] = role
        score = calculator._calculate_weighted_score(performance_data, role)
        print(f"{role} score: {score:.2f}")
        assert 0 <= score <= 100, f"Score {score} for {role} is out of range"
    
    # Test performance level determination
    print("\n2. Testing performance level determination...")
    levels = [95, 85, 75, 65, 55]
    for score in levels:
        level = calculator._determine_performance_level(score)
        print(f"Score {score} -> Level: {level}")
    
    # Test bonus calculation
    print("\n3. Testing bonus calculation...")
    base_salary = 20000000
    project_revenue = 500000000
    
    for role in roles:
        bonuses = calculator._calculate_bonus(base_salary, 'good', project_revenue, role, performance_data)
        print(f"{role} bonuses:")
        for bonus_type, amount in bonuses.items():
            if isinstance(amount, float) and amount > 0:
                print(f"  {bonus_type}: {amount:,.0f} VND")
            else:
                print(f"  {bonus_type}: {amount}")
    
    # Test role weights coverage
    print("\n4. Testing role weights coverage...")
    for role in roles:
        assert role in calculator.role_weights, f"Role {role} not found in weights"
        weights = calculator.role_weights[role]
        total_weight = sum(weights.values())
        print(f"{role}: total weight = {total_weight:.3f}")
        assert abs(total_weight - 1.0) < 0.001, f"Total weight for {role} is not 1.0"
    
    # Test profit sharing rates coverage
    print("\n5. Testing profit sharing rates coverage...")
    for role in roles:
        assert role in calculator.profit_sharing_rates, f"Role {role} not found in profit sharing rates"
        rate = calculator.profit_sharing_rates[role]
        print(f"{role}: profit sharing rate = {rate:.3f} ({rate*100:.1f}%)")
        assert 0 <= rate <= 0.1, f"Rate {rate} for {role} is out of range"
    
    # Test feature extraction
    print("\n6. Testing feature extraction...")
    features = calculator._extract_features(performance_data, 'developer')
    print(f"Feature shape: {features.shape}")
    assert features.shape[1] == 16, f"Expected 16 features, got {features.shape[1]}"  # 8 metrics + 6 role encodings + 2 project metrics
    
    # Test AI confidence
    print("\n7. Testing AI confidence...")
    confidence = calculator._calculate_ai_confidence(performance_data)
    print(f"AI confidence: {confidence:.2f}%")
    assert 0 <= confidence <= 100, f"Confidence {confidence} is out of range"
    
    # Test model info
    print("\n8. Testing model info...")
    info = calculator.get_model_info()
    print(f"Model type: {info['model_type']}")
    print(f"Is trained: {info['is_trained']}")
    
    print("\n✅ All tests passed successfully!")
    return True

if __name__ == "__main__":
    try:
        test_basic_functionality()
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
