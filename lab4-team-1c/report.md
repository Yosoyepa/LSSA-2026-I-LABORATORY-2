# Laboratory 4 — Quality Attribute Scenarios
**Team 1C** | Large-Scale Software Architecture 2026-I

---

## Question 1: Would a `mas` failure violate the 92% SoS threshold?

The 92% figure in QS-AV-SoS-1 is measured as the ratio of successfully completed non-ticketing transactions to the baseline rate. It was designed around the `tickets_ms` failure — a subsystem architecturally isolated from the safety path. In `model.arch`, `connector dependency tickets_ms -> tickets_db` shows its exclusive data partition, and no safety-critical component holds a dependency toward it. The 8% allowance corresponds precisely to the ticketing workload share.

A `mas` failure is categorically different. The `mas` sits at the convergence of the safety-critical graph: it receives position data via `connector data_flow mas -> position_time_ms`, route data via `connector data_flow mas -> routes_ms`, and issues commands through `connector control_command mas -> onboard_unit` and `connector control_command mas -> onboard_radio_unit`. It also ingests alerts via `connector data_flow alerts_ms -> mas` and persists state via `connector dependency mas -> event_store_db`. Without `mas`, no train receives movement authority, forcing a network-wide fail-safe halt. This reduces non-ticketing operational capacity toward zero, far below 92%.

A SoS-level availability scenario for `mas` failure would need the following measure: "A standby `mas` instance resumes processing within 500 ms (per QS-AV-SYS-1); zero confirmed movement authorities are lost; the SoS maintains 100% safety-critical capacity, measured as the ratio of trains holding valid authorities during recovery to total active trains." This shift in perspective proves that safety continuity, not throughput, is the appropriate metric for the movement authority.

---

## Question 2: Is the 3000 ms SoS threshold achievable if the 200 ms system threshold is violated?

Yes, the 3000 ms SoS threshold is achievable because the bounds address architecturally disjoint paths within ERTMS. The 3000 ms SoS path (QS-PE-SoS-1) traces the sequence: `portal` to `api_gateway` via `connector data_flow portal -> api_gateway`, then entering the logic tier via `connector data_flow api_gateway -> tickets_ms`, and persisting via `connector dependency tickets_ms -> tickets_db`. 

In complete contrast, the 200 ms system path (QS-PE-SYS-1) traces telemetry. It travels from `onboard_unit` to `position_time_ms` via `connector data_flow onboard_unit -> position_time_ms`, persisting through `connector dependency position_time_ms -> position_time_db`, and notifying safety logic via `connector data_flow mas -> position_time_ms`. Position updates from `onboard_unit` completely bypass the `api_gateway` because they flow directly through the physical-to-logic connector without traversing presentation layers.

Since no connector — neither `data_flow`, `dependency`, nor `async_event` — links the `tickets_ms` subsystem to the `position_time_ms` domain, they are not structurally coupled. Even if `position_time_ms` violates its 200 ms bound by saturating under a burst of concurrent position updates, the `api_gateway` continues routing ticketing transactions completely independently. The only relevant annotations mapped to the 3000 ms threshold are `interactive` SLA bands on the `api_gateway` nodes, ensuring that the 3000 ms SoS limit remains achievable regardless of telemetry backlogs.

---

## Question 3: A third security scenario for an uncovered boundary

The two provided security scenarios cover the public edge from the `portal` into the `api_gateway`, and the internal control channel from the `mas` into the `onboard_unit`. A component not referenced by either, but carrying severe systemic security implications, is the `maintenance_console` located in the presentation tier. It connects directly to the `api_gateway` via `connector data_flow maintenance_console -> api_gateway`. Because maintenance consoles carry elevated administrative privileges — such as executing configuration changes, overriding schedules, and performing safety-state inspection — this connector acts as a prime vector for privilege escalation that bypasses the simple public security gradient entirely.

To forge a third security scenario focused on this Privileged Maintenance Channel, we cast an insider threat or compromised terminal as the Source, and the injection of 500 unauthorized administrative commands within 30 seconds as the Stimulus. The structural Artifact under attack is the `connector data_flow maintenance_console -> api_gateway` boundary. The Environment represents normal operative baseline conditions where regular operator traffic flows without any prior detected security incidents or degraded states.

To secure this vulnerability, the Response specifies that the `api_gateway` must validate every `maintenance_console` request against a multi-factor authentication token with an explicit administrative role claim, immediately rejecting any uncredentialed requests and triggering a rate-limiting lockout after 10 sequential attempts. The final Response Measure mandates that exactly zero unauthorized commands reach logic-tier components like `mas`, `scheduling_ms`, or `alerts_ms`; detection and logging complete within 500 ms of the attack initiation; and the lockout mechanism activates within 5 seconds without disrupting validated sessions from other interfaces like the `dashboard`.
