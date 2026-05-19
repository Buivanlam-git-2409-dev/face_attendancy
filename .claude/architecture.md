# Architecture

## Current Structure

- app.py
  Main Flask monolith.

- models.py
  Student, Faculty, Attendance models.

- extensions.py
  Shared SQLAlchemy instance.

- static/images/users/
  Face image storage.

---

## Current Face Recognition Flow

1. Load images
2. Generate encodings
3. Webcam stream
4. Face matching
5. Save attendance

---

## Technical Debt

- Blocking loops
- Recomputed encodings
- Plaintext passwords
- Hardcoded SQLite path
- Business logic in routes