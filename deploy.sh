#!/bin/bash

# Marketing Automation MCP Deployment Script
# Easy deployment for demos and production

set -e

echo "🚀 Marketing Automation MCP Deployment"
echo "===================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env with your API credentials"
    echo "   Then run this script again."
    exit 1
fi

# Parse command line arguments
MODE=${1:-"demo"}
ACTION=${2:-"start"}

case "$MODE" in
    "demo")
        echo "📊 Starting in DEMO mode..."
        export DEMO_MODE=true
        
        if [ "$ACTION" = "start" ]; then
            # Start demo services
            docker-compose up -d postgres redis
            sleep 5  # Wait for services
            
            # Run demo
            echo "🎭 Running demo presentation..."
            docker-compose run --rm demo
            
            # Start dashboard
            echo "📈 Starting dashboard..."
            docker-compose up -d dashboard
            
            echo ""
            echo "✅ Demo started successfully!"
            echo "📊 Dashboard: http://localhost:8080"
            echo "📑 Presentation: Open doordash_demo_deck.html in your browser"
            echo ""
        elif [ "$ACTION" = "stop" ]; then
            docker-compose down
            echo "✅ Demo stopped"
        fi
        ;;
        
    "dev")
        echo "💻 Starting in DEVELOPMENT mode..."
        
        if [ "$ACTION" = "start" ]; then
            # Start all services including notebook
            docker-compose --profile development up -d
            
            echo ""
            echo "✅ Development environment started!"
            echo "📊 Dashboard: http://localhost:8080"
            echo "📓 Jupyter: http://localhost:8888"
            echo "🗄️  PostgreSQL: localhost:5432"
            echo "📮 Redis: localhost:6379"
            echo ""
        elif [ "$ACTION" = "stop" ]; then
            docker-compose --profile development down
            echo "✅ Development environment stopped"
        fi
        ;;
        
    "prod")
        echo "🏭 Starting in PRODUCTION mode..."
        export DEMO_MODE=false
        
        if [ "$ACTION" = "start" ]; then
            # Build images
            echo "🔨 Building Docker images..."
            docker-compose build
            
            # Start production services
            docker-compose up -d
            
            # Run database migrations
            echo "🗄️  Running database migrations..."
            docker-compose exec mcp-server alembic upgrade head
            
            echo ""
            echo "✅ Production deployment complete!"
            echo "📊 Dashboard: http://localhost:8080"
            echo ""
            echo "⚠️  Remember to:"
            echo "   - Set up SSL/TLS for production"
            echo "   - Configure firewall rules"
            echo "   - Set up monitoring and alerts"
            echo ""
        elif [ "$ACTION" = "stop" ]; then
            docker-compose down
            echo "✅ Production services stopped"
        elif [ "$ACTION" = "logs" ]; then
            docker-compose logs -f
        fi
        ;;
        
    "test")
        echo "🧪 Running tests..."
        
        # Start test database
        docker-compose up -d postgres
        sleep 5
        
        # Run tests
        docker-compose run --rm mcp-server pytest tests/ -v
        
        # Cleanup
        docker-compose down
        ;;
        
    *)
        echo "Usage: ./deploy.sh [demo|dev|prod|test] [start|stop|logs]"
        echo ""
        echo "Modes:"
        echo "  demo  - Run the DoorDash interview demo"
        echo "  dev   - Start development environment with Jupyter"
        echo "  prod  - Deploy production services"
        echo "  test  - Run test suite"
        echo ""
        echo "Actions:"
        echo "  start - Start services (default)"
        echo "  stop  - Stop services"
        echo "  logs  - View logs (prod only)"
        exit 1
        ;;
esac