# Napkin

## Corrections
| Date | Source | What Went Wrong | What To Do Instead |
|------|--------|----------------|-------------------|
| 2026-02-07 | self | Used exec_command to run apply_patch instead of apply_patch tool | Use apply_patch tool directly for patches |
| 2026-02-07 | self | Repeatedly used exec_command to run apply_patch despite warning | Always use apply_patch tool for patches |

## User Preferences
- (accumulate here as you learn them)

## Patterns That Work
- 2026-02-07: With permissions set to full access and Docker running, MinIO health check and ParquetReader validation succeeded locally.

## Patterns That Don't Work
- 2026-02-07: `python3 backend/scripts/load_domo.py --dataset ...` failed due to DNS resolution for `api.domo.com` in this environment. If ETL is required, run in an environment with outbound DNS/network access.
- 2026-02-07: MinIO access from this environment failed (`http://localhost:9000` PermissionError). Run ParquetReader validation in the user environment where MinIO is reachable.

## Domain Notes
- (project/domain context that matters)
