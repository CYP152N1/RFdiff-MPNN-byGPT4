import os
import sys
import warnings
import csv
from Bio.PDB import PDBParser, Superimposer, PDBIO, Selection

warnings.simplefilter('ignore')

def get_chain(structure, chain_id):
    """Retrieve a specific chain from the structure."""
    for model in structure:
        for chain in model:
            if chain.id == chain_id:
                return chain
    return None

def align_structures(ref_chain, target_chain):
    """Align two chains based on Cα atoms and return the superimposer object."""
    ref_atoms = [residue['CA'] for residue in ref_chain if 'CA' in residue]
    target_atoms = [residue['CA'] for residue in target_chain if 'CA' in residue]
    super_imposer = Superimposer()
    super_imposer.set_atoms(ref_atoms, target_atoms)
    super_imposer.apply(target_chain.get_parent().get_atoms())
    return super_imposer

def compute_rmsd(ref_atoms, target_atoms):
    """Compute RMSD between two sets of atoms."""
    super_imposer = Superimposer()
    super_imposer.set_atoms(ref_atoms, target_atoms)
    return super_imposer.rms

def process_structure(ref_file, target_file, output_file, prefix, model_idx, seq_idx):
    parser = PDBParser()
    ref_struct = parser.get_structure("Ref", ref_file)
    target_struct = parser.get_structure("Target", target_file)

    ref_chain_a = get_holder_chain(ref_struct, 'A')
    target_chain_a = get_chain(target_struct, 'A')

    if not ref_chain_a or not target_chain_a:
        print("Chain A not found in one of the structures.")
        return

    # Align the structure based on Chain A
    super_imposer = align_structures(ref_chain_a, target_chain_a)

    # Compute RMSD for each chain after alignment
    fieldnames = ['model', 'seq']
    results = {'model': model_idx, 'seq': seq_idx}

    for chain_id in target_struct[0].child_dict:
        target_chain = get_chain(target_struct, chain_id)
        ref_chain = get_chain(ref_struct, chain_id)
        if target_chain and ref_chain:
            ref_atoms = [residue['CA'] for residue in ref_chain if 'CA' in residue]
            target_atoms = [residue['CA'] for residue in target_chain if 'CA' in residue]
            rmsd = compute_rmsd(ref_atoms, target_atoms)
            results[f'rmsd_{chain_id}'] = rmsd
            fieldnames.append(f'rmsd_{chain_id}')

    # Save aligned structure and results
    io = PDBIO()
    io.set_structure(target_struct)
    io.save(output_file)

    # Write to CSV
    csv_file = f"{prefix}_align.csv"
    with open(csv_file, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not os.path.exists(csv_file):
            writer.writeheader()
        writer.writerow(results)

if __name__ == "__main__":
    process_structure(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]), int(sys.argv[6]))
