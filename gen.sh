#!/bin/bash
RFDIFFUSION_PATH=/pass/to/RFdiffusion
PROTEINMPNN_PATH=/pass/to/ProteinMPNN
GENSH_PATH=/pass/to/RFdiff-MPNN-byGPT4
RFDIFF_num_designs=2  # Default value for number of designs
MPNN_num_seq=2        # Default value for number of sequences
custom_output=""      # Default value, auto-generated from PDB unless specified
linker_range="10-40"  # Default linker range
remove_n=false        # Option to remove the initial linker
remove_c=false        # Option to remove the final linker

# Process command line arguments manually
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--pdb)
            input_pdb_path="$2"
            shift 2
            ;;
        -nd|--num_designs)
            RFDIFF_num_designs="$2"
            shift 2
            ;;
        -ns|--num_sequences)
            MPNN_num_seq="$2"
            shift 2
            ;;
        -c|--custom_out)
            custom_output="$2"
            shift 2
            ;;
        -l|--linker)
            linker_range="$2"
            shift 2
            ;;
        -rn)
            remove_n=true
            shift
            ;;
        -rc)
            remove_c=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

echo "PDB Path: $input_pdb_path"
echo "Remove N: $remove_n"
echo "Remove C: $remove_c"
echo "Linker Range: $linker_range"
echo "Command Args: $command_args"

# Validate mandatory PDB path
if [[ -z "$input_pdb_path" ]]; then
    echo "Error: No input PDB path provided."
    exit 1
fi

if [ ! -f "$input_pdb_path" ]; then
    echo "Error: File not found - $input_pdb_path"
    exit 1
fi

# Get current date in yyyy-mm-dd format
current_date=$(date +%Y-%m-%d)

# Extract the prefix from the PDB file name (the part before the extension)
pdb_prefix=$(basename "$input_pdb_path" .pdb)

# Set up the output directory path
output_pref="$(pwd)/output/$pdb_prefix/RFdiffusion/$current_date/$pdb_prefix"
output_dir="$(pwd)/output/$pdb_prefix/RFdiffusion/$current_date"

# コマンド引数の構築
command_args=""
[[ "$remove_n" == "true" ]] && command_args+="-rn "
[[ "$remove_c" == "true" ]] && command_args+="-rc "
command_args+="-l $linker_range"


echo "Command Args: $command_args"  # デバッグ出力

# Pythonスクリプトの実行
# Pythonスクリプトの実行条件を調整
if [[ -n "$custom_output" ]]; then
    # custom_outputが指定されている場合、Pythonスクリプトの実行をスキップ
    output="$custom_output"
else
    # custom_outputが指定されていない場合、Pythonスクリプトを実行
    output=$(python3 "${GENSH_PATH}"/input_recog.py "$input_pdb_path" $command_args)
    if [ $? -ne 0 ]; then
        echo "Error: Python script execution failed."
        exit 1
    fi
fi

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

${RFDIFFUSION_PATH}/scripts/run_inference.py inference.output_prefix=$output_pref 'contigmap.contigs=[$output]' inference.input_pdb=$input_pdb_path inference.num_designs=$RFDIFF_num_designs
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
        fixed_positions=$(python3 "${GENSH_PATH}"/MPNN-prep.py "$dir_name/$(basename "$file")")

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
python ${PROTEINMPNN_PATH}//helper_scripts/parse_multiple_chains.py --input_path=\$folder_with_pdbs --output_path=\$path_for_parsed_chains
python ${PROTEINMPNN_PATH}//helper_scripts/assign_fixed_chains.py --input_path=\$path_for_parsed_chains --output_path=\$path_for_assigned_chains --chain_list "\$chains_to_design"
python ${PROTEINMPNN_PATH}/helper_scripts/make_fixed_positions_dict.py --input_path=\$path_for_parsed_chains --output_path=\$path_for_fixed_positions --chain_list "\$chains_to_design" --position_list "\$fixed_positions"
python ${PROTEINMPNN_PATH}/protein_mpnn_run.py \
        --jsonl_path \$path_for_parsed_chains \
        --chain_id_jsonl \$path_for_assigned_chains \
        --fixed_positions_jsonl \$path_for_fixed_positions \
        --out_folder \$output_dir \
        --num_seq_per_target $MPNN_num_seq \
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

# 出力ディレクトリのパスを設定
output_mpnn_dir="$(pwd)/output/$pdb_prefix/ProteinMPNN/$current_date"
fasta_output_dir="$(pwd)/output/$pdb_prefix/fasta"
colab_output_dir="$(pwd)/output/$pdb_prefix/colabfold"
pdb_output_dir="$(pwd)/output/$pdb_prefix/pdb"
# fasta ディレクトリの作成
mkdir -p "$fasta_output_dir"
mkdir -p "$pdb_output_dir"

# 最後に、ProteinMPNN用に.faファイルを解析し、個別のファイルに分割する
echo "Processing .fa files for ProteinMPNN in $output_mpnn_dir and saving to $fasta_output_dir..."
for fa_file in $(find "$output_mpnn_dir" -name '*.fa'); do
    fa_basename=$(basename "$fa_file" .fa)

    # .faファイルを解析し、各サンプルに対して新しいファイルを作成
    awk -v out_dir="$fasta_output_dir" -v base_name="$fa_basename" '
    /^>/ {
        if (seq) print seq > filename
        sample = gensub(/^.*sample=([0-9]+).*$/, "\\1", "g", $0)
        filename = sprintf("%s/%s_seq_%s.fasta", out_dir, base_name, sample)
        print ">" base_name > filename
        seq = ""
        next
    }
    {
        seq = seq $0
    }
    END {
        if (seq) print seq > filename
    }' "$fa_file"
done

echo "Fasta files have been prepared and saved to $fasta_output_dir."

#colabfold_batch $fasta_output_dir $colab_output_dir
#cp ${colab_output_dir}/*.pdb ${pdb_output_dir}
