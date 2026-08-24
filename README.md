# Random Password Generator (Advanced Tier)

**Track:** Python Programming
**Task:** OIBSIP/Python-Task3-PasswordGenerator/

## Overview
A desktop GUI application built with `tkinter` that generates cryptographically
secure, random passwords based on user-defined criteria. Built for the Oasis
Infobyte Summer Internship Program (SIP), Python Programming track, Task 3 —
Advanced Tier.

## Features
- GUI with a length slider (8–64 characters) and checkboxes for character types
- Uses Python's `secrets` module (not `random`) for cryptographically secure generation
- Guarantees at least one character from every selected type
- Visual strength indicator (Weak / Medium / Strong) with a progress bar
- One-click "Copy to Clipboard" via `pyperclip`
- Optional exclusion of ambiguous characters (`0`, `O`, `l`, `1`, `I`, etc.)
- Session-only history of the last 5 generated passwords (never written to disk,
  for security)

## Tech Stack
- Python 3
- `tkinter` / `ttk` — GUI
- `secrets` — cryptographically secure random generation
- `pyperclip` — clipboard integration

## Setup
```bash
pip install pyperclip
python password_generator.py
```

## Security Notes
- Passwords are generated using `secrets`, which is suitable for
  security-sensitive applications (unlike the `random` module).
- Generated passwords are held only in memory for the duration of the
  session and are never written to a file or database.

## Demo
See the linked LinkedIn demo video for a full walkthrough (per OIBSIP
submission requirements: title card with name, track, and task title,
followed by a live functional demo).
