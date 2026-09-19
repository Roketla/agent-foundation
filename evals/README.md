# Evaluation records v0.3

`scripts/evaluate.py` reads a bounded JSON file (at most 2 MiB), validates it, and writes a JSON report. It performs no network calls and does not modify the input.

```sh
python3 scripts/evaluate.py report --input records.json
```

The input is an object with `schema_version: 1` and a `runs` array. A run uses this shape; evidence fields hold pointers such as artifact URLs or test-result IDs, never transcripts.

```json
{
  "run_id": "candidate-login-01",
  "case_id": "login",
  "variant": "candidate",
  "environment": "fixture-v1",
  "requested_model": "gpt-requested",
  "observed_model": "gpt-observed",
  "model_evidence": "run-metadata://candidate-login-01",
  "outcome": "accepted",
  "checks": [{"name": "login succeeds", "passed": true, "evidence": "test://login/01"}],
  "attempts": 1,
  "duration_seconds": 3.2,
  "input_tokens": 1200,
  "cached_input_tokens": 500,
  "output_tokens": 280,
  "human_interventions": 0,
  "evidence": ["artifact://candidate-login-01"]
}
```

All strings shown as identifiers or evidence pointers must be non-empty. `observed_model` and `model_evidence` may both be `null`; an observed model always needs its evidence pointer. Metrics may be `null` when unavailable, and cannot be negative. Token counts and interventions are integers. Cached input is a subset of input, so `cached_input_tokens <= input_tokens` and it is never added to total token volume. Accepted runs require at least one passing check; failed and blocked runs remain in totals.

The report groups runs by the exact `(case_id, environment)` pair. Each case reports baseline and candidate sample counts, outcomes, acceptance rates, attempts, complete-or-partial metric totals, observed-model state, and pairwise differences only when both sides have complete values. `unmatched` lists a missing variant. The report includes caveats: token totals are volume rather than money, and a single sample never proves an improvement.

Define acceptance before executing. Record the fixture commit, tool versions, skill
versions and model settings in the environment evidence. Compare the same task and
inputs; change one skill or routing policy at a time. Count failures and all attempts,
and retain independent verification evidence. Differences are raw totals, so unequal
sample counts cannot establish per-run efficiency. An observed model is the runtime's
recorded model, not the model's self-description or a routing recommendation.

CI only validates the deterministic implementation. Live pilots are manual and consume
the chosen engine's quota; keep raw transcripts in ignored `.local/`, never in fixtures.
Publish only reviewed, non-sensitive measurements and compact verification results.
