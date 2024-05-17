import sys
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

def analyze_pdb(file_path):
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure('PDB_structure', file_path)
    output_parts = ["10-40"]

    for model in structure:
        for chain in model:
            chain_id = chain.id
            ranges = find_residue_ranges(chain)
            for start, end in ranges:
                output_parts.append(f"/{chain_id}{start}-{end}/10-40")

    return ''.join(output_parts)

def main():
    if len(sys.argv) < 2:
        print("Usage: python input_recog.py <path_to_pdb_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    result = analyze_pdb(file_path)
    print(result)

if __name__ == '__main__':
    main()

