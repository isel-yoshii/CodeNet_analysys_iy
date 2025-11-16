import pandas as pd
import os
import shutil

#入力
metadata_dir = os.path.join("data", "metadata")
problem_list_path = os.path.join("data", "problem_list_ABC_rank_re.csv")

#出力
output_root = os.path.join("output", "problem_grouping")
os.makedirs(output_root, exist_ok=True)

#CSV読み込み・問題ID/難易度の辞書化
try:
    df = pd.read_csv(problem_list_path)
except FileNotFoundError:
    print(f"Error: {problem_list_path} not found.")
    exit(1)
id_to_rating = dict(zip(df["id"], df["rating"]))

#A~Fファイル作成・初期化
ranks = ["A", "B", "C", "D", "E", "F"]
for r in ranks:
    rank_dir = os.path.join(output_root, r)
    if os.path.exists(rank_dir):
        shutil.rmtree(rank_dir)
    os.makedirs(rank_dir)

#全ての問題を調べ、各難易度に振り分ける
for csv_name in os.listdir(metadata_dir):
    #CSV以外・辞書にない問題はスキップ
    if not csv_name.endswith(".csv"):
        continue
    problem_id = os.path.splitext(csv_name)[0]
    if problem_id not in id_to_rating:
        continue

    #問題の難易度を調べる
    rating = id_to_rating[problem_id]

    #問題のCSVファイルへのsymlinkを作成
    src = os.path.join(metadata_dir, csv_name)
    dst = os.path.join(output_root, rating, csv_name)
    rel_src = os.path.relpath(src, os.path.join(output_root, rating))
    os.symlink(rel_src, dst)

    #print(f"{csv_name} → {rating}")

print("\nClassification completed.")