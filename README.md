# RFdiffusion Script

このスクリプトは、タンパク質構造に基づいて新しいデザインを生成するために、RFdiffusionとProteinMPNNを利用します。指定されたPDBファイルから開始し、必要なデータを準備した後、複数の推論ステップを経て、タンパク質の新しい配列と構造を設計します。

## 必要条件

- 事前にインストールされたRFdiffusionとProteinMPNN
- 切り出されたタンパク質構造ファイル（.pdb形式）
- Biopythonライブラリ

## 依存関係

- RFdiffusion: [GitHub Repository](https://github.com/RosettaCommons/RFdiffusion)
- ProteinMPNN: [GitHub Repository](https://github.com/dauparas/ProteinMPNN)

## セットアップ

1. 必要なライブラリと依存関係をインストールします。
2. スクリプト内で以下のパスを確認し、必要に応じて更新してください：
   - `RFDIFFUSION_PATH`
   - `PROTEINMPNN_PATH`
   - `GENSH_PATH`

## 使用方法

スクリプトはコマンドラインから実行されます。以下のオプションを使用して、必要なパラメータを設定できます：

```bash
./gen.sh [オプション]
```

### オプション

- `-p|--pdb`: 入力PDBファイルのパス（必須）
- `-nd|--num_designs`: RFdiffusionによる設計数（デフォルトは2）
- `-ns|--num_sequences`: ProteinMPNNによるシーケンス数（デフォルトは2）
- `-c|--custom_out`: カスタム出力パス（指定なしで自動生成）
- `-l|--linker`: リンカーの範囲（デフォルトは "10-40"）
- `-rn|--remove_n_ter`: 最初のリンカーを除去（オプション）
- `-rc|--remove_c_ter`: 最後のリンカーを除去（オプション）
- `-nm|--num-models`: 生成するモデルの数（デフォルトは1）
- `-nr|--num-recycle`: リサイクル回数（デフォルトは3）
- `-tol|--recycle-early-stop-tolerance`: 早期停止の許容範囲
- `--rank`: モデルのランキング方法（デフォルトはauto）
- `--sort-queries-by`: クエリの並べ替え方法（デフォルトはlength）

### 実行例

以下のコマンドは、入力PDBファイルを指定し、2つの新しいデザインとシーケンスを生成します：

```bash
./gen.sh -p /path/to/your/input.pdb -nd 2 -ns 2
```


- `align_pdb.py`: 指定されたタンパク質構造のアラインメントを行い、統計情報を計算してCSVファイルに出力します。
- `input_recog.py`: 入力されたPDBファイルを解析し、タンパク質の特性を抽出し、後続のステップで利用するデータを準備します。
- `MPNN-prep.py`: ProteinMPNNを使用するためのデータを準備します。抽出された特性に基づいて、タンパク質のデザインデータを整形し、必要な情報を提供します。
- `pae_calculation.py`: Predicated Aligned Error (PAE) の計算を行い、結果を分析してCSVファイルに保存します。このスクリプトは、タンパク質のアラインメントエラーを解析し、その結果を評価するために使用されます。
- `scatter_plot.py`: CSVファイルのデータを基にして、グラフィカルな解析結果を生成します。RMSDとtPAEの関係を2次元散布図で示し、さらに詳細な分析を提供します。

## トラブルシューティング

- **ModuleNotFoundError**: 'torch' というエラーが出る場合は、`conda activate SE3nv` コマンド等で適切なConda環境をアクティブにするのを忘れている可能性があります。`conda info -e` で現在のConda環境のリストを確認してください。

RFdiffusionのインストールに問題がある場合は、下記を参照してみてください。

https://github.com/RosettaCommons/RFdiffusion/issues/14

https://github.com/truatpasteurdotfr/RFdiffusion/tree/main/env


#### Pythonスクリプトの説明

- `align_pdb.py`: 指定されたタンパク質構造のアラインメントを行い、統計情報を計算してCSVファイルに出力します。
- `input_recog.py`: 入力されたPDBファイルを解析し、タンパク質の特性を抽出し、後続のステップで利用するデータを準備します。
- `MPNN-prep.py`: ProteinMPNNを使用するためのデータを準備します。抽出された特性に基づいて、タンパク質のデザインデータを整形し、必要な情報を提供します。
- `pae_calculation.py`: Predicated Aligned Error (PAE) の計算を行い、結果を分析してCSVファイルに保存します。このスクリプトは、タンパク質のアラインメントエラーを解析し、その結果を評価するために使用されます。
- `scatter_plot.py`: CSVファイルのデータを基にして、グラフィカルな解析結果を生成します。RMSDとtPAEの関係を2次元散布図で示し、さらに詳細な分析を提供します。


