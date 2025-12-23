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
output_root = os.path.join("output", "resolution_rate")
os.makedirs(output_root, exist_ok=True)
output_rr_dist = os.path.join(output_root, "resolution_rate_" + PROBLEM_LEVEL + ".csv")

#問題リスト読み込み/辞書化
try:
    df = pd.read_csv(problem_list_path)
except FileNotFoundError:
    print(f"Error: {problem_list_path} not found.")
    exit(1)
df_filtered = df[df["rating"] == PROBLEM_LEVEL]
problem_ids = dict(zip(df_filtered["id"], df_filtered["rating"]))

#ユーザ読み込み
user_df = pd.read_csv(usergroup_path, dtype=str)
user_to_group = dict(zip(user_df["user_id"], user_df["group"]))

GROUP_ORDER = ["G1", "G2", "G3", "G4", "G5", "G6"]

LEVEL_TO_GROUPS = {
    "A": ["G1","G2","G3","G4","G5","G6"],
    "B": ["G2","G3","G4","G5","G6"],
    "C": ["G3","G4","G5","G6"],
    "D": ["G4","G5","G6"],
    "E": ["G5","G6"],
    "F": ["G6"]
}

ACTIVE_GROUPS = LEVEL_TO_GROUPS[PROBLEM_LEVEL]

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

stats = defaultdict(lambda: defaultdict(lambda: [0, 0]))

for problem_id in problem_ids:
    csv_path = os.path.join(metadata_dir, f"{problem_id}.csv")
    if not os.path.exists(csv_path):
        continue

    df = pd.read_csv(
        csv_path,
        usecols=["user_id", "date", "status"],
        dtype={"user_id": str, "date": int, "status": str}
    )

    #有効判定のみ
    df = df[df["status"].isin(VALID_STATUS)]
    if df.empty:
        continue

    #ユーザ・時間ソート
    df = df.sort_values(["user_id", "date"])

    #ユーザ単位で処理
    for user, df_u in df.groupby("user_id"):
        if user not in user_to_group:
            continue

        group = user_to_group[user]
        if group not in ACTIVE_GROUPS:
            continue

        statuses = df_u["status"].tolist()
        if not statuses:
            continue

        #最初がRJでなければ除外
        if statuses[0] not in RJ_STATUS:
            continue

        rj_set = set()
        solved = False

        for s in statuses:
            if s == "Accepted":
                solved = True
                break
            if s in RJ_STATUS:
                rj_set.add(s)

        if not rj_set:
            continue

        rj_key = "+".join(sorted(rj_set))
        stats[group][rj_key][0] += 1
        if solved:
            stats[group][rj_key][1] += 1

#出力
rows = []

for group in GROUP_ORDER:
    if group not in ACTIVE_GROUPS:
        continue
    if group not in stats:
        continue

    group_total = 0
    group_solved = 0

    for rj_key, (total, solved) in sorted(stats[group].items()):
        rate = solved / total if total > 0 else 0.0
        rows.append([
            group,
            rj_key,
            total,
            solved,
            f"{rate:.3f}"
        ])
        group_total += total
        group_solved += solved

    #合計
    if PROBLEM_LEVEL != "null":
        rows.append([
            group,
            "TOTAL",
            group_total,
            group_solved,
            f"{(group_solved / group_total):.3f}" if group_total > 0 else "0.000"
        ])

out_df = pd.DataFrame(
    rows,
    columns=["group", "RJ_pattern", "total_users", "solved_users", "resolution_rate"]
)
out_df.to_csv(output_rr_dist, index=False)

print("Calculating the resolution rate of Problem" + PROBLEM_LEVEL + ": completed.")