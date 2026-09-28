# Trap index

Which extractor trap each dev/test transcript is built around. Each of the 8 traps appears exactly once; `dev_5` and `test_5` are clean control transcripts with no embedded trap.

| Transcript | Trap |
|---|---|
| dev_1 | Two people both offer to take the same task, only one is confirmed (Owen and Felix both offer to build the dashboard demo; Felix is confirmed, Owen is not the owner) |
| dev_2 | A deadline that changes during the meeting, last date stated wins (compliance report due date moves 22nd → 18th → 20th; 20th is correct) |
| dev_3 | Vague timing only, no calendar date (password reset testing "soon, probably early next week"; billing sync "after we hear back from the vendor"; FAQ update "sometime after the launch settles down") |
| dev_4 | A conditional task, excluded unless the condition is stated as met (contract draft conditional on pricing acceptance, which happens mid-meeting so it's included; onboarding materials conditional on a signature that never happens, so it's excluded) |
| dev_5 | None (clean control transcript) |
| test_1 | A task assigned to one person, then reassigned to another (false-positive report starts with Kian, is explicitly moved to Vera) |
| test_2 | Someone volunteers another person who never accepts (Ingrid and Callum float Dana for the accessibility audit; Dana never confirms, so the task has no owner) |
| test_3 | A task that gets cancelled (the warehouse audit is scheduled, then explicitly called off: "forget the audit for now") |
| test_4 | An item someone says is already done (manuscript formatting, venue booking, and social media teasers are all reported as already complete, and excluded) |
| test_5 | None (clean control transcript) |
