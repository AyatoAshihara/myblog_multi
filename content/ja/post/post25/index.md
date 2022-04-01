---
title: "【徹底比較】センチメントスコア算出手法！！ - 第1回"
author: admin
date: 2022-03-21T00:00:00Z
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
summary: テキストからセンチメント情報を抽出する手法を数回にわたって紹介します。
output: 
  blogdown::html_page:
    toc: true
codefolding_show: "hide"
---
<script src="{{< blogdown/postref >}}index_files/kePrint/kePrint.js"></script>
<link href="{{< blogdown/postref >}}index_files/lightable/lightable.css" rel="stylesheet" />
<link href="{{< blogdown/postref >}}index_files/bsTable/bootstrapTable.min.css" rel="stylesheet" />
<script src="{{< blogdown/postref >}}index_files/bsTable/bootstrapTable.js"></script>
<script src="{{< blogdown/postref >}}index_files/kePrint/kePrint.js"></script>
<link href="{{< blogdown/postref >}}index_files/lightable/lightable.css" rel="stylesheet" />
<link href="{{< blogdown/postref >}}index_files/bsTable/bootstrapTable.min.css" rel="stylesheet" />
<script src="{{< blogdown/postref >}}index_files/bsTable/bootstrapTable.js"></script>
<script src="{{< blogdown/postref >}}index_files/kePrint/kePrint.js"></script>
<link href="{{< blogdown/postref >}}index_files/lightable/lightable.css" rel="stylesheet" />
<link href="{{< blogdown/postref >}}index_files/bsTable/bootstrapTable.min.css" rel="stylesheet" />
<script src="{{< blogdown/postref >}}index_files/bsTable/bootstrapTable.js"></script>
<script src="{{< blogdown/postref >}}index_files/kePrint/kePrint.js"></script>
<link href="{{< blogdown/postref >}}index_files/lightable/lightable.css" rel="stylesheet" />
<link href="{{< blogdown/postref >}}index_files/bsTable/bootstrapTable.min.css" rel="stylesheet" />
<script src="{{< blogdown/postref >}}index_files/bsTable/bootstrapTable.js"></script>
<script src="{{< blogdown/postref >}}index_files/kePrint/kePrint.js"></script>
<link href="{{< blogdown/postref >}}index_files/lightable/lightable.css" rel="stylesheet" />
<link href="{{< blogdown/postref >}}index_files/bsTable/bootstrapTable.min.css" rel="stylesheet" />
<script src="{{< blogdown/postref >}}index_files/bsTable/bootstrapTable.js"></script>
<script src="{{< blogdown/postref >}}index_files/kePrint/kePrint.js"></script>
<link href="{{< blogdown/postref >}}index_files/lightable/lightable.css" rel="stylesheet" />
<link href="{{< blogdown/postref >}}index_files/bsTable/bootstrapTable.min.css" rel="stylesheet" />
<script src="{{< blogdown/postref >}}index_files/bsTable/bootstrapTable.js"></script>
<script src="{{< blogdown/postref >}}index_files/kePrint/kePrint.js"></script>
<link href="{{< blogdown/postref >}}index_files/lightable/lightable.css" rel="stylesheet" />
<link href="{{< blogdown/postref >}}index_files/bsTable/bootstrapTable.min.css" rel="stylesheet" />
<script src="{{< blogdown/postref >}}index_files/bsTable/bootstrapTable.js"></script>

おはこんばんにちは。テキスト解析はデータ分析界隈ではもうかなり当たり前になってきています。テキストの感性情報(センチメント)を抽出する手法には、どのようなものがあるかあるのか調べたところかなり時代は進んでいると実感しました。これら数回にわたって、実際に`R`や`Python`で作成した機械学習モデルの精度を比較してみたいと思います。 今回はその第１回目ということで、データセットや全体感のお話です。





## 1. 解きたい問題

今回解きたい問題は「景況感を表す文書表現を学習し、実際の景気判断を予測する」というタスクです。 データセットには、内閣府が出している景気ウオッチャー調査を使用します。

### 景気ウオッチャー調査とは

景気ウオッチャー調査とは、内閣府が月次で公表している景気動向判断のための統計情報です。調査の目的は以下の通りです([内閣府Webサイト](https://www5.cao.go.jp/keizai3/watcher/watcher_mokuteki.html#mokuteki)より)。

\<調査の目的>

:   地域の景気に関連の深い動きを観察できる立場にある人々の協力を得て、地域ごとの景気動向を的確かつ迅速に把握し、景気動向判断の基礎資料とすることを目的とする。

では、この「地域の景気に関連の深い動きを観察できる立場にある人々」、「地域ごとの景気動向」、「的確かつ迅速に」という部分について少し深掘ってみます。

#### 調査の対象範囲

調査の対象範囲は47都道府県となっています。また、調査対象者は「家計動向、企業動向、雇用等、代表的な経済活動項目の動向を敏感に反映する現象を観察できる業種の適当な職種の中から選定した2,050人」となっており、例えば小売店や飲食店の店員・店長、タクシー運転手、製造業・非製造業企業の経営者・従業員、人材派遣会社社員などを対象に行われています。

#### 調査期日および期間

調査は月次で行われ、毎月25日から月末にかけて実施されます。当月の景況感について調査が行われ、翌月に公表されます。

#### 調査の実施方法

アンケート調査を電話・Webサイト・電子メールのいずれかで回答することになっています。質問項目は以下の通りです([調査票](https://www5.cao.go.jp/keizai3/watcher/chousahyo.pdf))。

1.  景気の現状に対する判断（方向性）

2.  1.の理由

3.  2.の追加説明及び具体的状況の説明(自由記述)

4.  景気の先行きに対する判断(方向性)

5.  (4)の理由

6.  (参考)景気の現状に対する判断(水準)

ご参考までに2016年1月調査のサンプルデータをお見せします。




```r
filePath <- r"(C:\Users\hogehoge\Watcher\RawData\watcher_2016.csv)"
```



```r
library(magrittr)
sample <- readr::read_csv(filePath,locale=readr::locale(encoding="SHIFT-JIS"), show_col_types=FALSE)
options(kableExtra.html.bsTable = TRUE)
knitr::kable(head(sample)) %>% 
  kableExtra::kable_styling(bootstrap_options = c("striped"))
```

<table class="table table-striped" style="margin-left: auto; margin-right: auto;">
 <thead>
  <tr>
   <th style="text-align:right;"> 基準年 </th>
   <th style="text-align:left;"> 基準日 </th>
   <th style="text-align:left;"> 景気の現状判断 </th>
   <th style="text-align:left;"> 業種・職種 </th>
   <th style="text-align:left;"> 判断の理由 </th>
   <th style="text-align:left;"> 追加説明及び具体的状況の説明 </th>
  </tr>
 </thead>
<tbody>
  <tr>
   <td style="text-align:right;"> 2016 </td>
   <td style="text-align:left;"> 1月31日 </td>
   <td style="text-align:left;"> ◎ </td>
   <td style="text-align:left;"> 旅行代理店（従業員） </td>
   <td style="text-align:left;"> 販売量の動き </td>
   <td style="text-align:left;"> ・店頭の取扱額が前年比約120％と好調であった。 </td>
  </tr>
  <tr>
   <td style="text-align:right;"> 2016 </td>
   <td style="text-align:left;"> 1月31日 </td>
   <td style="text-align:left;"> ◎ </td>
   <td style="text-align:left;"> 観光名所（従業員） </td>
   <td style="text-align:left;"> 来客数の動き </td>
   <td style="text-align:left;"> ・当施設の利用乗降客数は１月26日時点で前年比130.1％となっており、１月としては過去最高の利用乗降客数になることが確定したほどの入込状況にある。 </td>
  </tr>
  <tr>
   <td style="text-align:right;"> 2016 </td>
   <td style="text-align:left;"> 1月31日 </td>
   <td style="text-align:left;"> ○ </td>
   <td style="text-align:left;"> 一般小売店［酒］（経営者） </td>
   <td style="text-align:left;"> 単価の動き </td>
   <td style="text-align:left;"> ・年末の消費の反動もあってか、客の動きがやや鈍い。ただ、相変わらず高額商材が売れているということもあり、売上はそれなりの金額をキープしている。 </td>
  </tr>
  <tr>
   <td style="text-align:right;"> 2016 </td>
   <td style="text-align:left;"> 1月31日 </td>
   <td style="text-align:left;"> ○ </td>
   <td style="text-align:left;"> 百貨店（売場主任） </td>
   <td style="text-align:left;"> お客様の様子 </td>
   <td style="text-align:left;"> ・外国人観光客による売上が前年比152％と好調を継続しているほか、来客数が前年比102％と好調を維持している。月半ばに停滞した売上も下旬に入ってから回復傾向にあり、定価品、バーゲン品とも前年を上回っている。 </td>
  </tr>
  <tr>
   <td style="text-align:right;"> 2016 </td>
   <td style="text-align:left;"> 1月31日 </td>
   <td style="text-align:left;"> ○ </td>
   <td style="text-align:left;"> 百貨店（担当者） </td>
   <td style="text-align:left;"> 来客数の動き </td>
   <td style="text-align:left;"> ・積極的に景気が上向きにあるとまではいいづらいものの、３か月前との比較では改善している。 </td>
  </tr>
  <tr>
   <td style="text-align:right;"> 2016 </td>
   <td style="text-align:left;"> 1月31日 </td>
   <td style="text-align:left;"> ○ </td>
   <td style="text-align:left;"> 百貨店（販売促進担当） </td>
   <td style="text-align:left;"> それ以外 </td>
   <td style="text-align:left;"> ・気温が平年並みとなり、これまでの温暖、少雪の状態がみられなくなってきたことで、防寒衣料、雑貨商材を中心に多少改善の傾向がみられる。 </td>
  </tr>
</tbody>
</table>

### 問題設定

今回の問題設定は、「追加説明及び具体的状況の説明」に記載されているテキスト情報をもとに、「景気の現状判断」を予測するタスクになります。
「景気の現状判断」は「良い(◎)」、「やや良い(○)」、「変わらない(■)」、「やや悪い(▲)」、「悪い(×)」となっており、これを2値分類問題にして学習を行います(変わらない(■)はサンプルから除外)。

## 2. テキスト解析手法の進化の譜系

上記問題設定を解くためには、テキスト情報から感性情報(センチメント)を抽出する必要があります。私が調べた浅い知識によると、感性情報の抽出方法には以下のような手法があります。

1.  辞書ベース
2.  ナイーブベイズ分類器
3.  単語埋め込み(Word Embedding)を用いた方法
4.  Recurrent neural network(RNN)
5.  Transformer

おそらく、下に行くにつれてより最新の手法になっており、精度も高いのではないかと推察されます。 また、1,2,3はやり方にもよるんでしょうが文章が与えられた際にその語順関係を考慮しません。 今後、各手法について解析結果の記事を投稿する予定ですので、詳しい中身についてはそれぞれの回で触れたいと思います。

## 3. サンプルデータ概観

### サンプルデータの読み込み

今回使用する景気ウオッチャー調査のサンプルは2016年~2020年のものとなっています。現状判断の調査結果を格のしたcsvファイル(景気判断理由集)を月ごとに内閣府のWebページからダウンロードし、整形したものを年ごとに連結しています。




```r
filepath = r"(C:\Users\hogehoge\Watcher\RawData)"
```


```r
files <- stringr::str_c(filepath, "\\",list.files(filepath, pattern = "*.csv"))
sample <- readr::read_csv(files, locale=readr::locale(encoding="SHIFT-JIS"), show_col_types = FALSE)
# 「－」は回答が存在しない、「＊」は主だった回答等が存在しないため、除外
sample <- sample[sample$追加説明及び具体的状況の説明 != "－",]
sample <- sample[sample$追加説明及び具体的状況の説明 != "＊",]
```

知らなかったんですが、`readr::read_csv`って2.0.0からファイルパスのリストを引数としてcsvを読み込み、その結果を連結してくれるようになったんですね。地味に便利です。

### サンプルサイズ

サンプルサイズは76800でした。サンプルサイズとしては申し分ないかと思います。


```r
NROW(sample)
```

```
## [1] 76800
```

念のため、各年ごとにも見てみます。


```r
library(magrittr)
sample %>% 
  dplyr::group_by(基準年) %>% 
  dplyr::summarise(サンプルサイズ=dplyr::n()) %>% 
  dplyr::mutate(`割合(%)`=round(サンプルサイズ/sum(サンプルサイズ)*100, digits=1)) %>% 
  knitr::kable() %>% 
  kableExtra::kable_styling(bootstrap_options = c("striped"))
```

<table class="table table-striped" style="margin-left: auto; margin-right: auto;">
 <thead>
  <tr>
   <th style="text-align:right;"> 基準年 </th>
   <th style="text-align:right;"> サンプルサイズ </th>
   <th style="text-align:right;"> 割合(%) </th>
  </tr>
 </thead>
<tbody>
  <tr>
   <td style="text-align:right;"> 2016 </td>
   <td style="text-align:right;"> 15168 </td>
   <td style="text-align:right;"> 19.8 </td>
  </tr>
  <tr>
   <td style="text-align:right;"> 2017 </td>
   <td style="text-align:right;"> 16724 </td>
   <td style="text-align:right;"> 21.8 </td>
  </tr>
  <tr>
   <td style="text-align:right;"> 2018 </td>
   <td style="text-align:right;"> 14756 </td>
   <td style="text-align:right;"> 19.2 </td>
  </tr>
  <tr>
   <td style="text-align:right;"> 2019 </td>
   <td style="text-align:right;"> 14588 </td>
   <td style="text-align:right;"> 19.0 </td>
  </tr>
  <tr>
   <td style="text-align:right;"> 2020 </td>
   <td style="text-align:right;"> 15564 </td>
   <td style="text-align:right;"> 20.3 </td>
  </tr>
</tbody>
</table>

各年およそ14,000~16,000サンプルほど存在するようです。大きなバラツキもありません。

### `景気の現状判断`の分布

これから予測を行う`景気の現状判断`はどのような分布になっているでしょうか。


```r
sample$景気の現状判断 <- factor(sample$景気の現状判断, levels=c("◎","○","□","▲","×"))
sample %>% 
  dplyr::group_by(景気の現状判断) %>%
  dplyr::summarise(サンプルサイズ=dplyr::n()) %>% 
  dplyr::mutate(`割合(%)`=round(サンプルサイズ/sum(サンプルサイズ)*100, digits=1)) %>% 
  knitr::kable() %>% 
  kableExtra::kable_styling(bootstrap_options = c("striped"))
```

<table class="table table-striped" style="margin-left: auto; margin-right: auto;">
 <thead>
  <tr>
   <th style="text-align:left;"> 景気の現状判断 </th>
   <th style="text-align:right;"> サンプルサイズ </th>
   <th style="text-align:right;"> 割合(%) </th>
  </tr>
 </thead>
<tbody>
  <tr>
   <td style="text-align:left;"> ◎ </td>
   <td style="text-align:right;"> 1569 </td>
   <td style="text-align:right;"> 2.0 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> ○ </td>
   <td style="text-align:right;"> 14370 </td>
   <td style="text-align:right;"> 18.7 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> □ </td>
   <td style="text-align:right;"> 34438 </td>
   <td style="text-align:right;"> 44.8 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> ▲ </td>
   <td style="text-align:right;"> 18642 </td>
   <td style="text-align:right;"> 24.3 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> × </td>
   <td style="text-align:right;"> 7781 </td>
   <td style="text-align:right;"> 10.1 </td>
  </tr>
</tbody>
</table>

思ったよりキレイな分布をしている印象です。このサンプル期間では、「どちらとも言えない」が最も多く、また、比較的「やや悪い」や「悪い」が多いことがわかります。このあたりは2019年度以降のコロナ禍の影響を反映している可能性があるので、新たに時間軸を追加し、クロス集計をしてみましょう。


```r
sample %>% 
  dplyr::group_by(基準年, 景気の現状判断) %>% 
  dplyr::tally() %>% 
  tidyr::spread(景気の現状判断, n) %>% 
  knitr::kable() %>% 
  kableExtra::kable_styling(bootstrap_options = c("striped"))
```

<table class="table table-striped" style="margin-left: auto; margin-right: auto;">
 <thead>
  <tr>
   <th style="text-align:right;"> 基準年 </th>
   <th style="text-align:right;"> ◎ </th>
   <th style="text-align:right;"> ○ </th>
   <th style="text-align:right;"> □ </th>
   <th style="text-align:right;"> ▲ </th>
   <th style="text-align:right;"> × </th>
  </tr>
 </thead>
<tbody>
  <tr>
   <td style="text-align:right;"> 2016 </td>
   <td style="text-align:right;"> 235 </td>
   <td style="text-align:right;"> 2455 </td>
   <td style="text-align:right;"> 7546 </td>
   <td style="text-align:right;"> 4129 </td>
   <td style="text-align:right;"> 803 </td>
  </tr>
  <tr>
   <td style="text-align:right;"> 2017 </td>
   <td style="text-align:right;"> 375 </td>
   <td style="text-align:right;"> 4031 </td>
   <td style="text-align:right;"> 8681 </td>
   <td style="text-align:right;"> 3053 </td>
   <td style="text-align:right;"> 584 </td>
  </tr>
  <tr>
   <td style="text-align:right;"> 2018 </td>
   <td style="text-align:right;"> 349 </td>
   <td style="text-align:right;"> 3105 </td>
   <td style="text-align:right;"> 7340 </td>
   <td style="text-align:right;"> 3336 </td>
   <td style="text-align:right;"> 626 </td>
  </tr>
  <tr>
   <td style="text-align:right;"> 2019 </td>
   <td style="text-align:right;"> 237 </td>
   <td style="text-align:right;"> 2050 </td>
   <td style="text-align:right;"> 6743 </td>
   <td style="text-align:right;"> 4516 </td>
   <td style="text-align:right;"> 1042 </td>
  </tr>
  <tr>
   <td style="text-align:right;"> 2020 </td>
   <td style="text-align:right;"> 373 </td>
   <td style="text-align:right;"> 2729 </td>
   <td style="text-align:right;"> 4128 </td>
   <td style="text-align:right;"> 3608 </td>
   <td style="text-align:right;"> 4726 </td>
  </tr>
</tbody>
</table>

やはり、2019年以降「悪い」が多く出現していることがわかります。一方で、「やや悪い」はそれ以前の年でも恒常的に多いようです。

### 回答者の属性

次に回答者の属性を確認しましょう。回答者の属性は`業種・職種`から取得できます。まず、どういった業種が多く回答しているのか確認してみます。回答数上位10番目までの業種を表示させます。


```r
sample %>% 
  dplyr::mutate(業種 = stringr::str_remove(sample$`業種・職種`, "（.+）") %>% 
stringr::str_remove("［.+］")) %>% 
  dplyr::group_by(業種) %>% 
  dplyr::summarise(サンプルサイズ=dplyr::n()) %>% 
  dplyr::arrange(desc(サンプルサイズ)) %>% 
  dplyr::top_n(10, サンプルサイズ) %>% 
  dplyr::mutate(`割合(%)`=round(サンプルサイズ/sum(サンプルサイズ)*100, digits=1)) %>% 
  knitr::kable() %>% 
  kableExtra::kable_styling(bootstrap_options = c("striped"))
```

<table class="table table-striped" style="margin-left: auto; margin-right: auto;">
 <thead>
  <tr>
   <th style="text-align:left;"> 業種 </th>
   <th style="text-align:right;"> サンプルサイズ </th>
   <th style="text-align:right;"> 割合(%) </th>
  </tr>
 </thead>
<tbody>
  <tr>
   <td style="text-align:left;"> 百貨店 </td>
   <td style="text-align:right;"> 4959 </td>
   <td style="text-align:right;"> 15.1 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> スーパー </td>
   <td style="text-align:right;"> 4738 </td>
   <td style="text-align:right;"> 14.4 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> 一般小売店 </td>
   <td style="text-align:right;"> 3851 </td>
   <td style="text-align:right;"> 11.7 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> コンビニ </td>
   <td style="text-align:right;"> 3772 </td>
   <td style="text-align:right;"> 11.5 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> 乗用車販売店 </td>
   <td style="text-align:right;"> 2967 </td>
   <td style="text-align:right;"> 9.0 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> 通信会社 </td>
   <td style="text-align:right;"> 2866 </td>
   <td style="text-align:right;"> 8.7 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> 商店街 </td>
   <td style="text-align:right;"> 2734 </td>
   <td style="text-align:right;"> 8.3 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> 人材派遣会社 </td>
   <td style="text-align:right;"> 2700 </td>
   <td style="text-align:right;"> 8.2 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> 衣料品専門店 </td>
   <td style="text-align:right;"> 2128 </td>
   <td style="text-align:right;"> 6.5 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> 職業安定所 </td>
   <td style="text-align:right;"> 2088 </td>
   <td style="text-align:right;"> 6.4 </td>
  </tr>
</tbody>
</table>

回答数上位には、百貨店やスーパーなど小売店が目立ちます。また、車のディーラーの方や人材派遣会社など生産・雇用に関連する業種の回答者も多いようです。

次に、経営者や職員など職種の分布を確認します。こちらも上位10位までを表示します。


```r
sample %>% 
  dplyr::mutate(職種 = stringr::str_extract(sample$`業種・職種`, "（.+）") %>% 
  stringr::str_remove("（") %>%
  stringr::str_remove("）")) %>% 
  dplyr::group_by(職種) %>% 
  dplyr::summarise(サンプルサイズ=dplyr::n()) %>% 
  dplyr::arrange(desc(サンプルサイズ)) %>% 
  dplyr::top_n(10, サンプルサイズ) %>% 
  dplyr::mutate(`割合(%)`=round(サンプルサイズ/sum(サンプルサイズ)*100, digits=1)) %>% 
  knitr::kable() %>% 
  kableExtra::kable_styling(bootstrap_options = c("striped"))
```

<table class="table table-striped" style="margin-left: auto; margin-right: auto;">
 <thead>
  <tr>
   <th style="text-align:left;"> 職種 </th>
   <th style="text-align:right;"> サンプルサイズ </th>
   <th style="text-align:right;"> 割合(%) </th>
  </tr>
 </thead>
<tbody>
  <tr>
   <td style="text-align:left;"> 経営者 </td>
   <td style="text-align:right;"> 20612 </td>
   <td style="text-align:right;"> 40.0 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> 営業担当 </td>
   <td style="text-align:right;"> 7057 </td>
   <td style="text-align:right;"> 13.7 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> 従業員 </td>
   <td style="text-align:right;"> 4371 </td>
   <td style="text-align:right;"> 8.5 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> 店長 </td>
   <td style="text-align:right;"> 4343 </td>
   <td style="text-align:right;"> 8.4 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> NA </td>
   <td style="text-align:right;"> 3145 </td>
   <td style="text-align:right;"> 6.1 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> 職員 </td>
   <td style="text-align:right;"> 3118 </td>
   <td style="text-align:right;"> 6.1 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> 総務担当 </td>
   <td style="text-align:right;"> 2930 </td>
   <td style="text-align:right;"> 5.7 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> 代表者 </td>
   <td style="text-align:right;"> 2615 </td>
   <td style="text-align:right;"> 5.1 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> 社員 </td>
   <td style="text-align:right;"> 1796 </td>
   <td style="text-align:right;"> 3.5 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> 役員 </td>
   <td style="text-align:right;"> 1518 </td>
   <td style="text-align:right;"> 2.9 </td>
  </tr>
</tbody>
</table>

職種別では経営者がダントツで多い結果となりました。代表者など表記揺れもありますので、実態はもう少し多いと思います。想像では、現場の職員の方の回答が多いと思っていましたが予想とは異なる結果となりました。

### `(景気)判断の理由`の分布

次に`(景気)判断の理由`の分布を見ます。


```r
results <- sample %>% 
            dplyr::group_by(判断の理由) %>% 
            dplyr::summarise(サンプルサイズ=dplyr::n()) %>% 
            dplyr::arrange(desc(サンプルサイズ)) %>% 
            dplyr::mutate(`割合(%)`=round(サンプルサイズ/sum(サンプルサイズ)*100, digits=1))
            
results %>% 
  knitr::kable() %>% 
  kableExtra::kable_styling(bootstrap_options = c("striped"))
```

<table class="table table-striped" style="margin-left: auto; margin-right: auto;">
 <thead>
  <tr>
   <th style="text-align:left;"> 判断の理由 </th>
   <th style="text-align:right;"> サンプルサイズ </th>
   <th style="text-align:right;"> 割合(%) </th>
  </tr>
 </thead>
<tbody>
  <tr>
   <td style="text-align:left;"> 来客数の動き </td>
   <td style="text-align:right;"> 17432 </td>
   <td style="text-align:right;"> 22.7 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> 販売量の動き </td>
   <td style="text-align:right;"> 16153 </td>
   <td style="text-align:right;"> 21.0 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> お客様の様子 </td>
   <td style="text-align:right;"> 11511 </td>
   <td style="text-align:right;"> 15.0 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> 受注量や販売量の動き </td>
   <td style="text-align:right;"> 9033 </td>
   <td style="text-align:right;"> 11.8 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> 取引先の様子 </td>
   <td style="text-align:right;"> 5034 </td>
   <td style="text-align:right;"> 6.6 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> 求人数の動き </td>
   <td style="text-align:right;"> 4155 </td>
   <td style="text-align:right;"> 5.4 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> それ以外 </td>
   <td style="text-align:right;"> 4007 </td>
   <td style="text-align:right;"> 5.2 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> 単価の動き </td>
   <td style="text-align:right;"> 3654 </td>
   <td style="text-align:right;"> 4.8 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> 競争相手の様子 </td>
   <td style="text-align:right;"> 1603 </td>
   <td style="text-align:right;"> 2.1 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> 周辺企業の様子 </td>
   <td style="text-align:right;"> 1161 </td>
   <td style="text-align:right;"> 1.5 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> 受注価格や販売価格の動き </td>
   <td style="text-align:right;"> 1099 </td>
   <td style="text-align:right;"> 1.4 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> 求職者数の動き </td>
   <td style="text-align:right;"> 930 </td>
   <td style="text-align:right;"> 1.2 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> 採用者数の動き </td>
   <td style="text-align:right;"> 666 </td>
   <td style="text-align:right;"> 0.9 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> 雇用形態の様子 </td>
   <td style="text-align:right;"> 361 </td>
   <td style="text-align:right;"> 0.5 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> 販売量の動き </td>
   <td style="text-align:right;"> 1 </td>
   <td style="text-align:right;"> 0.0 </td>
  </tr>
</tbody>
</table>

「来客数の動き」と「販売量の動き」が多く、「お客様の様子」や「受注量や販売量の動き」まで含めると7割を占めます。回答業種に小売店が多いことから、このような項目が上位にきているのだと推察されます。

### 景気判断の理由に関するテキストマイニング

景気の現状判断に対する理由の追加説明及び具体的状況の説明を解析し、どのような単語が頻繁に使用されているかをWordCloudを用いて確認します。

まず、文書のトークン化を行います。日本語のような言語では英語などと異なり単語ごとの間にスペースがないため、別途区切りを入れてやる必要があります。区切られた各語は形態素と呼ばれ、言葉が意味を持つまとまりの単語の最小単位を指します。また、文章を形態素へ分割することを形態素解析と言います(英語のような場合単にTokenizationと言ったりします)。  
形態素解析を行うツールは以下のようなものが存在します。

-   MeCab
-   JUMAN
-   JANOME
-   Ginza
-   Sudachi

おそらく最も使用されているものはMecabではないかと思いますが、標準装備されている辞書(ipadic)の更新がストップしており、最近の新語に対応できないという問題があります。この点については新語に強いNEologd辞書を加えることで、対処可能であることを別記事で紹介していますが、今回はワークスアプリケーションズが提供しているSudachi[@TAKAOKA18.8884]を使用することにしたいと思います。公式GithubからSudachiの特長を引用します。

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


```python
from sudachipy import tokenizer
from sudachipy import dictionary

tokenizer_obj = dictionary.Dictionary().create()

mode = tokenizer.Tokenizer.SplitMode.A
[m.normalized_form() for m in tokenizer_obj.tokenize("選挙管理委員会", mode)]
```

```
## ['選挙', '管理', '委員', '会']
```

```python
mode = tokenizer.Tokenizer.SplitMode.B
[m.normalized_form() for m in tokenizer_obj.tokenize("選挙管理委員会", mode)]
```

```
## ['選挙', '管理', '委員会']
```

```python
mode = tokenizer.Tokenizer.SplitMode.C
[m.normalized_form() for m in tokenizer_obj.tokenize("選挙管理委員会", mode)]
```

```
## ['選挙管理委員会']
```

また、辞書についてもUniDicとNEologdをベースとして更新が続けられており、新語にも対応できます。


```python
mode = tokenizer.Tokenizer.SplitMode.C
[m.normalized_form() for m in tokenizer_obj.tokenize("新型コロナウイルス", mode)]
```

```
## ['新型コロナウイルス']
```

個人的に素晴らしいと思うポイントは表記正規化や文字正規化ができると言うことです。以下のように旧字等で同じ意味だが表記が異なる単語や英語/日本語、書き間違え等を正規化する機能があります。


```python
tokenizer_obj.tokenize("附属", mode)[0].normalized_form()
```

```
## '付属'
```

```python
tokenizer_obj.tokenize("SUMMER", mode)[0].normalized_form()
```

```
## 'サマー'
```

```python
tokenizer_obj.tokenize("シュミレーション", mode)[0].normalized_form()
```

```
## 'シミュレーション'
```

このような高性能な形態素解析ツールが無償でしかも商用利用も可というところに驚きを隠せません。次回以降で説明しますが、このSudachiで形態素解析を行ったWord2vecモデルであるChiveも提供されています。

説明が長くなりましたがSudachiでTokenizationを行いましょう。Sudachiは`Python`で使用することができます。説明が前後していますが、上記コードで行っているように`tokenizer`オブジェクトを作成し、`tokenize()`メソッドで文章をTokenizeします。Tokenizeされた結果は`MorphemeList`オブジェクトに格納されます。`MorphemeList`オブジェクトの各要素に対して`normalized_form()`メソッドを実行することで正規化された形態素を取得することができます。ここまでをやってみます。



まず、サンプルデータを読み込みます。


```python
from sudachipy import tokenizer
from sudachipy import dictionary
from sklearn.preprocessing import LabelEncoder
import pandas as pd

sample = pd.read_csv(r"C:\Users\hogehoge\Watcher\RawData\watcher_2016.csv",encoding="shift-jis")
sample = sample[(sample.追加説明及び具体的状況の説明=='−')|(sample.追加説明及び具体的状況の説明=='＊')==False|(sample.景気の現状判断=='□')]
```

読み込んだ`sample`をtokenizerでToken化していきます。


```python
tokenizer_obj = dictionary.Dictionary().create()
mode = tokenizer.Tokenizer.SplitMode.C
tokenizer_sudachi = lambda t: [m.normalized_form() for m in tokenizer_obj.tokenize(t, mode)]
tokens = sample.追加説明及び具体的状況の説明.map(tokenizer_sudachi)
tokens.head()
```

```
## 0    [・, 店頭, の, 取り扱い, 額, が, 前年, 比, 約, 120, %, と, 好調...
## 1    [・, 当, 施設, の, 利用, 乗降, 客数, は, 1, 月, 26, 日, 時点, ...
## 2    [・, 年, 末, の, 消費, の, 反動, も, 有る, て, か, 、, 客, の, ...
## 3    [・, 外国人, 観光客, に, よる, 売り上げ, が, 前年, 比, 152, %, と...
## 4    [・, 積極的, だ, 景気, が, 上向き, に, 有る, と, まで, は, 言う, 辛...
## Name: 追加説明及び具体的状況の説明, dtype: object
```

Tokenizeすることができました。
WordCloudを作成するために`Python`の`wordcloud`を用います。これは引数にTokenをスペースで区切った文字列を与える必要があるため、その整形を行います。


```python
word_lists = []
for token in tokens:
  for word in token:
    word_lists.append(word)
word_chain = ' '.join(word_lists)
```

では、wordcloudを作成していきます。日本語表示では文字化けが発生するため、[こちら](https://moji.or.jp/ipafont/ipaex00401/)でフォント「IPAexゴシック」を予めダウンロードし、フォルダに保存したものを読み込んでいます。




```python
font_path = r'C:\Users\hogehoge\Watcher\ipaexg.ttf'
```

`wordcloud.WordCloud.genetate()`でWordCloudを作成します。


```python
from wordcloud import WordCloud
import matplotlib.pyplot as plt
wc = WordCloud(background_color="white", font_path=font_path, max_words=100, max_font_size=100, contour_width=1, contour_color='steelblue')
wc.generate(word_chain)
plt.figure(figsize=(12,10))
plt.imshow(wc, cmap=plt.cm.gray, interpolation="bilinear")
plt.axis("off")
plt.show()
```

![alt text](/post/post25/wordcloud.png)

助詞や「為る」、「有る」、「居る」、「成る」など特徴のない語句が頻出しており、意味のある可視化になっていません。これらを`word_chain`から除き、もう一度実行してみます。


```python
stopwords = ["見る","為る","有る","居る","成る","は","に","よる","た","が","て","だ","など","と","も","の","や","で","から","を","おる","より","等"]
for stopword in stopwords:
  word_chain = word_chain.replace(stopword, "")
wc.generate(word_chain)
plt.figure(figsize=(12,10))
plt.imshow(wc, cmap=plt.cm.gray, interpolation="bilinear")
plt.axis("off")
plt.show()
```
![alt text](/post/post25/wordcloud2.png)

先ほどよりは意味のある可視化になっています。「来客数」、「売り上げ」、「販売量」などやはり小売店関連のワードが頻出しているようです。これは回答者属性とも整合的です。

## 4. 終わりに

これから各回で以下の手法を用いた予測モデルの構築を行っていきます。次回は、辞書ベースに基づくセンチメントの抽出を行い、文書のポジネガ分類を行います。

1.  辞書ベース
2.  ナイーブベイズ分類器
3.  単語埋め込み(Word Embedding)を用いた方法
4.  Recurrent neural network(RNN)
5.  Transformer

実は、解析自体は全て完了しており、文書を書くだけのフェーズになっています。ちゃんと結果も出ていますので、乞うご期待です！
