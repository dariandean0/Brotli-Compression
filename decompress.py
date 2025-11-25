import sys
from context_model import ContextModel

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
        all_data = fin.read()
    
    # Check if context model is present
    context_model = None
    has_context = False
    compressed_data = all_data
    
    if len(all_data) > 8:
        # Look for context model marker from the end
        marker_pos = all_data.rfind(b"CTXMODEL")
        
        if marker_pos != -1:
            has_context = True
            # Extract the actual compressed data (before marker)
            compressed_data = all_data[:marker_pos]
            
            # Extract model size and data
            model_size_pos = marker_pos + 8  # After marker
            if model_size_pos + 4 <= len(all_data):
                model_size = int.from_bytes(
                    all_data[model_size_pos:model_size_pos + 4],
                    byteorder='little'
                )
                model_data_pos = model_size_pos + 4
                
                if model_data_pos + model_size <= len(all_data):
                    model_data = all_data[model_data_pos:model_data_pos + model_size]
                    
                    # Deserialize context model
                    context_model = ContextModel()
                    context_model.deserialize(model_data)
                    print("Context model detected and loaded")
                    
                    # Show model statistics
                    stats = context_model.get_context_statistics()
                    print(f"  Contexts: {stats['total_contexts']}")

    # Stage 1: Extract Huffman codebook
    print("Decoding Huffman...")
    cb_size = int.from_bytes(compressed_data[:4], "big")
    cb_bytes = compressed_data[4:4 + cb_size]
    codebook_str = cb_bytes.decode()
    pad = compressed_data[4 + cb_size]
    packed = compressed_data[4 + cb_size + 1:]
    
    # Stage 2: Decode Huffman
    bits = bytes_to_bits(packed, pad)
    lz_data = huffman_decode(bits, codebook_str)
    
    # Stage 3: Decode LZ77
    print("Decoding LZ77...")
    decompressed_data = lz77_decompress(lz_data)

    # Write restored file
    with open(outputPath, "wb") as fout:
        fout.write(decompressed_data)

    print(f"\n{'='*60}")
    print("DECOMPRESSION COMPLETE")
    print(f"{'='*60}")
    print(f"  Compressed size:    {len(all_data):,} bytes")
    print(f"  Decompressed size:  {len(decompressed_data):,} bytes")
    print(f"  Expansion ratio:    {len(decompressed_data)/len(all_data):.2f}x")
    print(f"  Context modeling:   {'enabled' if has_context else 'disabled'}")
    print(f"{'='*60}")
    print(f"Output: {inputPath} → {outputPath}")

if __name__ == "__main__":
    main()
