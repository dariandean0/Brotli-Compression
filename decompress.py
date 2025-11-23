import sys

def lz77_decompress(compressed_data:bytes) -> bytes:
    n = len(compressed_data)
    i = 0
    out = bytearray()
    while i<n:
        flag = compressed_data[i]
        i+=1
        if flag == 0:
            out.append(compressed_data[i])
            i +=1
        elif flag ==1:
            length = compressed_data[i]
            distance = compressed_data[i+1]
            i +=2
            start = len(out) - distance
            for _ in range(length):
                out.append(out[start])
                start +=1
    return bytes(out)


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 decompress.py <input_file.br> <output_file>")
        sys.exit(1)

    inputPath = sys.argv[1]
    outputPath = sys.argv[2]

    # Read compressed file
    with open(inputPath, "rb") as fin:
        compressed_data = fin.read()

    # Decompress using Brotli
    decompressed_data = lz77_decompress(compressed_data)

    # Write restored file
    with open(outputPath, "wb") as fout:
        fout.write(decompressed_data)

    print(f"Decompressed {inputPath} → {outputPath}")

if __name__ == "__main__":
    main()
