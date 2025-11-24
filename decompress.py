import sys

# LZ77 Decompression
def lz77_decompress(comp: bytes) -> bytes:
    n = len(comp)
    i = 0
    out = bytearray()
    while i < n:
        flag = comp[i]
        i += 1
        if flag == 0:
            out.append(comp[i])
            i += 1
        elif flag == 1:
            length = comp[i]
            distance = comp[i + 1]
            i += 2
            start = len(out) - distance
            for _ in range(length):
                out.append(out[start])
                start += 1
    return bytes(out)

# Huffman decoding
def bytes_to_bits(data: bytes, pad: int):
    bits = "".join(f"{b:08b}" for b in data)
    return bits[:-pad] if pad else bits

def huffman_decode(bits: str, codebook):
    rev = {v: int(k) for k, v in (entry.split(":") for entry in codebook.split(";"))}
    out = bytearray()
    buf = ""
    for bit in bits:
        buf += bit
        if buf in rev:
            out.append(rev[buf])
            buf = ""
    return bytes(out)

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 decompress.py <input_file.br> <output_file>")
        sys.exit(1)

    inputPath = sys.argv[1]
    outputPath = sys.argv[2]

    with open(inputPath, "rb") as fin:
        blob = fin.read()

    cb_len = int.from_bytes(blob[0:4], "big")
    pos = 4
    codebook = blob[pos:pos+cb_len].decode()
    pos += cb_len
    pad = blob[pos]
    pos += 1
    packed = blob[pos:]

    bits = bytes_to_bits(packed, pad)
    lz_out = huffman_decode(bits, codebook)
    restored = lz77_decompress(lz_out)

    with open(outputPath, "wb") as fout:
        fout.write(restored)

    print(f"Decompressed {inputPath} → {outputPath}")

if __name__ == "__main__":
    main()
