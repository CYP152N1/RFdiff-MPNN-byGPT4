import sys
import argparse
from Bio.PDB import PDBParser

def find_residue_ranges(chain):
    residues = sorted(res.get_id()[1] for res in chain if res.id[0] == ' ')
    if not residues:
        return []
    ranges = []
    start = residues[0]
    current = start
    for res in residues[1:]:
        if res != current + 1:
            ranges.append((start, current))
            start = res
        current = res
    ranges.append((start, current))
    return ranges

def analyze_pdb(file_path, linker, remove_n, remove_c):
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure('PDB_structure', file_path)
    output_parts = []
    prev_chain = None

    for model in structure:
        for chain in model:
            chain_id = chain.id
            ranges = find_residue_ranges(chain)
            chain_ranges = []

            for start, end in ranges:
                range_str = f"{chain_id}{start}-{end}"
                chain_ranges.append(range_str)

            chain_ranges_str = f"/{linker}/".join(chain_ranges)
            if prev_chain:
                chain_ranges_str = linker + "/" + chain_ranges_str
            output_parts.append(chain_ranges_str)
            prev_chain = chain

    if not remove_n:
        output_parts.insert(0, linker)
    if not remove_c:
        output_parts.append(linker)

    return "/".join(output_parts)

def main():
    parser = argparse.ArgumentParser(description="Analyze PDB file and extract residue ranges.")
    parser.add_argument("pdb_file", help="Path to the PDB file")
    parser.add_argument("-l", "--linker", default="10-40", help="Linker to insert between ranges")
    parser.add_argument("-rn", "--remove_n", action="store_true", help="Remove the first linker")
    parser.add_argument("-rc", "--remove_c", action="store_true", help="Remove the last linker")
    args = parser.parse_args()

    result = analyze_pdb(args.pdb_file, args.linker, args.remove_n, args.remove_c)
    print(result)

if __name__ == '__main__':
    main()

