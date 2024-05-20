import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def plot_scatter_from_csv(align_csv_path, pae_stats_csv_path, prefix):
    # CSVファイルを読み込む
    align_df = pd.read_csv(align_csv_path)
    pae_stats_df = pd.read_csv(pae_stats_csv_path)

    # データフレームを結合
    df = pd.merge(align_df, pae_stats_df, on=['model', 'seq'])

    # 結合したデータフレームをCSVに保存
    df.to_csv(f"{prefix}_merged_data.csv", index=False)

    # カラーマップをリバースに設定
    cmap = plt.cm.CMRmap_r

    # 散布図をプロット
    scatter = plt.scatter(df['rmsd'], df['target_mean'], c=df['used_mean_tf'], cmap=cmap, vmin=0, vmax=100, s=20, alpha=0.7)
    plt.colorbar(scatter, label='Used Mean TempFactor')

    plt.xlabel('RMSD')
    plt.ylabel('Target Mean Error')
    plt.title('Scatter Plot of RMSD vs Target Mean Error')

    # X軸とY軸の範囲を設定
    plt.xlim(0, 30)
    plt.ylim(0, 30)

    # 図のタイトルとしてprefixを使用
    plt.title(f"{prefix} RMSD vs Target PAE")

    # 図を保存
    plt.savefig(f"{prefix}_RMSDvsTPAE.png")

# コマンドラインからプレフィックスを取得する場合
if __name__ == "__main__":
    import sys
    prefix = sys.argv[1]  # コマンドライン引数からプレフィックスを取得
    align_csv_path = prefix + '_align.csv'
    pae_stats_csv_path = prefix + '_pae_stats.csv'
    plot_scatter_from_csv(align_csv_path, pae_stats_csv_path, prefix)

