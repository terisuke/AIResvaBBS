# Task Completion Checklist

## Before Marking Any Task Complete

### 1. Code Quality Checks
- [ ] Run linting for the files you modified:
  - Frontend: `cd frontend && npm run lint`
  - Backend: Python files follow PEP 8
- [ ] No TypeScript errors (frontend)
- [ ] No Python type hint issues (backend)

### 2. Functionality Verification
- [ ] Test the feature/fix locally
- [ ] Verify WebSocket connections work (if modified)
- [ ] Check browser console for errors (frontend)
- [ ] Check backend logs for errors

### 3. Integration Testing
- [ ] Run the full development environment: `./run_dev.sh`
- [ ] Test the complete user flow
- [ ] Verify AI characters respond correctly (if applicable)
- [ ] Check LocalStorage persistence (if applicable)

### 4. Code Review Preparation
- [ ] Remove any debug console.log/print statements
- [ ] Ensure no hardcoded values (use env variables)
- [ ] API keys are in .env, not in code
- [ ] Rate limiting implemented for API calls

### 5. Documentation
- [ ] Update relevant documentation if needed
- [ ] Add to CLAUDE.md if introducing new patterns

## Quick Verification Commands
```bash
# Frontend lint
cd frontend && npm run lint

# Backend check (from backend dir with venv activated)
python -m py_compile *.py

# Full system test
./run_dev.sh
```

## Common Issues to Check
- WebSocket disconnection handling
- API rate limit compliance
- Proper error boundaries in React
- Async/await usage in backend
- Type safety in TypeScript