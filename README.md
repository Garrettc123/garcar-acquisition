# Garcar Auto Acquisition — DFW Contractors

Automated cold outreach engine. Runs Mon/Wed/Fri 9AM CDT via GitHub Actions.
No servers. No manual work. AWS SES for email delivery.

## Files
| File | Purpose |
|------|---------|
| auto_acquisition.py | Email sender (AWS SES) |
| dfw_lead_list.csv | 10 DFW contractor leads |
| sent_log.json | Tracks sequence stage per lead |
| .github/workflows/auto_acquisition.yml | GitHub Actions trigger |

## Secrets Required
Add in: Settings → Secrets → Actions
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

## Trigger Manually
Actions tab → Bootstrap + Auto Acquisition → Run workflow

## Lead Stages
| Stage | Content |
|-------|---------|
| 1 | Introduction — AI tools for contractors |
| 2 | Follow-up — demo offer |
| 3 | Final note — soft close |

All stages auto-advance per lead. sent_log.json committed back to repo after every run.
