# DentalNet IQ — Security Posture

## Core Principle: PHI-Free By Design

DentalNet IQ is intentionally architected to never require, accept, or store Protected Health Information (PHI).

### What the tool needs to answer a routing question:
- Payor name (e.g., "MetLife") — not PHI
- Plan type (e.g., "PDP Plus") — not PHI  
- State — not PHI
- Practice's contract list — not PHI

### What the tool explicitly does NOT need:
- ❌ Patient name
- ❌ Member ID
- ❌ Date of birth
- ❌ Social Security Number
- ❌ Claim number
- ❌ Any patient-identifying information

This is a **routing intelligence tool** — it answers "which network path will this claim take?" based on payor + plan type alone. The patient triggers the need for the lookup; the lookup itself contains zero patient data.

## Current Architecture (Local MVP)
- Runs entirely on localhost — no data transmitted
- Stateless queries — nothing persisted
- No database of patient records
- No HIPAA exposure

## SaaS Architecture (When Deployed)
- HTTPS required, no exceptions
- Stateless API — queries not logged or stored
- Role-based authentication
- BAA available but lightweight — tool processes no PHI
- Audit logs track access (who queried), not query content

## Selling Point
**"No BAA headache."** DSO compliance teams can deploy DentalNet IQ without a lengthy BAA negotiation because the tool never touches patient data. Payor relations staff can use it freely without HIPAA training requirements for the tool itself.

This is a **competitive advantage** — every competing solution that requires patient data creates compliance friction. We eliminate that entirely.
