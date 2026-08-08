# v1.6.0 Sources

The repository does not contain the original editable source used to export v1.5.0. Version 1.6.0 therefore uses the preserved v1.5.0 PDF as its historical base and applies controlled, reproducible revisions through `scripts/build_v1_6.py`.

Editable source is provided for all new v1.6.0 material:

- `DIAGNOSTIC_NOTE_v1.6.0.md`
- `COMPANION_NOTE_v1.6.0.md`

The build script removes superseded status markings from the base PDF, inserts the diagnostic note, applies the terminology and incident-analysis corrections, updates metadata, and generates the companion note.

Run the build and validation from the repository root:

```bash
python3 -m pip install -r requirements.txt
python3 scripts/build_v1_6.py
python3 scripts/validate_release.py
```
