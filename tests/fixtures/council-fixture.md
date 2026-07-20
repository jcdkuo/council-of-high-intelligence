---
name: council-fixture
description: "Fixture council member for converter tests."
model: sonnet
color: orange
tools: ["Read", "Grep", "Glob", "Bash", "WebSearch", "WebFetch"]
council:
  figure: Fixture
  domain: "Converter regression testing"
  polarity: "Catches serialization drift"
  polarity_pairs: ["socrates", "feynman"]
  triads: ["debugging"]
  provider_affinity: ["anthropic"]
---

## Identity

Fixture body used to assert the converter preserves everything below the
frontmatter verbatim. Do not edit this text without updating the test.
