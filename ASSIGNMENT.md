# SIT753 7.1C - Jenkins and DevSecOps

This repository contains the supplied `snyk-labs/nodejs-goof` application and three Jenkins pipeline scripts. The application is intentionally vulnerable. It is used here for a security scanning exercise.

## Pipeline files

| File | Task | What it does |
| --- | --- | --- |
| `Jenkinsfile.mock` | Part 1 Task 1 | Prints seven stages, their tasks and suitable tools. |
| `Jenkinsfile` | Part 1 Task 2 | Checks out the project, installs dependencies, runs the supplied test and coverage commands, and runs npm audit. |
| `Jenkinsfile.email` | Part 2 Task 2 | Adds an email with the status and logs after the test and security scan stages. |

The selected Part 2 option is **Email Notification**. No SonarCloud extension is required. Naming SonarQube as a possible tool in the mock pipeline does not mean the SonarCloud option has also been completed.

## Part 1 Task 1: stages and tools

The mock pipeline represents a possible Java application workflow. The separate npm exercise uses the supplied Node.js application. The seven mock stages only use `echo`; they do not run Maven, provision AWS servers or deploy the vulnerable application.

| Stage | Task and reason | Possible tool |
| --- | --- | --- |
| Build | Compile the source code and package it so it can be released. | Apache Maven |
| Unit and Integration Tests | Check individual methods, then check that components work together. | JUnit with Maven Surefire and Failsafe |
| Code Analysis | Find bugs, code smells and coding rule violations before release. | SonarQube and its Jenkins scanner plugin |
| Security Scan | Check libraries used by the project for known vulnerabilities. | OWASP Dependency-Check and its Jenkins plugin |
| Deploy to Staging | Copy the package to a server used for checking the release. | Ansible and an AWS EC2 staging instance |
| Integration Tests on Staging | Test APIs and connected services in a production-like environment. | Postman collections run with Newman |
| Deploy to Production | Release the checked package to the production server. | Ansible and an AWS EC2 production instance |

SonarQube can report problems in source code. Dependency-Check looks for known problems in third-party libraries. These checks cover different risks, so both are useful.

## Automatic builds

Each script uses `pollSCM('* * * * *')`. Jenkins checks for a new commit every minute. This is polling, so there can be a short delay after a push. A webhook is not needed. A first manual build registers the pipeline trigger. Later demonstrations should show `Started by an SCM change` in the console, with the corresponding new GitHub commit.

Configure each Jenkins job as **Pipeline script from SCM**, using Git, the `main` branch and the relevant script path. Leave **Lightweight checkout** unchecked. This allows the mock job to record the repository checkout used to read its script, while its seven named stages still only print messages.

## Part 1 Task 2: the real scan

The five stages use these tools:

1. **Checkout - Git:** downloads the application from GitHub.
2. **Install Dependencies - npm:** installs the packages listed by the project.
3. **Run Tests - npm and Snyk:** `npm test` invokes the upstream `snyk test` script.
4. **Generate Coverage Report - npm script runner:** runs the command from the task sheet. The supplied project has no `coverage` script, so this reports an error and continues. Istanbul/nyc would be a suitable coverage tool if a working test suite were added.
5. **NPM Audit - npm audit:** checks dependencies against security advisories.

The upstream revision used for this exercise is `add14ba59e98240d9e00a235dd7d42cd61ae9912`. Its `npm test` requires Snyk authentication. The task sheet's `|| true` allows the demonstration to continue after these errors. It does not fix the error, create a coverage report or prove that the tests passed. The npm audit stage can run without a Snyk account.

`npm audit` is a form of Software Composition Analysis (SCA). It checks dependencies; it is not a complete scan of the application's source code or running website. A finding should be reviewed using its package name, severity, affected version range and advisory link. Vulnerability totals can change as the registry adds advisories.

## Part 2: email notifications

The email pipeline uses Jenkins **Email Extension** and an SMTP server configured under **Manage Jenkins > System > Extended E-mail Notification**. Enter the recipient in the `NOTIFY_EMAIL` build parameter.

This local setup uses Mailpit as the SMTP server at `127.0.0.1:1025`, with an inbox at `http://localhost:8025`. The recipient is stored in Jenkins rather than in this public repository. The default parameter `$DEFAULT_RECIPIENTS` uses that configured address. Jenkins sends real SMTP messages to this test inbox, where their bodies and attachments can be opened. Mailpit captures the messages locally even if they are addressed to a Gmail account. This does not deliver them to Gmail or Outlook. An external inbox would require its provider's SMTP settings and credentials in Jenkins.

It sends one message after `Run Tests` and one after `NPM Audit (Security Scan)`. Each message contains the job name, build number, stage result, command exit code and build URL. It attaches the relevant stage log and the current Jenkins console log. Stage logs are also saved as build artifacts.

The script uses `returnStatus: true` to keep the real command exit code. If the command fails, `catchError` marks the stage as failed and allows the demonstration pipeline to continue. The overall build can finish successfully while a stage has failed. The email reports that failure, and the attached log explains whether it was a vulnerability finding or an execution error. This is a demonstration choice that follows the task sheet's continue-on-error behaviour. A real release should use suitable failure rules before deployment.

## Connection to the notes

Security checks happen during the pipeline, which gives earlier feedback. This is the main DevSecOps idea used here. Developers, testers, operations staff and security staff share responsibility for responding to problems. Git records changes, Jenkins repeats the checks, and email makes the results easier to notice.

Staging is useful because it gives a place to test the application before release. The cloud computing and Infrastructure as Code notes explain how environments can be managed consistently. Monitoring gives feedback after deployment; it is background for this exercise, rather than an extra stage required by the task sheet.

## Sources

- Supplied task sheet: `SIT753-7.1C.pdf`, pages 2-4 and 8-10.
- Supplied Week 7 screenshots: Jenkins and Git; Cloud Computing; Infrastructure as Code; Monitoring; Introduction to DevSecOps; What is DevSecOps; Application Security Testings in DevSecOps; DevSecOps Tools; DevSecOps and Australia Regulatory.
- [Jenkins Pipeline syntax](https://www.jenkins.io/doc/book/pipeline/syntax/) - stages, polling and error handling.
- [SonarQube integration with Jenkins](https://docs.sonarsource.com/sonarqube-server/2026.1/analyzing-source-code/ci-integration/jenkins-integration) - a possible source code analysis tool.
- [OWASP Dependency-Check Jenkins plugin](https://plugins.jenkins.io/dependency-check-jenkins-plugin/) - a possible dependency scan tool.
- [npm audit documentation](https://docs.npmjs.com/cli/v11/commands/npm-audit/) - dependency findings and exit codes.
- [Email Extension plugin](https://plugins.jenkins.io/email-ext/) and [pipeline step reference](https://www.jenkins.io/doc/pipeline/steps/email-ext/) - SMTP settings, messages and log attachments.
- [Original nodejs-goof repository](https://github.com/snyk-labs/nodejs-goof) - supplied vulnerable application.
- [Mailpit documentation](https://mailpit.axllent.org/docs/) - local SMTP test inbox and attachments.

Documentation checked on 10 September 2026.
