#!/bin/bash
# test_cluster.sh - Testing and Audit Script for ERTMS System

# Exit on first failure of set -e but we want to continue, so we don't use it.
AUDIT_DIR="audits"
mkdir -p "$AUDIT_DIR"
AUDIT_FILE="$AUDIT_DIR/audit_report_$(date +%Y%m%d_%H%M%S).txt"

echo "=========================================" | tee "$AUDIT_FILE"
echo "   ERTMS CLUSTER AUDIT & TEST REPORT     " | tee -a "$AUDIT_FILE"
echo "   Date: $(date)                         " | tee -a "$AUDIT_FILE"
echo "=========================================" | tee -a "$AUDIT_FILE"

TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

run_test() {
    local component=$1
    local test_name=$2
    local command=$3

    ((TOTAL_TESTS++))
    # Pad component name for vertical alignment
    printf "%-25s | %-25s : " "$component" "$test_name" | tee -a "$AUDIT_FILE"
    
    # Run the command and capture output for debugging if needed (hidden unless failure)
    local output
    if output=$(eval "$command" 2>&1); then
        echo "✅ PASS" | tee -a "$AUDIT_FILE"
        ((PASSED_TESTS++))
    else
        echo "❌ FAIL" | tee -a "$AUDIT_FILE"
        echo "   -> Reason: $output" >> "$AUDIT_FILE" # Log failure reason to file only
        ((FAILED_TESTS++))
    fi
}

echo "" | tee -a "$AUDIT_FILE"
echo "--- 1. CONTAINER HEALTH CHECKS ---" | tee -a "$AUDIT_FILE"
COMPONENTS=(
    "portal" "dashboard" "driver_interface"
    "api_gateway"
    "passengers_ms" "routes_ms" "trains_ms" "position_time_ms" "tickets_ms" "mas"
    "passengers_db" "routes_db" "trains_db" "position_time_db" "dl"
    "onboard_unit" "train_sensor" "brake_actuator" "balise"
)

for comp in "${COMPONENTS[@]}"; do
    run_test "$comp" "Is Running" "docker inspect -f '{{.State.Running}}' skeleton-${comp}-1 | grep true"
done

echo "" | tee -a "$AUDIT_FILE"
echo "--- 2. MICROSERVICES HTTP ENDPOINTS (T3) ---" | tee -a "$AUDIT_FILE"
MICROSERVICES=("passengers_ms" "routes_ms" "trains_ms" "position_time_ms" "tickets_ms" "mas")
# We use Python's urllib to avoid relying on curl which isn't in python:3.11-slim
for ms in "${MICROSERVICES[@]}"; do
    run_test "$ms" "HTTP GET /health" "docker exec skeleton-${ms}-1 python -c \"import urllib.request; urllib.request.urlopen('http://localhost:80/health').read()\""
    
    if [ "$ms" != "mas" ]; then
        run_test "$ms" "HTTP GET /records" "docker exec skeleton-${ms}-1 python -c \"import urllib.request; urllib.request.urlopen('http://localhost:80/records').read()\""
    fi
done

echo "" | tee -a "$AUDIT_FILE"
echo "--- 3. DATABASE CONNECTIONS (T4) ---" | tee -a "$AUDIT_FILE"
DATABASES=("passengers_db" "routes_db" "trains_db" "position_time_db")
for db in "${DATABASES[@]}"; do
    run_test "$db" "MySQL Ping inside Container" "docker exec skeleton-${db}-1 mysqladmin ping -proot --silent"
done

echo "" | tee -a "$AUDIT_FILE"
echo "--- 4. PHYSICAL LAYER SIMULATORS (T5) ---" | tee -a "$AUDIT_FILE"
PHYSICAL=("onboard_unit" "train_sensor" "balise")
for phys in "${PHYSICAL[@]}"; do
    # Physical layer prints logs in loop
    run_test "$phys" "Log Generation" "docker logs skeleton-${phys}-1 | tail -n 5 | grep -q '\[.*\]'"
done
# Actuator just executes once, so we check if its initialization log exists
run_test "brake_actuator" "Action Execution" "docker logs skeleton-brake_actuator-1 | grep -q '\[ACTUATOR brake_actuator\]'"

echo "" | tee -a "$AUDIT_FILE"
echo "=========================================" | tee -a "$AUDIT_FILE"
echo "   AUDIT SUMMARY                         " | tee -a "$AUDIT_FILE"
echo "=========================================" | tee -a "$AUDIT_FILE"
echo "Total Tests Executed: $TOTAL_TESTS" | tee -a "$AUDIT_FILE"
echo "Passed              : $PASSED_TESTS" | tee -a "$AUDIT_FILE"
echo "Failed              : $FAILED_TESTS" | tee -a "$AUDIT_FILE"

if [ "$FAILED_TESTS" -eq 0 ]; then
    echo "Overall Status: ✅ SYSTEM HEALTHY" | tee -a "$AUDIT_FILE"
else
    echo "Overall Status: ❌ SYSTEM HAS ERRORS" | tee -a "$AUDIT_FILE"
fi
echo "=========================================" | tee -a "$AUDIT_FILE"
echo "Audit report saved detailing any errors to: $AUDIT_FILE"
