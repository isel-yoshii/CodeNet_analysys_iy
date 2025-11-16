# CodeNet_analysys_iy

このリポジトリには、[Project CodeNet](https://github.com/IBM/Project_CodeNet)のメタデータのAtCoder Beginner Contest（ABC）についての解析とその結果が含まれています。
 - "data"フォルダには、解析に使用するデータセットが含まれています。
 - "output"フォルダには、解析結果が含まれています。フォルダ名は、プログラム名に対応しており、例えば"ABC.py"の実行結果は、"ABC"フォルダに格納されます。
 - "src"フォルダには、解析のために使用したプログラムが含まれています。

このリポジトリでは、[Project CodeNet](https://github.com/IBM/Project_CodeNet) のメタデータを使用します。

上記のリンクのREADME内にある **"Project CodeNet full dataset: Project_CodeNet.tar.gz"** をクリックし、データをダウンロードしてください。

解凍後、中にある"metadata"フォルダをそのまま本リポジトリのdataフォルダ内に移動してください。

コードの言語はPython 3.9.6です。カレントディレクトリがCodeNet_analysys_iyの状態で実行してください。 **pandas** を使用するので、
**pip install pandas** 
コマンドなどでインストールしてください。

## ABC.py
"data/metadata/problem_list.csv"から、AtCoder Beginner Contest（ABC）に属する問題のみを抽出し、"output/ABC/problem_list_ABC.csv"に保存します。

## 難易度(rating)の追加など
"problem_list_ABC.csv"には、"AtCoder Beginner Contest"という名前を含まないAtCoder Beginner Contest(例：Sumitomo Mitsui Trust Bank Programming Contest 2019)に関する情報が含まれていません。

そこで、これらのコンテストに関する情報を追加しました。

また、このファイルの全ての問題について、rating列にA~Fの難易度を追加しました。

参考：[過去のコンテスト](https://atcoder.jp/contests/archive?category=0&keyword=&page=6&ratedType=1)

以上の情報を追加したものが、"data/problem_list_ABC_re.csv"です。


## problem_grouping.py
"data/metadata"及び"data/problem_list_ABC_re.csv"が存在する状態で実行してください。

"data/metadata"内にある問題のCSVファイルを、難易度別に分類します。

"output/problem_grouping"内のA~Fフォルダ内に、該当する問題のCSVファイルへのsymlinkを作成します。

このプログラムを実行しなくても、後述の"user_grouping.py"は実行可能です。


## user_grouping.py
"data/metadata"及び"data/problem_list_ABC_re.csv"が存在する状態で実行してください。

各問題の提出履歴を解析し、ユーザをグループ分けします。

分類方法は、[オンラインジャッジシステムにおける問題難易度に着目したエラーの調査](https://esa-storage-tokyo.s3-ap-northeast-1.amazonaws.com/uploads/production/attachments/21530/2025/05/28/182552/1bbba696-279f-4238-aa3b-8dedb13585f4.pdf)の2~3ページの手法に従います。

ユーザのグループ分けを標準出力し、"output/user_grouping/user_counts.csv"に保存します。また、各ユーザに関する情報を"output/user_grouping/users.csv"に保存します。
