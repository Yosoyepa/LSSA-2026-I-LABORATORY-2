"""Validate that all component/connector references in report.md exist in model.arch."""
import re

# Parse model.arch for valid component names
with open('../model.arch') as f:
    arch = f.read()

components = set()
for m in re.finditer(r'component\s+\w+\s+\w+\s+(\w+)', arch):
    components.add(m.group(1))

# Parse connector patterns
connectors = set()
for m in re.finditer(r'connector\s+(\w+)\s+(\w+)\s+->\s+(\w+)', arch):
    connectors.add((m.group(2), m.group(3)))  # (from, to)

# Extract backtick-quoted names from report
with open('report.md') as f:
    report = f.read()

# Find all backtick-quoted identifiers
refs = re.findall(r'`([a-z_]+(?:\s*->\s*[a-z_]+)?)`', report)

errors = []
for ref in refs:
    ref_clean = ref.strip()
    if '->' in ref_clean:
        parts = [p.strip() for p in ref_clean.split('->')]
        if len(parts) == 2:
            if (parts[0], parts[1]) not in connectors:
                errors.append(f"CONNECTOR NOT FOUND: {ref_clean}")
    elif ref_clean in ('data_flow', 'control_command', 'event_notification', 
                       'dependency', 'async_event', 'authority_service',
                       'operator_ui', 'web_interface', 'driver_ui',
                       'api_gateway_type', 'microservice', 'database',
                       'data_lake', 'event_store', 'onboard_unit_type',
                       'sensor', 'actuator', 'balise_type',
                       'presentation', 'communication', 'logic', 'data', 'physical',
                       'availability', 'critical', 'performance', 'realtime',
                       'security', 'public', 'restricted', 'privileged',
                       'timeout_ms', 'encrypted', 'true', 'interactive'):
        pass  # keyword/annotation, not a component name
    elif ref_clean not in components:
        errors.append(f"COMPONENT NOT FOUND: {ref_clean}")

if errors:
    print("❌ VALIDATION ERRORS:")
    for e in errors:
        print(f"  - {e}")
else:
    print("✅ All component and connector references in report.md are valid against model.arch")

# Also show stats
print(f"\nStats: {len(components)} components in model.arch, {len(connectors)} connectors, {len(refs)} references in report")
