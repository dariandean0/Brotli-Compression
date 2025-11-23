# Brotli-Compression
CSE 4081 - Data Compression Group Project
Team: Vincenzo Barager, Darian Dean, Elton Batista

This project is an implementation of the Brotli compression algorithm in Python from scratch.

The (current) skeleton is two files, compress.py and decompress.py. compress.py takes an input file and produces a compressed output file and decompress.py will decompress the file into its original form (lossless). 

## Python Scripts

### compress.py
- Reads an input file
- Compresses it using Brotli
- Outputs a `.br` file

### decompress.py
- Reads a `.br` file
- Decompresses it back to the original file

---

## Workflow Example

1. Create a test file:
```bash
echo "hello hello hello world" > data/small.txt
```

2. Compress:
```bash
python3 compress.py data/small.txt out/small.br
```
Output:
```bash
Compressed data/small.txt → out/small.br
```

3. Decompress:
```bash
python3 decompress.py out/small.br restore/small.txt
```
Output:
```bash
Decompressed out/small.br → restore/small.txt
```

4. Verify Integrity:
```bash
diff -q data/small.txt restore/small.txt
```
No output means the files are identical.

5. Inspect file sizes:
```bash
ls -lh data/small.txt out/small.br restore/small.txt
```
Example Output:
```bash
-rw-r--r--  1 user  staff    24B data/small.txt
-rw-r--r--  1 user  staff    26B out/small.br
-rw-r--r--  1 user  staff    24B restore/small.txt
```
Note: Small files may not shrink (headers add overhead). Larger HTML/CSS/JS bundles show Brotli’s efficiency.
