# Comparison with existing BSB-LAN support

Updated 2026-11-10. The comparison target is upstream commit
`31e5efa1770b48792e7c813b5514261f8c8d003c`, independently checked against
`fredlcore/BSB-LAN` master during this investigation. Work continues in this
fork. The closed upstream PR is not being reopened, and no acceptance of this
contribution is implied.

## What upstream already provides

The [pinned discussion #482](https://github.com/fredlcore/BSB-LAN/discussions/482)
explains why a small default table is intentional. Different controllers can
use the same program number with different meanings, options, scales or units.
Upstream's preferred workflow reads the device's own parameter structure and
uses it to prepare a matching custom definition file. The generation step is
described as partly manual. A sparse default table is therefore not evidence
that the project lacks those parameters.

See the [installation documentation](https://docs.bsb-lan.de/de/install.html#generieren-der-geratespezifischen-parameterliste)
and the checked-in `docs/de/install.md`. The source implementation is the
`/QD` branch in `BSB_LAN/BSB_LAN.ino`; user documentation calls the download
command `/Q`. `/QDB` additionally activates a limited temporary table. That
temporary table is not equivalent to the full device-specific file.

LPB communication, raw `/JY` requests, per-request destinations, native daily
program formats and integration with external home automation already exist.
Our use of them is not a discovery of a new transport or API.

## What happened on these two old controllers

An earlier normal device-structure download identified the K as
RVA43.2223/500, family 22/254, OV 200.4, and the M as RVA46.531/500,
family 23/254, OV 200.6. Both sections ended with the upstream message
`Not supported by this device. No problem.` No complete IA1 directory was
obtained. The retained local report records this failure; it was not included
in the original PR's explanation prominently enough.

A new bounded comparison sent exactly one payload-free IQ1 (`0x12`, index 0)
header query per controller, followed by one ordinary read of operating mode.
Neither IQ1 request yielded a matching IA1 header. Both ordinary reads then
returned checksum-valid, correctly addressed answers (`00 01`, automatic).
Bus write mode remained disabled before and after the check. No bulk dump,
temporary parameter-table activation, device setting or restart was performed.

The adapter reported `rx_hex = 00` for the missing headers. This is not a valid
received LPB frame and must not be described as an explicit controller rejection
or as proof of a corrupt bus packet. These bounded results establish that the
usual header path did not work in the observed setup. They do not establish
that every alternative directory protocol is impossible, or that the maintainer
could not prepare a matching file using other information.

The fresh read evidence and the earlier report digest are retained in
[upstream-comparison-evidence.json](upstream-comparison-evidence.json).
This is a material installation-specific limitation to the otherwise valid
general advice to use a device-specific list.

## Classification of the work

| Item | Existing upstream capability / knowledge | Result of comparison |
| --- | --- | --- |
| LPB transport and raw queries | Already implemented | Existing functionality we used |
| Tailored parameter definitions | Established and recommended upstream workflow | Our tested directory-header path did not return a usable catalog; a maintainer-generated K/M file is not available for direct comparison |
| K/M addresses, scales, units and block offsets | Manufacturer descriptions already contain these | Independently read and partly physically verified on this installation; not a claim of first discovery |
| Panel 65 state versus retained KORR value | Shared scalar exists in manufacturer data | Controlled local change demonstrated the relationship; exposure as two fields is a fork feature |
| M normal continuous mode, code 4 | Operating modes already exist in manuals | Controlled test corrected our own initial shared K/M translation; not a demonstrated upstream firmware bug |
| Levels 0/1/2 on M | Operating-level concepts already exist | Locally observed frost/reduced/comfort sequence with return to Auto; second byte still unassigned |
| Native weekly-program writes | Existing LPB/BSB-LAN protocol support | Bounded K/M ACK/readback/restore and ten-minute normalization are device-specific verification |
| LPB request/reduction/status bits | Later manufacturer documentation describes selected objects | Scoped application and local correlations; no new meanings claimed for unresolved 503/505/506 bits |
| Offline Siemens description reader | Upstream also has device-description knowledge; its generation process is not public | A new tool in this fork, not proof of globally new protocol knowledge or more complete coverage |
| Dashboard, ioBroker history, observation models and gas anchors | External integrations already exist | Our application implementation; neither a new LPB protocol nor evidence of automatic energy savings |
| Raw URL preprocessing and string-frame mutation | Present in the compared upstream source | Two independently reproducible source-level differences, detailed below |

Counts such as 133 fields/123 object pairs describe the collector inventory.
They are not counts of globally new parameters or additions proven absent from
the maintainer's device-specific definitions.

## Two generic regression comparisons

The same unchanged host harnesses were compiled with g++ on Ubuntu against:

1. Isolated copies of the three relevant source files from exact upstream
   commit `31e5efa1770b48792e7c813b5514261f8c8d003c`.
2. The corresponding production source sections in this fork.

Both upstream harnesses compiled successfully and failed at runtime. Both fork
harnesses compiled and passed. This is not a comparison of differently written
tests or an expected compilation failure caused by missing fork-only types.

| Test | Upstream runtime result | Fork result | Scope |
| --- | --- | --- | --- |
| `test_json_raw_url.py` | Parsed payload differs from `{00, 00, 40}` | Pass | Generic JSON preprocessing modifies a raw `/JY` URL before raw parsing, losing payload data. Functional parsing assertions run before buffer-preservation assertions |
| `test_string_telegram.py` | `msg == original && crc_valid(msg)` fails | Pass | String decoding changes the original received frame; the fork keeps the original bytes/checksum intact |

The parser harness uses an in-memory example of a SET URL; it does not send a
SET or access a heating system. The string harness uses real-shaped synthetic
frames. These are bounded software regressions, independent of a parameter
catalog. They do not prove a live heating-control fault or establish that every
other aspect of either implementation is correct.

## Next work in this fork

- Retain the useful application and installation-specific tests without
  presenting all extracted manufacturer mappings as new discoveries.
- Keep generic code corrections separate from K/M profiles and research notes.
- If a matching controller-specific definition becomes available, compare exact
  CoIDs, scalar states, enums, ranges, units, access flags and daily-program
  representations rather than comparing only display names or field counts.
- Preserve negative results and uncertainty; do not turn a missing catalog
  header into a universal unsupported-device claim.
- No further upstream request or message follows from this report. A fresh
  proposal would first need a focused scope and prior maintainer agreement.
