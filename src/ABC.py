import pandas as pd
import os

#入力
input_path = os.path.join("data", "metadata", "problem_list.csv")

#出力
output_dir = os.path.join("output", "ABC")
os.makedirs(output_dir, exist_ok=True)  
output_path = os.path.join(output_dir, "problem_list_ABC.csv")


#AtcoderのABC問題のみを抽出
#"AtCoder Beginner Contest"を名前に含まない問題は後から手動で追加する
try:
    df = pd.read_csv(input_path)
except FileNotFoundError:
    print(f"Error: {input_path} not found.")
    exit(1)
df_atcoder = df[df["dataset"].str.contains("AtCoder", case=False, na=False)]
df_abc = df_atcoder[df_atcoder["name"].str.contains("AtCoder Beginner Contest", case=False, na=False)]

df_abc.to_csv(output_path, index=False)

