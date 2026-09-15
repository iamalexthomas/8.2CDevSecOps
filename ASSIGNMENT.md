# SIT753 Credit Task: Jenkins and DevSecOps

This repository contains the task-sheet sample application from
[snyk-labs/nodejs-goof](https://github.com/snyk-labs/nodejs-goof) and three Jenkins pipelines.
The application deliberately contains vulnerabilities for security demonstrations.

| Jenkins job | Script | Purpose |
| --- | --- | --- |
| SIT753-1-Mock | Jenkinsfile.mock | Seven stages printing task descriptions and tools |
| SIT753-2-DevSecOps | Jenkinsfile.basics | Original five-stage npm security-scan exercise |
| SIT753-3-Email | Jenkinsfile.email | Test and audit status notifications with attached logs |

Use **Pipeline script from SCM**, Git, branch `*/main`, with the script path shown above.
The mock and email jobs poll Git every minute. Run each once manually to initialise
the Jenkinsfile trigger, then push a change to `DEMO_COMMITS.md` and wait for polling.
The subsequent build must show **Started by an SCM change**. No webhook is needed.

## Agent prerequisites

Linux with Git, Node.js and npm. Jenkins needs the Pipeline, Git, Email Extension,
and Pipeline Stage View plugins. Maven, SonarQube, Ansible, Selenium and
Dependency-Check are named examples in the mock and need not be installed.
The mock illustrates a Java application; the other two jobs scan the Node.js sample.

## Email setup

Configure **Manage Jenkins > System > Extended E-mail Notification** using the
sender's SMTP host, port, encryption and Jenkins-stored credential. Configure
the system administrator sender address too. Set a global environment variable
`DEFAULT_NOTIFY_EMAIL` to the chosen recipient, or enter `NOTIFY_EMAIL` when
building the email job. Do not put account passwords in Git.

The email job sends after **Run Tests** and **NPM Audit (Security Scan)**.
Each message contains the individual command's SUCCESS/FAILURE status and attaches
the stage log, its exit-code file, and Jenkins' console output up to that point.
Nonzero exits mark the build UNSTABLE while letting later stages run.
Successful orchestration is not a claim that the vulnerable application is secure.

## Upstream limitations retained from the task-sheet example

At upstream commit `add14ba59e98240d9e00a235dd7d42cd61ae9912`:

- `npm test` invokes `snyk test`, which may require Snyk authentication. An
  authentication error is a tool failure, not a completed vulnerability assessment.
- No `coverage` script exists. `npm run coverage` therefore reports a missing
  script; no coverage percentage is claimed or invented.
- `npm audit` is the mandatory npm vulnerability scan and can run independently
  of Snyk authentication. Its findings change as advisories and dependency versions change.
- The basics pipeline retains the task's `|| true` behaviour. The email pipeline
  captures the original exit codes instead so notification statuses stay accurate.

Part 2 selects the **Email Notification** option only.
