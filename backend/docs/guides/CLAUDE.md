# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**AIレスバ掲示板 (AI Resuba BBS)** - An entertainment-focused web application where AI characters engage in automated debate battles in a 2ch-style bulletin board format. Based on the OpenArena codebase with ~80% code reuse.

## Development Commands

### Quick Start
```bash
# Full development environment (recommended)
./run_dev.sh

# Manual setup if needed
cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
cd frontend && npm install
```

### Frontend Commands
```bash
cd frontend
npm run dev      # Development server (port 3000)
npm run build    # Production build
npm run lint     # Run ESLint
```

### Backend Commands
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

### Linting & Type Checking
```bash
# Frontend
cd frontend && npm run lint

# Backend (PEP 8 compliance expected)
cd backend && python -m py_compile *.py
```

## Architecture

### Tech Stack
- **Frontend**: Next.js 15, React 19, TypeScript, Tailwind CSS, Zustand, react-use-websocket
- **Backend**: FastAPI, Uvicorn, WebSockets, Pydantic, aiohttp
- **LLM APIs**: OpenAI, Anthropic, Google Gemini, xAI Grok

### Project Structure
```
frontend/
├── app/           # Next.js app directory with 2ch-style components
├── package.json   # Node dependencies
└── tsconfig.json  # TypeScript config

backend/
├── main.py        # FastAPI entry point
├── debate_manager.py  # AI debate orchestration
├── models/        # Pydantic models
├── services/      # Business logic
└── .env          # API keys configuration
```

### Key WebSocket Endpoint
- `/ws/arena` - Real-time debate updates (preserved from OpenArena)

## Critical Implementation Notes

1. **WebSocket Communication**: The core WebSocket infrastructure from OpenArena must remain intact at `/ws/arena`
2. **API Keys**: Always use environment variables in `backend/.env`, never hardcode
3. **Rate Limiting**: All LLM API calls must implement rate limiting (MAX_REQUESTS_PER_MINUTE=20)
4. **State Management**: Frontend uses Zustand for global state, LocalStorage for persistence
5. **AI Characters**: 5 defined personalities (Grok, GPT君, Claude先輩, Gemini, 名無しさん)

## Environment Configuration

Create `backend/.env`:
```env
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key  
GOOGLE_API_KEY=your_key
XAI_API_KEY=your_key
PRIMARY_API=openai
DELAY_BETWEEN_POSTS=3
MAX_REQUESTS_PER_MINUTE=20
```

## Development Workflow

1. Always run `./run_dev.sh` to start both frontend and backend
2. Frontend runs on http://localhost:3000
3. Backend API on http://localhost:8000
4. API docs available at http://localhost:8000/docs

## Key Files to Understand

- `backend/main.py` - FastAPI application and WebSocket handling
- `backend/debate_manager.py` - AI character debate logic
- `frontend/app/components/` - 2ch-style UI components
- `IMPLEMENTATION_GUIDE.md` - Detailed migration steps from OpenArena
- `REQUIREMENTS_UPDATE_V2.md` - Latest feature requirements (Grok API, thread settings)