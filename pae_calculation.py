import os
import sys
import json
import numpy as np
import csv
from Bio.PDB import PDBParser

def extract_target_residues(structure, target_tempfactor=1.00):
    """Extract residues with a specific tempfactor."""
    target_residues = set()
    for model in structure:
        for chain in model:
            for residue in chain:
                for atom in residue:
                    if atom.get_name() == 'CA' and atom.get_bfactor() == target_tempfactor:
                        target_residues.add(residue.id[1])
    return target_residues

def load_error_matrix(json_path):
    """Load the predicted alignment error matrix from a JSON file."""
    with open(json_path, 'r') as file:
        data = json.load(file)
    return np.array(data['predicted_aligned_error'])

def calculate_stats_and_save_to_csv(error_matrix, target_mask, prefix, i, j):
    """Calculate stats and save results to a CSV file."""
    target_errors = error_matrix[target_mask][:, target_mask]
    non_target_errors = error_matrix[~target_mask][:, ~target_mask]
    cross_errors_1 = error_matrix[target_mask][:, ~target_mask]
    cross_errors_2 = error_matrix[~target_mask][:, target_mask]

    # Calculate means, minimums, and maximums
    target_mean, target_min, target_max = np.mean(target_errors), np.min(target_errors), np.max(target_errors)
    non_target_mean, non_target_min, non_target_max = np.mean(non_target_errors), np.min(non_target_errors), np.max(non_target_errors)
    cross_mean_1, cross_min_1, cross_max_1 = np.mean(cross_errors_1), np.min(cross_errors_1), np.max(cross_errors_1)
    cross_mean_2, cross_min_2, cross_max_2 = np.mean(cross_errors_2), np.min(cross_errors_2), np.max(cross_errors_2)

    # Prepare CSV data
    csv_file = f'{prefix}_pae_stats.csv'
    write_header = not os.path.exists(csv_file)
    with open(csv_file, 'a', newline='') as csvfile:
        fieldnames = ['model', 'seq', 'overall_mean', 'target_mean', 'target_min', 'target_max', 'non_target_mean', 'non_target_min', 'non_target_max', 'cross_mean_1', 'cross_min_1', 'cross_max_1', 'cross_mean_2', 'cross_min_2', 'cross_max_2']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow({
            'model': i,
            'seq': j,
            'overall_mean': np.mean(error_matrix),
            'target_mean': target_mean,
            'target_min': target_min,
            'target_max': target_max,
            'non_target_mean': non_target_mean,
            'non_target_min': non_target_min,
            'non_target_max': non_target_max,
            'cross_mean_1': cross_mean_1,
            'cross_min_1': cross_min_1,
            'cross_max_1': cross_max_1,
            'cross_mean_2': cross_mean_2,
            'cross_min_2': cross_min_2,
            'cross_max_2': cross_max_2
        })

def main(pdb_path, json_path, prefix, i, j):
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure('PDB', pdb_path)
    target_residues = extract_target_residues(structure)
    error_matrix = load_error_matrix(json_path)

    # Create a mask for indices of target residues
    all_residue_indices = {residue.id[1] for model in structure for chain in model for residue in chain}
    sorted_indices = sorted(all_residue_indices)
    index_map = {res_id: index for index, res_id in enumerate(sorted_indices)}
    target_indices = np.array([index_map[res_id] for res_id in target_residues if res_id in index_map])

    target_mask = np.zeros(len(sorted_indices), dtype=bool)
    target_mask[target_indices] = True

    calculate_stats_and_save_to_csv(error_matrix, target_mask, prefix, i, j)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])

