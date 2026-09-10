# Evidence provenance

These records were copied from
`codex/docs-review-baseline` at
`049514447781d77f73d8ec662e058bfc95363c08`. Their source path was
`docs/loom/dogfood/2026-09-01-docs-review-luna-controlled-experiment/`.

The two `run-*.json` files are the preserved outputs of two real Codex CLI
replays requesting `gpt-5.6-luna`. They record successful return codes, raw
responses, token usage, and elapsed time. They do not claim backend-attested
model identity. No new replay was substituted during this migration because
changing the model, prompt, input, or runtime would break the controlled
comparison.

## Migration integrity

- `README.md`: `b610fb92d2e7431f0abab0cf7c21a3f82225d9ace8627b688ed8a66cb5403f75`
- `corpus-manifest.json`: `6619f680c47fbc6cdcbbdc5fa3451c3eecfc8b2d1f538a7b5a4b2429f23a32a0`
- `input.txt`: `0e9a021e6dbfceaa4103a79fa2c672fcdad344c18cf890c3a05b3cb6de39cf84`
- `metrics.json`: `548bcf4adbef6f678fae3581d4604a5f52abde9537709226d584ccc425d747d0`
- `oracle.json`: `429ff2d9b3c64c98422b6dae0f413a44dad3bb8855c27bfd407b316dc6e68f9f`
- `prompt.txt`: `e9b154b6cb1c71e060795b935b4fc1861d9bc5feab9c397f6f4ca60c9da8bb8d`
- `run-1.json`: `12ee1d85550e48818a1a5d4557a7c94ccaa9009bc2e835895904995a6882b1d2`
- `run-2.json`: `0e01c940ac75d6881b193fc7f7be5cc8712a9cc771e6315027f9dc15e4bf7aa9`

Each SHA-256 value above matches the corresponding blob read directly from
the source branch. `corpus-manifest.json` separately pins the original source
revision, source blobs, input digest, and prompt digest.

## Scope boundary

This directory is an immutable experiment record, not a reusable runner,
benchmark service, or production evidence store. Its conclusion applies only
to the fixed three-document corpus described in `README.md`.
