import os
import sys
import warnings
import csv
from Bio.PDB import PDBParser, Superimposer, PDBIO

# 警告を無視する設定
warnings.simplefilter('ignore')

def extract_target_residues(structure, target_tempfactor=1.00):
    """Extract residues with a specific tempfactor."""
    target_residues = set()
    for model in structure:
        for chain in model:
            for residue in chain:
                for atom in residue:
                    if atom.get_bfactor() == target_tempfactor:
                        target_residues.add(residue.id[1])
    return target_residues

def extract_calpha_by_residues(structure, residues):
    """Extract CA atoms that belong to specified residues."""
    atoms = []
    for model in structure:
        for chain in model:
            for residue in chain:
                if residue.id[1] in residues:
                    ca_atom = next((atom for atom in residue if atom.get_name() == 'CA'), None)
                    if ca_atom:
                        atoms.append(ca_atom)
    return atoms

def compute_statistics(atoms):
    """Calculate statistics for a list of atoms."""
    tempfactors = [atom.get_bfactor() for atom in atoms]
    return {
        'mean': sum(tempfactors) / len(tempfactors),
        'max': max(tempfactors),
        'min': min(tempfactors)
    }

def align_pdb_and_compute_stats(ref_file, target_file, output_file, prefix, i, j, target_tempfactor=1.00):
    """Align PDBs based on specific criteria and compute statistics."""
    parser = PDBParser()
    ref_struct = parser.get_structure("Ref", ref_file)
    target_struct = parser.get_structure("Target", target_file)

    target_residues = extract_target_residues(ref_struct, target_tempfactor)
    ref_atoms = extract_calpha_by_residues(ref_struct, target_residues)
    target_atoms = extract_calpha_by_residues(target_struct, target_residues)

    super_imposer = Superimposer()
    if len(ref_atoms) == len(target_atoms):
        super_imposer.set_atoms(ref_atoms, target_atoms)
        super_imposer.apply(target_struct.get_atoms())

        io = PDBIO()
        io.set_structure(target_struct)
        io.save(output_file)

        rmsd = super_imposer.rms
        used_stats = compute_statistics(target_atoms)
        unused_target_atoms = [atom for atom in target_struct.get_atoms() if atom.get_name() == 'CA' and atom not in target_atoms]
        unused_stats = compute_statistics(unused_target_atoms)

        csv_file = prefix+'_align.csv'
        write_header = not os.path.exists(csv_file)
        with open(csv_file, 'a', newline='') as csvfile:
            fieldnames = ['model', 'seq', 'rmsd', 'used_mean_tf', 'used_max_tf', 'used_min_tf', 'unused_mean_tf', 'unused_max_tf', 'unused_min_tf']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if write_header:
                writer.writeheader()
            writer.writerow({
                'model': i,
                'seq': j,
                'rmsd': rmsd,
                'used_mean_tf': used_stats['mean'],
                'used_max_tf': used_stats['max'],
                'used_min_tf': used_stats['min'],
                'unused_mean_tf': unused_stats['mean'],
                'unused_max_tf': unused_stats['max'],
                'unused_min_tf': unused_stats['min']
            })
    else:
        print("Error: Atom lists differ in size, cannot align.")

if __name__ == "__main__":
    align_pdb_and_compute_stats(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])

