# Development research

## Contribution credits

The Eurocontrol K/M LPB extensions, research tooling, protocol findings and
regression tests in this contribution were developed collaboratively:

- **Human contributor: [@zonfacter](https://github.com/zonfacter)** — project
  direction, access to the heating installation, physical controller changes,
  observations and real-hardware verification.
- **AI assistance: OpenAI Codex** — protocol and source analysis,
  implementation, test development and documentation in collaboration with
  @zonfacter.
- **Contributor-supplied model/run designation: GPT 6.1 Sol High.**

Original project: [fredlcore/BSB-LAN](https://github.com/fredlcore/BSB-LAN),
with its existing authors and contributors. These credits identify the
Eurocontrol contribution submitted in
[upstream PR #836](https://github.com/fredlcore/BSB-LAN/pull/836), which was
closed without merging. Development continues in this fork.

## Findings and evidence

- [Comparison with existing upstream support](upstream-comparison.md):
  the supported device-specific-list workflow, the observed K/M directory
  limitation, two controlled source regressions, and limits on novelty claims.

- [K/M diagnostic signals and contribution boundaries](eurocontrol-lpb-diagnostics.md):
  scoped request/lock/status fields, burner/DHW configuration, evidence levels,
  open questions, and the relationship to the external dashboard.
- [Controlled M operating-mode test](eurocontrol-mode-test-20261110.json):
  selected checksum-verifiable read frames for continuous, standby and Auto return.
- [Read-only object index](eurocontrol-readonly-object-index.json):
  133 collector fields on 123 controller/object combinations; not automatic
  firmware definitions or authorization to write those objects.

- [Eurocontrol K legacy LPB observations](eurocontrol-k-lpb.md): confirmed object
  mappings, optional-value behavior, pump block layout, and review boundaries.
- [Eurocontrol M legacy LPB read profile](eurocontrol-m-lpb.md): read-only mixing
  controller values, pump/mixer contact layout, and physical validation limits.
- [Inspecting locally supplied Siemens system definitions](siemens-sysdef-research.md):
  offline package structure, reader usage, parser coverage, and known limits.
- [Compact verified facts](rva43-verified-facts.json): machine-readable evidence
  for targeted family-specific work; not a replacement for the full vendor data.
- [Eurocontrol M facts](rva46-verified-facts.json): successful read samples,
  source offsets, and the observed pump-on/mixer-off comparison.

The development branch is based on the upstream project, with independent code
fixes kept separate from research tooling and findings. Vendor archives and
private device configuration are not part of this repository.
