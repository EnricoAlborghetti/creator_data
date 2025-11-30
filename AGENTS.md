# AGENTS.md

## Project Structure
This project is designed to run on Zoho Catalyst.
- `src/`: Source code root.
  - `models/`: Pydantic models for data validation.
  - `data/`: Data access layer (Mock WorkDrive, CRM, State).
  - `ai/`: AI integration (OpenAI Vision).
  - `core/`: Configuration and logging.
- `workdrive_mock/`: Local directory simulating Zoho WorkDrive.
- `crm_output.json`: Output file mocking Zoho CRM storage.
- `state.json`: State file tracking processed files.

## Coding Standards
- Use Python 3.12+.
- Use Pydantic for all data structures.
- Use structured logging.
- Handle `poppler` missing gracefully (fallback or error logging).
- **Execution:** The script runs in batches (default 50 files) and exits.
