#!/bin/bash
PROJECT_DIR="/Users/sarp/Desktop/docs/cmpe 260 new project"
cd "$PROJECT_DIR"

PASSED=0
FAILED=0
TOTAL=0

echo "Running CMPE 260 Interpreter Tests..."
echo "--------------------------------------"

# Function to run a test
run_test() {
    local test_file=$1
    local scope=$2
    local expected=$3
    local base=$(basename "$test_file" .txt)
    local actual="${test_file%.txt}.actual"
    
    TOTAL=$((TOTAL + 1))
    
    if [ "$scope" == "dynamic" ]; then
        python3 interpreter.py --scope dynamic "$test_file" > "$actual" 2>&1
    elif [ "$scope" == "static" ]; then
        python3 interpreter.py --scope static "$test_file" > "$actual" 2>&1
    else
        python3 interpreter.py "$test_file" > "$actual" 2>&1
    fi
    
    if diff -q "$expected" "$actual" > /dev/null; then
        echo "✅ $base ($scope): PASSED"
        PASSED=$((PASSED + 1))
    else
        echo "❌ $base ($scope): FAILED"
        echo "   Diff:"
        diff -u "$expected" "$actual" | head -n 5
        FAILED=$((FAILED + 1))
    fi
}

# 1. Main tests (Lexical)
for test_file in tests/*.txt; do
    [ -f "$test_file" ] || continue
    run_test "$test_file" "default" "tests/$(basename "$test_file" .txt).expected"
done

# 2. Bonus tests
if [ -d "tests/bonus" ]; then
    echo ""
    echo "Running Bonus Tests..."
    echo "----------------------"
    for test_file in tests/bonus/*.txt; do
        [ -f "$test_file" ] || continue
        base=$(basename "$test_file" .txt)
        
        # Determine scope based on filename
        if [[ "$base" == *"_dynamic" ]]; then
            scope="dynamic"
        elif [[ "$base" == *"_static" ]]; then
            scope="static"
        else
            scope="default"
        fi
        
        run_test "$test_file" "$scope" "tests/bonus/$base.expected"
    done
fi

echo "--------------------------------------"
echo "Summary: $PASSED / $TOTAL passed."
if [ $FAILED -gt 0 ]; then
    exit 1
fi
