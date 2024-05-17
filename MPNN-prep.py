import sys
from Bio.PDB import PDBParser

def extract_residues_with_tempfactor(file_path, target_tempfactor=1.00):
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure('PDB', file_path)

    residues_with_target_tempfactor = set()

    for model in structure:
        for chain in model:
            for residue in chain:
                for atom in residue:
                    if atom.get_bfactor() == target_tempfactor:
                        residues_with_target_tempfactor.add(residue.id[1])

    return sorted(list(residues_with_target_tempfactor))

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <path_to_pdb_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    residues = extract_residues_with_tempfactor(file_path)
    print(" ".join(map(str, residues)))

if __name__ == '__main__':
    main()

