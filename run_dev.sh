#!/bin/bash

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   LLM Debate Arena Development Setup   ${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if Ollama is running
check_ollama() {
    echo -e "${YELLOW}Checking Ollama status...${NC}"
    if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Ollama is running${NC}"
        return 0
    else
        echo -e "${RED}✗ Ollama is not running${NC}"
        echo -e "${YELLOW}Please start Ollama with: ollama serve${NC}"
        return 1
    fi
}

# Function to check available models
check_models() {
    echo -e "${YELLOW}Checking available models...${NC}"
    
    # Get list of models from Ollama
    models=$(curl -s http://localhost:11434/api/tags | python3 -c "
import json, sys
data = json.load(sys.stdin)
if 'models' in data:
    for model in data['models']:
        print(model['name'])
" 2>/dev/null)
    
    if [ -z "$models" ]; then
        echo -e "${RED}✗ No models found${NC}"
        echo -e "${YELLOW}Recommended models to install:${NC}"
        echo "  - ollama pull llama3.2:3b"
        echo "  - ollama pull gemma2:2b"
        echo "  - ollama pull qwen2.5:3b"
        echo ""
        echo -e "${YELLOW}For better performance (if you have enough RAM):${NC}"
        echo "  - ollama pull qwen2.5:32b"
        echo "  - ollama pull llama3.2:8b"
        return 1
    else
        echo -e "${GREEN}✓ Found models:${NC}"
        echo "$models" | while read -r model; do
            echo "  - $model"
        done
        return 0
    fi
}

# Function to check Python dependencies
check_python_deps() {
    echo -e "${YELLOW}Checking Python dependencies...${NC}"
    
    if ! command_exists python3; then
        echo -e "${RED}✗ Python 3 is not installed${NC}"
        return 1
    fi
    
    # Check if virtual environment exists
    if [ -d "backend/venv" ]; then
        echo -e "${GREEN}✓ Virtual environment found${NC}"
    else
        echo -e "${YELLOW}Creating virtual environment...${NC}"
        cd backend
        python3 -m venv venv
        cd ..
    fi
    
    # Activate virtual environment and install dependencies
    source backend/venv/bin/activate
    
    echo -e "${YELLOW}Installing Python dependencies...${NC}"
    pip install -q -r backend/requirements.txt
    
    echo -e "${GREEN}✓ Python dependencies installed${NC}"
    return 0
}

# Function to check Node.js dependencies
check_node_deps() {
    echo -e "${YELLOW}Checking Node.js dependencies...${NC}"
    
    if ! command_exists npm; then
        echo -e "${RED}✗ Node.js/npm is not installed${NC}"
        return 1
    fi
    
    if [ ! -d "frontend/node_modules" ]; then
        echo -e "${YELLOW}Installing Node.js dependencies...${NC}"
        cd frontend
        npm install
        cd ..
    fi
    
    echo -e "${GREEN}✓ Node.js dependencies installed${NC}"
    return 0
}

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down services...${NC}"
    
    # Kill backend process
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo -e "${GREEN}✓ Backend stopped${NC}"
    fi
    
    # Kill frontend process
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo -e "${GREEN}✓ Frontend stopped${NC}"
    fi
    
    exit 0
}

# Set up trap to cleanup on script exit
trap cleanup EXIT INT TERM

# Main execution
main() {
    echo -e "${YELLOW}Starting dependency checks...${NC}"
    echo ""
    
    # Check Ollama
    if ! check_ollama; then
        echo -e "${RED}Please start Ollama before running the development environment${NC}"
        exit 1
    fi
    echo ""
    
    # Check models
    check_models
    echo ""
    
    # Check Python dependencies
    if ! check_python_deps; then
        echo -e "${RED}Failed to set up Python dependencies${NC}"
        exit 1
    fi
    echo ""
    
    # Check Node.js dependencies
    if ! check_node_deps; then
        echo -e "${RED}Failed to set up Node.js dependencies${NC}"
        exit 1
    fi
    echo ""
    
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}   Starting Development Environment     ${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    
    # Start backend
    echo -e "${YELLOW}Starting backend server...${NC}"
    cd backend
    source venv/bin/activate
    uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    cd ..
    
    # Wait for backend to start
    sleep 3
    
    # Check if backend is running
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend running at http://localhost:8000${NC}"
    else
        echo -e "${RED}✗ Backend failed to start${NC}"
        exit 1
    fi
    echo ""
    
    # Start frontend
    echo -e "${YELLOW}Starting frontend server...${NC}"
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    # Wait for frontend to start
    sleep 5
    
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}   Development Environment Ready!       ${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${GREEN}✓ Backend API: ${NC}http://localhost:8000"
    echo -e "${GREEN}✓ Frontend UI: ${NC}http://localhost:3000"
    echo -e "${GREEN}✓ API Docs:    ${NC}http://localhost:8000/docs"
    echo ""
    echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
    echo ""
    
    # Keep script running
    wait
}

# Run main function
main