# Offline validator runtime backup

`wheelhouse/` contains the pinned validator dependencies for this user's current contest machine:
macOS arm64 with Python 3.9.6. It is a recovery source, not an active environment.

The active environment is `~/.codex/cumcm-national-paper-runtime/validator-v25`. Run
`scripts/contest_doctor.py --strict` before relying on it. If the machine, architecture, or Python
version changes, the doctor must fail; download a new compatible wheelhouse instead of forcing these
wheels to install.
