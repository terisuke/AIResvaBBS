# Codebase Structure

## Root Directory
```
/Users/teradakousuke/Developer/AIResvaBBS/
├── frontend/          # Next.js frontend application
├── backend/           # FastAPI backend server
├── .serena/          # Serena project config
├── .claude/          # Claude configuration
├── PRD.md            # Product Requirements Document
├── TDD.md            # Technical Design Document  
├── IMPLEMENTATION_GUIDE.md  # Step-by-step implementation guide
├── TEST_PLAN.md      # Testing strategy
├── REQUIREMENTS_UPDATE_V2.md  # v2.0 requirements (Grok API, etc.)
├── README.md         # Project overview
├── run_dev.sh        # Development startup script
└── setup.sh          # Initial setup script
```

## Frontend Structure
```
frontend/
├── app/              # Next.js app directory
│   ├── components/   # React components (2ch-style UI)
│   ├── hooks/        # Custom React hooks
│   └── stores/       # Zustand state stores
├── public/           # Static assets
├── package.json      # Node dependencies
├── next.config.ts    # Next.js configuration
├── tsconfig.json     # TypeScript config
└── tailwind.config.* # Tailwind CSS config
```

## Backend Structure
```
backend/
├── models/           # Pydantic data models
├── services/         # Business logic services
├── main.py          # FastAPI application entry
├── debate_manager.py # AI debate orchestration
├── llm_arena.py     # LLM interaction layer (to be modified)
├── characters.py    # AI character definitions (new)
├── requirements.txt  # Python dependencies
├── .env             # Environment variables
└── arena_config.yaml # Configuration (to be replaced)
```

## Key WebSocket Endpoint
- `/ws/arena` - Main WebSocket connection for real-time debate updates

## Data Flow
1. Frontend connects via WebSocket to backend
2. Backend manages AI character interactions through cloud APIs
3. Debate messages sent in real-time to frontend
4. Frontend displays in 2ch-style thread format
5. Threads persisted in browser LocalStorage