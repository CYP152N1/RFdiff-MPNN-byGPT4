# RFdiffusion Script

このスクリプトは、タンパク質構造に基づいて新しいデザインを生成するために、RFdiffusionとProteinMPNNを利用します。これは、指定されたPDBファイルから開始して、必要なデータを準備し、複数の推論ステップを経て、タンパク質の新しい配列と構造を設計します。

## 必要条件

- 切り出されてたタンパク質構造ファイル（.pdb形式）

## 依存関係

- RFdiffusion: 

https://github.com/RosettaCommons/RFdiffusion

https://github.com/RosettaCommons/RFdiffusion/issues/14

https://github.com/truatpasteurdotfr/RFdiffusion/tree/main/env

- ProteinMPNN

https://github.com/dauparas/ProteinMPNN


`gen.sh` は以下の Python スクリプトを実行しますので、これらのスクリプトが事前に適切な場所に設置されている必要があります:

- `input_recog.py`: PDBファイルを解析し、関連する特性を抽出します。
- `MPNN-prep.py`: 抽出した特性を基に、ProteinMPNN 用のデータを準備します。



# RFdiffusion Script

このスクリプトは、タンパク質構造に基づいて新しいデザインを生成するために、RFdiffusionとProteinMPNNを利用します。これは、指定されたPDBファイルから開始して、必要なデータを準備し、複数の推論ステップを経て、タンパク質の新しい配列と構造を設計します。

## 必要条件

- 事前にインストールされたRFdiffusionとProteinMPNN
- 切り出されたタンパク質構造ファイル（.pdb形式）
- Biopythonライブラリ


## 依存関係

- RFdiffusion: 

https://github.com/RosettaCommons/RFdiffusion

https://github.com/RosettaCommons/RFdiffusion/issues/14

https://github.com/truatpasteurdotfr/RFdiffusion/tree/main/env

- ProteinMPNN

https://github.com/dauparas/ProteinMPNN

## セットアップ

1. 必要なライブラリと依存関係をインストールします。
2. 以下のパスを確認し、必要に応じてスクリプト内でパスを更新してください：
   - `RFDIFFUSION_PATH`
   - `PROTEINMPNN_PATH`
   - `GENSH_PATH`

## 使用方法

スクリプトはコマンドラインから実行されます。以下のオプションを使用して、必要なパラメータを設定できます：

```
./gen.sh [オプション]
```

### オプション

- `-p`: 入力PDBファイルのパス（必須）
- `-nd`: RFdiffusionによる設計数（デフォルトは2）
- `-ns`: ProteinMPNNによるシーケンス数（デフォルトは2）
- `-c`: リンカーのカスタム指定（指定されていない場合はinput_recog.pyで生成）
- `-l`: リンカーの範囲（デフォルトは "10-40"）
- `-rn`: 最初のリンカーを除去（オプション）
- `-rc`: 最後のリンカーを除去（オプション）

### 実行例

以下のコマンドは、入力PDBファイルを指定し、2つの新しいデザインとシーケンスを生成します：

```
./gen.sh -p /path/to/your/input.pdb -nd 2 -ns 2
```

## `input_recog.py` について

このPythonスクリプトは、指定されたPDBファイルを解析し、リンカーを挿入しながら、各チェーンの残基範囲を抽出します。スクリプトは以下のオプションを受け取ります：

- `-l`, `--linker`: リンカーの範囲（デフォルトは "10-40"）
- `-rn`, `--remove_n`: 最初のリンカーを除去
- `-rc`, `--remove_c`: 最後のリンカーを除去

スクリプトは、PDBファイル内の各モデルおよびチェーンをトラバースし、指定されたリンカーを挿入して、最終的な出力形式を生成します。

## トラブルシューティング

- **ModuleNotFoundError**: 'torch' というエラーが出る場合は、`conda activate SE3nv` コマンドで適切なConda環境をアクティブにするのを忘れている可能性があります。`conda info -e` で現在のConda環境のリストを確認してください。



