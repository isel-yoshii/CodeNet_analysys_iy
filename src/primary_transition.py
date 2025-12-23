import pandas as pd
import os
import csv
from collections import defaultdict

#入力
PROBLEM_LEVEL = 'F' #調査する問題(A~F) 
metadata_dir = os.path.join("data", "metadata")
problem_list_path = os.path.join("data", "problem_list_ABC_rank_re.csv")
usergroup_path = os.path.join("output", "user_grouping", "users.csv")

#出力
output_root = os.path.join("output", "primary_transition")
level_dir = os.path.join(output_root, PROBLEM_LEVEL)
os.makedirs(level_dir, exist_ok=True)

VALID_STATUS = {
    "Accepted",
    "Wrong Answer",
    "Runtime Error",
    "Time Limit Exceeded",
    "Compile Error"
}

RJ_STATUS = [
    "Wrong Answer",
    "Runtime Error",
    "Time Limit Exceeded",
    "Compile Error"
]

#問題リスト読み込み/辞書化
try:
    df = pd.read_csv(problem_list_path)
except FileNotFoundError:
    print(f"Error: {problem_list_path} not found.")
    exit(1)
df_filtered = df[df["rating"] == PROBLEM_LEVEL]
problem_ids = dict(zip(df_filtered["id"], df_filtered["rating"]))

#ユーザ読み込み
if os.path.exists(usergroup_path):
    user_df = pd.read_csv(usergroup_path, dtype=str)
    user_to_group = dict(zip(user_df["user_id"], user_df["group"]))
else:
    user_to_group = {}

first_status_count = defaultdict(int)
transitions = defaultdict(list)

#問題ごとに処理
for problem_id in problem_ids:
    csv_path = os.path.join(metadata_dir, f"{problem_id}.csv")
    if not os.path.exists(csv_path):
        continue

    df = pd.read_csv(
        csv_path,
        usecols=["user_id", "date", "status"],
        dtype={"user_id": str, "date": int, "status": str}
    )

    #ユーザ・時間ソート
    df = df.sort_values(["user_id", "date"])

    #ユーザ単位で処理
    for user, df_u in df.groupby("user_id"):
        group = user_to_group.get(user, "") 

        records = list(df_u[["date", "status"]].itertuples(index=False, name=None))
        if not records:
            continue

        #最初の判定
        first_idx = None
        had_invalid_before_first = False

        for i, (_, s) in enumerate(records):
            if s not in VALID_STATUS:
                had_invalid_before_first = True
                continue
            first_idx = i
            first_status = s
            break

        if first_idx is None:
            continue

        #最初の判定分布
        first_status_count[first_status] += 1

        #RJで始まらなければ遷移モデル対象外
        if first_status not in RJ_STATUS:
            continue

        prev_status = first_status
        prev_time = records[first_idx][0]
        prev_invalid = had_invalid_before_first

        #遷移調査
        for date, status in records[first_idx + 1:]:

            #invalid判定
            if status not in VALID_STATUS:
                prev_invalid = True
                continue

            #遷移記録
            transitions[first_status].append({
                "from_status": prev_status,
                "to_status": status,
                "delta_time": date - prev_time,
                "prev_invalid": prev_invalid,
                "group": group,
                "user_id": user,
                "problem_id": problem_id
            })

            prev_status = status
            prev_time = date
            prev_invalid = False

            #AC到達で終了
            if status == "Accepted":
                break

#出力
#最初の判定
pd.DataFrame(
    sorted(first_status_count.items()),
    columns=["first_status", "count"]
).to_csv(
    os.path.join(level_dir, "first_status_count.csv"),
    index=False
)

#RJごとの遷移モデル
for rj in RJ_STATUS:
    rows = transitions.get(rj, [])
    if not rows:
        continue

    pd.DataFrame(rows).to_csv(
        os.path.join(level_dir, f"model_{rj}.csv"),
        index=False
    )

print(f"RJ transition model (with invalid-aware, self-transition) for level {PROBLEM_LEVEL}: completed.")
