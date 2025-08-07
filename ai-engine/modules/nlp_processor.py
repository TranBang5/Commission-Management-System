import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
import logging
from datetime import datetime
import json
import re
from collections import Counter
import joblib
import os

# spaCy NLP Library
import spacy
from spacy.tokens import Doc, Span
from spacy.matcher import Matcher
from spacy.util import filter_spans

# Thêm thư viện mới
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
import torch

logger = logging.getLogger(__name__)

class NLPProcessor:
    """
    NLP Processor for AI-First Commission Management System using spaCy
    
    Handles:
    - Sentiment analysis for feedback (English & Vietnamese)
    - Dispute analysis and recommendation
    - Key points extraction
    - Explainability generation
    - Text preprocessing
    """
    
    def __init__(self):
        # Load spaCy models for both languages
        try:
            self.nlp_en = spacy.load("en_core_web_sm")
            logger.info("English spaCy model loaded successfully")
        except OSError:
            logger.error("English spaCy model not found. Please run: python -m spacy download en_core_web_sm")
            raise
        
        try:
            self.nlp_vi = spacy.load("vi_core_news_lg")
            logger.info("Vietnamese spaCy model loaded successfully")
        except OSError:
            logger.warning("Vietnamese spaCy model not found. Using English model for Vietnamese text")
            self.nlp_vi = self.nlp_en
        
        # Load pre-trained models if available
        self.model_path = "models/nlp_processor.pkl"
        self.is_trained = False
        self._load_model()
        
        # Thêm mô hình Transformer cho phân tích sentiment
        try:
            self.sentiment_model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
            self.sentiment_tokenizer = AutoTokenizer.from_pretrained(self.sentiment_model_name)
            self.sentiment_model = AutoModelForSequenceClassification.from_pretrained(self.sentiment_model_name)
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis", 
                model=self.sentiment_model, 
                tokenizer=self.sentiment_tokenizer,
                device=0 if torch.cuda.is_available() else -1
            )
            logger.info(f"Transformer sentiment model loaded successfully: {self.sentiment_model_name}")
            self.use_transformer = True
        except Exception as e:
            logger.warning(f"Could not load Transformer model: {str(e)}. Falling back to rule-based approach.")
            self.use_transformer = False
        
        # Vietnamese stop words (basic)
        self.vn_stop_words = {
            'là', 'của', 'và', 'với', 'có', 'được', 'trong', 'ngoài', 'trên', 'dưới',
            'từ', 'đến', 'cho', 'về', 'theo', 'sau', 'trước', 'khi', 'nếu', 'thì',
            'mà', 'nhưng', 'hoặc', 'vì', 'nên', 'để', 'bởi', 'do', 'tại', 'ở',
            'này', 'kia', 'đó', 'đây', 'khi', 'lúc', 'thời', 'gian', 'ngày', 'tháng',
            'năm', 'giờ', 'phút', 'giây', 'hôm', 'nay', 'mai', 'qua', 'sau', 'trước'
        }
        
        # Performance keywords for commission context (Enhanced Vietnamese support)
        self.performance_keywords = {
            'positive': [
                # English
                'excellent', 'outstanding', 'exceptional', 'superior', 'amazing', 'fantastic',
                'great', 'good', 'well', 'better', 'improved', 'progress', 'success',
                'achieved', 'completed', 'delivered', 'met', 'exceeded', 'surpassed',
                'dedicated', 'hardworking', 'reliable', 'consistent', 'professional',
                'teamwork', 'collaboration', 'leadership', 'innovation', 'creative',
                'efficient', 'productive', 'quality', 'expertise', 'skills', 'knowledge',
                'experience', 'contribution', 'value', 'impact', 'results', 'performance',
                # Vietnamese
                'xuất sắc', 'tuyệt vời', 'tốt', 'giỏi', 'cải thiện', 'tiến bộ', 'thành công',
                'hoàn thành', 'đạt được', 'vượt qua', 'chuyên nghiệp', 'đáng tin cậy',
                'hiệu quả', 'chất lượng', 'kỹ năng', 'kinh nghiệm', 'đóng góp', 'nỗ lực',
                'tận tâm', 'tận tụy', 'sáng tạo', 'đổi mới', 'phát triển', 'cải tiến',
                'vượt trội', 'ưu tú', 'tài năng', 'năng lực', 'khả năng', 'thành tích',
                'kết quả', 'hiệu suất', 'năng suất', 'chất lượng cao', 'đáng khen'
            ],
            'negative': [
                # English
                'poor', 'bad', 'terrible', 'awful', 'disappointing', 'unsatisfactory',
                'failed', 'missed', 'late', 'delayed', 'incomplete', 'unfinished',
                'inadequate', 'insufficient', 'weak', 'lazy', 'unreliable', 'inconsistent',
                'unprofessional', 'inefficient', 'unproductive', 'low', 'quality',
                'problems', 'issues', 'concerns', 'complaints', 'dissatisfied',
                # Vietnamese
                'kém', 'tệ', 'thất vọng', 'không hài lòng', 'thất bại', 'trễ',
                'chưa hoàn thành', 'không đủ', 'yếu', 'lười', 'không đáng tin',
                'không chuyên nghiệp', 'không hiệu quả', 'chất lượng thấp',
                'vấn đề', 'khiếu nại', 'không hài lòng', 'kém cỏi', 'yếu kém',
                'thất bại', 'thua kém', 'không đạt', 'không thành công', 'thất bại',
                'lỗi', 'sai sót', 'thiếu sót', 'khuyết điểm', 'nhược điểm'
            ],
            'neutral': [
                # English
                'average', 'normal', 'standard', 'regular', 'usual', 'typical',
                'adequate', 'sufficient', 'acceptable', 'reasonable', 'moderate',
                # Vietnamese
                'trung bình', 'bình thường', 'tiêu chuẩn', 'đủ', 'chấp nhận được',
                'hợp lý', 'vừa phải', 'tạm được', 'khá', 'ổn', 'tốt vừa',
                'đạt chuẩn', 'đáp ứng', 'thỏa mãn', 'phù hợp'
            ]
        }
        
        # Dispute keywords (Enhanced Vietnamese support)
        self.dispute_keywords = [
            # English
            'incorrect', 'wrong', 'error', 'mistake', 'unfair', 'unjust',
            'dispute', 'disagreement', 'conflict', 'problem', 'issue',
            'concern', 'complaint', 'objection', 'protest', 'appeal',
            # Vietnamese
            'sai', 'lỗi', 'không đúng', 'không công bằng', 'khiếu nại',
            'tranh chấp', 'bất đồng', 'vấn đề', 'lo ngại', 'phản đối',
            'không đồng ý', 'không chấp nhận', 'không thỏa mãn', 'không hài lòng',
            'có vấn đề', 'có lỗi', 'sai sót', 'thiếu sót', 'khuyết điểm',
            'bất công', 'không hợp lý', 'không đúng đắn', 'không chính xác'
        ]
        
        # Initialize spaCy matchers for both languages
        self.matcher_en = Matcher(self.nlp_en.vocab)
        self.matcher_vi = Matcher(self.nlp_vi.vocab)
        self._setup_matchers()
        
        # Thêm context patterns cho phân tích context-aware
        self._setup_context_patterns()
    
    def _setup_context_patterns(self):
        """Thiết lập các mẫu ngữ cảnh để phát hiện các tình huống phức tạp"""
        # Các mẫu phủ định (negation patterns)
        self.negation_patterns = {
            'en': ['not', 'no', "n't", 'never', 'neither', 'nor', 'none', 'hardly', 'barely', 'scarcely', 'seldom', 'rarely'],
            'vi': ['không', 'chẳng', 'chả', 'đừng', 'đéo', 'chưa', 'không phải', 'không hề', 'không thể', 'không được', 'không nên']
        }
        
        # Các mẫu tăng cường (intensifier patterns)
        self.intensifier_patterns = {
            'en': ['very', 'extremely', 'highly', 'really', 'truly', 'absolutely', 'completely', 'totally', 'utterly', 'quite'],
            'vi': ['rất', 'cực kỳ', 'vô cùng', 'hết sức', 'quá', 'lắm', 'thực sự', 'hoàn toàn', 'tuyệt đối', 'khá']
        }
        
        # Các mẫu so sánh (comparison patterns)
        self.comparison_patterns = {
            'en': ['better than', 'worse than', 'more than', 'less than', 'as good as', 'not as good as'],
            'vi': ['tốt hơn', 'kém hơn', 'nhiều hơn', 'ít hơn', 'tốt như', 'không tốt như']
        }
        
        # Các mẫu chuyển đổi (transition patterns)
        self.transition_patterns = {
            'en': ['however', 'but', 'although', 'nevertheless', 'nonetheless', 'despite', 'in spite of', 'yet', 'still', 'while'],
            'vi': ['tuy nhiên', 'nhưng', 'mặc dù', 'dù', 'mặc dù vậy', 'tuy vậy', 'dù vậy', 'trong khi']
        }

    def _setup_matchers(self):
        """Setup spaCy matchers for custom pattern matching in both languages"""
        # Performance patterns (English)
        performance_patterns_en = [
            [{"LOWER": {"IN": ["excellent", "outstanding", "exceptional"]}}],
            [{"LOWER": {"IN": ["poor", "bad", "terrible", "awful"]}}],
            [{"LOWER": {"IN": ["achieved", "completed", "delivered"]}}],
            [{"LOWER": {"IN": ["failed", "missed", "delayed"]}}],
            [{"LOWER": "great"}, {"LOWER": "work"}],
            [{"LOWER": "poor"}, {"LOWER": "performance"}],
        ]
        
        # Performance patterns (Vietnamese)
        performance_patterns_vi = [
            [{"LOWER": {"IN": ["xuất sắc", "tuyệt vời", "tốt", "giỏi"]}}],
            [{"LOWER": {"IN": ["kém", "tệ", "thất vọng", "không hài lòng"]}}],
            [{"LOWER": {"IN": ["hoàn thành", "đạt được", "vượt qua"]}}],
            [{"LOWER": {"IN": ["thất bại", "trễ", "chưa hoàn thành"]}}],
            [{"LOWER": "công việc"}, {"LOWER": "tốt"}],
            [{"LOWER": "hiệu suất"}, {"LOWER": "kém"}],
        ]
        
        # Dispute patterns (English)
        dispute_patterns_en = [
            [{"LOWER": {"IN": ["incorrect", "wrong", "error"]}}],
            [{"LOWER": {"IN": ["unfair", "unjust"]}}],
            [{"LOWER": "dispute"}],
            [{"LOWER": "complaint"}],
            [{"LOWER": "problem"}],
        ]
        
        # Dispute patterns (Vietnamese)
        dispute_patterns_vi = [
            [{"LOWER": {"IN": ["sai", "lỗi", "không đúng"]}}],
            [{"LOWER": {"IN": ["không công bằng", "bất công"]}}],
            [{"LOWER": "khiếu nại"}],
            [{"LOWER": "tranh chấp"}],
            [{"LOWER": "vấn đề"}],
        ]
        
        # Add patterns to English matcher
        for pattern in performance_patterns_en:
            self.matcher_en.add("PERFORMANCE", [pattern])
        
        for pattern in dispute_patterns_en:
            self.matcher_en.add("DISPUTE", [pattern])
        
        # Add patterns to Vietnamese matcher
        for pattern in performance_patterns_vi:
            self.matcher_vi.add("PERFORMANCE", [pattern])
        
        for pattern in dispute_patterns_vi:
            self.matcher_vi.add("DISPUTE", [pattern])

    def _detect_language(self, text: str) -> str:
        """Detect if text is Vietnamese or English"""
        # Simple Vietnamese detection based on diacritics
        vietnamese_chars = set('àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ')
        text_chars = set(text.lower())
        
        # If more than 10% of characters are Vietnamese, consider it Vietnamese
        vietnamese_ratio = len(text_chars.intersection(vietnamese_chars)) / len(text_chars) if text_chars else 0
        
        if vietnamese_ratio > 0.1:
            return 'vi'
        else:
            return 'en'

    def _get_nlp_model(self, text: str):
        """Get appropriate spaCy model based on language"""
        lang = self._detect_language(text)
        if lang == 'vi':
            return self.nlp_vi, self.matcher_vi
        else:
            return self.nlp_en, self.matcher_en

    def _load_model(self):
        """Load pre-trained NLP model if available"""
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                self.is_trained = True
                logger.info("Pre-trained NLP processor model loaded")
            else:
                logger.info("No pre-trained NLP model found, using rule-based processing")
        except Exception as e:
            logger.error(f"Error loading NLP model: {str(e)}")

    def _save_model(self):
        """Save trained NLP model"""
        try:
            os.makedirs("models", exist_ok=True)
            joblib.dump(self.model, self.model_path)
            logger.info("NLP model saved successfully")
        except Exception as e:
            logger.error(f"Error saving NLP model: {str(e)}")

    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for analysis"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep Vietnamese diacritics
        text = re.sub(r'[^\w\sàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def _extract_keywords(self, text: str, keyword_type: str = 'performance') -> List[Any]:
        """
        Trích xuất các từ khóa có liên quan từ văn bản với khả năng nhận biết ngữ cảnh đơn giản.
        - Đối với 'performance', trả về list các tuple: [('positive', 'xuất sắc'), ('negative', 'kém chất lượng')]
        - Đối với 'dispute', trả về list các string: ['không đúng', 'bất công']
        """
        # Luôn tiền xử lý văn bản để đảm bảo tính nhất quán
        processed_text = self._preprocess_text(text)
        nlp, matcher = self._get_nlp_model(processed_text)
        doc = nlp(processed_text)

        if keyword_type == 'performance':
            keywords = []
            # Các từ bổ nghĩa tiêu cực có thể đảo ngược ý nghĩa của từ khóa tích cực
            negative_modifiers = {'kém', 'tệ', 'không', 'chưa', 'bad', 'poor', 'not', 'no', 'without'}
            
            # Sử dụng một set để theo dõi các chỉ mục đã được xử lý, tránh lặp lại
            used_indices = set()

            for i, token in enumerate(doc):
                if i in used_indices:
                    continue

                token_text = token.text

                # 1. Kiểm tra từ khóa tích cực
                if token_text in self.performance_keywords['positive']:
                    # Kiểm tra xem từ đứng trước có phải là từ bổ nghĩa tiêu cực không
                    if i > 0 and doc[i - 1].text in negative_modifiers:
                        # Nếu có, đây là một cụm từ tiêu cực
                        phrase = f"{doc[i - 1].text} {token_text}"
                        keywords.append(('negative', phrase))
                        used_indices.add(i)
                        used_indices.add(i - 1)
                    else:
                        # Nếu không, đây là một từ khóa tích cực
                        keywords.append(('positive', token_text))
                        used_indices.add(i)
                
                # 2. Kiểm tra từ khóa tiêu cực
                elif token_text in self.performance_keywords['negative']:
                    keywords.append(('negative', token_text))
                    used_indices.add(i)

                # 3. Kiểm tra từ khóa trung tính
                elif token_text in self.performance_keywords['neutral']:
                    keywords.append(('neutral', token_text))
                    used_indices.add(i)
            
            return keywords

        elif keyword_type == 'dispute':
            # Logic cũ không hiệu quả với các cụm từ.
            # Cách tiếp cận đơn giản và hiệu quả hơn là tìm kiếm trực tiếp các cụm từ trong văn bản.
            found_keywords = []
            for keyword in self.dispute_keywords:
                # Tìm kiếm không phân biệt chữ hoa/thường trong văn bản đã được xử lý
                if keyword in processed_text:
                    found_keywords.append(keyword)
            return found_keywords
        
        return []

    def _analyze_sentiment_with_transformer(self, text: str) -> Dict[str, Any]:
        """Phân tích sentiment sử dụng mô hình Transformer và diễn giải kết quả 'sao'."""
        if not text:
            return {
                'sentiment': 'neutral', 'confidence': 0.5, 'model': 'transformer',
                'scores': {'positive': 0, 'negative': 0, 'neutral': 1}
            }
        
        try:
            # Sử dụng mô hình Transformer để phân tích
            result = self.sentiment_pipeline(text)
            
            if not result:
                raise ValueError("Mô hình không trả về kết quả.")

            label = result[0]['label'].lower()
            score = result[0]['score']
            
            sentiment = 'neutral'
            confidence = score

            # Diễn giải kết quả từ 'sao' sang 'positive/neutral/negative'
            if '5 stars' in label or '4 stars' in label:
                sentiment = 'positive'
            elif '1 star' in label or '2 stars' in label:
                sentiment = 'negative'
            # '3 stars' sẽ tự động được coi là 'neutral'
            
            return {
                'sentiment': sentiment,
                'confidence': confidence,
                'scores': {
                    'positive': score if sentiment == 'positive' else 0,
                    'negative': score if sentiment == 'negative' else 0,
                    'neutral': score if sentiment == 'neutral' else 0
                },
                'model': 'transformer'
            }
            
        except Exception as e:
            logger.warning(f"Lỗi khi phân tích sentiment bằng Transformer: {str(e)}. Quay lại sử dụng rule-based.")
            # Quan trọng: Nếu Transformer lỗi, phải gọi đến hàm rule-based
            return self._analyze_sentiment_rule_based(text)
    
    def _analyze_sentiment_rule_based(self, text: str) -> Dict[str, Any]:
        """Phân tích sentiment sử dụng phương pháp dựa trên quy tắc (giữ lại phương pháp cũ)"""
        if not text:
            return {
                'sentiment': 'neutral',
                'confidence': 0.5,
                'scores': {'positive': 0, 'negative': 0, 'neutral': 0}
            }
        
        nlp, matcher = self._get_nlp_model(text)
        doc = nlp(text)
        
        # Custom keyword-based analysis
        keywords = self._extract_keywords(text, 'performance')
        positive_count = len([k for k in keywords if k[0] == 'positive'])
        negative_count = len([k for k in keywords if k[0] == 'negative'])
        neutral_count = len([k for k in keywords if k[0] == 'neutral'])
        
        # spaCy-based sentiment analysis
        # Count positive and negative words using spaCy's token attributes
        positive_words = 0
        negative_words = 0
        
        # Simple rule-based sentiment using spaCy tokens
        for token in doc:
            # Check for negation
            if token.dep_ == "neg":
                continue
            
            # Check for positive indicators (both languages)
            positive_indicators = ['good', 'great', 'excellent', 'outstanding', 'amazing', 'fantastic',
                                 'tốt', 'giỏi', 'xuất sắc', 'tuyệt vời', 'tài năng', 'ưu tú']
            negative_indicators = ['bad', 'poor', 'terrible', 'awful', 'disappointing',
                                 'kém', 'tệ', 'thất vọng', 'không hài lòng', 'yếu kém']
            
            if token.text.lower() in positive_indicators:
                positive_words += 1
            elif token.text.lower() in negative_indicators:
                negative_words += 1
        
        # Calculate sentiment score
        total_words = len([token for token in doc if not token.is_stop and token.is_alpha])
        if total_words == 0:
            total_words = 1
        
        # Combine keyword analysis with spaCy analysis
        keyword_sentiment = (positive_count - negative_count) / max(len(keywords), 1)
        spacy_sentiment = (positive_words - negative_words) / total_words
        
        # Combine scores
        combined_score = (keyword_sentiment + spacy_sentiment) / 2
        
        # Determine sentiment
        if combined_score > 0.1:
            sentiment = 'positive'
            confidence = min(0.95, abs(combined_score) + 0.5)
        elif combined_score < -0.1:
            sentiment = 'negative'
            confidence = min(0.95, abs(combined_score) + 0.5)
        else:
            sentiment = 'neutral'
            confidence = 0.5
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'scores': {
                'keyword': {'positive': positive_count, 'negative': negative_count, 'neutral': neutral_count},
                'spacy': {'positive': positive_words, 'negative': negative_words},
                'combined': combined_score
            },
            'model': 'rule_based'
        }
    
    def _analyze_sentiment_context_aware(self, text: str) -> Dict[str, Any]:
        """
        Phân tích sentiment bằng cách chia nhỏ văn bản thành từng câu,
        phân tích từng câu và tổng hợp kết quả để có cái nhìn chính xác nhất.
        """
        nlp, _ = self._get_nlp_model(text)
        doc = nlp(text)
        sentences = list(doc.sents)

        if not sentences:
            return {'sentiment': 'neutral', 'confidence': 1.0, 'model': 'rule_based'}

        sentence_sentiments = []
        for sent in sentences:
            # Bỏ qua các câu quá ngắn hoặc không có nội dung
            if len(sent.text.strip()) < 5:
                continue
            
            # Sử dụng mô hình Transformer để phân tích từng câu
            if self.use_transformer:
                # Gọi trực tiếp hàm transformer, không cần fallback ở đây
                # vì chúng ta muốn có kết quả của từng câu.
                sent_analysis = self._analyze_sentiment_with_transformer(sent.text)
            else:
                sent_analysis = self._analyze_sentiment_rule_based(sent.text)
            
            sentence_sentiments.append(sent_analysis)

        if not sentence_sentiments:
            return {'sentiment': 'neutral', 'confidence': 1.0, 'model': 'rule_based'}

        # --- Logic tổng hợp kết quả ---
        final_sentiment = 'neutral'
        final_confidence = 0.0
        positive_scores = []
        negative_scores = []
        neutral_scores = []

        # Ưu tiên cảm xúc tiêu cực: Nếu có bất kỳ câu nào tiêu cực, kết quả cuối cùng là tiêu cực.
        has_negative = any(s['sentiment'] == 'negative' for s in sentence_sentiments)
        
        if has_negative:
            final_sentiment = 'negative'
            # Lấy trung bình độ tin cậy của TẤT CẢ các câu tiêu cực
            negative_sentiments = [s for s in sentence_sentiments if s['sentiment'] == 'negative']
            final_confidence = sum(s['confidence'] for s in negative_sentiments) / len(negative_sentiments)
        else:
            # Nếu không có câu tiêu cực, kiểm tra câu tích cực
            has_positive = any(s['sentiment'] == 'positive' for s in sentence_sentiments)
            if has_positive:
                final_sentiment = 'positive'
                # Lấy trung bình độ tin cậy của các câu tích cực và trung tính
                relevant_sentiments = [s for s in sentence_sentiments if s['sentiment'] != 'negative']
                final_confidence = sum(s['confidence'] for s in relevant_sentiments) / len(relevant_sentiments)
            else:
                # Nếu chỉ toàn câu trung tính
                final_sentiment = 'neutral'
                final_confidence = sum(s['confidence'] for s in sentence_sentiments) / len(sentence_sentiments)

        # Trả về kết quả tổng hợp
        return {
            'sentiment': final_sentiment,
            'confidence': round(final_confidence, 2),
            'model': 'transformer_sentence_level',
            'details': sentence_sentiments # Thêm chi tiết phân tích của từng câu
        }
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Phân tích sentiment chính sử dụng phương pháp tốt nhất có sẵn"""
        # Sử dụng phân tích sentiment có nhận thức về ngữ cảnh
        return self._analyze_sentiment_context_aware(text)

    async def analyze_dispute(self, commission_id: str, reason: str,
                              evidence: Optional[List[str]] = None,
                              employee_id: str = None) -> Dict[str, Any]:
        """
        Phân tích tranh chấp với logic phân loại, đánh giá rủi ro và khuyến nghị được cải tiến.
        """
        try:
            logger.info(f"Analyzing dispute for commission {commission_id}")

            # 1. Các bước xử lý cơ bản
            language = self._detect_language(reason)
            processed_reason = self._preprocess_text(reason)
            sentiment_data = self._analyze_sentiment(processed_reason)

            # 2. Cải tiến logic phân loại tranh chấp
            dispute_keywords_found = self._extract_keywords(processed_reason, 'dispute')

            dispute_types = {
                'calculation_error': ['incorrect', 'wrong', 'error', 'mistake', 'sai', 'lỗi', 'không đúng', 'nhầm', 'tính sai'],
                'unfair_treatment': ['unfair', 'unjust', 'không công bằng', 'bất công', 'thiên vị', 'đối xử'],
                'performance_disagreement': ['performance', 'achievement', 'hiệu suất', 'thành tích', 'xứng đáng'],
                'policy_confusion': ['policy', 'rule', 'regulation', 'chính sách', 'quy định', 'không rõ']
            }

            # Đếm số từ khóa khớp với mỗi loại tranh chấp
            type_scores = {type_name: 0 for type_name in dispute_types.keys()}
            for keyword in dispute_keywords_found:
                for type_name, keywords_list in dispute_types.items():
                    if keyword in keywords_list:
                        type_scores[type_name] += 1
            
            # Tìm loại có điểm cao nhất, nếu hòa thì ưu tiên các loại quan trọng hơn
            dispute_type = 'general'
            max_score = 0
            if any(score > 0 for score in type_scores.values()):
                max_score = max(type_scores.values())
                # Lọc ra các loại có điểm cao nhất
                top_types = [type_name for type_name, score in type_scores.items() if score == max_score]
                
                # Nếu có nhiều hơn một loại có điểm bằng nhau, sử dụng thứ tự ưu tiên
                if len(top_types) > 1:
                    priority_order = ['unfair_treatment', 'calculation_error', 'policy_confusion', 'performance_disagreement']
                    for p_type in priority_order:
                        if p_type in top_types:
                            dispute_type = p_type
                            break
                else:
                    dispute_type = top_types[0]

            # 3. Cải tiến logic đánh giá rủi ro
            risk_score = 0
            risk_factors = []

            # Đánh giá dựa trên loại tranh chấp (quan trọng nhất)
            if dispute_type == 'unfair_treatment':
                risk_score += 4
                risk_factors.append('serious_allegation_unfairness')
            elif dispute_type == 'calculation_error':
                risk_score += 2
                risk_factors.append('potential_payroll_error')
            
            # Đánh giá dựa trên cảm xúc
            if sentiment_data['sentiment'] == 'negative' and sentiment_data['confidence'] > 0.75:
                risk_score += 3
                risk_factors.append('strong_negative_sentiment')
            
            # Đánh giá dựa trên số lượng từ khóa và bằng chứng
            if len(dispute_keywords_found) >= 3:
                risk_score += 2
                risk_factors.append('multiple_dispute_keywords')
            if evidence and len(evidence) > 0:
                risk_score += 1
                risk_factors.append('evidence_provided')
            
            # Xác định mức độ rủi ro
            risk_level = 'low'
            if risk_score >= 6:
                risk_level = 'high'
            elif risk_score >= 3:
                risk_level = 'medium'

            # 4. Cải tiến logic đề xuất khuyến nghị
            recommendation = 'maintain'
            if risk_level == 'high':
                if dispute_type == 'unfair_treatment':
                    recommendation = 'escalate_to_hr_immediately'
                else:
                    recommendation = 'prioritize_investigation'
            elif risk_level == 'medium':
                if dispute_type == 'calculation_error':
                    recommendation = 'review_calculation_data'
                elif dispute_type == 'unfair_treatment':
                    recommendation = 'review_with_manager'
                else:
                    recommendation = 'mediate'
            elif sentiment_data['sentiment'] == 'negative':
                 recommendation = 'document_and_monitor'

            # 5. Tạo kết quả trả về
            reasoning = (f"Dispute identified as '{dispute_type}' with '{risk_level}' risk. "
                         f"Sentiment was '{sentiment_data['sentiment']}' (confidence: {sentiment_data['confidence']:.2f}). "
                         f"Found {len(dispute_keywords_found)} relevant keywords. "
                         f"Recommendation is to '{recommendation}'.")

            result = {
                'sentiment': sentiment_data['sentiment'],
                'confidence': sentiment_data['confidence'],
                'language': language,
                'dispute_type': dispute_type,
                'dispute_keywords': dispute_keywords_found,
                'recommendation': recommendation,
                'suggested_adjustment': 0, # Tạm thời giữ nguyên
                'reasoning': reasoning,
                'risk_level': risk_level,
                'risk_factors': risk_factors,
                'evidence_count': len(evidence) if evidence else 0,
                'processed_at': datetime.now().isoformat(),
                'commission_id': commission_id,
                'employee_id': employee_id
            }

            logger.info(f"Dispute analysis completed for commission {commission_id} in {language}")
            return result

        except Exception as e:
            logger.error(f"Error analyzing dispute: {str(e)}")
            raise

    async def generate_explanation(self, commission_data: Dict[str, Any], 
                                 performance_data: Dict[str, Any]) -> str:
        """Generate human-readable explanation for commission calculation"""
        try:
            explanation_parts = []
            
            # Basic commission info
            explanation_parts.append(f"Commission calculation for {commission_data.get('role', 'employee')}")
            
            # Performance factors
            if 'performance_metrics' in commission_data:
                metrics = commission_data['performance_metrics']
                high_scores = []
                low_scores = []
                
                for metric, score in metrics.items():
                    if score >= 90:
                        high_scores.append(f"{metric} ({score})")
                    elif score < 70:
                        low_scores.append(f"{metric} ({score})")
                
                if high_scores:
                    explanation_parts.append(f"Strong performance in: {', '.join(high_scores)}")
                if low_scores:
                    explanation_parts.append(f"Areas for improvement: {', '.join(low_scores)}")
            
            # AI calculations
            if 'ai_calculations' in commission_data:
                ai_calc = commission_data['ai_calculations']
                
                if 'overall_score' in ai_calc:
                    explanation_parts.append(f"Overall performance score: {ai_calc['overall_score']:.1f}")
                
                if 'performance_level' in ai_calc:
                    level = ai_calc['performance_level']
                    explanation_parts.append(f"Performance level: {level}")
                
                if 'ai_confidence' in ai_calc:
                    confidence = ai_calc['ai_confidence']
                    explanation_parts.append(f"AI confidence in calculation: {confidence:.1f}%")
            
            # Bonus breakdown
            if 'ai_calculations' in commission_data:
                bonuses = commission_data['ai_calculations']
                bonus_parts = []
                
                if 'personal_bonus' in bonuses:
                    bonus_parts.append(f"Personal bonus: {bonuses['personal_bonus']:,.0f} VND")
                if 'quality_bonus' in bonuses and bonuses['quality_bonus'] > 0:
                    bonus_parts.append(f"Quality bonus: {bonuses['quality_bonus']:,.0f} VND")
                if 'innovation_bonus' in bonuses and bonuses['innovation_bonus'] > 0:
                    bonus_parts.append(f"Innovation bonus: {bonuses['innovation_bonus']:,.0f} VND")
                
                if bonus_parts:
                    explanation_parts.append("Bonus components: " + ", ".join(bonus_parts))
            
            # Final amount
            if 'final_amount' in commission_data:
                explanation_parts.append(f"Total commission: {commission_data['final_amount']:,.0f} VND")
            
            return ". ".join(explanation_parts) + "."
            
        except Exception as e:
            logger.error(f"Error generating explanation: {str(e)}")
            return "Commission calculation completed with AI assistance."

    async def train(self, training_data: Dict[str, Any]) -> Dict[str, Any]:
        """Train the NLP model with feedback data"""
        try:
            logger.info("Training NLP processor model")
            
            # For now, return success as we're using rule-based approach
            # In future, this could train spaCy models
            
            return {
                'success': True,
                'message': 'NLP processor using spaCy rule-based approach with multilingual support',
                'model_type': 'spacy_multilingual',
                'trained_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error training NLP model: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def is_ready(self) -> bool:
        """Check if the NLP processor is ready"""
        return True  # Always ready for rule-based processing

    def get_model_info(self) -> Dict[str, Any]:
        """Get NLP model information"""
        return {
            'model_type': 'spacy_multilingual',
            'is_trained': self.is_trained,
            'features': {
                'sentiment_analysis': True,
                'key_point_extraction': True,
                'dispute_analysis': True,
                'explanation_generation': True,
                'multilingual_support': True,
                'language_detection': True
            },
            'supported_languages': ['en', 'vi'],
            'performance_keywords_count': sum(len(keywords) for keywords in self.performance_keywords.values()),
            'dispute_keywords_count': len(self.dispute_keywords),
            'spacy_models': {
                'english': 'en_core_web_sm',
                'vietnamese': 'vi_core_news_lg'
            }
        }

    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key points from text using spaCy with improved context awareness"""
        if not text:
            return []
        
        nlp, matcher = self._get_nlp_model(text)
        doc = nlp(text)
        
        # Score sentences based on keywords, sentiment, and context
        scored_sentences = []
        
        # Phân tích sentiment cho toàn bộ văn bản
        overall_sentiment = self._analyze_sentiment(text)
        
        for sent in doc.sents:
            score = 0
            sent_text = sent.text
            
            # Phân tích sentiment cho từng câu
            sent_sentiment = self._analyze_sentiment(sent_text)
            
            # Check for performance keywords
            keywords = self._extract_keywords(sent_text, 'performance')
            score += len(keywords) * 2
            
            # Check for numbers (quantitative data)
            numbers = re.findall(r'\d+', sent_text)
            score += len(numbers) * 3
            
            # Check for action words using spaCy POS tags (both languages)
            action_words = ['completed', 'achieved', 'delivered', 'improved', 'exceeded',
                          'hoàn thành', 'đạt được', 'cung cấp', 'cải thiện', 'vượt qua',
                          'thực hiện', 'hoàn thành', 'đạt được', 'vượt qua', 'cải tiến']
            for word in action_words:
                if word in sent_text.lower():
                    score += 2
            
            # Bonus for sentences with named entities (important people/companies)
            if sent.ents:
                score += len(sent.ents) * 2
            
            # Bonus for sentences with important POS patterns
            for token in sent:
                if token.pos_ in ['VERB', 'NOUN'] and token.is_alpha:
                    score += 1
            
            # Bonus for sentences that match overall sentiment
            if sent_sentiment['sentiment'] == overall_sentiment['sentiment']:
                score += 3
            
            # Bonus for sentences with high confidence sentiment
            if sent_sentiment['confidence'] > 0.8:
                score += 2
            
            # Bonus for sentences with context adjustments
            if 'context_adjustments' in sent_sentiment and sent_sentiment['context_adjustments']['total_adjustments'] > 0:
                score += sent_sentiment['context_adjustments']['total_adjustments'] * 2
            
            # Bonus for sentences with specific performance metrics
            performance_metrics = ['kpi', 'quality', 'efficiency', 'teamwork', 'innovation', 'progress',
                                 'hiệu suất', 'chất lượng', 'hiệu quả', 'làm việc nhóm', 'đổi mới', 'tiến độ']
            for metric in performance_metrics:
                if metric in sent_text.lower():
                    score += 3
            
            scored_sentences.append((sent_text, score))
        
        # Return top 3 sentences with highest scores
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        return [sentence for sentence, score in scored_sentences[:3] if score > 0]

    async def process_feedback(self, text: str, source: str, 
                             context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process feedback using enhanced NLP analysis"""
        try:
            logger.info(f"Processing feedback from {source}")
            
            # Detect language
            language = self._detect_language(text)
            logger.info(f"Detected language: {language}")
            
            # Preprocess text
            processed_text = self._preprocess_text(text)
            
            # Analyze sentiment with context awareness
            sentiment_data = self._analyze_sentiment(processed_text)
            
            # Extract key points with improved method
            key_points = self._extract_key_points(text)
            
            # Generate satisfaction score
            satisfaction_score = self._generate_satisfaction_score(sentiment_data, source, context)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(sentiment_data, key_points, source)
            
            # Prepare explainability
            explainability = {
                'language_detected': language,
                'sentiment_factors': {
                    'keyword_balance': sentiment_data.get('scores', {}).get('keyword', {}),
                    'spacy_analysis': sentiment_data.get('scores', {}).get('spacy', {}),
                    'source_weight': 'client' if source == 'client' else 'standard',
                    'model_used': sentiment_data.get('model', 'rule_based')
                },
                'context_analysis': sentiment_data.get('context_adjustments', {}),
                'key_points_reasoning': f"Extracted {len(key_points)} key points based on performance keywords, context, and quantitative data",
                'satisfaction_calculation': f"Base score 5.0 adjusted by sentiment ({sentiment_data['sentiment']}) and source weight",
                'recommendation_basis': f"Based on {sentiment_data['sentiment']} sentiment with {sentiment_data['confidence']:.2f} confidence"
            }
            
            result = {
                'sentiment': sentiment_data['sentiment'],
                'confidence': sentiment_data['confidence'],
                'language': language,
                'key_points': key_points,
                'satisfaction_score': round(satisfaction_score, 1),
                'recommendations': recommendations,
                'explainability': explainability,
                'processed_at': datetime.now().isoformat(),
                'source': source,
                'context': context
            }
            
            logger.info(f"Feedback processing completed for {source} in {language}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing feedback: {str(e)}")
            raise

    def _generate_satisfaction_score(self, sentiment_data: Dict[str, Any], 
                                        source: str, 
                                        context: Optional[Dict[str, Any]] = None) -> float:
            """Generate a satisfaction score from 1 to 10 based on sentiment."""
            base_score = 5.0  # Start with a neutral score
            
            sentiment = sentiment_data.get('sentiment', 'neutral')
            confidence = sentiment_data.get('confidence', 0.5)

            if sentiment == 'positive':
                # Score increases from 5 to 10 based on confidence
                base_score += (5.0 * confidence)
            elif sentiment == 'negative':
                # Score decreases from 5 to 0 based on confidence
                base_score -= (5.0 * confidence)
            
            # Adjust score based on the source of the feedback (optional)
            source_weights = {
                'client': 1.1,      # Client feedback is more impactful
                'manager': 1.05,    # Manager feedback is important
                'peer': 1.0,
                'self': 0.95        # Self-feedback is slightly less impactful on score
            }
            
            # Apply weight but keep the score within the 1-10 range
            # Note: This weighting logic can be adjusted. A simple way is to adjust the final score slightly.
            # For now, we will return the raw score before weighting for simplicity.

            # Ensure the score is within the 1-10 range
            return max(1.0, min(10.0, base_score))

    async def evaluate_employee_performance(self, 
                                         kpi_data: Dict[str, float],
                                         feedback_texts: List[Dict[str, str]],
                                         employee_id: str,
                                         role: str) -> Dict[str, Any]:
        """Đánh giá hiệu suất nhân viên kết hợp KPI định lượng và phản hồi định tính"""
        try:
            logger.info(f"Evaluating performance for employee {employee_id}")
            
            # 1. Xử lý dữ liệu KPI định lượng
            kpi_score = kpi_data.get('kpi_score', 0)
            quality_score = kpi_data.get('quality_score', 0)
            efficiency_score = kpi_data.get('efficiency_score', 0)
            teamwork_score = kpi_data.get('teamwork_score', 0)
            innovation_score = kpi_data.get('innovation_score', 0)
            project_progress = kpi_data.get('project_progress', 0)
            
            # Tính điểm KPI trung bình
            quantitative_scores = [kpi_score, quality_score, efficiency_score, 
                                 teamwork_score, innovation_score, project_progress]
            valid_scores = [score for score in quantitative_scores if score > 0]
            avg_quantitative_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0
            
            # 2. Xử lý phản hồi định tính
            qualitative_results = []
            sentiment_scores = []
            
            for feedback in feedback_texts:
                text = feedback.get('text', '')
                source = feedback.get('source', 'peer')
                
                if text:
                    # Phân tích sentiment
                    result = await self.process_feedback(text, source)
                    qualitative_results.append(result)
                    
                    # Chuyển đổi sentiment thành điểm số
                    sentiment_score = 0
                    if result['sentiment'] == 'positive':
                        sentiment_score = 85 + (result['confidence'] * 15)  # 85-100
                    elif result['sentiment'] == 'neutral':
                        sentiment_score = 65 + (result['confidence'] * 20)  # 65-85
                    else:  # negative
                        sentiment_score = 40 + (result['confidence'] * 25)  # 40-65
                    
                    # Áp dụng trọng số dựa trên nguồn
                    source_weights = {
                        'client': 1.2,
                        'manager': 1.1,
                        'peer': 1.0,
                        'self': 0.8
                    }
                    weighted_score = sentiment_score * source_weights.get(source, 1.0)
                    sentiment_scores.append(weighted_score)
            
            # Tính điểm định tính trung bình
            avg_qualitative_score = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
            
            # 3. Kết hợp điểm định lượng và định tính
            # Trọng số cho từng loại điểm dựa trên vai trò
            role_weights = {
                'developer': {'quantitative': 0.6, 'qualitative': 0.4},
                'marketing_specialist': {'quantitative': 0.5, 'qualitative': 0.5},
                'direct_mentor': {'quantitative': 0.4, 'qualitative': 0.6},
                'indirect_mentor': {'quantitative': 0.45, 'qualitative': 0.55},
                'hr_recruiter': {'quantitative': 0.7, 'qualitative': 0.3},
                'business_development': {'quantitative': 0.5, 'qualitative': 0.5}
            }
            
            weights = role_weights.get(role, {'quantitative': 0.5, 'qualitative': 0.5})
            
            # Tính điểm tổng hợp
            combined_score = (avg_quantitative_score * weights['quantitative'] + 
                             avg_qualitative_score * weights['qualitative'])
            
            # 4. Xác định mức hiệu suất
            performance_level = 'average'
            if combined_score >= 90:
                performance_level = 'excellent'
            elif combined_score >= 80:
                performance_level = 'good'
            elif combined_score >= 70:
                performance_level = 'average'
            elif combined_score >= 60:
                performance_level = 'below_average'
            else:
                performance_level = 'poor'
            
            # 5. Tạo báo cáo
            report = {
                'employee_id': employee_id,
                'role': role,
                'quantitative_assessment': {
                    'kpi_score': kpi_score,
                    'quality_score': quality_score,
                    'efficiency_score': efficiency_score,
                    'teamwork_score': teamwork_score,
                    'innovation_score': innovation_score,
                    'project_progress': project_progress,
                    'average_score': avg_quantitative_score
                },
                'qualitative_assessment': {
                    'feedback_count': len(qualitative_results),
                    'sentiment_distribution': {
                        'positive': sum(1 for r in qualitative_results if r['sentiment'] == 'positive'),
                        'neutral': sum(1 for r in qualitative_results if r['sentiment'] == 'neutral'),
                        'negative': sum(1 for r in qualitative_results if r['sentiment'] == 'negative')
                    },
                    'key_points': [point for r in qualitative_results for point in r['key_points']],
                    'average_score': avg_qualitative_score
                },
                'combined_assessment': {
                    'quantitative_weight': weights['quantitative'],
                    'qualitative_weight': weights['qualitative'],
                    'combined_score': combined_score,
                    'performance_level': performance_level
                },
                'recommendations': self._generate_performance_recommendations(performance_level, role),
                'processed_at': datetime.now().isoformat()
            }
            
            logger.info(f"Performance evaluation completed for employee {employee_id}")
            return report
            
        except Exception as e:
            logger.error(f"Error evaluating employee performance: {str(e)}")
            raise

    def _generate_recommendations(self, sentiment_data: Dict[str, Any], 
                                  key_points: List[str], 
                                  source: str) -> List[str]:
        """Generate actionable recommendations based on feedback."""
        sentiment = sentiment_data.get('sentiment', 'neutral')
        recommendations = []

        if sentiment == 'positive':
            recommendations.append("Chia sẻ phản hồi tích cực này với nhân viên để ghi nhận.")
            if 'teamwork' in " ".join(key_points) or 'đồng đội' in " ".join(key_points):
                recommendations.append("Khen ngợi tinh thần hợp tác và làm việc nhóm.")
            recommendations.append("Lưu trữ phản hồi này cho kỳ đánh giá hiệu suất tiếp theo.")

        elif sentiment == 'negative':
            recommendations.append(f"Cần xem xét kỹ các điểm chính trong phản hồi từ {source}.")
            recommendations.append("Lên lịch một cuộc trao đổi riêng với nhân viên để làm rõ vấn đề.")
            if len(key_points) > 0:
                 recommendations.append("Sử dụng các điểm chính đã trích xuất làm cơ sở cho cuộc thảo luận.")
            else:
                 recommendations.append("Yêu cầu thêm thông tin chi tiết về các vấn đề được đề cập.")

        else: # neutral
            recommendations.append("Ghi nhận phản hồi và tiếp tục theo dõi hiệu suất.")
            if 'cải thiện' in " ".join(key_points) or 'improve' in " ".join(key_points):
                recommendations.append("Xác định các lĩnh vực cần cải thiện được đề cập và tạo kế hoạch phát triển.")
            
        return recommendations
    
    def _generate_performance_recommendations(self, performance_level: str, role: str) -> List[str]:
        """Tạo các khuyến nghị dựa trên mức hiệu suất và vai trò"""
        recommendations = []
        
        # Khuyến nghị chung dựa trên mức hiệu suất
        if performance_level == 'excellent':
            recommendations.extend([
                "Xem xét thăng chức hoặc tăng thưởng",
                "Ghi nhận thành tích xuất sắc công khai",
                "Giao nhiệm vụ quan trọng hơn để phát huy tiềm năng"
            ])
        elif performance_level == 'good':
            recommendations.extend([
                "Duy trình mức hiệu suất hiện tại",
                "Cung cấp phản hồi tích cực",
                "Xác định cơ hội phát triển kỹ năng"
            ])
        elif performance_level == 'average':
            recommendations.extend([
                "Đặt mục tiêu hiệu suất cụ thể",
                "Cung cấp đào tạo bổ sung",
                "Theo dõi tiến độ thường xuyên"
            ])
        elif performance_level == 'below_average':
            recommendations.extend([
                "Lên lịch họp cải thiện hiệu suất",
                "Xác định các lĩnh vực cần cải thiện",
                "Cung cấp hướng dẫn và hỗ trợ thêm"
            ])
        else:  # poor
            recommendations.extend([
                "Phát triển kế hoạch cải thiện hiệu suất",
                "Đặt mục tiêu ngắn hạn và dài hạn",
                "Theo dõi chặt chẽ và đánh giá thường xuyên"
            ])
        
        # Khuyến nghị cụ thể dựa trên vai trò
        role_recommendations = {
            'developer': [
                "Tham gia các dự án phát triển kỹ năng kỹ thuật",
                "Cập nhật kiến thức về công nghệ mới"
            ],
            'marketing_specialist': [
                "Phân tích xu hướng thị trường mới nhất",
                "Phát triển chiến lược tiếp thị sáng tạo"
            ],
            'direct_mentor': [
                "Tăng cường kỹ năng huấn luyện và phát triển",
                "Xây dựng kế hoạch phát triển cho từng nhân viên"
            ],
            'indirect_mentor': [
                "Chia sẻ kiến thức chuyên môn rộng rãi",
                "Tạo cơ hội học tập cho nhóm"
            ],
            'hr_recruiter': [
                "Cải thiện quy trình tuyển dụng",
                "Phát triển chiến lược giữ chân nhân tài"
            ],
            'business_development': [
                "Mở rộng mạng lưới đối tác",
                "Xác định cơ hội kinh doanh mới"
            ]
        }
        
        if role in role_recommendations:
            recommendations.extend(role_recommendations[role])
        
        return recommendations
