# Development Commands

## Setup
```bash
# Initial setup (if not done)
./setup.sh

# Or manual setup:
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cd ../frontend
npm install
```

## Development
```bash
# Run both frontend and backend (recommended)
./run_dev.sh

# Or run separately:
# Backend
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm run dev
```

## Frontend Commands
```bash
cd frontend
npm run dev      # Start development server
npm run build    # Build for production
npm run start    # Start production server
npm run lint     # Run ESLint
```

## Backend Commands
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000  # Dev server
python main.py                          # Alternative start
```

## Environment Setup
```bash
# Create backend/.env file with:
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
GOOGLE_API_KEY=your_key
XAI_API_KEY=your_key
PRIMARY_API=openai
DELAY_BETWEEN_POSTS=3
MAX_REQUESTS_PER_MINUTE=20
```

## URLs
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Git Commands
```bash
git status
git add .
git commit -m "feat: your message"
git push origin your-branch
```