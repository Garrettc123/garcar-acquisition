import boto3
import csv
import json
import os
from datetime import datetime

REGION = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
STAGE_MODE = os.environ.get('STAGE_MODE', 'all')
FROM_EMAIL = 'garrett@garcarenterprise.com'

STAGES = {
    1: {
        'subject': 'Quick question about your projects — Garcar Enterprise',
        'body': """Hi {name},

My name is Garrett Carroll — I run Garcar Enterprise out of Grandview, TX.

We build AI-powered systems for contractors in DFW that handle lead qualification, follow-up, and proposal generation automatically — so your team focuses on the work, not the admin.

Are you currently using any software to manage incoming leads or generate estimates?

Either way, I'd love to hear how things are going for you. Happy to share what we've built for similar {type} companies in the area.

Best,
Garrett Carroll
Garcar Enterprise
Grandview, TX
"""
    },
    2: {
        'subject': 'Following up — AI tools for {name}',
        'body': """Hi {name},

Just circling back on my note from earlier this week.

We recently helped a roofing company in the DFW area cut their estimate turnaround from 3 days to under 4 hours using our AI proposal system — no extra staff required.

If that sounds interesting, I can walk you through a 15-minute demo this week. No pitch, just a look at the system.

Would Wednesday or Thursday work for a quick call?

Garrett Carroll
Garcar Enterprise
"""
    },
    3: {
        'subject': 'Last note — Garcar Enterprise',
        'body': """Hi {name},

I'll keep this short — I've reached out a couple of times about AI tools built specifically for {type} companies in DFW.

If the timing isn't right, no problem at all. If you ever want to see how we're helping local contractors close more jobs with less overhead, just reply and I'll set something up.

Appreciate your time.

Garrett Carroll
Garcar Enterprise
garrett@garcarenterprise.com
"""
    }
}

def load_leads(path='dfw_lead_list.csv'):
    leads = []
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            leads.append(row)
    return leads

def load_log(path='sent_log.json'):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}

def save_log(log, path='sent_log.json'):
    with open(path, 'w') as f:
        json.dump(log, f, indent=2)

def send_email(ses, to_email, subject, body):
    try:
        ses.send_email(
            Source=FROM_EMAIL,
            Destination={'ToAddresses': [to_email]},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': body}}
            }
        )
        print(f'  ✅ Sent to {to_email}')
        return True
    except Exception as e:
        print(f'  ❌ Failed {to_email}: {e}')
        return False

def run():
    ses = boto3.client('ses', region_name=REGION)
    leads = load_leads()
    log = load_log()
    now = datetime.utcnow().isoformat()
    sent_count = 0

    for lead in leads:
        name = lead['name']
        email = lead['email']
        lead_type = lead['type']

        if not email:
            print(f'  SKIP {name} — no email')
            continue

        current_stage = log.get(name, {}).get('stage', 0)
        next_stage = current_stage + 1

        if next_stage > 3:
            print(f'  DONE {name} — all stages sent')
            continue

        if STAGE_MODE != 'all' and STAGE_MODE != f'only_stage_{next_stage}':
            print(f'  SKIP {name} — stage {next_stage} not in mode {STAGE_MODE}')
            continue

        stage_data = STAGES[next_stage]
        subject = stage_data['subject'].format(name=name, type=lead_type)
        body = stage_data['body'].format(name=name, type=lead_type)

        print(f'Sending Stage {next_stage} to {name} <{email}>')
        success = send_email(ses, email, subject, body)

        if success:
            log[name] = {'stage': next_stage, 'last_sent': now, 'email': email}
            sent_count += 1

    save_log(log)
    print(f'\nDone. Sent {sent_count} emails.')

if __name__ == '__main__':
    run()
