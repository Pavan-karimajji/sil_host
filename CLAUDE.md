# sil_host

The SIL integration host — builds and runs component SIL DLLs together in one
process. Not a shippable ADAS component.

## Role

Proves that component C-API DLLs (`df` + others) can be composed and run in one
process. The host owns config and time; components stay host-agnostic.

## Local constraints

- **The host owns time and data:** it loads config, serializes protobuf at each
  boundary, and calls each DLL's `Exec(handle, dtS, …)` — the DLLs never read a
  clock or disk (R-SIL-1).
- Links component C-API DLLs; wire new components via
  `../../.claude/workflows/sil_integration.md`.
- `perception-core` is **not wired in yet** (no real Conan package — R-SIL-2).
  `--local` leaves editables registered. Header `COMPONENT: SIL`.

## AI operational layer — root-canonical

Part of `1v-superproject`. Cross-cutting rules/skills/templates/workflows live
once at the superproject root `.claude/` (spec:
`docs/ai_operational_layer_spec.md`). Load `../../.claude/rules/*` + the matching
`skills/*`; do not duplicate them here. This file holds only what is local to
`sil_host`.
