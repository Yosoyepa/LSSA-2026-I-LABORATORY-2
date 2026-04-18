# Laboratory 4 — Quality Attribute Scenarios
**Team 1C** | Large-Scale Software Architecture 2026-I

---

## Question 1: Would a `mas` failure violate the 92% SoS threshold?

The 92% figure in QS-AV-SoS-1 is measured as *the ratio of successfully completed non-ticketing transactions to the baseline rate*. It was designed around the `tickets_ms` failure — a subsystem architecturally isolated from the safety path. In `model.arch`, `connector dependency tickets_ms -> tickets_db` shows its exclusive data partition, and no safety-critical component holds a dependency toward it. The 8% allowance corresponds precisely to the ticketing workload share.

A `mas` failure is categorically different. The `mas` sits at the convergence of the safety-critical graph: it receives position data via `connector data_flow mas -> position_time_ms`, route data via `connector data_flow mas -> routes_ms`, and issues commands through `connector control_command mas -> onboard_unit` and `connector control_command mas -> onboard_radio_unit`. It also ingests alerts via `connector data_flow alerts_ms -> mas` and persists state via `connector dependency mas -> event_store_db`. Without `mas`, **no train receives movement authority**, forcing a network-wide fail-safe halt. This reduces non-ticketing operational capacity toward zero — far below 92%.

A SoS-level availability scenario for `mas` failure would need: *"A standby `mas` instance resumes processing within 500 ms (per QS-AV-SYS-1); zero confirmed movement authorities are lost; the SoS maintains 100% safety-critical capacity, measured as the ratio of trains holding valid authorities during recovery to total active trains."* The metric shifts from throughput to **safety continuity**.

---

## Question 2: Is the 3 000 ms SoS threshold achievable if the 200 ms system threshold is violated?

Yes. The two thresholds address **architecturally disjoint paths**. The 3 000 ms SoS path (QS-PE-SoS-1) traces: `portal` → `api_gateway` (via `connector data_flow portal -> api_gateway`) → `tickets_ms` (via `connector data_flow api_gateway -> tickets_ms`) → `tickets_db` (via `connector dependency tickets_ms -> tickets_db`). Alternatively, traffic arrives via `connector data_flow portal -> load_balancer` and `connector data_flow load_balancer -> passengers_ms`.

The 200 ms system path (QS-PE-SYS-1) traces: `onboard_unit` → `position_time_ms` (via `connector data_flow onboard_unit -> position_time_ms`) → `position_time_db` (via `connector dependency position_time_ms -> position_time_db`), with notification to `mas` (via `connector data_flow mas -> position_time_ms`). Critically, **position updates from `onboard_unit` bypass the `api_gateway` entirely** — they flow directly to `position_time_ms` via the physical-to-logic connector, never traversing the presentation or communication tiers.

No connector — neither `data_flow`, `dependency`, nor `async_event` — links `tickets_ms` to `position_time_ms`. Even if `position_time_ms` is saturated processing 500 concurrent updates (violating its 200 ms bound), the `api_gateway` continues routing ticketing transactions independently. The annotations most relevant are `performance: realtime` on `position_time_ms` and `timeout_ms: 200` on its inbound connector — constraints confined to the telemetry path. The SoS threshold of 3 000 ms, mapped to the `interactive` performance level, remains achievable because its critical path contains no `realtime`-annotated component.

---

## Question 3: A third security scenario for an uncovered boundary

The two provided scenarios cover the public edge (`portal` → `api_gateway`) and the internal control channel (`mas` → `onboard_unit`). A component not referenced by either but carrying security implications is **`maintenance_console`** (presentation tier, `operator_ui`). It connects to the `api_gateway` via `connector data_flow maintenance_console -> api_gateway`. Maintenance consoles carry elevated administrative privileges — configuration changes, schedule overrides, safety-state inspection — making this connector a vector for privilege escalation that bypasses the public security gradient.

**QS-SE-SYS-2 — Security at System level (Privileged Maintenance Channel)**

| Element | Description |
|---------|-------------|
| **Source** | Insider threat or compromised maintenance terminal |
| **Stimulus** | Injection of 500 unauthorized administrative commands through `maintenance_console` within 30 seconds |
| **Artifact** | `maintenance_console` → `api_gateway` connector (`data_flow` type, `model.arch`) |
| **Environment** | Normal operation — regular operator traffic; no prior incident |
| **Response** | The `api_gateway` validates each `maintenance_console` request for a valid multi-factor authentication token with administrative role; requests lacking credentials are rejected; a rate-limiting lockout triggers after 10 consecutive failures |
| **Response Measure** | Zero unauthorized commands reach any logic-tier component (`mas`, `scheduling_ms`, `alerts_ms`); detection and logging complete within 500 ms of the first unauthorized request; lockout activates within 5 seconds without disrupting authenticated sessions from `dashboard` or `ccs_monitor` |
