# Unser Eurocontrol-K/M-Fork

Dieses Repository ist die Entwicklungsbasis von **@zonfacter** für die eigene
Eurocontrol-K/M-Anlage. Ausgangspunkt ist
[fredlcore/BSB-LAN](https://github.com/fredlcore/BSB-LAN). Die Mitarbeit und
KI-Unterstützung sind in den [Credits](README.md#contribution-credits) genannt.

Aktiver Branch: `codex/eurocontrol-lpb-research`. `upstream/master` dient als
Vergleichsbasis. Neue Beiträge oder Nachrichten an das Originalprojekt erfolgen
nur auf ausdrücklichen Wunsch des Nutzers. Der geschlossene PR #836 wird nicht
wieder geöffnet. Fehlerkorrekturen, Controllerprofile und Protokollforschung
bleiben als getrennte Commits nachvollziehbar.

## Was wo liegt

| Bestandteil | Ort | Aktueller Umfang |
| --- | --- | --- |
| ESP32-/Due-Firmware | `BSB_LAN/` in diesem Fork | Zwei allgemeine Parser-/Decoderkorrekturen; sechs K- und 23 M-Programme mit begrenztem, geprüftem Zugriff |
| K/M-Protokollbefunde | `docs/development/` | Skalierungen, optionale Zustände, Relaisblock, dokumentierte Signalattribute und kontrollierte Vergleiche |
| Offline-Siemens-Reader | `tools/siemens_sysdef.py` | Lokale Analyse selbst beschaffter Beschreibungen; keine Buszugriffe oder automatische Freigabe von Parametern |
| Moderne Oberfläche, ioBroker, Historie und Lernmodelle | [SmartHome_py, Branch codex/heating-dashboard](https://github.com/zonfacter/SmartHome_py/tree/codex/heating-dashboard) | Externe Anwendung mit getrennten Ansichten für EG, OG und Warmwasser |
| Private Konfiguration und Messdaten | Nur auf den jeweiligen Geräten / im lokalen Arbeitsverzeichnis | Gehören nicht ins öffentliche Repository |

Die **133 Felder auf 123 Controller-/Objektkombinationen** gehören zum externen
Collector. Sie sind kein Versprechen, dass alle diese Felder bereits als
Firmware-Programme in diesem Fork angelegt sind. Der
[Objektindex](eurocontrol-readonly-object-index.json) zeigt die Decoder und
Abfragegruppen; [K-Profil](eurocontrol-k-lpb.md) und
[M-Profil](eurocontrol-m-lpb.md) zeigen die tatsächlich ergänzten Programme.

## Getestete Anlage und Grenzen

- K: RVA43.2223/500, Familie 22 / Variante 254, OV 200.4; direkter OG-Heizkreis,
  Kessel und Warmwasser.
- M: RVA46.531/500, Familie 23 / Variante 254, OV 200.6; gemischter EG-Heizkreis.
- Adapter der beobachteten Anlage: Olimex ESP32-EVB, Ethernet, LPB.
- In dieser Anlage war K Zieladresse 0 und M Zieladresse 1. Andere Anlagen
  müssen ihre tatsächlichen Geräteadressen und Profile prüfen.

Eine Übereinstimmung der Familie allein beweist keine vollständige Kompatibilität.
Kein Profil erzwingt die Identifikation eines anderen Reglers. Fehlende oder
ungültige Raumfühler bleiben unverfügbar; ein Sollwert oder Ersatzwert wird
nicht als gemessene Raumtemperatur ausgegeben.

Der vorhandene BSB-LAN-Weg zur gerätespezifischen Parameterdatei bleibt ein
gültiger Ausgangspunkt. Unsere K/M-Strukturabfragen lieferten bislang keinen
auswertbaren Verzeichniskopf. Der genaue Vergleich und seine Grenzen stehen im
[Upstream-Abgleich](upstream-comparison.md).

## Firmware vorbereiten und nur bauen

1. Von diesem Fork den aktiven Branch beziehen. Vorhandene private Dateien
   sichern und weiterverwenden. Bei einer neuen Installation die mitgelieferten
   `.default`-Vorlagen als lokale `BSB_LAN_config.h` und
   `BSB_LAN_custom_defs.h` anlegen. Eine bestehende gerätespezifische Tabelle
   wird beim Aktualisieren geprüft zusammengeführt.
2. In privaten Dateien Board, Netzwerk und Bus passend zur tatsächlichen
   Hardware konfigurieren. Keine Zugangsdaten oder private Parameterdateien
   committen. Die neue Betriebsartdarstellung für M liegt im Defaultprofil;
   eine bereits vorhandene eigene Tabelle muss für Programm 700 die
   M-spezifische `RVA_M_MODE_ENUM` übernehmen.
3. Die ergänzten `DEV_022_254`- und `DEV_023_254`-Zeilen aus der Defaulttabelle
   in eine vorhandene eigene Tabelle sortiert übernehmen. Dabei abweichende
   Profile und vorhandene Definitionen erhalten.
4. Mit der installierten Arduino-Toolchain bauen. Für den früher erfolgreich
   verwendeten ESP32-EVB-Aufbau lautet der Build-Aufruf:

```sh
arduino-cli compile \
  --fqbn esp32:esp32:esp32-evb:PartitionScheme=min_spiffs \
  --libraries BSB_LAN/libraries \
  --output-dir local-output/esp32-evb \
  BSB_LAN
```

Der frühere ESP32-EVB-Build verwendete Core 3.3.10. Die laufende GitHub-CI baut
zusätzlich für Arduino Due und prüft Produktionscode mit einem Host-Compiler.
Ein erfolgreicher Due-Build ersetzt keinen ESP32-Build der jeweiligen Revision.
Der obige Aufruf lädt keine Firmware hoch. Eine Änderung im Fork oder eine
erfolgreiche CI aktualisiert den laufenden ESP32 nicht automatisch.

## Lesender Betrieb und Schreiben

M-Programme sind in der Firmware zunächst schreibgeschützt. Bei K sind nur die
bereits unabhängig geprüften Anpassungs- und Schaltdifferenzfälle vorgesehen;
die bestehende globale Schreibsperre gilt weiterhin. Für Parameter 65 ist die
Beziehung zwischen Aktivierungszustand und gespeichertem KORR-Wert bestätigt,
aber kein fernbedienter SET-Versuch als erfolgreich dokumentiert.

Die externe Wochenprogramm-Übertragung besitzt eine eigene Freigabe sowie
Vorschau, Konfliktprüfung, Rücklesen und Wiederherstellung. Ihre Beispielkonfiguration
deaktiviert Schreibzugriffe. Die Lernmodelle bleiben im Beobachtungsmodus;
sie ändern weder Heizzeiten noch Sollwerte oder Warmwasserregelung.

Für neue Schreibfunktionen werden zuerst Objekt, Feldaufbau, Grenzwerte und
Zustandsbytes geklärt. Ein später ausdrücklich beauftragter Gerätetest sichert
den Ausgangswert, prüft ACK und unabhängiges Rücklesen und stellt den
Ausgangszustand wieder her. Aus einem erfolgreichen Lesezugriff folgt keine
Schreibfreigabe.

## Weitere Entwicklung

Die [zentrale Issue-Übersicht #1](https://github.com/zonfacter/BSB-LAN/issues/1)
verknüpft abgeschlossene Arbeiten und offene Nachweise. Die Einzelissues
enthalten Quellen, Abschlusskriterien und Grenzen; ihr GitHub-Status ist der
aktuelle Arbeitsstand. Ein geschlossenes Implementierungsissue bedeutet
nicht, dass sämtliche Folgefragen bereits geklärt sind.

| Priorität | Aufgabe | Nächster Nachweis |
| --- | --- | --- |
| 1 | [Weitere gelesene Felder in die Firmware übernehmen · #9](https://github.com/zonfacter/BSB-LAN/issues/9) | Passende Programmnummern, exakte Layouts, Tests und zunächst lesende Profile |
| 2 | [M-Betriebsniveau verständlich darstellen · #10](https://github.com/zonfacter/BSB-LAN/issues/10) | Beobachtete Werte 0/1/2 von der noch offenen Attributbedeutung trennen |
| 3 | [Pumpenkontext und Sperrsignale verfeinern · #12](https://github.com/zonfacter/BSB-LAN/issues/12) | Natürliche Warmwasser-/Nachlaufphasen und zeitlich zusammenpassende Signale; unbekannte Bits bleiben roh |
| 4 | [K-Code 4 am Bedienfeld geprüft · #11](https://github.com/zonfacter/BSB-LAN/issues/11) | Beide Bedienzustände liefern Code 4. Die Firmware zeigt für K beide Bedeutungen an. |
| 5 | [Passende gerätespezifische Definition vergleichen · #13](https://github.com/zonfacter/BSB-LAN/issues/13) | CoIDs, Zustände, Enums, Skalierungen, Einheiten, Zugriffe und Zeitprogrammformate vergleichen |
| 6 | [Fern-SET für K-Parameter 65 klären · #14](https://github.com/zonfacter/BSB-LAN/issues/14) | Exakte Zustandsdarstellung, Faktor erhalten, später separat beauftragter Gerätetest |

Diese Liste beschreibt offene Arbeit. Sie behauptet weder vollständige
Entschlüsselung der Sperrsignale noch globale Neuheit der Herstellerdaten.
Physische Tests am Regler werden einzeln mit dem Nutzer abgestimmt.

## Prüfen und veröffentlichen

```sh
python -m unittest discover -s tests -p 'test_*.py' -v
python -m unittest discover -s tests/host -v
git diff --check
```

Die Hosttests benötigen einen C++-Compiler; auf dem bisherigen Windows-Rechner
wurde dafür die vorhandene Ubuntu-WSL-Umgebung verwendet. Die Prüfungen senden
keine Telegramme. Umfangreiche Live-Abfragen sollen die laufende Erfassung
nicht unnötig unterbrechen. Ein Relaiskontakt bleibt eine Regleranzeige und
ist keine unabhängige Messung von Wasserfluss oder Pumpendrehzahl.

Neue Änderungen gehen zuerst in diesen Fork. Beim Veröffentlichen werden
Code, selbst erstellte Dokumentation und bereinigte Testdaten geprüft.
Zugangsdaten, private Heizungs-/Tado-Konfigurationen, Gaszählerstände,
Messdatenbanken und vollständige Herstellerarchive bleiben lokal.
