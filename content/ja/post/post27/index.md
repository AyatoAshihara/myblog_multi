---
title: "【徹底比較】センチメントスコア算出手法！！ - 第2回"
author: admin
date: 2022-03-24T00:00:00Z
categories: ["単発"]
tags: ["Python","前処理","機械学習","テキスト解析"]
draft: false
featured: false
slug: ["sentiment_score"]
image:
  caption: ''
  focal_point: ""
  placement: 2
  preview_only: false
lastmod: ""
projects: []
summary: 機械学習を用いたセンチメントスコアの算出方法の発展を簡単にさらっていきます。
output: 
  blogdown::html_page:
    toc: true
codefolding_show: "hide"
bibliography: references.bib
---

<script src="{{< blogdown/postref >}}index_files/kePrint/kePrint.js"></script>
<link href="{{< blogdown/postref >}}index_files/lightable/lightable.css" rel="stylesheet" />
<link href="{{< blogdown/postref >}}index_files/bsTable/bootstrapTable.min.css" rel="stylesheet" />
<script src="{{< blogdown/postref >}}index_files/bsTable/bootstrapTable.js"></script>

おはこんばんにちは。センチメントスコア算出企画の第2弾です。
今回は辞書ベースのセンチメントスコア算出方法を実践します。

## 1. 分析手法の説明

### 辞書ベース手法とは

辞書ベース手法はその名の通り、辞書を用いてセンチメントスコアを算出する手法です。各単語が持つ感情極性(ここでは、ポジティブな意味かネガティブな意味かを表す)をスコア化したものをあらかじめ辞書として保存し、文書内で出現した単語とそれぞれの辞書スコアを紐付け、(何らかの方法で)集計することで、その文書全体のセンチメントスコアを算出します。

### センチメントスコアを参照する辞書

上記においては、スコアをどのように算出するのかが重要になります。現在公開されている日本語辞書の中で有名な東京工業大学の高村研究室が作成した辞書(Takamura, Inui, and Okumura 2005)では以下のような方法で算出を行っているようです([原典はこちら](http://lr-www.pi.titech.ac.jp/wp/?page_id=4))。

> まず，辞書，シソーラス（類義語辞典），コーパスデータを用いて，極性が同じになりやすい単語ペアを抽出し，そしてそれらのペアを連結することにより巨大な語彙ネットワークを構築します．たとえば，「良い」と「良好」が類義語関係にあるので，この二単語を結ぶなどの作業を行います．ここで，単語の感情極性を電子スピンの方向とみなし，語彙ネットワークをスピン系とみなして，語彙ネットワークの状態（各スピンがどの方向を向いているか）を計算します．この計算結果を見ることにより，単語の感情極性がわかるのです．

こちらの辞書はHPで公開されており、非営利目的であれば利用が可能のようです。ちょっと覗いてみましょう。

    ##       単語 読み仮名   品詞 感情極性スコア
    ## 1   優れる すぐれる   動詞       1.000000
    ## 2     良い     よい 形容詞       0.999995
    ## 3     喜ぶ よろこぶ   動詞       0.999979
    ## 4   褒める   ほめる   動詞       0.999979
    ## 5 めでたい めでたい 形容詞       0.999645
    ## 6     賢い かしこい 形容詞       0.999486

センチメントスコアは1から-1までを取り、1に近いほどポジティブを表します。最もポジティブな単語は「優れる」となっていることがわかります。

### 辞書ベース手法の利点・欠点

<利点>手法のわかりやすさ/教師データが不要:thumbsup:  
辞書を利用する良い点は、手法のわかりやすさと教師データを必要としない点です。特に後者は辞書ベースならではの長所です。通常、文書分類器を作成するためには、その文書がポジティブ・ネガティブのどちらであるかという正解ラベルの付いた教師データが必要です。必要なデータは文脈にもよると思いますが、少なくとも100件は必要でしょう。これは分析者が少なくとも100件以上の文書を読んで、手作業でラベルを付与しなければならないことを意味します。

<欠点>辞書の性能に結果が大きく依存する:thumbsdown:  
短所としては、特殊な文脈におけるセンチメントスコアを参集する場合は専用の辞書が必要になるという点です。辞書ベースの分類法の場合、辞書に含まれない単語はセンチメントスコアへ影響を全く与えません。また、一般に公開されている辞書はwikipedia等のオールジャンルの文書を学習することによって開発されていることが多いため、感情極性が文脈に対してニュートラルになっています。よって、例えば金融等の文脈におけるセンチメントスコアを算出する場合、専門用語の感性極性が0となったり、文脈を考慮した感性極性が得られないことから、直感と異なる結果が出る可能性があります。

## 2. 辞書ベース手法の実践

### 使用データ

では、実際に辞書ベース手法を用いて、景気ウォッチャー調査の文章からセンチメントスコアの抽出を試みます。景気ウオッチャー調査では、タクシー運転手や小売店の店主、旅館の経営者など景気に敏感な方々(景気ウオッチャー)に対して、5段階の景況感とその理由を毎月アンケートしています。5段階は、「良い(◎)」、「やや良い(○)」、「変わらない(■)」、「やや悪い(▲)」、「悪い(×)」となっています。

データを覗いてみると、以下のようになっています。

<table class="table table-striped" style="margin-left: auto; margin-right: auto;">
<thead>
<tr>
<th style="text-align:right;">
基準年
</th>
<th style="text-align:left;">
基準日
</th>
<th style="text-align:left;">
景気の現状判断
</th>
<th style="text-align:left;">
業種・職種
</th>
<th style="text-align:left;">
判断の理由
</th>
<th style="text-align:left;">
追加説明及び具体的状況の説明
</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align:right;">
2016
</td>
<td style="text-align:left;">
1月31日
</td>
<td style="text-align:left;">
◎
</td>
<td style="text-align:left;">
旅行代理店（従業員）
</td>
<td style="text-align:left;">
販売量の動き
</td>
<td style="text-align:left;">
・店頭の取扱額が前年比約120％と好調であった。
</td>
</tr>
<tr>
<td style="text-align:right;">
2016
</td>
<td style="text-align:left;">
1月31日
</td>
<td style="text-align:left;">
◎
</td>
<td style="text-align:left;">
観光名所（従業員）
</td>
<td style="text-align:left;">
来客数の動き
</td>
<td style="text-align:left;">
・当施設の利用乗降客数は１月26日時点で前年比130.1％となっており、１月としては過去最高の利用乗降客数になることが確定したほどの入込状況にある。
</td>
</tr>
<tr>
<td style="text-align:right;">
2016
</td>
<td style="text-align:left;">
1月31日
</td>
<td style="text-align:left;">
○
</td>
<td style="text-align:left;">
一般小売店［酒］（経営者）
</td>
<td style="text-align:left;">
単価の動き
</td>
<td style="text-align:left;">
・年末の消費の反動もあってか、客の動きがやや鈍い。ただ、相変わらず高額商材が売れているということもあり、売上はそれなりの金額をキープしている。
</td>
</tr>
<tr>
<td style="text-align:right;">
2016
</td>
<td style="text-align:left;">
1月31日
</td>
<td style="text-align:left;">
○
</td>
<td style="text-align:left;">
百貨店（売場主任）
</td>
<td style="text-align:left;">
お客様の様子
</td>
<td style="text-align:left;">
・外国人観光客による売上が前年比152％と好調を継続しているほか、来客数が前年比102％と好調を維持している。月半ばに停滞した売上も下旬に入ってから回復傾向にあり、定価品、バーゲン品とも前年を上回っている。
</td>
</tr>
<tr>
<td style="text-align:right;">
2016
</td>
<td style="text-align:left;">
1月31日
</td>
<td style="text-align:left;">
○
</td>
<td style="text-align:left;">
百貨店（担当者）
</td>
<td style="text-align:left;">
来客数の動き
</td>
<td style="text-align:left;">
・積極的に景気が上向きにあるとまではいいづらいものの、３か月前との比較では改善している。
</td>
</tr>
<tr>
<td style="text-align:right;">
2016
</td>
<td style="text-align:left;">
1月31日
</td>
<td style="text-align:left;">
○
</td>
<td style="text-align:left;">
百貨店（販売促進担当）
</td>
<td style="text-align:left;">
それ以外
</td>
<td style="text-align:left;">
・気温が平年並みとなり、これまでの温暖、少雪の状態がみられなくなってきたことで、防寒衣料、雑貨商材を中心に多少改善の傾向がみられる。
</td>
</tr>
</tbody>
</table>

「景気の現状判断」が景況感を表しており、その判断の理由が「追加説明及び具体的状況の説明」にある形です。よって、前者を教師データ、後者を説明データとする教師あり学習データとして利用することができます。

### 前処理

まず、各手法で共通の前処理を行います。以下では、使用するモジュールを呼び出し、学習データのうち有効回答のみを抽出します。
なお、使用するモジュールの関係でPythonでの処理を紹介しますが、Rでも同じ処理ができます。

``` python
from sudachipy import tokenizer
from sudachipy import dictionary
from sklearn.preprocessing import LabelEncoder
import pandas as pd

sample = pd.read_csv(r"C:\Users\hogehoge\景気ウオッチャー\生データ\watcher_2016.csv",encoding="shift-jis")
sample = sample[(sample.追加説明及び具体的状況の説明=='−')|(sample.追加説明及び具体的状況の説明=='＊')==False|(sample.景気の現状判断=='□')]
```

次に、文書のトークン化を行います。日本語のような言語では英語などと異なり単語ごとの間にスペースがないため、別途区切りを入れてやる必要があります。区切られた各語は形態素と呼ばれ、言葉が意味を持つまとまりの単語の最小単位を指します。また、文章を形態素へ分割することを形態素解析と言います(英語のような場合単にTokenizationと言ったりします)。形態素解析を行うツールは以下のようなものが存在します。

-   MeCab
-   JUMAN
-   JANOME
-   Ginza
-   Sudachi

おそらく最も使用されているものはMecabではないかと思いますが、標準装備されている辞書(ipadic)の更新がストップしており、最近の新語に対応できないという問題があります。この点については新語に強いNEologd辞書を加えることで、対処可能であることを別記事で紹介していますが、今回はワークスアプリケーションズが提供しているSudachi(Takaoka et al. 2018)を使用することにしたいと思います。公式GithubからSudachiの特長を引用します。

-   複数の分割単位の併用

    -   必要に応じて切り替え
    -   形態素解析と固有表現抽出の融合

-   多数の収録語彙

    -   UniDic と NEologd をベースに調整

-   機能のプラグイン化

    -   文字正規化や未知語処理に機能追加が可能

-   同義語辞書との連携

    -   後日公開予定

特質すべきは「複数の分割単位の併用」でしょう。Sudachiでは短い方から A, B, Cの3つの分割モードを提供しています。AはUniDic短単位相当、Cは固有表現相当、BはA, Cの中間的な単位となっており、以下のように同じ「選挙管理委員会」という単語でも形態素が異なることが確認できます。これはSudachi特有の特長になります。

``` python
tokenizer_obj = dictionary.Dictionary().create()

mode = tokenizer.Tokenizer.SplitMode.A
[m.normalized_form() for m in tokenizer_obj.tokenize("選挙管理委員会", mode)]
```

    ## ['選挙', '管理', '委員', '会']

``` python
mode = tokenizer.Tokenizer.SplitMode.B
[m.normalized_form() for m in tokenizer_obj.tokenize("選挙管理委員会", mode)]
```

    ## ['選挙', '管理', '委員会']

``` python
mode = tokenizer.Tokenizer.SplitMode.C
[m.normalized_form() for m in tokenizer_obj.tokenize("選挙管理委員会", mode)]
```

    ## ['選挙管理委員会']

また、辞書についてもUniDicとNEologdをベースとして更新が続けられており、新語にも対応できます。

``` python
mode = tokenizer.Tokenizer.SplitMode.C
[m.normalized_form() for m in tokenizer_obj.tokenize("新型コロナウイルス", mode)]
```

    ## ['新型コロナウイルス']

個人的に素晴らしいと思うポイントは表記正規化や文字正規化ができると言うことです。以下のように旧字等で同じ意味だが表記が異なる単語や英語/日本語、書き間違え等を正規化する機能があります。

``` python
tokenizer_obj.tokenize("附属", mode)[0].normalized_form()
```

    ## '付属'

``` python
tokenizer_obj.tokenize("SUMMER", mode)[0].normalized_form()
```

    ## 'サマー'

``` python
tokenizer_obj.tokenize("シュミレーション", mode)[0].normalized_form()
```

    ## 'シミュレーション'

このような高性能な形態素解析ツールが無償でしかも商用利用も可というところに驚きを隠せません。後述しますが、このSudachiで形態素解析を行ったWord2vecモデルであるChiveもワークスアプリケーションズは提供をしています。

説明が長くなりましたがSudachiでTokenizationを行いましょう。Sudachiは`Python`で使用することができます。説明が前後していますが、上記コードで行っているように`tokenizer`オブジェクトを作成し、`tokenize()`メソッドで文章をTokenizeします。Tokenizeされた結果は`MorphemeList`オブジェクトに格納されます。`MorphemeList`オブジェクトの各要素に対して`normalized_form()`メソッドを実行することで正規化された形態素を取得することができます。ここまでをやってみます。

``` python
tokenizer_obj = dictionary.Dictionary().create()
mode = tokenizer.Tokenizer.SplitMode.C
tokenizer_sudachi = lambda t: [m.normalized_form() for m in tokenizer_obj.tokenize(t, mode)]
tokens = sample.追加説明及び具体的状況の説明.map(tokenizer_sudachi)
tokens.head()
```

    ## 0    [・, 店頭, の, 取り扱い, 額, が, 前年, 比, 約, 120, %, と, 好調...
    ## 1    [・, 当, 施設, の, 利用, 乗降, 客数, は, 1, 月, 26, 日, 時点, ...
    ## 2    [・, 年, 末, の, 消費, の, 反動, も, 有る, て, か, 、, 客, の, ...
    ## 3    [・, 外国人, 観光客, に, よる, 売り上げ, が, 前年, 比, 152, %, と...
    ## 4    [・, 積極的, だ, 景気, が, 上向き, に, 有る, と, まで, は, 言う, 辛...
    ## Name: 追加説明及び具体的状況の説明, dtype: object

Tokenizeすることができました。次に5段階の景況判断をLabel Encodingに変換します。変換には`Scikit-Learn`の`LabelEncoder`を使用します。

``` python
score_mapping = {'◎': 1, '○': 1, '▲': 0, '×':0}
label = sample.景気の現状判断.map(score_mapping)
```

これで前処理は完了です。

### センチメントスコアの抽出

では、実践です。`quanteda`というパッケージを用いるため、`R`で行っていきます。前処理は`R`で実施済みで、`toks_sent`という変数に各文書の形態素が文書別に格納されています。

この`toks_sent`から文書行列を生成します。文書行列とは、単語と文書の関係を表す行列で、各行が単語(token)、各列が文書を表し、各要素は文書中の単語の出現回数となっています。

``` r
# 文書行列の生成
dfmt_sent <- toks_sent %>% 
              quanteda::dfm(remove = "") %>% 
              quanteda::dfm_trim(min_termfreq = 10)
```

文書行列`dfmt_sent`と各単語のスコアベクトルの内積を取り、文書のセンチメントスコアを算出します。

``` r
# 単語感情極性対応表
PNdict <- read.delim("http://www.lr.pi.titech.ac.jp/~takamura/pubs/pn_ja.dic",header=FALSE,sep=":")

# 辞書の並びに合わせて文書行列の列を入れ替える。
dfmt_sent_arranged <- quanteda::dfm_match(dfmt_sent, PNdict$V1)

# 文書のセンチメントスコア算出
n <- unname(quanteda::rowSums(dfmt_sent_arranged))
score_dict <- ifelse(n>0, quanteda::rowSums(dfmt_sent_arranged %*% PNdict$V4)/n, NA)
sample_with_score_dict <- sample %>% cbind(score_dict) 
sample_with_score_dict %>% head()
```

    ##   基準年  基準日 景気の現状判断                 業種・職種   判断の理由
    ## 1   2016 1月31日             ◎       旅行代理店（従業員） 販売量の動き
    ## 2   2016 1月31日             ◎         観光名所（従業員） 来客数の動き
    ## 3   2016 1月31日             ○ 一般小売店［酒］（経営者）   単価の動き
    ## 4   2016 1月31日             ○         百貨店（売場主任） お客様の様子
    ## 5   2016 1月31日             ○           百貨店（担当者） 来客数の動き
    ## 6   2016 1月31日             ○     百貨店（販売促進担当）     それ以外
    ##                                                                                                                                                                               追加説明及び具体的状況の説明
    ## 1                                                                                                                                                            ・店頭の取扱額が前年比約120％と好調であった。
    ## 2                                                            ・当施設の利用乗降客数は１月26日時点で前年比130.1％となっており、１月としては過去最高の利用乗降客数になることが確定したほどの入込状況にある。
    ## 3                                                           ・年末の消費の反動もあってか、客の動きがやや鈍い。ただ、相変わらず高額商材が売れているということもあり、売上はそれなりの金額をキープしている。
    ## 4 ・外国人観光客による売上が前年比152％と好調を継続しているほか、来客数が前年比102％と好調を維持している。月半ばに停滞した売上も下旬に入ってから回復傾向にあり、定価品、バーゲン品とも前年を上回っている。
    ## 5                                                                                                                 ・積極的に景気が上向きにあるとまではいいづらいものの、３か月前との比較では改善している。
    ## 6                                                                     ・気温が平年並みとなり、これまでの温暖、少雪の状態がみられなくなってきたことで、防寒衣料、雑貨商材を中心に多少改善の傾向がみられる。
    ##     score_dict
    ## 1 -0.348178400
    ## 2 -0.565735877
    ## 3 -0.612866000
    ## 4 -0.325386370
    ## 5  0.006678875
    ## 6 -0.476283793

``` r
# 結果の可視化
library(ggplot2)
ggplot(sample_with_score_dict, aes(x=景気の現状判断,y=score_dict)) + geom_boxplot()
```

<img src="{{< blogdown/postref >}}index_files/figure-html/unnamed-chunk-13-1.png" width="672" />

「景気の現状判断」毎にboxplotを書いてみましたが、ぱっと見はあまり変わらない結果になりました。
どの判断も-0.5くらいが平均で、ほんの少し緩やかに右肩上がりのような気もしますが、文書を分類できている言える結果ではないことがわかります。

## 3. 終わりに

最も簡易な手法ということで予想はしていましたが、辞書ベース手法ではセンチメントスコアの抽出はできませんでした。もちろん、私のやり方が悪いのが理由で上手くやれば文書の分類は可能かもしれません。ただ、経済に特化した極性辞書を準備しなければ難しいのではないかというのが、私の感想です。
次はナイーブベイズ分類器を用いた文書分類に取り組みます。
ここまで、読み進めて頂きましてありがとうございました。次回の記事も期待していてください。

<div id="refs" class="references csl-bib-body hanging-indent">

<div id="ref-takamura2005" class="csl-entry">

Takamura, Hiroya, Takashi Inui, and Manabu Okumura. 2005. “The 43rd Annual Meeting.” In. Association for Computational Linguistics. <https://doi.org/10.3115/1219840.1219857>.

</div>

<div id="ref-TAKAOKA18.8884" class="csl-entry">

Takaoka, Kazuma, Sorami Hisamoto, Noriko Kawahara, Miho Sakamoto, Yoshitaka Uchida, and Yuji Matsumoto. 2018. “Sudachi: A Japanese Tokenizer for Business.” In *Proceedings of the Eleventh International Conference on Language Resources and Evaluation (LREC 2018)*, edited by Nicoletta Calzolari (Conference chair), Khalid Choukri, Christopher Cieri, Thierry Declerck, Sara Goggi, Koiti Hasida, Hitoshi Isahara, et al. Paris, France: European Language Resources Association (ELRA).

</div>

</div>
