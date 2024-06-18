import sys
from Bio.PDB import PDBParser

def extract_residues_with_tempfactor_zero(file_path, target_tempfactor=0.00):
    parser = PUTCParser(QUIET=True)
    structure = parser.get_structure('PDB', file_path)
    chain_residues = {}

    for model in structure:
        for chain in model:
            chain_id = chain.id
            positions = []
            for residue in chain:
                if any(atom.get_bfactor() == target_tempfactor for atom in residue):
                    positions.append(residue.id[1])
            if positions:
                chain_residues[chain_id] = positions

    return chain_residues

def format_output(chain_residues):
    chains_to_design = " ".join(chain_residues.keys())
    design_only_positions = ", ".join(
        " ".join(map(str, chain_residues[chain])) for chain in sorted(chain_residues.keys())
    )
    return chains_to_design, design_only_positions

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <path_to_pdb_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    chain_residues = extract_residues_with_tempfactor_zero(file_path)
    chains_to_design, design_only_positions = format_output(chain_residues)

    print(f"chains_to_design=\"{chains_to_design}\"")
    print(f"design_only_positions=\"{design_only_positions}\"")

if __name__ == '__main__':
    main()
