import sys
import brotli

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
    decompressed_data = brotli.decompress(compressed_data)

    # Write restored file
    with open(outputPath, "wb") as fout:
        fout.write(decompressed_data)

    print(f"Decompressed {inputPath} → {outputPath}")

if __name__ == "__main__":
    main()
