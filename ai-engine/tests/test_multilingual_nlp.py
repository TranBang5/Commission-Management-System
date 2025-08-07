#!/usr/bin/env python3
"""
Test script for Multilingual NLPProcessor
"""

import sys
import os
import asyncio

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.nlp_processor import NLPProcessor

async def test_multilingual_nlp():
    """Test NLPProcessor multilingual functionality"""
    print("Testing Multilingual NLPProcessor...")
    
    # Create NLP processor instance
    nlp = NLPProcessor()
    
    # Test 1: Language Detection
    print("\n1. Testing language detection...")
    
    test_texts = [
        "Employee performed exceptionally well on this project. Great teamwork and delivered on time.",
        "Nhân viên làm việc xuất sắc trong dự án này. Tinh thần đồng đội tốt và hoàn thành đúng hạn.",
        "The calculation seems incorrect based on my performance. I worked very hard.",
        "Tính toán có vẻ không đúng dựa trên hiệu suất của tôi. Tôi đã làm việc rất chăm chỉ.",
        "Average performance this month. Some improvements needed.",
        "Hiệu suất trung bình trong tháng này. Cần một số cải thiện."
    ]
    
    for i, text in enumerate(test_texts, 1):
        detected_lang = nlp._detect_language(text)
        print(f"Text {i}: {text[:50]}...")
        print(f"  Detected language: {detected_lang}")
        print()
    
    # Test 2: Multilingual Sentiment Analysis
    print("\n2. Testing multilingual sentiment analysis...")
    
    multilingual_texts = [
        {
            "text": "Employee performed exceptionally well on this project. Great teamwork and delivered on time.",
            "expected_lang": "en",
            "description": "English positive feedback"
        },
        {
            "text": "Nhân viên làm việc xuất sắc trong dự án này. Tinh thần đồng đội tốt và hoàn thành đúng hạn.",
            "expected_lang": "vi",
            "description": "Vietnamese positive feedback"
        },
        {
            "text": "The calculation seems incorrect based on my performance. I worked very hard.",
            "expected_lang": "en",
            "description": "English negative feedback"
        },
        {
            "text": "Tính toán có vẻ không đúng dựa trên hiệu suất của tôi. Tôi đã làm việc rất chăm chỉ.",
            "expected_lang": "vi",
            "description": "Vietnamese negative feedback"
        },
        {
            "text": "Average performance this month. Some improvements needed.",
            "expected_lang": "en",
            "description": "English neutral feedback"
        },
        {
            "text": "Hiệu suất trung bình trong tháng này. Cần một số cải thiện.",
            "expected_lang": "vi",
            "description": "Vietnamese neutral feedback"
        }
    ]
    
    for i, test_case in enumerate(multilingual_texts, 1):
        result = await nlp.process_feedback(test_case["text"], "client")
        print(f"Test {i}: {test_case['description']}")
        print(f"  Text: {test_case['text'][:50]}...")
        print(f"  Detected language: {result['language']}")
        print(f"  Expected language: {test_case['expected_lang']}")
        print(f"  Sentiment: {result['sentiment']}")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"  Satisfaction: {result['satisfaction_score']}")
        print(f"  Key points: {len(result['key_points'])}")
        print()
    
    # Test 3: Multilingual Dispute Analysis
    print("\n3. Testing multilingual dispute analysis...")
    
    dispute_texts = [
        {
            "text": "The commission calculation is incorrect. I deserve more based on my performance.",
            "expected_lang": "en",
            "description": "English calculation error dispute"
        },
        {
            "text": "Tính toán hoa hồng không đúng. Tôi xứng đáng được nhiều hơn dựa trên hiệu suất của mình.",
            "expected_lang": "vi",
            "description": "Vietnamese calculation error dispute"
        },
        {
            "text": "This is unfair treatment. Other employees with similar performance got higher bonuses.",
            "expected_lang": "en",
            "description": "English unfair treatment dispute"
        },
        {
            "text": "Đây là sự đối xử không công bằng. Các nhân viên khác có hiệu suất tương tự được thưởng cao hơn.",
            "expected_lang": "vi",
            "description": "Vietnamese unfair treatment dispute"
        }
    ]
    
    for i, test_case in enumerate(dispute_texts, 1):
        result = await nlp.analyze_dispute(
            commission_id=f"comm_{i}",
            reason=test_case["text"],
            evidence=["performance_report.pdf"],
            employee_id=f"emp_{i}"
        )
        print(f"Dispute {i}: {test_case['description']}")
        print(f"  Text: {test_case['text'][:50]}...")
        print(f"  Detected language: {result['language']}")
        print(f"  Expected language: {test_case['expected_lang']}")
        print(f"  Type: {result['dispute_type']}")
        print(f"  Recommendation: {result['recommendation']}")
        print(f"  Risk level: {result['risk_level']}")
        print(f"  Keywords: {len(result['dispute_keywords'])}")
        print()
    
    # Test 4: Vietnamese Keywords
    print("\n4. Testing Vietnamese keyword extraction...")
    
    vietnamese_texts = [
        "Nhân viên này làm việc rất xuất sắc và chuyên nghiệp. Hiệu suất cao và đáng khen.",
        "Công việc kém chất lượng và không đạt yêu cầu. Cần cải thiện ngay.",
        "Hiệu suất trung bình, cần nỗ lực thêm để đạt kết quả tốt hơn."
    ]
    
    for i, text in enumerate(vietnamese_texts, 1):
        keywords = nlp._extract_keywords(text, 'performance')
        positive_keywords = [k for k in keywords if k[0] == 'positive']
        negative_keywords = [k for k in keywords if k[0] == 'negative']
        neutral_keywords = [k for k in keywords if k[0] == 'neutral']
        
        print(f"Vietnamese text {i}: {text}")
        print(f"  Positive keywords: {[k[1] for k in positive_keywords]}")
        print(f"  Negative keywords: {[k[1] for k in negative_keywords]}")
        print(f"  Neutral keywords: {[k[1] for k in neutral_keywords]}")
        print()
    
    # Test 5: Model Info
    print("\n5. Testing model info...")
    info = nlp.get_model_info()
    print(f"Model type: {info['model_type']}")
    print(f"Is trained: {info['is_trained']}")
    print(f"Supported languages: {info['supported_languages']}")
    print(f"Performance keywords: {info['performance_keywords_count']}")
    print(f"Dispute keywords: {info['dispute_keywords_count']}")
    print(f"spaCy models: {info['spacy_models']}")
    print()
    
    # Test 6: Language Detection Accuracy
    print("\n6. Testing language detection accuracy...")
    
    detection_tests = [
        ("This is English text", "en"),
        ("Đây là văn bản tiếng Việt", "vi"),
        ("Mixed text with some Vietnamese characters: à á ạ ả ã", "vi"),
        ("Pure English without any diacritics", "en"),
        ("Vietnamese with numbers: 123 và 456", "vi"),
        ("English with numbers: 123 and 456", "en")
    ]
    
    correct_detections = 0
    total_tests = len(detection_tests)
    
    for text, expected in detection_tests:
        detected = nlp._detect_language(text)
        is_correct = detected == expected
        if is_correct:
            correct_detections += 1
        
        print(f"Text: {text}")
        print(f"  Expected: {expected}, Detected: {detected}, Correct: {is_correct}")
    
    accuracy = correct_detections / total_tests * 100
    print(f"\nLanguage detection accuracy: {accuracy:.1f}% ({correct_detections}/{total_tests})")
    print()
    
    print("✅ All Multilingual NLPProcessor tests completed successfully!")
    return True

if __name__ == "__main__":
    try:
        asyncio.run(test_multilingual_nlp())
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
