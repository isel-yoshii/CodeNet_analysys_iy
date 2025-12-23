import pandas as pd
import os
import csv
from collections import defaultdict
import numpy as np

#入力
PROBLEM_LEVEL = 'F' #調査する問題(A~F) 
TIME_LIMIT = 43200
metadata_dir = os.path.join("data", "metadata")
problem_list_path = os.path.join("data", "problem_list_ABC_rank_re.csv")
usergroup_path = os.path.join("output", "user_grouping", "users.csv")

#出力
output_root = os.path.join("output", "resolution_time")
os.makedirs(output_root, exist_ok=True)
output_csv = os.path.join(
    output_root, f"resolution_time_{PROBLEM_LEVEL}.csv"
)

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

RJ_BIT = {
    "Wrong Answer": 1,
    "Runtime Error": 2,
    "Time Limit Exceeded": 4,
    "Compile Error": 8
}

BIT_TO_RJ = {
    1: "Wrong Answer",
    2: "Runtime Error",
    4: "Time Limit Exceeded",
    8: "Compile Error"
}

def bitmask_to_label(mask: int) -> str:
    return "+".join(
        BIT_TO_RJ[b] for b in sorted(BIT_TO_RJ) if mask & b
    )

tats = defaultdict(lambda: defaultdict(list))

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

    for user, df_u in df.groupby("user_id"):
        if user not in user_to_group:
            continue

        group = user_to_group[user]
        if group not in ACTIVE_GROUPS:
            continue

        statuses = df_u["status"].tolist()
        times = df_u["date"].tolist()
        if not statuses:
            continue

        #最初のRJを探す
        first_rj_time = None
        rj_set = set()

        for s, t in zip(statuses, times):
            if s in RJ_STATUS:
                first_rj_time = t
                rj_set.add(s)
                break

        if first_rj_time is None:
            continue  

        #RJ後の最初のACを探す
        solved_time = None
        for s, t in zip(statuses, times):
            if t <= first_rj_time:
                continue
            if s == "Accepted":
                solved_time = t
                break
            if s in RJ_STATUS:
                rj_set.add(s)

        #ACなし
        if solved_time is None:
            continue 

        #時間調べる
        delta = solved_time - first_rj_time
        if delta <= 0 or delta > TIME_LIMIT:
            continue

        rj_key = "+".join(sorted(rj_set))
        tats[group][rj_key].append(delta)
"""
    cur_user = None
    group = None
    first_rj_time = None
    rj_mask = 0
    invalid = False

    for user, date, status in df.itertuples(index=False):
        # ユーザ切り替え
        if user != cur_user:
            cur_user = user
            group = user_to_group.get(user)
            first_rj_time = None
            rj_mask = 0
            invalid = False

        if group not in ACTIVE_GROUPS:
            continue

        # 最初の判定
        if first_rj_time is None:
            if status in RJ_BIT:
                first_rj_time = date
                rj_mask = RJ_BIT[status]
            else:
                invalid = True
            continue

        if invalid:
            continue

        # AC 到達
        if status == "Accepted":
            delta = date - first_rj_time
            if 0 < delta <= TIME_LIMIT:
                stats[group][rj_mask].append(delta)
            invalid = True
            continue

        # 途中 RJ
        if status in RJ_BIT:
            rj_mask |= RJ_BIT[status]
"""
#出力
"""
rows = []

for group, group_data in stats.items():
    for mask, times in group_data.items():
        arr = np.array(times)
        rows.append([
            group,
            bitmask_to_label(mask),
            len(arr),
            int(np.median(arr)),
            int(np.percentile(arr, 25)),
            int(np.percentile(arr, 75)),
            int(arr.min()),
            int(arr.max())
        ])

out_df = pd.DataFrame(
    rows,
    columns=[
        "group",
        "RJ_pattern",
        "n",
        "median_time",
        "p25_time",
        "p75_time",
        "min_time",
        "max_time"
    ]
)

out_df.to_csv(output_csv, index=False)
print(f"Resolution time analysis ({PROBLEM_LEVEL}) completed.")
"""
rows = []

for group in GROUP_ORDER:
    if group not in ACTIVE_GROUPS:
        continue
    if group not in tats:
        continue

    for rj_key in sorted(tats[group].keys()):
        times = tats[group][rj_key]
        if not times:
            continue

        for t in times:
            rows.append([
                group,
                rj_key,
                t
            ])

out_df = pd.DataFrame(
    rows,
    columns=["group", "RJ_pattern", "resolution_time_sec"]
)
out_df.to_csv(output_csv, index=False)

print(f"Resolution time analysis for Problem {PROBLEM_LEVEL} completed.")