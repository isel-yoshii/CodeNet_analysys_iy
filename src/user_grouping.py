import pandas as pd
import os
import csv
from collections import defaultdict

#入力
metadata_dir = os.path.join("data", "metadata")
problem_list_path = os.path.join("data", "problem_list_ABC_rank_re.csv")

#出力
output_root = os.path.join("output", "user_grouping")
os.makedirs(output_root, exist_ok=True)
output_users = os.path.join(output_root, "users.csv")
output_groups = os.path.join(output_root, "user_counts.csv")


#CSV読み込み・問題ID/難易度の辞書化
try:
    df = pd.read_csv(problem_list_path)
except FileNotFoundError:
    print(f"Error: {problem_list_path} not found.")
    exit(1)
id_to_rating = dict(zip(df["id"], df["rating"]))

users = {} 

#ユーザ追加(提出回数・各難易度ごとAC有無・グループ分け)
def new_user():
    return {
        "count": 0,
        "solved": {r: False for r in ["A","B","C","D","E","F"]},
        "group": None
    }

#chunksize設定
CHUNK = 4096

VALID_STATUS = {
    "Accepted",
    "Wrong Answer",
    "Runtime Error",
    "Time Limit Exceeded",
    "Compile Error"
}

for csv_name in sorted(os.listdir(metadata_dir)):
    #CSV以外・辞書にない問題はスキップ
    if not csv_name.endswith(".csv"):
        continue
    problem_id = os.path.splitext(csv_name)[0]
    if problem_id not in id_to_rating:
        continue

    file_path = os.path.join(metadata_dir, csv_name)
    rating = id_to_rating[problem_id]

    try:
        #chunkで読み込む
        reader = pd.read_csv(
            file_path,
            usecols=["user_id", "date", "status"],
            dtype=str,
            #parse_dates=["date"],
            #infer_datetime_format=True,
            chunksize=CHUNK
        )
    except Exception as e:
        print(f"Failed to read {csv_name}: {e}")
        continue

    #chunkごとに処理
    for tmp in reader:
        #data列をUNIXタイムからdatetimeに変換
        if "date" in tmp.columns:
            tmp["date"] = pd.to_datetime(tmp["date"].astype(int), unit="s")

        #user_id,dateでソート
        if "date" in tmp.columns:
            tmp = tmp.sort_values(["user_id", "date"])
        else:
            tmp = tmp.sort_values(["user_id"])

        #1行ずつ処理
        for row in tmp.itertuples(index=False):
            user = str(row.user_id)
            status = str(row.status) if getattr(row, "status", None) is not None else ""

            #対象外の判定は無視
            if status not in VALID_STATUS:
                continue

            if user not in users:
                users[user] = new_user()

            #提出をカウント
            users[user]["count"] += 1

            #Acceptedの場合、対応難易度のsolvedをTrueに
            if status.strip().lower() == "accepted":
                if rating in users[user]["solved"]:
                    users[user]["solved"][rating] = True

#提出回数3回未満のユーザを削除
users = {u: d for u, d in users.items() if d["count"] >= 3}

#グループ分け
def assign_group(solved):
    s = solved
    # G6: A,B,C,D,E,F 全て True
    if all(s[r] for r in ["A","B","C","D","E","F"]):
        return "G6"
    # G5: A-E True, F False
    if all(s[r] for r in ["A","B","C","D","E"]) and not s["F"]:
        return "G5"
    # G4: A-D True, E/F False
    if all(s[r] for r in ["A","B","C","D"]) and not s["E"] and not s["F"]:
        return "G4"
    # G3: A-C True, D/E/F False
    if all(s[r] for r in ["A","B","C"]) and not any(s[r] for r in ["D","E","F"]):
        return "G3"
    # G2: A,B True, others False
    if all(s[r] for r in ["A","B"]) and not any(s[r] for r in ["C","D","E","F"]):
        return "G2"
    # G1: A True, others False
    if s["A"] and not any(s[r] for r in ["B","C","D","E","F"]):
        return "G1"
    return None

for u, data in users.items():
    data["group"] = assign_group(data["solved"])

#どこにも属さないユーザを削除
users = {u: d for u, d in users.items() if d["group"] is not None}

#まとめ・標準出力
group_order = ["G1","G2","G3","G4","G5","G6"]
group_counts = {g: 0 for g in group_order}
for d in users.values():
    group_counts[d["group"]] += 1

total = sum(group_counts.values())

for g in group_order:
    print(f"{g}: {group_counts[g]}")
print(f"Total: {total}")

#集計をCSV出力
with open(output_groups, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["group","count"])
    for g in group_order:
        writer.writerow([g, group_counts[g]])
    writer.writerow(["Total", total])

#ユーザ情報をCSV出力
with open(output_users, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["user_id", "count", "A","B","C","D","E","F", "group"])
    for u, d in users.items():
        s = d["solved"]
        writer.writerow([u, d["count"], s["A"], s["B"], s["C"], s["D"], s["E"], s["F"], d["group"]])

print("Classification completed.")