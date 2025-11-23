import sys
import brotli

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
    compressed_data = brotli.compress(data)

    # Write compressed output
    with open(outputPath, "wb") as fout:
        fout.write(compressed_data)

    print(f"Compressed {inputPath} → {outputPath}")

if __name__ == "__main__":
    main()
