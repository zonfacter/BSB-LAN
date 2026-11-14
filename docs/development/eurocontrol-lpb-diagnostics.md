# Legacy Eurocontrol K/M diagnostic findings

This report records findings through 2026-11-14 for one installation with a
Eurocontrol K (family 22, variant 254) and M/RVA46 (family 23, variant 254).
The K controls a direct radiator circuit, boiler and domestic hot water; the M
controls a separate mixed floor-heating circuit. These functions and destination
addresses are installation-specific. LPB destinations are not modern HC1/HC2
program numbers.

The firmware additions, parser fixes and offline description reader are in
this branch. Later diagnostic interpretation, history, pump events, schedule
editing, ioBroker integration and observation-only learning are implemented in
the separate [SmartHome dashboard](https://github.com/zonfacter/SmartHome_py/tree/codex/heating-dashboard).
The dashboard reads raw LPB objects through BSB-LAN; it is not firmware running
inside the ESP32. The object index below is a candidate/reference list for
future firmware work, not a claim that 133 new programs have been added here.

## Evidence levels

1. Exact device-description handlers establish field positions and encodings.
   They do not prove that a device answers a query or accepts a write.
2. Payload-free TYPE_QUR 06 / TYPE_ANS 07 reads verify the responding controller,
   object, byte layout and frame checksum. An invalid scalar is still an answer;
   it is not a real temperature and must not be replaced with 20 C.
3. Controlled physical comparisons establish observed changes, with other
   controllers left unchanged. The M mode sequence now includes a return to Auto.
4. Manufacturer descriptions of later LPB generations are used only for matching
   object/layout combinations. They do not establish every effect of the old K/M.
5. A protocol indication and a time correlation do not prove the unique physical
   reason for a stopped pump. Contact state is not a water-flow measurement.

Private network configuration, credentials, household schedules, recorder
databases, photos, vendor binaries and the complete extracted vendor catalogs
are excluded. The checked-in fixtures are selected self-recorded protocol data;
the index and notes are self-authored. Vendor documents are linked, not bundled.

## Read-only object inventory

[eurocontrol-readonly-object-index.json](eurocontrol-readonly-object-index.json)
lists all 133 fields used by the external collector, grouped into 123
controller/object pairs. Each field records its decoder kind, unit, polling
group and one sample's quality, without publishing the live configuration.
Multiple fields can share one object. A `valid` transport/field sample does not
establish calibrated sensor accuracy, and `unavailable` does not mean the
object itself is unsupported.

Notable configuration objects, read on K unless marked K/M:

| CoID | Meaning | Encoding / restriction |
| --- | --- | --- |
| `0500071E` | DHW request source | Legacy boolean: valid `00 00` sensor, `00 FF` thermostat |
| `05000727` | DHW separation setting | Cascade separation; not circulation-pump shutdown |
| `05000930` | Burner configuration | Valid `00 00` single-stage, `00 FF` two-stage; does not prove wiring or stage power |
| `0500092D` | OEM boiler minimum | Scalar temperature, signed 16-bit /64 |
| `05000932`, `05000933` | Second-stage release/reset integral | Scalar K min, not a temperature or a fixed time delay |
| `05000924` | Boiler mode setting | Legacy valid `00 00` continuous, `00 FF` automatic; distinct from room-heating mode |
| `05000925` | Chimney-sweep state | Read only; do not enable to provoke status bits |
| `05000602` (K/M) | Startup room-setpoint boost | Scalar temperature difference, K |
| `0500060D`, `0500060E` (K/M) | Adaptation sensitivities ZAF1/ZAF2 | Signed byte after scalar state |
| `05000067` (K/M) | Plant type code | Keep raw controller code; no invented hydraulic topology |
| `0500006D` (K/M) | Clock source | Own clock / LPB without remote setting / LPB with remote setting / master |
| `05000082` (K/M) | Outside-temperature source | Two block fields: segment, device; no scalar validity prefix |

The default firmware table exposes the first and third configuration objects
above as read-only K programs. Both use the scalar state byte followed by the
exact enum byte. Other fields in the inventory remain candidates for separate review.

| Firmware program | CoID | Decoded values |
| --- | --- | --- |
| 5730.1 | `0500071E` | `00 00` storage tank sensor, `00 FF` storage tank thermostat |
| 5770.1 | `05000930` | `00 00` configured single stage, `00 FF` configured two stages |

The burner configuration describes the controller setting. Actual wiring and
operation of a second stage require separate evidence. The read decoder retains
unrecognized enum values and the original response bytes.

Burner hours were identified only in the K's nine-byte `11000209` producer
block, bytes 5..8 as a signed seconds counter. Do not apply that interpretation
to M's superficially similar producer block. Burner relay indication, flame
operation, nameplate input/output and an empirical gas-meter calibration are
different measurements.

## Request, lock, force and producer-status objects

The reference is [Brötje ISR MODBM 7715040-06, 2019-07-24, pp. 34-35](https://polo.broetje.de/pdf/7715040%3D6%3Dpdf_%28bdr_a4_manual%29%3Dde-de_ma_modbm.pdf).
The retained local source SHA-256 is
`84bc5e6043d481b06ca5872ff83aeec8d6e9a174e1c64da89c0ac4c9a41414be`.
Use the source's object scope, not a generic rule that bit 0 always means valid.

| CoID | LPB object | Supported interpretation | Still open |
| --- | --- | --- | --- |
| `210001F4`, `250001F4`, `190001F4` | 500 | Four bytes: signed temperature /64, then 16-bit attributes | Unique physical pump-switching cause |
| `150001F5` | 501 | Five-byte field layout only | Do not copy the four-byte request mask here |
| `110001F7` | 503 | Catalog: producer-group reduction byte and attribute byte; both retained raw | Attribute semantics and old-controller effects |
| `150001F8` | 504 | Signed percent byte, attribute byte | Actual reduction at each consumer |
| `190001F9` | 505 | Catalog: consumer-mixer reduction byte and attribute byte; both retained raw | Attribute semantics and effect in the tested plant |
| `110001FA` | 506 | Catalog: producer-group forced value and attribute byte; both retained raw | Exact meaning of the observed attribute bit |
| `150001FB` | 507 | Signed percent byte, attribute byte | Actual consumer action |
| `11000209` | 521 | Raw producer block; bounded K counter above | Do not copy object 522 status mask here |
| `1500020A` | 522 | Five bytes, leading 16-bit attributes | Remaining power/auxiliary fields |
| `2D00020B` | 523 | M first byte 0/1/2 observed frost/reduced/comfort | Second byte and other values |

For the matching four-byte object-500 requests, attribute bit 0 is validity,
bit 1 requests a transport pump, bits 2/3 indicate absolute/shifting DHW
priority. Priority flags are interpreted only when validity is set. A transport
pump request is not automatically the local Q1 contact. Unknown bits are retained.
For example, `08 40 00 02` has a 33 C temperature field but no valid request;
it must not be shown as active heat demand. `0A 00 00 03` carries a valid 40 C
request; on the tested M, the local mixed-flow target was separately 30 C.

For object 504, bit 0 marks a valid reduction; bit 1 marks mandatory reduction.
A percent field alone does not establish a pump stop. For object 507, bit 0
marks validity and bit 1 distinguishes force to all consumers from afterrun
only. With bit 1 clear, a retained 50 percent byte is not a command to force
every consumer to 50 percent.

For object 522, bit 0 instead means **producer present**. Documented bits
1,2,3,4,5,8 indicate ECO/outdoor limit, producer fault, chimney sweep, manual
producer lock, unavailable for space heating due to DHW charging, and manual
mode. When producer presence is not confirmed, the other flags are not treated
as active conditions. Other bits remain unassigned.

## Observed pump context and timing limits

During natural DHW charging, K pump-off observations coincided with Q3 on and
`64 01` in object 504. M could keep its pump on with that same reduction value,
consistent with restricting a mixed circuit through its valve. These are
correlations, not independent controlled proof of all priority effects.

### Overnight comparison, 2026-11-14

A read-only review of natural transitions found four space-heating burner
runs with K's direct-circuit pump on and Q3 off. Three starts associated with
a valid DHW request coincided with K's pump turning off and object 504
reporting a valid 100% reduction. K reported the configured DHW priority
as shifting. On two recoveries, K's pump restarted before the burner run
ended, with Q3 still on and object 504 back to `00 00`.

| Observed phase | K object 503 | K object 505 | K object 506 | K object 504 |
| --- | --- | --- | --- | --- |
| Space-heating burner run, K pump on, Q3 off | `02 03`, `04 03` | `00 00` | `32 00` | `02 03`, `05 03` |
| First DHW start, K pump off before Q3 switched on | `01 03`, `10 03`, `18 03` | `00 00` | `32 00` | `64 03` |
| Repeated DHW runs, K pump off and Q3 on | `00 00` when available | `00 00` | `32 00` | Mainly `64 01` |
| DHW pump overrun, K pump back on | `00 00` | `00 00` | `32 00`, `32 01` | `00 00` |

M kept its pump on during the observed DHW runs. Its 503/505/506 fields
were all `00 00` when available in these phases, including while 504 reported
a reduction. K's nonzero 503 readings occurred with its pump both on and off,
and 503 returned to zero during sustained reduction at 504. K's second byte
in 506 changed during an overrun window. These observations bound when the
fields changed and leave their attributes unassigned. Low K boiler temperature
and the mandatory reduction observed before Q3 switched on are compatible
with a startup contribution. The records are sequential reads and do not
establish an exact transition order within a polling cycle.

### 24-hour comparison, 2026-11-13 to 2026-11-14

The Siemens system-definition files `D0016682.apw` (related K profile) and
`D0017684.apw` (M profile) agree on the layout of 503, 505 and 506.
Their label rows 261–262, 265–266 and 269–270 respectively describe a signed
byte at offset 0 and a mask byte at offset 1. The catalog abbreviations
`EG` (producer group) and `VM` (consumer mixer) describe signal roles, not
the floors of this installation. The referenced rows identify the layout;
they do not establish a bit definition for these controllers.

The comparison uses the external collector's event rows from 13 November
09:10:20 through 14 November 09:10:20 (Europe/Berlin). For each object, an event
was usable when the object, local pump contact, Q3, 504 and 507 readings were
valid, at most 90 s old and within 30 s of each other. Counts describe
recorded event rows, not run durations or independent observations.

| Object | K (OG), usable / total | M (EG), usable / total | Observed result |
| --- | ---: | ---: | --- |
| 503 | 1188 / 1196 | 1276 / 1290 | K had eleven nonzero readings. K returned the same `01 03` with the OG pump contact on and off. M returned `00 00` throughout. |
| 505 | 1189 / 1196 | 1272 / 1290 | Both returned only `00 00`, including while M commanded its mixer closed. |
| 506 | 1189 / 1196 | 1276 / 1290 | K returned `32 00` 1100 times and `32 01` 89 times. M returned only `00 00`. |

All 89 comparable K event rows with `32 01` also had `32 01` in 507 and an
on OG pump contact. Q3 was off in 41 rows and on in 48. One row had 507
`32 01` while 506 still read `32 00`; sequential requests can straddle a
transition. There were 16 evaluable rising edges in 506, each bracketed by
opposite readings no more than 90 s apart. All 16 overlapped the interval
between the last burner-relay-on sample and first off sample, allowing 10 s
of slack. The separate burner history had 19 eligible on-to-off intervals;
the other three did not have an evaluable 506 edge under these criteria.
The history records the burner relay, with no independent flame or flow
measurement in this comparison.

| Local time | Samples aligned for comparison |
| --- | --- |
| 13 Nov, 09:23:38 | K: 503 `01 03`, 504 `01 03`, OG pump on, Q3 off. |
| 14 Nov, 04:00:58 | K: 503 `01 03`, 504 `64 03`, OG pump off, Q3 off. |
| 13 Nov, 09:27:15 | K: 506/507 `32 01`, burner relay off, OG pump on, Q3 off. |
| 13 Nov, 11:49:37 | K: 506/507 `32 01`, burner relay off, OG pump on, Q3 on. |
| 13 Nov, 11:01:29 | M: 505 `00 00`, 504 `64 01`, Q3 on, EG pump off, mixer closing contact on, no valid local heat request. |
| 13 Nov, 15:21:05 | M: 505 `00 00`, 504 `64 01`, Q3 on, EG pump on, mixer opening contact on, valid local heat request. |

Object 506 now has a plausible burner-afterrun context across space heating
and DHW. Siemens describes a forced LPB signal following burner switch-off
for the [RVP360, section 12.4.5](https://cache.industry.siemens.com/dl/files/924/109788924/att_1045682/v1/A6V10331099.pdf#page=53).
That functional comparison supports the hypothesis without assigning
a 507 bit definition to 506. Object 503 alone does not predict the OG pump
contact, and the M counterexamples show that zero in 505 does not exclude
mixer activity. No new bit is used for automatic diagnosis.

### Follow-up observation, 2026-11-14

The next recorded space-heating burner run (09:36:40 to 09:40:55 local time)
ended with K objects 506 and 507 both changing to `32 01`. Q1 stayed on,
Q3 stayed off and the local heating request remained valid. The next
recorded DHW burner run (09:50:25 to 10:10:11) ended with the same paired
signal, Q1 back on and Q3 still on. At 10:15:20 the two objects returned
to `32 00` and `00 00` respectively. K reports a five-minute pump
overrun setting (`05000BCC`). Times identify sampled states.

At 11:32:25, after another DHW burner run, both force signals read
`32 01` while Q1 was off, Q3 was on and no valid space-heating request
was present. Both force signals returned to baseline at 11:37:35.
This observation shows why the OG pump display requires its actual relay
contact in addition to the two bus signals. The dashboard displays its
OG afterrun indication when the two observed patterns agree, K4 is off
and Q1 is on, with valid readings at most 90 s old and 30 s apart.

The [Brötje LPB table for object 507](https://polo.broetje.de/pdf/7715040%3D6%3Dpdf_%28bdr_a4_manual%29%3Dde-de_ma_modbm.pdf#page=35)
describes a valid overrun-only request. The [RVA43.222 OEM table, line 8](https://manualzz.com/doc/48218186/sime-rva43-222-boiler-controller-installation-and-operati...)
describes pump overrun time after burner switch-off. The role of 506 here
is established by the local comparison. Its general attribute map remains
open.

The external collector groups each controller's related reads. Diagnosis
requires valid samples, age no more than 90 s and a combined timestamp span no
more than 30 s for the fields actually used. It abstains for missing or skewed
data. It reports demand, afterrun, DHW reduction and producer-status indications
as compatible contexts; the unique physical cause remains unresolved. It does
not infer an off motor from a cached or missing relay sample.

The [M mode fixture](eurocontrol-mode-test-20261110.json) covers
Auto -> continuous -> standby -> Auto. It independently distinguishes normal
continuous mode from emergency manual operation and reproduces levels 1 -> 2
-> 0 -> 1. The return restored the original reduced setpoint, inactive local
heat demand and off pump contact. The unresolved lock/force bytes did not
acquire a new semantic meaning from that experiment.

The M candidate `0500065E`, present in later device descriptions as lock-signal
gain, returned TYPE_ERR 07 on the tested M. It is excluded from periodic reads.
This bounded negative result does not prove the whole function is inaccessible.

## Remaining verification work

- Capture the K's chimney-sweep status during a scheduled flue-gas
  measurement for [#11](https://github.com/zonfacter/BSB-LAN/issues/11).
- Observe naturally occurring DHW priority and boiler startup/afterrun phases;
  make one authorized controller change at a time, retain before/after reads,
  verify restoration, and compare actual device indications.
- Do not force overheating, sensor failures, frost, relay tests or disabled
  protections to manufacture signal changes.
- Keep unresolved objects 503/505/506 and level attributes raw until exact
  documentation or controlled comparisons establish them.
- Propose independently reviewed firmware program numbers and access flags for
  additional objects. Readability never establishes writability.

## Reproducing the offline checks

From this repository root:

```sh
python -m unittest discover -s tests -p 'test_*.py' -v
python -m unittest discover -s tests/host -v
```

The first command checks the offline description reader and retained frame
evidence without vendor files or hardware. The second compiles production
firmware sections with a host C++ compiler, including device-specific lookup,
independent K/M mode enums, decoder failures and bounded SET behavior. Neither
command sends bus traffic. A complete embedded build remains a separate check.
