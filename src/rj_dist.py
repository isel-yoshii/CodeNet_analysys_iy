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
output_root = os.path.join("output", "rj_dist")
os.makedirs(output_root, exist_ok=True)
output_rj_dist = os.path.join(output_root, "rj_dist_" + PROBLEM_LEVEL + ".csv")

#問題リスト読み込み/辞書化
try:
    df = pd.read_csv(problem_list_path)
except FileNotFoundError:
    print(f"Error: {problem_list_path} not found.")
    exit(1)
df_filtered = df[df["rating"] == PROBLEM_LEVEL]
id_to_rating = dict(zip(df_filtered["id"], df_filtered["rating"]))

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

counts = {
    g: {s: 0 for s in VALID_STATUS}
    for g in ACTIVE_GROUPS
}

CHUNK = 4096

#問題ごとに処理
for problem_id in id_to_rating.keys():
    csv_path = os.path.join(metadata_dir, problem_id + ".csv")
    if not os.path.exists(csv_path):
        continue

    try:
        reader = pd.read_csv(
            csv_path,
            usecols=["user_id", "status"],
            dtype=str,
            chunksize=CHUNK
        )
    except Exception as e:
        print(f"Failed to read {problem_id}: {e}")
        continue

    for tmp in reader:
        for row in tmp.itertuples(index=False):
            user = str(row.user_id)
            status = str(row.status) if row.status is not None else ""

            if status not in VALID_STATUS:
                continue
            if user not in user_to_group:
                continue

            group = user_to_group[user]
            if group not in counts:
                continue
            counts[group][status] += 1

def r(x):
    return f"{x:.5f}"

#出力
with open(output_rj_dist, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    header = [
        "group",
        "Accepted",
        "Wrong Answer",
        "Runtime Error",
        "Time Limit Exceeded",
        "Compile Error",
        "RJ_total",
        "WA_ratio",
        "RE_ratio",
        "TLE_ratio",
        "CE_ratio"
    ]
    writer.writerow(header)

    total_counts = {s: 0 for s in VALID_STATUS}

    for g in ACTIVE_GROUPS:
        ac = counts[g]["Accepted"]
        wa = counts[g]["Wrong Answer"]
        re = counts[g]["Runtime Error"]
        tle = counts[g]["Time Limit Exceeded"]
        ce = counts[g]["Compile Error"]

        total_counts["Accepted"] += ac
        total_counts["Wrong Answer"] += wa
        total_counts["Runtime Error"] += re
        total_counts["Time Limit Exceeded"] += tle
        total_counts["Compile Error"] += ce

        rj_total = wa + re + tle + ce

        if rj_total > 0:
            wa_r = wa / rj_total
            re_r = re / rj_total
            tle_r = tle / rj_total
            ce_r = ce / rj_total
        else:
            wa_r = re_r = tle_r = ce_r = 0.0

        writer.writerow([
            g,
            ac,
            wa,
            re,
            tle,
            ce,
            rj_total,
            r(wa_r),
            r(re_r),
            r(tle_r),
            r(ce_r)
        ])
    if PROBLEM_LEVEL != "F":
        ac = total_counts["Accepted"]
        wa = total_counts["Wrong Answer"]
        re = total_counts["Runtime Error"]
        tle = total_counts["Time Limit Exceeded"]
        ce = total_counts["Compile Error"]

        rj_total = wa + re + tle + ce

        if rj_total > 0:
            wa_r = wa / rj_total
            re_r = re / rj_total
            tle_r = tle / rj_total
            ce_r = ce / rj_total
        else:
            wa_r = re_r = tle_r = ce_r = 0.0

        writer.writerow([
            "ALL",
            ac,
            wa,
            re,
            tle,
            ce,
            rj_total,
            r(wa_r),
            r(re_r),
            r(tle_r),
            r(ce_r)
    ])

print("Problem" + PROBLEM_LEVEL + " distribution analysis completed.")