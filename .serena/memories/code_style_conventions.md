# Code Style and Conventions

## Python (Backend)
- **Style Guide**: PEP 8 compliant
- **Type Hints**: Use type hints for all function parameters and returns
- **Async/Await**: Use async functions for all I/O operations
- **Docstrings**: Not required unless complex logic
- **Naming**:
  - Functions/variables: snake_case
  - Classes: PascalCase
  - Constants: UPPER_SNAKE_CASE
- **File Organization**: One class/service per file when possible

## TypeScript/JavaScript (Frontend)
- **Style**: ESLint configuration (already set up)
- **React**: Functional components with hooks only
- **Type Safety**: Strict TypeScript, avoid 'any' type
- **Naming**:
  - Components: PascalCase
  - Functions/variables: camelCase
  - Constants: UPPER_SNAKE_CASE
- **Imports**: Absolute imports preferred
- **State Management**: Zustand for global state, useState for local

## Git Commit Convention
- Use Conventional Commits format:
  - `feat:` New feature
  - `fix:` Bug fix
  - `refactor:` Code refactoring
  - `docs:` Documentation
  - `test:` Testing
  - `chore:` Maintenance

## Important Guidelines
- **NO COMMENTS** unless explicitly requested or for complex algorithms
- Preserve existing WebSocket communication patterns from OpenArena
- Follow existing patterns in the codebase
- API keys must use environment variables, never hardcode
- All API calls must implement rate limiting
- Test locally before committing

## Branch Strategy
```
main
├── develop
│   ├── feature/phase1-migration
│   ├── feature/phase2-backend
│   ├── feature/phase3-frontend
│   └── feature/phase4-integration
```