import sys
import argparse
from Bio.PDB import PDBParser

def find_residue_ranges(chain):
    # 残基のIDを取得し、ソートする
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

def analyze_pdb(file_path, adapter):
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure('PDB_structure', file_path)
    output_parts = []

    for model in structure:
        model_output = []
        for chain in model:
            chain_id = chain.id
            ranges = find_residue_ranges(chain)
            chain_output = []
            last_end = 0

            for start, end in ranges:
                # 欠落している残基範囲を計算
                if start > last_end + 1:
                    missing_count = start - last_end - 1
                    missing_range = f"{last_end+1}-{start-1}/{missing_count}-{missing_count}"
                    chain_output.append(missing_range)
                range_str = f"{chain_id}{start}-{end}"
                chain_output.append(range_str)
                last_end = end

            # 最後に '/0' を追加する前にリストが空でないことを確認
            if chain_output:
                chain_output[-1] += "/0"
                model_output.append("/".join(chain_output))

        if model_output:
            output_parts.append(" ".join(model_output))

    # アダプターを追加
    if adapter:
        output_parts.append(adapter)
    return " ".join(output_parts)

def main():
    parser = argparse.ArgumentParser(description="Analyze PDB file and customize chain formats with adapters.")
    parser.add_argument("pdb_file", help="Path to the PDB file")
    parser.add_argument("-a", "--adapter", default="", help="Adapter sequence to append at the end")
    args = parser.parse_args()

    result = analyze_pdb(args.pdb_file, args.adapter)
    print(result)

if __name__ == '__main__':
    main()
