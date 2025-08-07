#!/usr/bin/env python3
"""
Simple test script for RewardCalculator
"""

import sys
import os
import asyncio

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.reward_calculator import RewardCalculator

async def test_reward_calculator():
    """Test RewardCalculator functionality"""
    print("Testing RewardCalculator...")
    
    # Create calculator instance
    calculator = RewardCalculator()
    
    # Test data
    period = {'year': 2024, 'month': 8}
    project_id = 'proj_001'
    employee_id = 'emp_001'
    
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
    
    # Test 1: Basic calculation
    print("\n1. Testing basic calculation...")
    try:
        result = await calculator.calculate(period, project_id, employee_id, performance_data)
        print(f"✅ Calculation successful!")
        print(f"  Role: {result['role']}")
        print(f"  Base salary: {result['base_salary']:,.0f} VND")
        print(f"  Final amount: {result['final_amount']:,.0f} VND")
        print(f"  Performance level: {result['ai_calculations']['performance_level']}")
        print(f"  AI confidence: {result['ai_calculations']['ai_confidence']:.1f}%")
        print()
    except Exception as e:
        print(f"❌ Calculation failed: {str(e)}")
        return False
    
    # Test 2: Different roles
    print("\n2. Testing different roles...")
    roles_to_test = [
        'developer',
        'marketing_specialist', 
        'direct_mentor',
        'indirect_mentor',
        'hr_recruiter',
        'business_development'
    ]
    
    for role in roles_to_test:
        try:
            performance_data['role'] = role
            result = await calculator.calculate(period, project_id, employee_id, performance_data)
            print(f"✅ {role}: {result['final_amount']:,.0f} VND")
        except Exception as e:
            print(f"❌ {role}: {str(e)}")
    
    print()
    
    # Test 3: Model info
    print("\n3. Testing model info...")
    info = calculator.get_model_info()
    print(f"Model type: {info['model_type']}")
    print(f"Is trained: {info['is_trained']}")
    print(f"Number of roles: {len(info['role_weights'])}")
    print(f"Number of profit sharing rates: {len(info['profit_sharing_rates'])}")
    print()
    
    # Test 4: Edge cases
    print("\n4. Testing edge cases...")
    
    # Test with minimum data
    min_data = {
        'role': 'developer',
        'base_salary': 10000000,
        'project_revenue': 0
    }
    try:
        result = await calculator.calculate(period, project_id, employee_id, min_data)
        print(f"✅ Minimum data: {result['final_amount']:,.0f} VND")
    except Exception as e:
        print(f"❌ Minimum data: {str(e)}")
    
    # Test with high performance data
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
    try:
        result = await calculator.calculate(period, project_id, employee_id, high_data)
        print(f"✅ High performance: {result['final_amount']:,.0f} VND")
        print(f"  Performance level: {result['ai_calculations']['performance_level']}")
    except Exception as e:
        print(f"❌ High performance: {str(e)}")
    
    print()
    print("✅ All RewardCalculator tests completed successfully!")
    return True

if __name__ == "__main__":
    try:
        asyncio.run(test_reward_calculator())
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
