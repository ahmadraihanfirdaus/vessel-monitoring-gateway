# NET-002 Host Development Boundaries (Batch 2)

The offline host store preserves a latest binary state buffer (<=256 bytes) and
an eight-entry **critical event** ring in process memory. Eviction is counted,
never claimed lossless. Invalid writes do not erase a previous valid latest state.

These capacities are temporary host implementation bounds, **not approved
production storage numbers**. No ESP-IDF NVS/flash wear protection, power-loss
retention, cloud delivery, encrypted at-rest storage, or network integration
is implemented or tested. Formal NET-002 remains PARTIAL / NOT_RUN.
