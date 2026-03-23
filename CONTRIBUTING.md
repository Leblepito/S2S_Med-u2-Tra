# Contributing to BabelFlow

## Development Methodology

**TDD (Test-Driven Development):**
1. Write failing test (RED)
2. Implement minimum code to pass (GREEN)
3. Refactor (keep GREEN)

## Conventional Commits

```
feat: new feature
fix: bug fix
refactor: code restructuring (no behavior change)
test: adding/updating tests
docs: documentation
```

## Code Standards

### Python (Backend)
- `async def` + `await` for all I/O
- Type hints on every function (params + return)
- Pydantic V2 `BaseModel` for all data structures
- Docstring on every public function
- `logger` instead of `print()`
- Specific exception handling (no bare `except:`)
- Function max 30 lines, file max 200 lines
- WebSocket handler max 50 lines
- Import order: stdlib, third-party, local

### TypeScript (Frontend)
- Functional components + hooks only
- `const` default, `let` when needed, no `var`
- No `any` — proper typing
- `AudioWorkletNode` (not `ScriptProcessorNode`)
- Tailwind CSS inline classes

## Running Tests

```bash
cd backend
pytest tests/ -v
pytest tests/ -v --cov=app --cov-report=term-missing
```

## File Ownership (3-Terminal Model)

| Engineer | Scope | Don't Touch |
|----------|-------|-------------|
| Engineer A (Backend) | `backend/`, `tests/` | `frontend/` |
| Engineer B (Frontend) | `frontend/` | `backend/` |
| Architect | `docs/`, `CLAUDE.md`, `.claude/` | Large code changes |

## Audio Constants

- Input: PCM16 LE, 16kHz, Mono, 480 samples (30ms) = 960 bytes
- TTS Output: PCM16 LE, 24kHz, Mono
- Supported languages: tr, ru, en, th, vi, zh, id
