# Security

## Report a vulnerability

Use the repository's private vulnerability reporting feature when available. Do not publish sensitive input, credentials or exploitable details in public issues. Include a minimal synthetic example, affected version, operating system and expected impact.

## Local processing

The application has no network client, telemetry, automatic update check, settings writer or source-history store. SVG is passed through anonymous pipes to a renderer helper, without a temporary SVG file. Exports contain raster pixels rather than source metadata or source paths. Application errors omit source content and OS exception paths. OS dialogs, caches and crash facilities can retain information independently.

Untrusted XML is parsed with defusedxml. DTDs, entities, external/data references, event attributes, scripts, images, text, filters and style blocks are rejected. Input length, node count, output dimensions and execution time are bounded. Linux additionally limits helper memory and CPU; other platforms use the portable validation and wall timeout. These controls are not a full OS sandbox.

## Dependencies and distribution

Runtime versions are pinned in requirements.txt; development and packaging requirements are separate. Review updates and run regression tests before changing pins. Advisory scans do not cover every embedded native library and cannot establish that a build has no vulnerabilities.

Release actions are pinned to commits. Only the release job receives repository write permission. Windows/macOS packaging and signing must be verified on native runners; Linux validation does not establish compatibility with those platforms.
