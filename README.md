# jpgrep

grep for japanese text

## これは何ですか？

日本語の文章から言葉を見つけ出すためのツールです。
単純な文字列の比較ではなく形態素解析にもとづいた結果が得られます。
例えば「事」を検索した場合に、別の単語である「事実」にはマッチしません。

## インストール

Python のパッケージマネージャ PIP を使ってインストールします。
```
$ pip install git+https://github.com/momijiame/jpgrep.git
```

## 使い方

インストールすると jpgrep コマンドが使えるようになります。

特定のファイルから言葉を検索するには、検索する言葉とファイルまたはファイルが格納されているディレクトリを指定します。
```
$ jpgrep <word> <directory or file>
```

標準入力から検索する場合にはファイルの指定は不要です。
```
$ jpgrep <word>
```

一致しないものを探すには -v (--inverse) オプションをつけます。
```
$ jpgrep -v <word>
```

## 例

次のファイルには「事実」と「事」というふたつの単語が含まれています。
この中から「事」が含まれる行だけを検索してみましょう。
```
$ cat << EOF > sample.txt
それは事実です
そういう事です
EOF
$ jpgrep "事" sample.txt
sample.txt:そういう事です
```

標準入力から検索する場合にはファイルを指定する必要がありません。
```
$ cat sample.txt | jpgrep "事"
そういう事です
```

一致しないものを探すには -v オプションを使います。
```
$ jpgrep -v "事" sample.txt
sample.txt:それは事実です
sample.txt:
```
