# RFdiff-MPNN-byGPT4

## 概要
`gen.sh` は、特定の PDB ファイルに対して複数の解析スクリプトを実行し、その結果に基づいて ProteinMPNN の入力を準備する Bash スクリプトです。このスクリプトは、主に構造データから特定の特徴を抽出し、後続の処理のためにそれらを準備します。

## 依存関係
`gen.sh` は以下の Python スクリプトを実行しますので、これらのスクリプトが事前に適切な場所に設置されている必要があります:

- `input_recog.py`: PDBファイルを解析し、関連する特性を抽出します。
- `MPNN-prep.py`: 抽出した特性を基に、ProteinMPNN 用のデータを準備します。

これらのスクリプトが `gen.sh` の冒頭で指定するディレクトリに配置されていることを確認してください。

RFDIFFUSION_PATH=/path/to/RFdiffusion

PROTEINMPNN_PATH=/path/to//ProteinMPNN

GENSH_PATH=/path/to/RFdiff-MPNN-byGPT4

RFDIFF_num_designs=4

MPNN_num_seq=5

## 使用方法
コマンドラインから `gen.sh` スクリプトを直接実行できます。スクリプトを実行するには、以下の形式を使用してください:

```bash
git clone https://github.com/CYP152N1/RFdiff-MPNN-byGPT4
cd RFdiff-MPNN-byGPT4
./gen.sh path_to_your_pdb_file.pdb

```
## 注意
RFdiffusionやProteinMPNNのpathを変更する必要があります。


## Overview
`gen.sh` is a Bash script that executes multiple analysis scripts on a specific PDB file and prepares the input for ProteinMPNN based on the results. This script mainly extracts specific features from structural data and prepares them for subsequent processing.

## Dependencies
`gen.sh` runs the following Python scripts, so these scripts need to be placed properly before running `gen.sh`:

- `input_recog.py`: Analyzes the PDB file and extracts relevant features.
- `MPNN-prep.py`: Prepares the data for ProteinMPNN based on the extracted features.

Ensure that these scripts are located in the same directory as `gen.sh` or in a directory included in the system's PATH.

## Usage
To run the `gen.sh` script, use the following command format from the command line:

```bash
./gen.sh path_to_your_pdb_file.pdb
