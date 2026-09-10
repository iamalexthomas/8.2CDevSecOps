"""Wait for this scan to finish, then print and save real SonarCloud results."""
import json
import os
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE = 'https://sonarcloud.io'
output = Path('sonar-results')
output.mkdir(exist_ok=True)
report = dict(line.split('=', 1) for line in
              Path('.scannerwork/report-task.txt').read_text().splitlines() if '=' in line)


def api(path, params, filename):
    request = Request(BASE + path + '?' + urlencode(params),
                      headers={'Authorization': 'Bearer ' + os.environ['SONAR_TOKEN']})
    with urlopen(request, timeout=60) as response:
        print(f'SonarCloud API {path}: HTTP {response.status}', flush=True)
        data = json.load(response)
    (output / filename).write_text(json.dumps(data, indent=2) + '\n')
    return data


# The report upload and the server processing are separate steps.
for attempt in range(60):
    task = api('/api/ce/task', {'id': report['ceTaskId']}, 'processing.json')['task']
    print('Analysis processing:', task['status'], flush=True)
    if task['status'] == 'SUCCESS':
        break
    if task['status'] in {'FAILED', 'CANCELED'}:
        raise SystemExit('SonarCloud could not process this analysis.')
    time.sleep(5)
else:
    raise SystemExit('SonarCloud analysis processing timed out. Check the dashboard.')

gate = api('/api/qualitygates/project_status', {'analysisId': task['analysisId']}, 'quality-gate.json')
print('Quality gate:', gate['projectStatus']['status'])
metrics = api('/api/measures/component', {
    'component': report['projectKey'],
    'metricKeys': 'bugs,vulnerabilities,code_smells,security_hotspots,coverage,ncloc'
}, 'measures.json')
for measure in metrics['component'].get('measures', []):
    print(measure['metric'] + ': ' + measure.get('value', 'not available'))
issues = api('/api/issues/search', {'componentKeys': report['projectKey'], 'ps': 20, 'resolved': 'false'}, 'issues.json')
print('First issues reported by SonarCloud:')
for issue in issues.get('issues', []):
    print(f"- {issue.get('severity', '')}: {issue['message']} ({issue['component']}, line {issue.get('line', '?')})")
print('Dashboard:', report['dashboardUrl'])
print('A completed scan does not mean that the vulnerable application passed its quality gate.')
