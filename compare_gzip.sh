# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'
BOLD='\033[1m'

# Test file
TEST_FILE="${1:-LOTR-The_Fellowship_of_the_Ring}"

if [ ! -f "$TEST_FILE" ]; then
    echo -e "${RED}Error: File '$TEST_FILE' not found${NC}"
    echo "Usage: $0 [filename]"
    exit 1
fi

echo -e "${BOLD}${BLUE}========================================"
echo "  GZIP vs Our Brotli Comparison"
echo -e "========================================${NC}"
echo

ORIGINAL_SIZE=$(wc -c < "$TEST_FILE")
echo -e "${BOLD}Test File:${NC} $TEST_FILE"
echo -e "${BOLD}Original Size:${NC} $ORIGINAL_SIZE bytes ($(echo "scale=2; $ORIGINAL_SIZE/1024" | bc) KB)"
echo

# Temporary files
BROTLI_OUT="temp_brotli.br"
BROTLI_DEC="temp_brotli_dec.txt"
GZIP_OUT="temp_gzip.gz"

echo -e "${BOLD}${BLUE}=======================================${NC}"
echo -e "${BOLD}${BLUE}  Testing Our Brotli Implementation${NC}"
echo -e "${BOLD}${BLUE}=======================================${NC}"

# Test our Brotli implementation
echo -e "${YELLOW}Compressing with our Brotli...${NC}"
BROTLI_START=$(date +%s.%N)
python3 compress.py "$TEST_FILE" "$BROTLI_OUT" 2>&1 | grep -E "COMPRESSION COMPLETE|Original size|Final compressed|Compression ratio|Space savings|Bits per byte" || true
BROTLI_END=$(date +%s.%N)
BROTLI_TIME=$(echo "$BROTLI_END - $BROTLI_START" | bc)

if [ ! -f "$BROTLI_OUT" ]; then
    echo -e "${RED}✗ Compression failed${NC}"
    exit 1
fi

BROTLI_SIZE=$(wc -c < "$BROTLI_OUT")
BROTLI_RATIO=$(echo "scale=3; $BROTLI_SIZE / $ORIGINAL_SIZE" | bc)
BROTLI_SAVINGS=$(echo "scale=1; (1 - $BROTLI_RATIO) * 100" | bc)
BROTLI_BPB=$(echo "scale=2; $BROTLI_SIZE * 8 / $ORIGINAL_SIZE" | bc)

echo
echo -e "${GREEN}Compressed:${NC} $BROTLI_SIZE bytes ($(echo "scale=2; $BROTLI_SIZE/1024" | bc) KB)"
echo -e "${GREEN}Ratio:${NC} $BROTLI_RATIO"
echo -e "${GREEN}Savings:${NC} $BROTLI_SAVINGS%"
echo -e "${GREEN}Bits/Byte:${NC} $BROTLI_BPB"
echo -e "${GREEN}Time:${NC} ${BROTLI_TIME}s"

# Verify decompression
echo -e "${YELLOW}Verifying decompression...${NC}"
python3 decompress.py "$BROTLI_OUT" "$BROTLI_DEC" > /dev/null 2>&1

if diff -q "$TEST_FILE" "$BROTLI_DEC" > /dev/null 2>&1; then
    echo -e "${GREEN}Decompression successful - files match${NC}"
else
    echo -e "${RED}Decompression failed - files don't match${NC}"
    exit 1
fi

echo

echo -e "${BOLD}${BLUE}========================================${NC}"
echo -e "${BOLD}${BLUE}  Testing GZIP${NC}"
echo -e "${BOLD}${BLUE}========================================${NC}"

# Test GZIP (level 9)
echo -e "${YELLOW}Compressing with GZIP (level 9)...${NC}"
GZIP_START=$(date +%s.%N)
gzip -9 -c "$TEST_FILE" > "$GZIP_OUT"
GZIP_END=$(date +%s.%N)
GZIP_TIME=$(echo "$GZIP_END - $GZIP_START" | bc)

GZIP_SIZE=$(wc -c < "$GZIP_OUT")
GZIP_RATIO=$(echo "scale=3; $GZIP_SIZE / $ORIGINAL_SIZE" | bc)
GZIP_SAVINGS=$(echo "scale=1; (1 - $GZIP_RATIO) * 100" | bc)
GZIP_BPB=$(echo "scale=2; $GZIP_SIZE * 8 / $ORIGINAL_SIZE" | bc)

echo -e "${GREEN}Compressed:${NC} $GZIP_SIZE bytes ($(echo "scale=2; $GZIP_SIZE/1024" | bc) KB)"
echo -e "${GREEN}Ratio:${NC} $GZIP_RATIO"
echo -e "${GREEN}Savings:${NC} $GZIP_SAVINGS%"
echo -e "${GREEN}Bits/Byte:${NC} $GZIP_BPB"
echo -e "${GREEN}Time:${NC} ${GZIP_TIME}s"

# Verify GZIP decompression
echo -e "${YELLOW}Verifying GZIP decompression...${NC}"
if gunzip -t "$GZIP_OUT" 2>/dev/null; then
    echo -e "${GREEN}GZIP decompression successful${NC}"
else
    echo -e "${RED}GZIP verification failed${NC}"
fi

echo

echo -e "${BOLD}${BLUE}========================================${NC}"
echo -e "${BOLD}${BLUE}  Comparison Results${NC}"
echo -e "${BOLD}${BLUE}========================================${NC}"

# Calculate differences
SIZE_DIFF=$(echo "$BROTLI_SIZE - $GZIP_SIZE" | bc)
SIZE_DIFF_PERCENT=$(echo "scale=1; ($BROTLI_SIZE / $GZIP_SIZE - 1) * 100" | bc)
SAVINGS_DIFF=$(echo "scale=1; $GZIP_SAVINGS - $BROTLI_SAVINGS" | bc)
SPEED_RATIO=$(echo "scale=1; $BROTLI_TIME / $GZIP_TIME" | bc)

echo
printf "%-25s %15s %15s %15s\n" "Metric" "Our Brotli" "GZIP" "Difference"
echo "--------------------------------------------------------------------------"
printf "%-25s %15s %15s %15s\n" "Compressed Size" "$BROTLI_SIZE bytes" "$GZIP_SIZE bytes" "+$SIZE_DIFF bytes"
printf "%-25s %15s %15s %15s\n" "Compression Ratio" "$BROTLI_RATIO" "$GZIP_RATIO" "$(echo "scale=3; $BROTLI_RATIO - $GZIP_RATIO" | bc)"
printf "%-25s %15s %15s %15s\n" "Space Savings" "$BROTLI_SAVINGS%" "$GZIP_SAVINGS%" "-$SAVINGS_DIFF%"
printf "%-25s %15s %15s %15s\n" "Bits per Byte" "$BROTLI_BPB" "$GZIP_BPB" "$(echo "scale=2; $BROTLI_BPB - $GZIP_BPB" | bc)"
printf "%-25s %15s %15s %15s\n" "Compression Time" "${BROTLI_TIME}s" "${GZIP_TIME}s" "${SPEED_RATIO}× slower"
echo

echo -e "${BOLD}Summary:${NC}"
echo -e "  - GZIP compressed ${SIZE_DIFF_PERCENT}% better than our implementation"
echo -e "  - GZIP achieved ${SAVINGS_DIFF}% more space savings"
echo -e "  - GZIP was ${SPEED_RATIO}× faster"

# Clean up
rm -f "$BROTLI_OUT" "$BROTLI_DEC" "$GZIP_OUT"

echo
