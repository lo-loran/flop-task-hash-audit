# FLOP Task Hash Vector Audit

Independent offline audit of the public direct_rail_v1 fixture.

## Reproduce

Download the fixture from the pinned source commit:
curl -fL https://raw.githubusercontent.com/flop-labs/yellowpaper/70e691c/evidence/wire-format-v1.json -o /tmp/wire-format-v1.json

Run from this directory:
export FLOP_VECTOR_FIXTURE=/tmp/wire-format-v1.json
python3 verify_vector.py "$FLOP_VECTOR_FIXTURE"
python3 -m unittest -v test_verify_vector.py

## Scope

Checks task preimage, task hash, report-data binding, six individual task-hash input mutations, output-hash and report-data tampering, malformed JSON, missing sections, wrong-length hash fields, and out-of-range nonces. The suite contains 9 test methods: one positive test and eight negative test methods, including six task-hash mutation subtests.

This is an offline fixture audit. It does not execute the FLOP runtime, verify a production PoUI proof, or establish runtime enforcement.

Reference: FLOP Labs, Yellow Paper 0.5.0 draft, 2026, commit 70e691c.
The source LICENSE explicitly covers the specification text. The source JSON fixture is not bundled here.

## Attribution and licensing



The reference vector is maintained by FLOP Labs and is fetched from the public Yellow Paper repository at commit 70e691c. The upstream LICENSE explicitly covers the specification text; this package does not redistribute the vector and makes no claim about a separate license for it.



The audit code in this package is licensed under MIT. This project is an independent community tool, not an official FLOP Labs project, and its publication does not imply endorsement.
