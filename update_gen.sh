#!/bin/bash

# スクリプトと条件ファイルのパスを定義
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
GENSH_FILE="${SCRIPT_DIR}/gen.sh"
CONDITION_PATH="${SCRIPT_DIR}/condition.sh"

# condition.sh から設定を読み込む
source $CONDITION_PATH

# 各変数がデフォルト値に一致するか確認し、コメントを出力
check_default_value() {
    local var_name=$1
    local default_value=$2
    local current_value=$(grep "^$var_name=" $CONDITION_PATH | cut -d'=' -f2)

    if [ "$current_value" == "$default_value" ]; then
        echo "$var_name はデフォルト値 ($default_value) に設定されています。環境に合わせて更新してください。"
	echo "condition.sh を編集するには、次のコマンドを実行してください: vim $CONDITION_PATH"
	echo "更新後、このスクリプトを再実行してください。"
	exit 1  # スクリプトを終了させる
    fi
}

# 各変数をチェック
check_default_value "RFDIFFUSION_PATH" "/path/to/RFdiffusion"
check_default_value "PROTEINMPNN_PATH" "/path/to/ProteinMPNN"
check_default_value "GENSH_PATH" "/path/to/RFdiff-MPNN-byGPT4"
check_default_value "CONDA_PATH" "/path/to/conda/envs/your_environment_name"

# gen.sh の変数を更新する関数を定義
update_variable() {
    local var_name=$1
    local default_path=$2
    local new_path=$(grep "^$var_name=" $CONDITION_PATH | cut -d'=' -f2)

    # gen.sh から現在の値を取得
    local current_path=$(grep "^$var_name=" $GENSH_FILE | cut -d'=' -f2)

    if [ "$current_path" == "$default_path" ]; then
        # gen.sh 内の値を更新
        sed -i "s|^$var_name=.*|$var_name=$new_path|" $GENSH_FILE
        echo "$var_name をデフォルトから $new_path に更新しました。"
        # CONDA_PATH が更新された場合の追加アクション
        if [ "$var_name" == "CONDA_PATH" ]; then
            echo "更新された $var_name で必要なPythonパッケージをインストールしています..."
            $new_path/bin/python -m pip install biopython
            $new_path/bin/python -m pip install matplotlib
            $new_path/bin/python -m pip install pandas
        fi
    else
        echo "$var_name は現在 $current_path に設定されており、更新されませんでした。"
    fi
}

# デフォルト値と新しい値を使用して変数を更新
update_variable "RFDIFFUSION_PATH" "/path/to/RFdiffusion" "$RFDIFFUSION_PATH"
update_variable "PROTEINMPNN_PATH" "/path/to/ProteinMPNN" "$PROTEINMPNN_PATH"
update_variable "GENSH_PATH" "/path/to/RFdiff-MPNN-byGPT4" "$GENSH_PATH"
update_variable "CONDA_PATH" "/path/to/conda/envs/your_environment_name" "$CONDA_PATH"

