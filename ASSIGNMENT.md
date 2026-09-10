# SIT753 7.1C - Jenkins and DevSecOps

This repository contains the supplied `snyk-labs/nodejs-goof` application and the Jenkins pipeline scripts. The application is intentionally vulnerable. It is used here for a security scanning exercise.

## Pipeline files

| File | Task | What it does |
| --- | --- | --- |
| `Jenkinsfile.mock` | Part 1 Task 1 | Prints seven stages, their tasks and suitable tools. |
| `Jenkinsfile` | Part 1 Task 2 | Checks out the project, installs dependencies, runs the supplied test and coverage commands, and runs npm audit. |
| `Jenkinsfile.sonarcloud` | Part 2 Task 1 | Keeps the five npm stages and adds source-code analysis with SonarCloud. |
| `sonar-project.properties` | SonarCloud setup | Defines the project, organization, sources, exclusions and optional LCOV report path. |
| `sonar-results.py` | Scan results | Waits for processing and prints the actual API responses and findings. |

The selected Part 2 option is **SonarCloud.io** (now called SonarQube Cloud). The previous email job is retired. Only the SonarCloud extension is used for the third video.

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

## Part 2: SonarCloud analysis

`Jenkinsfile.sonarcloud` keeps the five stages from Part 1 Task 2 and adds **SonarCloud Analysis**. It downloads the Linux SonarScanner CLI ZIP from SonarSource, extracts it and runs the scanner from the repository folder. Git, npm, curl, unzip, Python 3 and the scanner are the tools used in this pipeline.

Create a SonarCloud project bound to this GitHub repository and copy its exact project key and organization key into `sonar-project.properties`. Disable SonarCloud Automatic Analysis for this project because Jenkins performs the analysis. The free plan's main-branch analysis is sufficient for this exercise.

Save the generated token in a private local text file outside this repository, then add it to Jenkins as **Secret text**, with ID **SONAR_TOKEN**. The task sheet calls this "Secret key". The `withCredentials` block makes the secret available only to the analysis stage. SonarScanner reads the environment variable directly; no actual token belongs in the properties file or GitHub.

The properties file sets the LCOV path to `coverage/lcov.info`. The supplied application has no coverage script, so that report is currently absent. SonarCloud can still analyse the source code; an absent report does not establish test coverage.

After the upload, `sonar-results.py` waits for the server to finish processing the task. It prints real HTTP response codes, the quality gate, available measures and the first 20 unresolved issues, and saves the JSON responses as Jenkins artifacts. HTTP 200 means the API request succeeded. The separate processing status must be SUCCESS before the returned results can be treated as this completed analysis. A quality gate failure is a finding, not an upload failure.

SonarCloud performs Static Application Security Testing (SAST) and code quality checks. This complements npm audit, which checks dependency vulnerabilities. Show an actual finding, its source location and the analysis time in the video. Do not invent findings or say the application is safe because Jenkins finished successfully.

## Connection to the notes

Security checks happen during the pipeline, which gives earlier feedback. This is the main DevSecOps idea used here. Developers, testers, operations staff and security staff share responsibility for responding to problems. Git records changes, Jenkins repeats the checks, and SonarCloud makes code issues visible in a dashboard.

Staging is useful because it gives a place to test the application before release. The cloud computing and Infrastructure as Code notes explain how environments can be managed consistently. Monitoring gives feedback after deployment; it is background for this exercise, rather than an extra stage required by the task sheet.

## Sources

- Supplied task sheet: `SIT753-7.1C.pdf`, pages 2-7 and 9-10.
- Supplied Week 7 screenshots: Jenkins and Git; Cloud Computing; Infrastructure as Code; Monitoring; Introduction to DevSecOps; What is DevSecOps; Application Security Testings in DevSecOps; DevSecOps Tools; DevSecOps and Australia Regulatory.
- [Jenkins Pipeline syntax](https://www.jenkins.io/doc/book/pipeline/syntax/) - stages, polling and error handling.
- [SonarQube integration with Jenkins](https://docs.sonarsource.com/sonarqube-server/2026.1/analyzing-source-code/ci-integration/jenkins-integration) - a possible source code analysis tool.
- [OWASP Dependency-Check Jenkins plugin](https://plugins.jenkins.io/dependency-check-jenkins-plugin/) - a possible dependency scan tool.
- [npm audit documentation](https://docs.npmjs.com/cli/v11/commands/npm-audit/) - dependency findings and exit codes.
- [Original nodejs-goof repository](https://github.com/snyk-labs/nodejs-goof) - supplied vulnerable application.

Documentation checked on 10 September 2026.

- [SonarScanner CLI](https://docs.sonarsource.com/sonarqube-cloud/analyzing-source-code/scanners/sonarscanner-cli) - official download and SONAR_TOKEN authentication.
- [SonarCloud Web API](https://docs.sonarsource.com/sonarqube-cloud/advanced-setup/web-api) - authenticated result requests.
- [Automatic analysis](https://docs.sonarsource.com/sonarqube-cloud/advanced-setup/automatic-analysis) - switch to CI-based analysis for Jenkins.
