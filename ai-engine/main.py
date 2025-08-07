from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

# Import AI modules
from modules.reward_calculator import RewardCalculator
from modules.nlp_processor import NLPProcessor
from modules.anomaly_detector import AnomalyDetector
from modules.kpi_suggester import KPISuggester
from modules.forecast_assistant import ForecastAssistant
from modules.top_performer_analyzer import TopPerformerAnalyzer

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ai_engine.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Commission Management Engine",
    description="AI-First Commission Management System - AI Engine",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize AI modules
reward_calculator = RewardCalculator()
nlp_processor = NLPProcessor()
anomaly_detector = AnomalyDetector()
kpi_suggester = KPISuggester()
forecast_assistant = ForecastAssistant()
top_performer_analyzer = TopPerformerAnalyzer()

# Pydantic models
class PerformanceData(BaseModel):
    employee_id: str
    project_id: str
    role: str
    kpi_scores: Dict[str, float]
    project_progress: float
    client_satisfaction: float
    deadline_adherence: float
    quality_score: float
    efficiency_score: float
    teamwork_score: float
    innovation_score: float
    base_salary: float
    project_profit: float

class FeedbackData(BaseModel):
    text: str
    source: str  # 'client', 'manager', 'peer'
    context: Optional[Dict[str, Any]] = None

class CommissionRequest(BaseModel):
    period: Dict[str, int]  # year, month
    project_id: str
    employee_id: str
    performance_data: PerformanceData

class DisputeData(BaseModel):
    commission_id: str
    reason: str
    evidence: Optional[List[str]] = None
    employee_id: str

class ForecastRequest(BaseModel):
    employee_id: str
    project_id: str
    historical_data: List[Dict[str, Any]]
    current_performance: Dict[str, Any]

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "modules": {
            "reward_calculator": reward_calculator.is_ready(),
            "nlp_processor": nlp_processor.is_ready(),
            "anomaly_detector": anomaly_detector.is_ready(),
            "kpi_suggester": kpi_suggester.is_ready(),
            "forecast_assistant": forecast_assistant.is_ready(),
            "top_performer_analyzer": top_performer_analyzer.is_ready()
        }
    }

# Reward calculation endpoint
@app.post("/calculate-reward")
async def calculate_reward(
    request: CommissionRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        logger.info(f"Calculating reward for employee {request.employee_id}")
        
        # Validate token (implement your token validation logic)
        # await validate_token(credentials.credentials)
        
        # Calculate reward using AI
        result = await reward_calculator.calculate(
            period=request.period,
            project_id=request.project_id,
            employee_id=request.employee_id,
            performance_data=request.performance_data.dict()
        )
        
        logger.info(f"Reward calculation completed for employee {request.employee_id}")
        
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error calculating reward: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating reward: {str(e)}"
        )

# NLP feedback processing endpoint
@app.post("/process-feedback")
async def process_feedback(
    feedback: FeedbackData,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        logger.info(f"Processing feedback from {feedback.source}")
        
        # Process feedback using NLP
        result = await nlp_processor.process_feedback(
            text=feedback.text,
            source=feedback.source,
            context=feedback.context
        )
        
        logger.info(f"Feedback processing completed for {feedback.source}")
        
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error processing feedback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing feedback: {str(e)}"
        )

# Anomaly detection endpoint
@app.post("/detect-anomalies")
async def detect_anomalies(
    data: Dict[str, Any],
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        logger.info("Detecting anomalies in data")
        
        # Detect anomalies
        result = await anomaly_detector.detect(data)
        
        logger.info("Anomaly detection completed")
        
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error detecting anomalies: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error detecting anomalies: {str(e)}"
        )

# KPI suggestion endpoint
@app.post("/suggest-kpis")
async def suggest_kpis(
    project_data: Dict[str, Any],
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        logger.info("Suggesting KPIs for project")
        
        # Suggest KPIs
        result = await kpi_suggester.suggest(project_data)
        
        logger.info("KPI suggestion completed")
        
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error suggesting KPIs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error suggesting KPIs: {str(e)}"
        )

# Forecast endpoint
@app.post("/forecast-commission")
async def forecast_commission(
    request: ForecastRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        logger.info(f"Forecasting commission for employee {request.employee_id}")
        
        # Generate forecast
        result = await forecast_assistant.forecast(
            employee_id=request.employee_id,
            project_id=request.project_id,
            historical_data=request.historical_data,
            current_performance=request.current_performance
        )
        
        logger.info(f"Commission forecast completed for employee {request.employee_id}")
        
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error forecasting commission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error forecasting commission: {str(e)}"
        )

# Top performer analysis endpoint
@app.post("/analyze-top-performers")
async def analyze_top_performers(
    data: Dict[str, Any],
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        logger.info("Analyzing top performers")
        
        # Analyze top performers
        result = await top_performer_analyzer.analyze(data)
        
        logger.info("Top performer analysis completed")
        
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error analyzing top performers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing top performers: {str(e)}"
        )

# Dispute analysis endpoint
@app.post("/analyze-dispute")
async def analyze_dispute(
    dispute: DisputeData,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        logger.info(f"Analyzing dispute for commission {dispute.commission_id}")
        
        # Analyze dispute using NLP
        result = await nlp_processor.analyze_dispute(
            commission_id=dispute.commission_id,
            reason=dispute.reason,
            evidence=dispute.evidence,
            employee_id=dispute.employee_id
        )
        
        logger.info(f"Dispute analysis completed for commission {dispute.commission_id}")
        
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error analyzing dispute: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing dispute: {str(e)}"
        )

# Batch processing endpoint
@app.post("/batch-process")
async def batch_process(
    requests: List[CommissionRequest],
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        logger.info(f"Processing batch of {len(requests)} commission requests")
        
        results = []
        for request in requests:
            try:
                result = await reward_calculator.calculate(
                    period=request.period,
                    project_id=request.project_id,
                    employee_id=request.employee_id,
                    performance_data=request.performance_data.dict()
                )
                results.append({
                    "employee_id": request.employee_id,
                    "success": True,
                    "data": result
                })
            except Exception as e:
                results.append({
                    "employee_id": request.employee_id,
                    "success": False,
                    "error": str(e)
                })
        
        logger.info(f"Batch processing completed for {len(requests)} requests")
        
        return {
            "success": True,
            "data": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in batch processing: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in batch processing: {str(e)}"
        )

# Model training endpoint (admin only)
@app.post("/train-models")
async def train_models(
    training_data: Dict[str, Any],
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        logger.info("Training AI models")
        
        # Train all models
        results = {
            "reward_calculator": await reward_calculator.train(training_data),
            "nlp_processor": await nlp_processor.train(training_data),
            "anomaly_detector": await anomaly_detector.train(training_data),
            "kpi_suggester": await kpi_suggester.train(training_data),
            "forecast_assistant": await forecast_assistant.train(training_data),
            "top_performer_analyzer": await top_performer_analyzer.train(training_data)
        }
        
        logger.info("Model training completed")
        
        return {
            "success": True,
            "data": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error training models: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error training models: {str(e)}"
        )

if __name__ == "__main__":
    port = int(os.getenv("AI_ENGINE_PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    ) 