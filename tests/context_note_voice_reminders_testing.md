# Context Note: Voice Reminders Testing Session

## Overview
I'm helping the user debug and understand test failures for a voice reminders system they've built. The user is learning through a "teach me" approach rather than having me directly fix the code.

## Key Context

### System Architecture
- **Voice Reminders System**: A Python tool that plays voice reminders at scheduled times using OpenAI TTS
- **Lazy Loading**: The system uses a custom `python_builtins` class (originally named `builtins`) that lazy-loads Python modules
- **Persistence**: Reminders are saved to JSON files and survive server restarts
- **Threading**: Uses a daemon thread to check and play due reminders

### Testing Approach
- User follows "red-green-refactor" methodology
- Tests are written to fail first, then code is implemented
- User prefers to understand WHY tests fail rather than just getting fixes

### Key Issues Encountered

1. **Hardcoded Dates**: Tests used fixed dates (e.g., Dec 25, 2024) that became past dates, failing FutureDatetime validation
   - Solution: Use relative dates like `datetime.now() + timedelta(hours=1)`

2. **Mocking Read-Only Properties**: Tried to patch lazy-loaded properties that have no setters
   - Solution: Mock the returned values, not the property itself

3. **Time Control in Tests**: Need to test time-dependent behavior (reminders becoming due)
   - Solution: Create future reminders, then mock time.time() to simulate passage of time

4. **Pydantic Model Constraints**: Can't bypass validation with `__new__` due to Pydantic's internal state
   - Solution: Use `model_construct()` or work within validation constraints

### Current Status
- Fixed test file name: `test_nag_user_with_voice_reminders.py`
- Renamed `builtins` to `python_builtins` to avoid confusion
- Working through test failures one by one
- Teaching user about Python testing patterns and common pitfalls

### User's Preferences
- Wants to understand the "why" behind issues
- Prefers learning over quick fixes
- Uses comprehensive Google-style docstrings
- Follows specific code architecture steps (PRD → MVP → tests → implementation)

### Next Steps
Continue working through remaining test failures, explaining:
- Root cause of each failure
- Python/testing concepts involved
- Best practices for similar situations