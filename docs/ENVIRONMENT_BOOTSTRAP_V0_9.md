# Environment Bootstrap v0.9

## Runtime pins

Current verified top-level pins at artifact generation time:
- `pydantic-ai==2.63.0`
- `pydantic-ai-harness==0.63.0`

Harness is still a 0.x package; exact versions must be captured for every validation run.

## Bootstrap philosophy

1. create isolated virtual environment;
2. upgrade pip tooling;
3. install exact top-level pins;
4. attempt hashed transitive lock generation when `uv` is available;
5. capture environment evidence;
6. run no-tool probes.

If a hashed lock is unavailable, the v1 release gate remains blocked.
