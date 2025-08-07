#!/bin/bash

# AI Commission Management System - Startup Script
echo "🚀 Starting AI Commission Management System..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p uploads
mkdir -p models
mkdir -p nginx/ssl

# Copy environment file if not exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your configuration before starting the system."
fi

# Function to check if ports are available
check_port() {
    local port=$1
    local service=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo "❌ Port $port is already in use by another service. Please stop it first."
        exit 1
    fi
}

# Check if required ports are available
echo "🔍 Checking port availability..."
check_port 3000 "Frontend"
check_port 5000 "Backend API"
check_port 8000 "AI Engine"
check_port 27017 "MongoDB"
check_port 6379 "Redis"
check_port 80 "Nginx"
check_port 5555 "Flower"

# Build and start services
echo "🐳 Building and starting Docker services..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🏥 Checking service health..."

# Check MongoDB
if curl -s http://localhost:27017 > /dev/null 2>&1; then
    echo "✅ MongoDB is running"
else
    echo "❌ MongoDB is not responding"
fi

# Check Redis
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is running"
else
    echo "❌ Redis is not responding"
fi

# Check Backend API
if curl -s http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ Backend API is running"
else
    echo "❌ Backend API is not responding"
fi

# Check AI Engine
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ AI Engine is running"
else
    echo "❌ AI Engine is not responding"
fi

# Check Frontend
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is running"
else
    echo "❌ Frontend is not responding"
fi

echo ""
echo "🎉 AI Commission Management System is starting up!"
echo ""
echo "📊 Service URLs:"
echo "   Frontend:     http://localhost:3000"
echo "   Backend API:  http://localhost:5000"
echo "   AI Engine:    http://localhost:8000"
echo "   API Docs:     http://localhost:5000/docs"
echo "   Flower:       http://localhost:5555"
echo ""
echo "🔧 Management Commands:"
echo "   View logs:    docker-compose logs -f"
echo "   Stop system:  docker-compose down"
echo "   Restart:      docker-compose restart"
echo "   Update:       docker-compose pull && docker-compose up -d"
echo ""
echo "📝 Next steps:"
echo "   1. Open http://localhost:3000 in your browser"
echo "   2. Register an admin account or use default credentials"
echo "   3. Configure your settings in the admin panel"
echo "   4. Start creating projects and managing commissions!"
echo ""
echo "💡 Default admin credentials (if available):"
echo "   Email: admin@ai-commission.com"
echo "   Password: admin123"
echo ""
echo "🔒 Security Note: Please change default passwords in production!" 