# Pre-Phase 9 F05 Post-Commit Archive Summary

**Decision:** `F05_POSTCOMMIT_ARCHIVE_EVIDENCE_PASS`

The clean public source archive procedure was executed from committed
`develop@b784a78` after both scanner false-positive fixes.

Results:

- source commit: `b784a78819d01e81c2620a5e9b2f52ce7ae8ca4d`;
- focused scanner/fixture regression: PASS (6/6);
- tracked files represented exactly: 309/309;
- archive filename: `vessel-monitoring-gateway-public-b784a78.zip`;
- archive SHA-256: `b46ec209714d163d713459e68dfec7fda609572138a3eea392b0e7e69aa91f21`;
- archive size: 558264 bytes;
- forbidden archive entries: 0;
- machine-local user path hits: 0;
- high-confidence secret hits: 0;
- Git metadata entries: 0;
- F01 status/traceability regression: PASS;
- automated security regression: PASS;
- LOCKED SHA gate: PASS (2/2).

The generated ZIP remains an operator-local artifact and is not added to Git.

After this evidence is committed, the pre-Phase-9 repair scope is complete.
The total system remains PARTIAL and Phase 9 has not yet started. This does not
authorize publication, deployment, physical integration, certification,
calibration, field operation, or production readiness.
