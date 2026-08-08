# Governance Framework Diagnostic: The Fuman Manifesto

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Type: Thought Experiment](https://img.shields.io/badge/Type-Thought_Experiment-blue.svg)](#status)
[![Status: Public Diagnostic Edition](https://img.shields.io/badge/Status-Public_Diagnostic_Edition-green.svg)](#status)
[![Version: 1.6.0](https://img.shields.io/badge/Version-1.6.0-2E6696.svg)](CHANGELOG.md)

**A satirical stress test for determining whether a governance framework constrains real execution or merely documents its own operation.**

*Developed by FERZ, Inc.*

## Status

This repository contains a diagnostic thought experiment. It is not a standard, policy proposal, product specification, or FERZ offering. No human-avian integration program exists, is planned, or is endorsed by FERZ, Inc.

**Current version:** 1.6.0, Public Diagnostic Edition, August 2026.

**TL;DR:** The Fuman Manifesto is internally elaborate and operationally hollow. It contains metrics, classifications, declarations, audit duties, incident procedures, and extensive records. It does not establish that a specific effect-bearing action was authorized before execution.

## Diagnostic Premise

Governance form can be complete while governance function remains absent. A framework may define its own terms precisely, evaluate itself consistently, and generate extensive evidence without connecting those mechanisms to external reality or enforceable authority.

The Fuman Manifesto reproduces recognizable features of governance frameworks in a fictional domain: human-bird flight hybrids. The domain removes disputes about technical feasibility and leaves the framework's structure exposed for inspection.

Version 1.6.0 distinguishes three separate questions:

| Test | Question | What failure means |
|---|---|---|
| **Grounding Test** | Do the framework's terms and measurements connect to states of the world that exist independently of the framework? | Internal definitions validate other internal definitions. |
| **Authorization Boundary Test** | Must every effect-bearing action cross a fail-closed, pre-execution authorization boundary before release? | Monitoring and procedure do not constrain execution. |
| **Reconstruction Test** | Can an independent party reconstruct the authorization verdict from the governed inputs, policy state, authority state, and recorded outcome without access to the governed system? | The record describes execution but does not establish permission. |

A framework can pass the Grounding Test and still fail the Authorization Boundary and Reconstruction Tests.

## The Instrument

The Manifesto contains:

- A canonical metric, CAST, with a formal measurement protocol and operational thresholds
- An unintended-descent severity taxonomy, UD-1 through UD-4
- Vertical Nonconformance categories with reporting windows
- Declarations, licenses, audit artifacts, retention periods, and escalation procedures
- Stakeholder representation, dispute resolution, insurance tiers, and enforcement consequences
- A canonical incident analysis tracing one event through the entire framework

These mechanisms create substantial observability. They do not create an authorization artifact.

## Observability Versus Authorization

The Manifesto's First Axiom states that governance creates traceability. Within the satire, that statement is intentionally incomplete.

A record of execution may explain what happened without establishing that the action was permitted before it happened. Logs, audit trails, declarations, and post-event sanctions are not substitutes for a pre-execution authorization verdict.

For effect-bearing actions, a serious governance framework should establish:

1. A non-bypassable runtime authorization boundary before execution
2. Fail-closed treatment of missing, unresolved, or invalid authority
3. An authorization artifact binding the proposed action, governed inputs, policy state, authority state, time, and verdict
4. An independently reconstructable verdict

## How to Use the Diagnostic

1. Select a governance framework or control system.
2. Map its metrics, classifications, approvals, audit requirements, and execution controls to the Manifesto's equivalents.
3. Apply the Grounding, Authorization Boundary, and Reconstruction Tests.
4. Identify which controls constrain execution and which controls only produce evidence after execution.
5. Record any point at which absence of permission can become tacit permission.

The central question is:

> **What does your framework provide that the Fuman Manifesto does not?**

If the answer is limited to real subject matter, better metrics, more complete logs, or more credible institutions, the authorization question remains unresolved.

## Repository Contents

| File | Description |
|---|---|
| [`THE_FUMAN_MANIFESTO_v1.6.0.pdf`](THE_FUMAN_MANIFESTO_v1.6.0.pdf) | Current public diagnostic edition |
| [`COMPANION_NOTE_v1.6.0.pdf`](COMPANION_NOTE_v1.6.0.pdf) | Status, intent, and diagnostic interpretation |
| [`THE_FUMAN_MANIFESTO_v1.5.0.pdf`](THE_FUMAN_MANIFESTO_v1.5.0.pdf) | Preserved historical edition |
| [`sources/`](sources/) | Editable v1.6.0 diagnostic and companion-note sources |
| [`scripts/build_v1_6.py`](scripts/build_v1_6.py) | Reproducible PDF build |
| [`scripts/validate_release.py`](scripts/validate_release.py) | Release validation checks |
| [`CHANGELOG.md`](CHANGELOG.md) | Version history |
| [`CITATION.cff`](CITATION.cff) | Machine-readable citation metadata |
| [`LICENSE`](LICENSE) | CC BY 4.0 license notice |

## Build and Validation

```bash
python3 -m pip install -r requirements.txt
python3 scripts/build_v1_6.py
python3 scripts/validate_release.py
```

The v1.6.0 build preserves the v1.5.0 artifact as its historical base, removes superseded draft markings, replaces the unused page 5 with the diagnostic note, updates the cross-domain analysis, and generates the companion note from Markdown source.

## Citation

```text
FERZ, Inc. (2026). The Fuman Manifesto: A Governance Framework Diagnostic
(Version 1.6.0). https://github.com/edmeyman/governance-diagnostics
```

## License

CC BY 4.0. Attribution is required.

## About FERZ

FERZ develops deterministic authorization infrastructure for AI systems operating in regulated environments. Its work separates observability from authorization and places a fail-closed authorization boundary before effect-bearing execution.

https://ferz.ai
