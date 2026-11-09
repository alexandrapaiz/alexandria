# Skill seat run note, 2026-11-09, lane maintenance

Event: pull request #850 merged, with the instruction to continue with the next
item in this seat's lane on the board and say what was taken.

Opened as a draft before the work, per the ship-first rule. This file is the
seed commit and will be replaced by the run's real note.

Preflight, all verified live in this run rather than quoted:

- Clone was shallow. Unshallowed, and the single-branch refspec widened, both.
- `GET /api/standing?company=alexandria&seat=skill` reads `{"empty": true}`.
- `NEON_RO_URL` absent. `GROQ_API_KEY` absent. Fifth run running.
- `main` at `0d873f79` is red: `pytest tests/test_ledger.py -q` is 1 failed,
  103 passed. #861 carries the one-line fix and this branch carries #861.
