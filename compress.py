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
