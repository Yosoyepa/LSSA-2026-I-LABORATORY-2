#!/usr/bin/env python3
"""Generate report.pdf for LSSA Lab 2 - SoS Metamodel Evolution."""
from fpdf import FPDF

class Report(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, 'LSSA 2026-I | Laboratory 2 - Architectural Modeling | Team 1C', align='C')
        self.ln(6)
        self.set_draw_color(180, 180, 180)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

pdf = Report('P', 'mm', 'A4')
pdf.set_auto_page_break(auto=True, margin=12)
pdf.add_page()

# --- Title ---
pdf.set_font('Helvetica', 'B', 13)
pdf.set_text_color(30, 30, 30)
pdf.cell(0, 7, 'Report: ERTMS System-of-Systems Metamodel', align='C', new_x='LMARGIN', new_y='NEXT')
pdf.ln(2)

# --- Q1 ---
pdf.set_font('Helvetica', 'B', 10)
pdf.set_text_color(40, 40, 120)
pdf.cell(0, 6, '1. Translating the C&C View into a DSL Model', new_x='LMARGIN', new_y='NEXT')
pdf.set_font('Helvetica', '', 9)
pdf.set_text_color(30, 30, 30)

q1 = (
    "The spatial mapping of components from the C&C diagram to the DSL was straightforward: "
    "each box became a 'component' declaration with explicit tier and type. "
    "However, two areas required significant judgment:\n\n"
    "Adaptation 1 - SoS Structuring: The professor's feedback required us to extend the "
    "original flat grammar with a 'System' construct to model the SoS envelope. We introduced "
    "'architecture <name>:' as the root and 'system <name> { ... }' blocks to declare "
    "operationally independent subsystems. The CCS (Command Control & Signalling) subsystem "
    "was modeled inside a system block with its own balises and MAS, demonstrating managerial "
    "and operational independence - a defining SoS characteristic.\n\n"
    "Adaptation 2 - Component Type Expansion: Lab 1 identified 11 missing components "
    "(mobile_app, message_broker, load_balancer, gsm_r_gateway, alerts_ms, scheduling_ms, "
    "tickets_db, alerts_db, scheduling_db, event_store_db, onboard_radio_unit). The original "
    "grammar lacked types for these. We added four new ComponentTypes (load_balancer, "
    "message_broker, radio_gateway, event_store) and a new ConnectorType (async_event) to "
    "represent event-driven communication patterns identified in the Lab 1 analysis. "
    "The semantic challenge was mapping real-world heterogeneous components into the "
    "constrained EBNF vocabulary while preserving domain meaning."
)
pdf.multi_cell(0, 4.2, q1)
pdf.ln(2)

# --- Q2 ---
pdf.set_font('Helvetica', 'B', 10)
pdf.set_text_color(40, 40, 120)
pdf.cell(0, 6, '2. DSL/Transformation Limitations & Workarounds', new_x='LMARGIN', new_y='NEXT')
pdf.set_font('Helvetica', '', 9)
pdf.set_text_color(30, 30, 30)

q2 = (
    "Limitation 1 - Connectors Are Semantically Ignored (ADR-001): The transformation engine "
    "does not traverse the AST's Connector objects. Database associations rely on a heuristic "
    "string substitution (db.replace('_db','') in name) and API Gateway routes are hardcoded. "
    "Workaround: We enforced strict Convention-over-Configuration - all component names use "
    "_ms/_db suffixes so the heuristic resolves deterministically. The ROUTES dict in the API "
    "Gateway was manually extended to include the new /alerts and /scheduling prefixes.\n\n"
    "Limitation 2 - Port Collision on MySQL (ADR-002): The original generator assigned port "
    "3306 to all databases. With 8 MySQL instances (up from 4), this was critical. "
    "Workaround: Dynamic port allocation using the component's enumeration index "
    "(3306+i:3306), yielding ports 3306-3313 with zero collisions.\n\n"
    "Limitation 3 - Flat Network (ADR-003): The MDE cannot segment network topologies. All "
    "35 containers share a single Docker bridge network. While this sacrifices tier isolation, "
    "it enables Docker's internal DNS to resolve inter-container HTTP calls by service name, "
    "which is essential since the generator ignores connector targets.\n\n"
    "Limitation 4 - SoS Traversal: The original apply_transformations() only iterated "
    "model.elements. With the new System construct, components inside system blocks were "
    "invisible. Workaround: We implemented a recursive _collect_elements() helper that "
    "traverses both model.elements and each system.elements, merging all components into a "
    "unified dictionary before generation. This preserves the flat deployment model (ADR-003) "
    "while supporting hierarchical modeling in the DSL."
)
pdf.multi_cell(0, 4.2, q2)
pdf.ln(2)

# --- Cluster Summary ---
pdf.set_font('Helvetica', 'B', 10)
pdf.set_text_color(40, 40, 120)
pdf.cell(0, 6, '3. Final Cluster Validation (35 containers)', new_x='LMARGIN', new_y='NEXT')
pdf.set_font('Helvetica', '', 9)
pdf.set_text_color(30, 30, 30)

q3 = (
    "Audit result: 65/70 tests passed. The 5 failures correspond to one-shot containers "
    "(dl, brake_actuator, balise, ccs_balise_a, ccs_balise_b) that exit after executing - "
    "architecturally correct behavior for non-persistent IoT emulators. All 30 persistent "
    "services (8 microservices, 4 T2 communication, 8 databases, 5 UIs, 5 physical) are "
    "healthy and responsive. The CCS subsystem operates independently with its own MAS "
    "and balise pair, validating the SoS decomposition."
)
pdf.multi_cell(0, 4.2, q3)

pdf.output('report.pdf')
print('report.pdf generated successfully.')
