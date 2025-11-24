#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================"
echo "  Brotli Compression Test Suite"
echo "========================================"
echo ""

# Check if test_files directory exists
if [ ! -d "test_files" ]; then
    echo -e "${RED}Error: test_files directory not found!${NC}"
    exit 1
fi

# Count test files
num_files=$(ls test_files/test*.txt test_files/test*.py test_files/test*.json test_files/test*.html test_files/test*.csv 2>/dev/null | wc -l)
echo "Found $num_files test files"
echo ""

passed=0
failed=0

# Function to test a file
test_file() {
    local input_file=$1
    local test_name=$(basename "$input_file")
    local output_no_ctx="${test_name}.no_ctx.br"
    local output_ctx="${test_name}.ctx.br"
    local restored_no_ctx="${test_name}.no_ctx.restored"
    local restored_ctx="${test_name}.ctx.restored"
    
    echo -e "${BLUE}Testing: $test_name${NC}"
    echo "----------------------------------------"
    
    # Get original size
    original_size=$(wc -c < "$input_file")
    echo "  Original size: $original_size bytes"
    
    # Test without context
    echo -e "${YELLOW}  [1/2] Compressing without context...${NC}"
    if python3 compress.py "$input_file" "$output_no_ctx" > /dev/null 2>&1; then
        compressed_size=$(wc -c < "$output_no_ctx")
        ratio=$(echo "scale=2; $compressed_size * 100 / $original_size" | bc)
        echo "    Compressed: $compressed_size bytes (${ratio}% of original)"
        
        # Decompress and verify
        if python3 decompress.py "$output_no_ctx" "$restored_no_ctx" > /dev/null 2>&1; then
            if diff -q "$input_file" "$restored_no_ctx" > /dev/null 2>&1; then
                echo -e "    ${GREEN}✓ Verified: decompression successful${NC}"
                ((passed++))
            else
                echo -e "    ${RED}✗ Failed: files don't match${NC}"
                ((failed++))
            fi
        else
            echo -e "    ${RED}✗ Failed: decompression error${NC}"
            ((failed++))
        fi
    else
        echo -e "    ${RED}✗ Failed: compression error${NC}"
        ((failed++))
    fi
    
    # Test with context
    echo -e "${YELLOW}  [2/2] Compressing with context...${NC}"
    if python3 compress.py "$input_file" "$output_ctx" --use-context > /dev/null 2>&1; then
        compressed_size=$(wc -c < "$output_ctx")
        ratio=$(echo "scale=2; $compressed_size * 100 / $original_size" | bc)
        echo "    Compressed: $compressed_size bytes (${ratio}% of original)"
        
        # Decompress and verify
        if python3 decompress.py "$output_ctx" "$restored_ctx" > /dev/null 2>&1; then
            if diff -q "$input_file" "$restored_ctx" > /dev/null 2>&1; then
                echo -e "    ${GREEN}✓ Verified: decompression successful${NC}"
                ((passed++))
            else
                echo -e "    ${RED}✗ Failed: files don't match${NC}"
                ((failed++))
            fi
        else
            echo -e "    ${RED}✗ Failed: decompression error${NC}"
            ((failed++))
        fi
    else
        echo -e "    ${RED}✗ Failed: compression error${NC}"
        ((failed++))
    fi
    
    # Cleanup
    rm -f "$output_no_ctx" "$output_ctx" "$restored_no_ctx" "$restored_ctx"
    
    echo ""
}

# Test all files
for file in test_files/test*.txt test_files/test*.py test_files/test*.json test_files/test*.html test_files/test*.csv; do
    if [ -f "$file" ]; then
        test_file "$file"
    fi
done

# Summary
echo "========================================"
echo "  Test Results"
echo "========================================"
total=$((passed + failed))
echo -e "Total tests: $total"
echo -e "${GREEN}Passed: $passed${NC}"
if [ $failed -gt 0 ]; then
    echo -e "${RED}Failed: $failed${NC}"
else
    echo -e "Failed: $failed"
fi
echo ""

if [ $failed -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    exit 1
fi
