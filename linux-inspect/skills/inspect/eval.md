# inspect Eval

## Trigger Tests
- "inspect my servers"
- "run a security audit on my hosts"
- "inspect setup"
- "linux inspection"
- "check my servers for vulnerabilities"
- "batch inspect hosts"
- "inspect config"
- "host security check"

## Negative Trigger Tests
- "inspect the code"
- "review this pull request"
- "check the build status"
- "scan my domain for intel"

## Output Assertions
- [ ] Correctly identifies user intent (setup/run/status/report/config/help)
- [ ] Checks for config file existence before running
- [ ] Prompts for setup if config missing
- [ ] Setup offers three host definition methods (Quick / Detailed / Ansible file)
- [ ] Quick path accepts comma-separated hostnames without asking per-host connection details
- [ ] Quick path asks about sudo as a single follow-up question
- [ ] Detailed path rejects 10+ hosts and redirects to Ansible file path
- [ ] Tests SSH connectivity after setup completes
- [ ] Uses defaults section values for missing per-host fields in connectivity test
