# Generation Guardrails

## Safe generation
The generator may create:
- scaffold source files
- README/docs
- placeholder tests
- seed manifest
- builder handoff report

## Unsafe generation
The generator must not:
- fetch from the network
- mutate unrelated repo files
- write outside its temp workspace
- invent binary assets
