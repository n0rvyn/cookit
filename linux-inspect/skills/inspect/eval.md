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
- "inspect profile web1"
- "show host profiles"
- "suppress finding SEC-001-1 on web1"

## Negative Trigger Tests
- "inspect the code"
- "review this pull request"
- "check the build status"
- "scan my domain for intel"

## Output Assertions
- [ ] Correctly identifies user intent (setup/run/status/report/config/profile/help)
- [ ] Checks for config file existence before running
- [ ] Prompts for setup if config missing
- [ ] Setup creates profiles/ directory alongside reports/
- [ ] Setup verifies python3 + PyYAML availability
- [ ] Run uses collector.sh (single SSH per host), not per-check SSH
- [ ] Run creates profile from discovery for first-run hosts
- [ ] Run updates discovery for hosts with existing profiles
- [ ] Run dispatches analysis agents with structured JSON, not raw text
- [ ] Run dispatches profile-evolver after analysis
- [ ] Non-sensitive proposals auto-applied; sensitive proposals require confirmation
- [ ] Report includes delta section (new/resolved findings)
- [ ] Report includes profile evolution summary
- [ ] Profile intent lists/shows/manages host profiles correctly
- [ ] Suppress command asks for reason and expiry via AskUserQuestion
