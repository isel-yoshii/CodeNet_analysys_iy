import pandas as pd
import os
from collections import defaultdict

#入力
PROBLEM_LEVEL = 'F'
input_root = os.path.join("output", "primary_transition_re", PROBLEM_LEVEL)

#出力
output_root = os.path.join("output", "transition_investigation")
level_dir = os.path.join(output_root, PROBLEM_LEVEL)
os.makedirs(level_dir, exist_ok=True)


#RJ一覧
RJ_STATUS = [
    "Wrong Answer",
    "Runtime Error",
    "Time Limit Exceeded",
    "Compile Error"
]

#格納用
transition_count = defaultdict(int)
from_count = defaultdict(int)

#遷移を含むsession
transition_sessions = defaultdict(set)

#session単位で最終ACしたか
session_final_ac = dict()

#遷移時間
time_rows = []

#RJごとに処理
for first_error in RJ_STATUS:
    path = os.path.join(input_root, f"model_{first_error}.csv")
    if not os.path.exists(path):
        continue

    df = pd.read_csv(path)

    #sessionごとの最終AC判定
    for (uid, pid), g in df.groupby(["user_id", "problem_id"]):
        session_id = (uid, pid)
        session_final_ac[session_id] = (g["to_status"] == "Accepted").any()

    #遷移処理
    for _, r in df.iterrows():
        key = (
            PROBLEM_LEVEL,
            first_error,
            r["from_status"],
            r["to_status"]
        )

        session_id = (r["user_id"], r["problem_id"])

        #遷移回数
        transition_count[key] += 1
        from_count[(PROBLEM_LEVEL, first_error, r["from_status"])] += 1

        #遷移を含むsession
        transition_sessions[key].add(session_id)

        # 遷移時間
        time_rows.append({
            "difficulty": PROBLEM_LEVEL,
            "first_error": first_error,
            "from_state": r["from_status"],
            "to_state": r["to_status"],
            "delta_time": r["delta_time"],
            "group": r["group"]
        })

#遷移確率
prob_rows = []

for (diff, fe, fs, ts), cnt in transition_count.items():
    total = from_count[(diff, fe, fs)]
    prob_rows.append({
        "difficulty": diff,
        "first_error": fe,
        "from_state": fs,
        "to_state": ts,
        "count": cnt,
        "probability": round(cnt / total, 5) if total > 0 else 0
    })

pd.DataFrame(prob_rows).to_csv(
    os.path.join(level_dir, f"transition_prob_{PROBLEM_LEVEL}.csv"),
    index=False
)

#AC到達率（最終AC基準）
ac_rows = []

for key, sessions in transition_sessions.items():
    ac_sessions = [
        s for s in sessions if session_final_ac.get(s, False)
    ]

    ac_rows.append({
        "difficulty": key[0],
        "first_error": key[1],
        "from_state": key[2],
        "to_state": key[3],
        "sessions": len(sessions),
        "ac_sessions": len(ac_sessions),
        "ac_rate": round(len(ac_sessions) / len(sessions), 5) if sessions else 0
    })

pd.DataFrame(ac_rows).to_csv(
    os.path.join(level_dir, f"transition_ac_rate_{PROBLEM_LEVEL}.csv"),
    index=False
)

#遷移時間（箱ひげ図用統計量）
time_df = pd.DataFrame(time_rows)

box_rows = []

group_cols = ["difficulty", "first_error", "from_state", "to_state", "group"]

for keys, g in time_df.groupby(group_cols):
    box_rows.append({
        **dict(zip(group_cols, keys)),
        "count": len(g),
        "min": g["delta_time"].min(),
        "q1": g["delta_time"].quantile(0.25),
        "median": g["delta_time"].median(),
        "q3": g["delta_time"].quantile(0.75),
        "max": g["delta_time"].max()
    })

pd.DataFrame(box_rows).to_csv(
    os.path.join(level_dir, f"transition_time_box_{PROBLEM_LEVEL}.csv"),
    index=False
)

print(f"Transition investigation for level {PROBLEM_LEVEL}: completed.")