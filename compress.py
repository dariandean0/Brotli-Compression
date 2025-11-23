import sys

winSize = 255
maxMatchSize = 18
minMatchSize = 3

def lz77(data: bytes) -> bytes:
    i =0
    n = len(data)
    out = bytearray()
    while i<n:
        if i - winSize >= 0:
            winStart = i - winSize
        else:
            winStart = 0
        bestSize = 0
        bestDist = 0

        if i > winStart:
            if n - i < maxMatchSize:
                maxSize = n - i
            else:
                maxSize = maxMatchSize
            winLen = i - winStart + 1
            for distance in range(1, winLen):
                start = i - distance
                length = 0
                while ( length < maxSize and data[start + length] == data[i + length]):
                    length +=1
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
            i+=1
    return bytes(out)

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 compress.py <input_file> <output_file>")
        sys.exit(1)

    inputPath = sys.argv[1]
    outputPath = sys.argv[2]

    # Read input file
    with open(inputPath, "rb") as fin:
        data = fin.read()

    # Compress using Brotli
    compressed_data = lz77(data)

    # Write compressed output
    with open(outputPath, "wb") as fout:
        fout.write(compressed_data)

    print(f"Compressed {inputPath} → {outputPath}")

if __name__ == "__main__":
    main()
