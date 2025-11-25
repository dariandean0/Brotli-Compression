# Brotli-Compression
CSE 4081 - Data Compression Group Project
Team: Vincenzo Barager, Darian Dean, Elton Batista

This project is an implementation of the Brotli compression algorithm in Python from scratch.

---

## Algorithm Overview

Our implementation uses a three-stage compression pipeline:

### Stage 1: LZ77 Compression
**Purpose:** Replace repeated sequences with backreferences

**How it works:**
- Maintains a sliding window of the last 255 bytes
- Searches for matches of length 3-18 bytes
- Encodes matches as `(flag=1, length, distance)` tuples
- Encodes non-matching bytes as `(flag=0, byte)` literals

### Stage 2: Context Modeling
**Purpose:** Predict next symbol based on previous context

**How it works:**
- Trains first-order Markov model on input data
- Learns which symbols typically follow others
- Adjusts Huffman frequencies for predictable symbols
- Serializes model with compressed data using pickle library for simplicity and time

**Trade-off:**
- Adds ~1KB overhead for model storage
- Only beneficial for larger files with predictable patterns
- Our implementation shows limited benefit on small files

### Stage 3: Huffman Coding
**Purpose:** Assign shorter bit codes to frequent symbols

**How it works:**
- Builds frequency table from LZ77 output
- Constructs binary tree with frequent symbols near root
- Generates variable-length codes (frequent → short, rare → long)
- Stores codebook in compressed file for decompression

---

## Quick Start

### Basic Compression
```bash
# Compress a file
python3 compress.py input.txt output.br

# Decompress a file
python3 decompress.py output.br restored.txt

# Verify integrity
diff input.txt restored.txt
```

### With Context Modeling
```bash
# Compress with context modeling
python3 compress.py input.txt output.br --use-context

# Decompress (automatically detects context model)
python3 decompress.py output.br restored.txt
```

---

## Running Tests

### Run All Tests
```bash
./test_all.sh
```

This will:
- Test all 10 sample files in `test_files/`
- Compress with and without context modeling
- Verify data integrity with `diff`
- Display pass/fail results with color coding

### Individual File Tests
```bash
# Test with large file (LOTR)
python3 compress.py LOTR-The_Fellowship_of_the_Ring lotr.br --use-context
python3 decompress.py lotr.br lotr_restored.txt
diff LOTR-The_Fellowship_of_the_Ring lotr_restored.txt
```

### Sample Results

**LOTR File (1 MB):**
```
Original size:      1,001,864 bytes (978 KB)
Compressed size:    790,051 bytes (771 KB)
Compression ratio:  0.789
Space savings:      21.1%
Bits per byte:      6.31
```

**Small Test Files (< 2 KB):**
```
Most files EXPAND instead of compress:
- test10_small.txt: 79 → 414 bytes (5.2× larger)
- test2_english.txt: 1442 → 3335 bytes (2.3× larger)
- test1_repetitive.txt: 721 → 589 bytes (18% savings)
```

---

## Performance Analysis

### Why Small Files Don't Compress Well

Our implementation suffers from **high overhead** on small files:

**1. Codebook Storage**
- Huffman codebook stored as text: `"65:0101;66:0110;..."`
- For an 80-byte file, codebook is 400 bytes

**2. LZ77 Expansion**
- LZ77 output often LARGER than input for small files
- Each literal: 2 bytes (flag + data)
- Each match: 3 bytes (flag + length + distance)
- No repeated patterns in tiny files

**3. Context Model Overhead (~1 KB)**
- Pickle serialization of context model
- Only beneficial for larger files
- Smaller files: overhead exceeds benefit

### Limitations of This Implementation

**1. Small Window Size (255 bytes)**
- Real Brotli uses 16 MB window
- Our 255-byte window misses long-range patterns

**2. Short Max Match (18 bytes)**
- Real Brotli: up to 16 MB match
- Our limit: 18 bytes
- Long repeated sections require multiple matches

**3. Inefficient Codebook Format**
- Text-based storage wastes space
- Binary format would save space

**4. No Block Compression**
- Processes entire file at once
- Real Brotli splits into blocks with separate dictionaries

**5. Python vs C**
- Pure Python is slower
- No low-level bit manipulation optimizations

---

## Comparison with GZIP
### Why GZIP is Better

**1. Larger Window (32 KB vs 255 bytes)**
- GZIP can find repeated patterns from much further back
- Our window: last 255 bytes only
- GZIP window: last 32,768 bytes

**2. Optimized C Implementation**
- GZIP: assembly-optimized, 30+ years of refinement
- Ours: simple Python code

**3. Efficient Format**
- GZIP uses DEFLATE format (binary, compact)
- Our codebook: text-based, verbose

**4. Better Algorithm**
- GZIP: lazy matching, optimal parsing
- Ours: greedy matching
- GZIP makes smarter compression decisions

**5. Block Processing**
- GZIP: dynamic blocks with separate Huffman trees
- Ours: single Huffman tree for entire file
- GZIP adapts to changing data patterns
