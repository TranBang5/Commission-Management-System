#!/usr/bin/env python3
"""
Test script for NLPProcessor
"""

import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.nlp_processor import NLPProcessor

async def test_nlp_processor():
    """Test NLPProcessor functionality"""
    print("Testing NLPProcessor...")
    
    # Create NLP processor instance
    nlp = NLPProcessor()
    
    # Test 1: Sentiment Analysis
    print("\n1. Testing sentiment analysis...")
    
    test_texts = [
        "Employee performed exceptionally well on this project. Great teamwork and delivered on time.",
        "The calculation seems incorrect based on my performance. I worked very hard.",
        "Average performance this month. Some improvements needed.",
        "Nhân viên làm việc xuất sắc trong dự án này. Tinh thần đồng đội tốt và hoàn thành đúng hạn.",
        "Tính toán có vẻ không đúng dựa trên hiệu suất của tôi. Tôi đã làm việc rất chăm chỉ."
    ]
    
    for i, text in enumerate(test_texts, 1):
        result = await nlp.process_feedback(text, "client")
        print(f"Text {i}: {text[:50]}...")
        print(f"  Sentiment: {result['sentiment']}")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"  Satisfaction: {result['satisfaction_score']}")
        print(f"  Key points: {len(result['key_points'])}")
        print()
    
    # Test 2: Dispute Analysis
    print("\n2. Testing dispute analysis...")
    
    dispute_texts = [
        "The commission calculation is incorrect. I deserve more based on my performance.",
        "This is unfair treatment. Other employees with similar performance got higher bonuses.",
        "I disagree with the performance evaluation. The metrics don't reflect my actual contribution.",
        "Tính toán hoa hồng không đúng. Tôi xứng đáng được nhiều hơn dựa trên hiệu suất của mình.",
        "Đây là sự đối xử không công bằng. Các nhân viên khác có hiệu suất tương tự được thưởng cao hơn."
    ]
    
    for i, text in enumerate(dispute_texts, 1):
        result = await nlp.analyze_dispute(
            commission_id=f"comm_{i}",
            reason=text,
            evidence=["performance_report.pdf"],
            employee_id=f"emp_{i}"
        )
        print(f"Dispute {i}: {text[:50]}...")
        print(f"  Type: {result['dispute_type']}")
        print(f"  Recommendation: {result['recommendation']}")
        print(f"  Risk level: {result['risk_level']}")
        print(f"  Keywords: {len(result['dispute_keywords'])}")
        print()
    
    # Test 3: Explanation Generation
    print("\n3. Testing explanation generation...")
    
    commission_data = {
        'role': 'developer',
        'performance_metrics': {
            'kpi_score': 95,
            'quality_score': 88,
            'efficiency_score': 92,
            'teamwork_score': 90,
            'innovation_score': 85,
            'project_progress': 95
        },
        'ai_calculations': {
            'overall_score': 91.2,
            'performance_level': 'excellent',
            'ai_confidence': 87.5,
            'personal_bonus': 15000000,
            'quality_bonus': 2000000,
            'innovation_bonus': 1000000
        },
        'final_amount': 35000000
    }
    
    performance_data = {
        'kpi_score': 95,
        'quality_score': 88,
        'efficiency_score': 92,
        'teamwork_score': 90,
        'innovation_score': 85,
        'project_progress': 95
    }
    
    explanation = await nlp.generate_explanation(commission_data, performance_data)
    print(f"Generated explanation: {explanation}")
    print()
    
    # Test 4: Model Info
    print("\n4. Testing model info...")
    info = nlp.get_model_info()
    print(f"Model type: {info['model_type']}")
    print(f"Is trained: {info['is_trained']}")
    print(f"Supported languages: {info['supported_languages']}")
    print(f"Performance keywords: {info['performance_keywords_count']}")
    print(f"Dispute keywords: {info['dispute_keywords_count']}")
    print()
    
    # Test 5: Ready Status
    print("\n5. Testing ready status...")
    is_ready = nlp.is_ready()
    print(f"Is ready: {is_ready}")
    print()
    
    # Test 6: Training
    print("\n6. Testing training...")
    training_data = {
        'feedback_samples': [
            {'text': 'Great performance', 'sentiment': 'positive'},
            {'text': 'Poor work quality', 'sentiment': 'negative'},
            {'text': 'Average results', 'sentiment': 'neutral'}
        ]
    }
    
    train_result = await nlp.train(training_data)
    print(f"Training result: {train_result}")
    print()
    
    print("✅ All NLPProcessor tests completed successfully!")
    return True

if __name__ == "__main__":
    try:
        asyncio.run(test_nlp_processor())
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
