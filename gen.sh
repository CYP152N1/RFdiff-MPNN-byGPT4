#!/bin/bash

# このスクリプトは、input_pdbのパスを引数として受け取ります。
if [[ -z "$1" ]]; then
    echo "Usage: $0 <path_to_input_pdb>"
    exit 1
fi
input_pdb_path=$1

if [ ! -f "$input_pdb_path" ]; then
    echo "Error: File not found - $input_pdb_path"
    exit 1
fi


# 日付を yyyy-mm-dd 形式で取得
current_date=$(date +%Y-%m-%d)

# PDB ファイルの名前からプレフィックスを抽出（拡張子前の部分のみ取得）
pdb_prefix=$(basename "$input_pdb_path" .pdb)

# 出力ディレクトリのパスを設定
output_pref="$(pwd)/output/$pdb_prefix/RFdiffusion/$current_date/$pdb_prefix"
output_dir="$(pwd)/output/$pdb_prefix/RFdiffusion/$current_date"

# Pythonスクリプトを実行し、出力を変数に格納します。
output=$(python3 input_recog.py "$input_pdb_path")
if [ $? -ne 0 ]; then
    echo "Error: Python script execution failed."
    exit 1
fi
# シェルスクリプトを生成します。
cat <<EOF > run_inference.sh
#!/bin/bash

# 以下のコマンドは生成されたパラメータを用いて実行されます。
# ModuleNotFoundError: No module named 'torchと出る場合は conda activate SE3nvを忘れています。
# conda info -e等で読み込むconda環境の名前を確認してください。
# 環境構築がうまく行かない場合は参照: https://github.com/RosettaCommons/RFdiffusion/issues/14

/home/mdonoda/data/RFdiffusion/RFdiffusion/scripts/run_inference.py inference.output_prefix=$output_pref 'contigmap.contigs=[$output]' inference.input_pdb=$input_pdb_path inference.num_designs=100
EOF

# 生成したシェルスクリプトを実行可能にします。
chmod +x run_inference.sh
if [ $? -ne 0 ]; then
    echo "Error: Failed to make the script executable."
    exit 1
fi

# スクリプトの内容を表示します
cat run_inference.sh

# スクリプトを実行します
./run_inference.sh
if [ $? -ne 0 ]; then
    echo "Error: Inference script failed to execute successfully."
    exit 1
fi

# PDBファイルを個別のフォルダに移動
echo "Looking for PDB files starting with prefix: $output_pref"
for file in ${output_pref}_*.pdb
do
    echo "Checking file: $file"
    if [ -f "$file" ]; then
        echo "Found file: $file"
        dir_name="${file%.*}" # Remove the extension to use as directory name
        echo "Creating directory: $dir_name"
        mkdir -p "$dir_name"
        echo "Moving $file to $dir_name"
        mv "$file" "$dir_name/"

        # Run Python script to prepare data for ProteinMPNN
        echo "Preparing data for ProteinMPNN with: $dir_name/$(basename "$file")"
        fixed_positions=$(python3 MPNN-prep.py "$dir_name/$(basename "$file")")

        # Generate and execute a script for ProteinMPNN
        protein_mpnn_output_dir="$(pwd)/output/$pdb_prefix/ProteinMPNN/$current_date/$(basename "$dir_name")"
        mkdir -p "$protein_mpnn_output_dir"
        cat <<MPNNEOF > "${dir_name}/generated_script.sh"
#!/bin/bash
#SBATCH -p gpu
#SBATCH --mem=32g
#SBATCH --gres=gpu:rtx2080:1
#SBATCH -c 3
#SBATCH --output=${protein_mpnn_output_dir}/${current_date}.out

folder_with_pdbs="$dir_name"
output_dir="$protein_mpnn_output_dir"
path_for_parsed_chains="\$output_dir/parsed_pdbs.jsonl"
path_for_assigned_chains="\$output_dir/assigned_pdbs.jsonl"
path_for_fixed_positions="\$output_dir/fixed_pdbs.jsonl"
chains_to_design="A"
fixed_positions="$fixed_positions"

# Run ProteinMPNN helper scripts and main script
python /home/mdonoda/data/RFdiffusion/ProteinMPNN/helper_scripts/parse_multiple_chains.py --input_path=\$folder_with_pdbs --output_path=\$path_for_parsed_chains
python /home/mdonoda/data/RFdiffusion/ProteinMPNN/helper_scripts/assign_fixed_chains.py --input_path=\$path_for_parsed_chains --output_path=\$path_for_assigned_chains --chain_list "\$chains_to_design"
python /home/mdonoda/data/RFdiffusion/ProteinMPNN/helper_scripts/make_fixed_positions_dict.py --input_path=\$path_for_parsed_chains --output_path=\$path_for_fixed_positions --chain_list "\$chains_to_design" --position_list "\$fixed_positions"
python /home/mdonoda/data/RFdiffusion/ProteinMPNN/protein_mpnn_run.py \
        --jsonl_path \$path_for_parsed_chains \
        --chain_id_jsonl \$path_for_assigned_chains \
        --fixed_positions_jsonl \$path_for_fixed_positions \
        --out_folder \$output_dir \
        --num_seq_per_target 100 \
        --sampling_temp "0.1" \
        --seed 37 \
        --batch_size 1

MPNNEOF

        # Make script executable and run it
        chmod +x "${dir_name}/generated_script.sh"
        "${dir_name}/generated_script.sh"
    else
        echo "File not found: $file"
    fi
done

