import sys
from context_model import ContextModel, analyze_context_benefit

# LZ77
winSize = 255
maxMatchSize = 18
minMatchSize = 3

def lz77(data: bytes) -> bytes:
    i = 0
    n = len(data)
    out = bytearray()
    while i < n:
        winStart = max(0, i - winSize)
        bestSize = 0
        bestDist = 0

        if i > winStart:
            maxSize = min(maxMatchSize, n - i)
            winLen = i - winStart + 1
            for distance in range(1, winLen):
                start = i - distance
                length = 0
                while length < maxSize and data[start + length] == data[i + length]:
                    length += 1
                if length >= minMatchSize and length > bestSize:
                    bestSize = length
                    bestDist = distance
        if bestSize >= minMatchSize:
            out.append(1)
            out.append(bestSize)
            out.append(bestDist)
            i += bestSize
        else:
            out.append(0)
            out.append(data[i])
            i += 1
    return bytes(out)

# Huffman coding
class Node:
    def __init__(self, symbol=None, freq=0, left=None, right=None):
        self.symbol = symbol
        self.freq = freq
        self.left = left
        self.right = right

def build_frequency(data: bytes):
    freq = {}
    for b in data:
        freq[b] = freq.get(b, 0) + 1
    return freq

def build_tree(freq):
    nodes = [Node(sym, f) for sym, f in freq.items()]
    while len(nodes) > 1:
        nodes.sort(key=lambda n: n.freq)
        left = nodes.pop(0)
        right = nodes.pop(0)
        merged = Node(None, left.freq + right.freq, left, right)
        nodes.append(merged)
    return nodes[0]

def generate_codes(node, prefix="", codebook=None):
    if codebook is None:
        codebook = {}
    if node.symbol is not None:
        codebook[node.symbol] = prefix or "0"
    else:
        generate_codes(node.left, prefix + "0", codebook)
        generate_codes(node.right, prefix + "1", codebook)
    return codebook

def huffman_encode(data: bytes, codebook):
    return "".join(codebook[b] for b in data)

def bits_to_bytes(bits: str):
    pad = (8 - len(bits) % 8) % 8
    bits += "0" * pad
    out = bytearray()
    for i in range(0, len(bits), 8):
        out.append(int(bits[i:i+8], 2))
    return bytes(out), pad

def main():
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Usage: python3 compress.py <input_file> <output_file> [--use-context]")
        sys.exit(1)

    inputPath = sys.argv[1]
    outputPath = sys.argv[2]
    use_context = len(sys.argv) == 4 and sys.argv[3] == "--use-context"

    with open(inputPath, "rb") as fin:
        data = fin.read()

    # Analyze if context modeling would be beneficial
    if use_context:
        print("Analyzing data for context modeling benefit...")
        analysis = analyze_context_benefit(data, order=1)
        print(f"  Predictable symbols: {analysis['predictable_ratio']:.1%}")
        print(f"  Estimated entropy reduction: {analysis['entropy_reduction']:.1%}")
        print(f"  Recommendation: {analysis['recommendation']}")
        
        # Train context model
        print("\nTraining context model...")
        context_model = ContextModel(order=1)
        context_model.train(data)
        
        # Get context statistics
        stats = context_model.get_context_statistics()
        print(f"  Contexts learned: {stats['total_contexts']}")
        print(f"  Total observations: {stats['total_observations']}")

    # Stage 1: LZ77 compression
    print(f"\nApplying LZ77 compression...")
    lz_out = lz77(data)
    print(f"  After LZ77: {len(lz_out):,} bytes")

    # Stage 2: Build frequency table (with or without context modeling)
    if use_context:
        print("\nApplying context-aware frequencies for Huffman...")
        freq = context_model.get_adaptive_frequencies(lz_out)
    else:
        freq = build_frequency(lz_out)
    
    # Stage 3: Huffman encoding
    print("Applying Huffman encoding...")
    tree = build_tree(freq)
    codebook = generate_codes(tree)
    encoded_bits = huffman_encode(lz_out, codebook)
    packed, pad = bits_to_bytes(encoded_bits)
    print(f"  After Huffman: {len(packed):,} bytes")

    # Save: codebook size + codebook + pad + packed bits
    codebook_str = ";".join(f"{k}:{v}" for k, v in codebook.items())
    cb_bytes = codebook_str.encode()
    with open(outputPath, "wb") as fout:
        fout.write(len(cb_bytes).to_bytes(4, "big"))
        fout.write(cb_bytes)
        fout.write(bytes([pad]))
        fout.write(packed)
        
        # If context modeling was used, append the serialized model
        if use_context:
            # Add a marker to indicate context model is present
            fout.write(b"CTXMODEL")
            serialized_model = context_model.serialize()
            # Write model size then model data
            fout.write(len(serialized_model).to_bytes(4, byteorder='little'))
            fout.write(serialized_model)

    # Calculate final statistics
    original_size = len(data)
    import os
    compressed_size = os.path.getsize(outputPath)
    ratio = compressed_size / original_size if original_size > 0 else 0
    
    print(f"\n{'='*60}")
    print("COMPRESSION COMPLETE")
    print(f"{'='*60}")
    print(f"  Original size:      {original_size:,} bytes")
    print(f"  LZ77 output:        {len(lz_out):,} bytes ({len(lz_out)/original_size:.1%})")
    print(f"  Huffman output:     {len(packed):,} bytes ({len(packed)/len(lz_out):.1%} of LZ77)")
    print(f"  Final compressed:   {compressed_size:,} bytes")
    print(f"  Compression ratio:  {ratio:.3f}")
    print(f"  Space savings:      {(1-ratio)*100:.1f}%")
    print(f"  Bits per byte:      {(compressed_size * 8) / original_size:.2f}")
    print(f"  Context modeling:   {'enabled' if use_context else 'disabled'}")
    print(f"{'='*60}")
    print(f"Output: {inputPath} → {outputPath}")

if __name__ == "__main__":
    main()
import sys

# LZ77
winSize = 255
maxMatchSize = 18
minMatchSize = 3

def lz77(data: bytes) -> bytes:
    i = 0
    n = len(data)
    out = bytearray()
    while i < n:
        winStart = max(0, i - winSize)
        bestSize = 0
        bestDist = 0

        if i > winStart:
            maxSize = min(maxMatchSize, n - i)
            winLen = i - winStart + 1
            for distance in range(1, winLen):
                start = i - distance
                length = 0
                while length < maxSize and data[start + length] == data[i + length]:
                    length += 1
                if length >= minMatchSize and length > bestSize:
                    bestSize = length
                    bestDist = distance
        if bestSize >= minMatchSize:
            out.append(1)
            out.append(bestSize)
            out.append(bestDist)
            i += bestSize
        else:
            out.append(0)
            out.append(data[i])
            i += 1
    return bytes(out)

# Huffman coding
class Node:
    def __init__(self, symbol=None, freq=0, left=None, right=None):
        self.symbol = symbol
        self.freq = freq
        self.left = left
        self.right = right

def build_frequency(data: bytes):
    freq = {}
    for b in data:
        freq[b] = freq.get(b, 0) + 1
    return freq

def build_tree(freq):
    nodes = [Node(sym, f) for sym, f in freq.items()]
    while len(nodes) > 1:
        nodes.sort(key=lambda n: n.freq)
        left = nodes.pop(0)
        right = nodes.pop(0)
        merged = Node(None, left.freq + right.freq, left, right)
        nodes.append(merged)
    return nodes[0]

def generate_codes(node, prefix="", codebook=None):
    if codebook is None:
        codebook = {}
    if node.symbol is not None:
        codebook[node.symbol] = prefix or "0"
    else:
        generate_codes(node.left, prefix + "0", codebook)
        generate_codes(node.right, prefix + "1", codebook)
    return codebook

def huffman_encode(data: bytes, codebook):
    return "".join(codebook[b] for b in data)

def bits_to_bytes(bits: str):
    pad = (8 - len(bits) % 8) % 8
    bits += "0" * pad
    out = bytearray()
    for i in range(0, len(bits), 8):
        out.append(int(bits[i:i+8], 2))
    return bytes(out), pad

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 compress.py <input_file> <output_file>")
        sys.exit(1)

    inputPath = sys.argv[1]
    outputPath = sys.argv[2]

    with open(inputPath, "rb") as fin:
        data = fin.read()

    # Stage 1: LZ77
    lz_out = lz77(data)

    # Stage 2: Huffman
    freq = build_frequency(lz_out)
    tree = build_tree(freq)
    codebook = generate_codes(tree)
    encoded_bits = huffman_encode(lz_out, codebook)
    packed, pad = bits_to_bytes(encoded_bits)

    # Save: codebook size + codebook + pad + packed bits
    codebook_str = ";".join(f"{k}:{v}" for k, v in codebook.items())
    cb_bytes = codebook_str.encode()
    with open(outputPath, "wb") as fout:
        fout.write(len(cb_bytes).to_bytes(4, "big"))
        fout.write(cb_bytes)
        fout.write(bytes([pad]))
        fout.write(packed)

    print(f"Compressed {inputPath} → {outputPath}")

if __name__ == "__main__":
    main()
