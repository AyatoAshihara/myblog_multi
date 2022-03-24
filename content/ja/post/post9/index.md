---
title: "rvestでyahoo競馬にある過去のレース結果をクローリングしてみた"
author: admin
date: 2018-05-19T00:00:00Z
categories: ["競馬","Webスクレイピング"]
tags: ["前処理","R"]
slug: ["rvest"]
draft: false
featured: false
image:
  caption: ''
  focal_point: ""
  placement: 2
  preview_only: false
lastmod: 2018-06-10T00:00:00Z
projects: []
summary: 今、競馬×データサイエンスが熱いです。ウマナリティクスなるものがあり、これまでのレース結果からなんらかのモデルを作成し、順位予想や回収率を高める馬券購入方法を考えようとする人が一定数いるようです。今回は競馬をデータ解析するためのデータを取得します。rvestを用いて、ごりごりにクローリングを行いました。
output: 
  blogdown::html_page:
    number_sections: false
    toc: true
    df_print: "paged"
---



みなさん、おはこんばんにちは。

競馬のレース結果を的中させるモデルを作ろうということで研究をはじめましたが、まずはデータを自分で取ってくるところからやろうとおもいます。どこからデータを取ってくるのかという点が重要になるわけですが、データ先としてはdatascisotistさんがまとめられた非常にわかりやすい記事があります。どこからデータが取れるのかというと大きく分けて二つで、①JRA提供のJRA-VANや電子競馬新聞でおなじみの？JRJDといったデータベース、②netkeiba、yahoo競馬とといった競馬情報サイト、となっています。②の場合は自分でコードを書き、クローリングを行う必要があります。今回は②を選択し、yahoo競馬のデータをクローリングで落としてきたいと思います。Rでクローリングを行うパッケージとしては、rvest, httr, XMLがありますが、今回は1番簡単に使えるrvestを用います。yahoo競馬では以下のように各レース結果が表にまとめられています（5月の日本ダービーの結果）。

[yahoo競馬](https://keiba.yahoo.co.jp/race/result/1805021210/)

各馬のざっくりとした特徴やレース結果（通過順位等含む）、オッズが掲載されています。とりあえず、このぐらい情報があれば良いのではないかと思います（オッズの情報はもう少し欲しいのですが）。ただ、今後は少しずつ必要になった情報を拡充していこうとも思っています。1986年までのレース結果が格納されており、全データ数は50万件を超えるのではないかと思っています。ただ、単勝オッズが利用できるのは1994年からのようなので今回は1994年から直近までのデータを落としてきます。今回のゴールは、このデータをcsvファイル or SQLに格納することです。

## 1. Rvestとは

Rvestとは、webスクレイピングパッケージの一種でdplyrでおなじみのHadley Wickhamさんによって作成されたパッケージです。たった数行でwebスクレイピングができる優れものとなっており、操作が非常に簡単であるのが特徴です。今回は以下の本を参考にしました。

[Rによるスクレイピング入門](http://www.amazon.co.jp/exec/obidos/ASIN/486354216X/hatena-blog-22/)
![](https://images-na.ssl-images-amazon.com/images/I/51ZBnu8oSvL._SX350_BO1,204,203,200_.jpg)

 そもそも、htmlも大学1年生にやった程度でほとんど忘れていたのですが、この本はそこも非常にわかりやすく解説されており、非常に実践的な本だと思います。

## 2. レース結果をスクレイピングしてみる

実際にyahoo競馬からデータを落としてみたいと思います。コードは以下のようになっています。ご留意頂きたいのはこのコードをそのまま使用してスクレイピングを行うことはご遠慮いただきたいという事です。webスクレイピングは高速でサイトにアクセスするため、サイトへの負荷が大きくなる可能性があります。スクレイピングを行う際は、時間を空けるコーディングするなどその点に留意をして行ってください（最悪訴えられる可能性がありますが、こちらは一切の責任を取りません）。




```r
# rvestによる競馬データのwebスクレイピング

#install.packages("rvest")
#if (!require("pacman")) install.packages("pacman")
pacman::p_load(qdapRegex)
library(rvest)
library(stringr)
library(dplyr)
```

 使用するパッケージは`qdapRegex`、`rvest`、`stringr`、`dplyr`です。`qdapRegex`はカッコ内の文字を取り出すために使用しています。


```r
keiba.yahoo <- read_html(str_c("https://keiba.yahoo.co.jp/schedule/list/2016/?month=",k))
race_url <- keiba.yahoo %>%
html_nodes("a") %>%
html_attr("href") # 全urlを取得

# レース結果のをurlを取得
race_url <- race_url[str_detect(race_url, pattern="result")==1] # 「result」が含まれるurlを抽出
```

 まず、read_htmlでyahoo競馬のレース結果一覧のhtml構造を引っ張ってきます（リンクは2016年1月の全レース）。ここで、kと出ているのは月を表し、k=1であれば2016年1月のレース結果を引っ張ってくるということです。keiba.yahooを覗いてみると以下のようにそのページ全体のhtml構造が格納されているのが分かります。


```r
keiba.yahoo
```

```
## {html_document}
## <html xmlns="http://www.w3.org/1999/xhtml">
## [1] <head>\n<!---京---><meta http-equiv="Content-Type" content="text/html; cha ...
## [2] <body>\n<noscript>\n  <iframe src="//b.yjtag.jp/iframe?c=QXMP4c3" width=" ...
```

 race_urlにはyahoo.keibaのうちの2016年k月にあった全レース結果のリンクを格納しています。html_nodeとはhtml構造のうちどの要素を引っ張るかを指定し、それを引っ張る関数で、簡単に言えばほしいデータの住所を入力する関数であると認識しています（おそらく正しくない）。ここではa要素を引っ張ることにしています。注意すべきことは、html_nodeは欲しい情報をhtml形式で引っ張ることです。なので、テキストデータとしてリンクを保存するためにはhtml_attrを使用する必要があります。html_attrの引数として、リンク属性を表すhrefを渡しています。これでレース結果のurlが取れたと思いきや、実はこれでは他のリンクもとってしまっています。一番わかりやすいのが広告のリンクです。こういったリンクは除外する必要があります。レース結果のurlには"result"が含まれているので、この文字が入っている要素だけを抽出したのが一番最後のコードです。


```r
for (i in 1:length(race_url)){
  race1 <- read_html(str_c("https://keiba.yahoo.co.jp",race_url[i])) # レース結果のurlを取得

  # レース結果をスクレイピング
  race_result <- race1 %>% html_nodes(xpath = "//table[@id = 'raceScore']") %>%
  html_table()
  race_result <- do.call("data.frame",race_result) # リストをデータフレームに変更
  colnames(race_result) <- c("order","frame_number","horse_number","horse_name/age","time/margin","passing_rank/last_3F","jockey/weight","popularity/odds","trainer") #　列名変更
```
     
 さて、いよいよレース結果のスクレイピングを行います。さきほど取得したリンク先のhtml構造を一つ一つ取得し、その中で必要なテキスト情報を引っ張るという作業をRに実行させます（なのでループを使う）。race_1にはあるレース結果ページのhtml構造が格納されおり、race_resultにはその結果が入っています。html_nodesの引数に入っているxpathですが、これはXLMフォーマットのドキュメントから効率的に要素を抜き出す言語です。先ほど説明した住所のようなものと思っていただければ良いと思います。その横に書いてある`//table[@id = 'raceScore']`が住所です。これはwebブラウザから簡単に探すことができます。Firefoxの説明になりますが、ほかのブラウザでも同じような機能があると思います。スクレイプしたい画面で`Ctrl+Shift+C`を押すと下のような画面が表示されます。

このインスペクターの横のマークをクリックすると、カーソルで指した部分のhtml構造（住所）が表示されます。この場合だと、レース結果はtable属性の`id`がraceScoreの場所に格納されていることが分かります。なので、上のコードでは`xpath=`のところにそれを記述しているのです。そして、レース結果は表（table）形式でドキュメント化されているので、`html_table`でごっそりとスクレイプしました。基本的にリスト形式で返されるので、それをデータフレームに変換し、適当に列名をつけています。


```r
# 通過順位と上り3Fのタイム
  race_result <- dplyr::mutate(race_result,passing_rank=as.character(str_extract_all(race_result$`passing_rank/last_3F`,"(\\d{2}-\\d{2}-\\d{2}-\\d{2})|(\\d{2}-\\d{2}-\\d{2})|(\\d{2}-\\d{2})")))
  race_result <- dplyr::mutate(race_result,last_3F=as.character(str_extract_all(race_result$`passing_rank/last_3F`,"\\d{2}\\.\\d")))
  race_result <- race_result[-6]

# タイムと着差
  race_result <- dplyr::mutate(race_result,time=as.character(str_extract_all(race_result$`time/margin`,"\\d\\.\\d{2}\\.\\d|\\d{2}\\.\\d")))
  race_result <- dplyr::mutate(race_result,margin=as.character(str_extract_all(race_result$`time/margin`,"./.馬身|.馬身|.[:space:]./.馬身|[ア-ン-]+")))
  race_result <- race_result[-5]

# 馬名、馬齢、馬体重
  race_result <- dplyr::mutate(race_result,horse_name=as.character(str_extract_all(race_result$`horse_name/age`,"[ァ-ヴー・]+")))
  race_result <- dplyr::mutate(race_result,horse_age=as.character(str_extract_all(race_result$`horse_name/age`,"牡\\d+|牝\\d+|せん\\d+")))
  race_result <- dplyr::mutate(race_result,horse_weight=as.character(str_extract_all(race_result$`horse_name/age`,"\\d{3}")))
  race_result <- dplyr::mutate(race_result,horse_weight_change=as.character(str_extract_all(race_result$`horse_name/age`,"\\([\\+|\\-]\\d+\\)|\\([\\d+]\\)")))
  race_result$horse_weight_change <- sapply(rm_round(race_result$horse_weight_change, extract=TRUE), paste, collapse="")
  race_result <- race_result[-4]

# ジョッキー
  race_result <- dplyr::mutate(race_result,jockey=as.character(str_extract_all(race_result$`jockey/weight`,"[ぁ-ん一-龠]+\\s[ぁ-ん一-龠]+|[:upper:].[ァ-ヶー]+")))
  race_result <- race_result[-4]

# オッズと人気
  race_result <- dplyr::mutate(race_result,odds=as.character(str_extract_all(race_result$`popularity/odds`,"\\(.+\\)")))
  race_result <- dplyr::mutate(race_result,popularity=as.character(str_extract_all(race_result$`popularity/odds`,"\\d+[^(\\d+.\\d)]")))
  race_result$odds <- sapply(rm_round(race_result$odds, extract=TRUE), paste, collapse="")
  race_result <- race_result[-4]
```

ここまででデータは取得できたわけなのですが、そのデータは綺麗なものにはなっていません。 上のコードでは、その整形作業を行っています。現在、取得したデータは以下のようになっています。


```r
head(race_result)
```

<div data-pagedtable="false">
  <script data-pagedtable-source type="application/json">
{"columns":[{"label":[""],"name":["_rn_"],"type":[""],"align":["left"]},{"label":["order"],"name":[1],"type":["int"],"align":["right"]},{"label":["frame_number"],"name":[2],"type":["int"],"align":["right"]},{"label":["horse_number"],"name":[3],"type":["int"],"align":["right"]},{"label":["trainer"],"name":[4],"type":["chr"],"align":["left"]},{"label":["passing_rank"],"name":[5],"type":["chr"],"align":["left"]},{"label":["last_3F"],"name":[6],"type":["chr"],"align":["left"]},{"label":["time"],"name":[7],"type":["chr"],"align":["left"]},{"label":["margin"],"name":[8],"type":["chr"],"align":["left"]},{"label":["horse_name"],"name":[9],"type":["chr"],"align":["left"]},{"label":["horse_age"],"name":[10],"type":["chr"],"align":["left"]},{"label":["horse_weight"],"name":[11],"type":["chr"],"align":["left"]},{"label":["horse_weight_change"],"name":[12],"type":["chr"],"align":["left"]},{"label":["jockey"],"name":[13],"type":["chr"],"align":["left"]},{"label":["odds"],"name":[14],"type":["chr"],"align":["left"]},{"label":["popularity"],"name":[15],"type":["chr"],"align":["left"]},{"label":["race_date"],"name":[16],"type":["chr"],"align":["left"]},{"label":["race_name"],"name":[17],"type":["chr"],"align":["left"]}],"data":[{"1":"1","2":"2","3":"2","4":"河野 通文","5":"06-07-06-06","6":"35.1","7":"3.19.7","8":"character(0)","9":"センゴクシルバー","10":"牡6","11":"478","12":"+2","13":"田中 勝春","14":"2.3","15":"1","16":"1994年1月31日","17":"第44回ダイヤモンドステークス（GIII）","_rn_":"1"},{"1":"2","2":"6","3":"9","4":"武 邦彦","5":"06-05-04-04","6":"35.7","7":"3.19.9","8":"1 1/4馬身","9":"ジャムシード","10":"牡6","11":"480","12":"0","13":"柴田 政人","14":"14","15":"7","16":"1994年1月31日","17":"第44回ダイヤモンドステークス（GIII）","_rn_":"2"},{"1":"3","2":"7","3":"10","4":"白井 寿昭","5":"08-07-06-06","6":"35.7","7":"3.20.1","8":"1 1/2馬身","9":"ホクセツギンガ","10":"牡6","11":"500","12":"+4","13":"小屋敷 昭","14":"7.5","15":"3","16":"1994年1月31日","17":"第44回ダイヤモンドステークス（GIII）","_rn_":"3"},{"1":"4","2":"7","3":"11","4":"矢野 進","5":"03-03-03-02","6":"36.3","7":"3.20.4","8":"1 3/4馬身","9":"サマーワイン","10":"牝5","11":"422","12":"-4","13":"木幡 初広","14":"32.6","15":"9","16":"1994年1月31日","17":"第44回ダイヤモンドステークス（GIII）","_rn_":"4"},{"1":"5","2":"1","3":"1","4":"秋山 史郎","5":"12-12-12-12","6":"35.6","7":"3.20.5","8":"1/2馬身","9":"ダイワジェームス","10":"牡6","11":"472","12":"+6","13":"大塚 栄三郎","14":"5.9","15":"2","16":"1994年1月31日","17":"第44回ダイヤモンドステークス（GIII）","_rn_":"5"},{"1":"6","2":"5","3":"7","4":"須貝 彦三","5":"11-10-06-06","6":"36.1","7":"3.20.5","8":"ハナ","9":"シゲノランボー","10":"牡7","11":"438","12":"-6","13":"須貝 尚介","14":"8.7","15":"4","16":"1994年1月31日","17":"第44回ダイヤモンドステークス（GIII）","_rn_":"6"}],"options":{"columns":{"min":{},"max":[10]},"rows":{"min":[10],"max":[10]},"pages":{}}}
  </script>
</div>

 ご覧のように、`\n`が入っていたり、通過順位と上り3ハロンのタイムが一つのセルに入っていたりとこのままでは分析ができません。不要なものを取り除いたり、データを二つに分割する作業が必要になります。今回の記事ではこの部分について詳しくは説明しません。この部分は正規表現を駆使する必要がありますが、私自身全く詳しくないからです。今回も手探りでやりました。


```r
# レース情報
  race_date <- race1 %>% html_nodes(xpath = "//div[@id = 'raceTitName']/p[@id = 'raceTitDay']") %>%
    html_text()
  race_name <- race1 %>% html_nodes(xpath = "//div[@id = 'raceTitName']/h1[@class = 'fntB']") %>%
    html_text()

  race_result <- dplyr::mutate(race_result,race_date=as.character(str_extract_all(race_date,"\\d+年\\d+月\\d+日")))
  race_result <- dplyr::mutate(race_result,race_name=as.character(str_replace_all(race_name,"\\s","")))

# ファイル格納
  if (k ==1 && i == 1){
    dataset <- race_result
  } else {
    dataset <- rbind(dataset,race_result)
  }# if文の終わり
} # iループの終わり

    write.csv(race_result,"race_result.csv")
```

 最後に、レース日時とレース名を抜き出し、データを一時的に格納するコードとcsvファイルに書き出すコードを書いて終了です。完成データセットは以下のような状態になっています。


```r
head(dataset)
```

<div data-pagedtable="false">
  <script data-pagedtable-source type="application/json">
{"columns":[{"label":[""],"name":["_rn_"],"type":[""],"align":["left"]},{"label":["order"],"name":[1],"type":["chr"],"align":["left"]},{"label":["frame_number"],"name":[2],"type":["int"],"align":["right"]},{"label":["horse_number"],"name":[3],"type":["int"],"align":["right"]},{"label":["trainer"],"name":[4],"type":["chr"],"align":["left"]},{"label":["passing_rank"],"name":[5],"type":["chr"],"align":["left"]},{"label":["last_3F"],"name":[6],"type":["chr"],"align":["left"]},{"label":["time"],"name":[7],"type":["chr"],"align":["left"]},{"label":["margin"],"name":[8],"type":["chr"],"align":["left"]},{"label":["horse_name"],"name":[9],"type":["chr"],"align":["left"]},{"label":["horse_age"],"name":[10],"type":["chr"],"align":["left"]},{"label":["horse_weight"],"name":[11],"type":["chr"],"align":["left"]},{"label":["horse_weight_change"],"name":[12],"type":["chr"],"align":["left"]},{"label":["jockey"],"name":[13],"type":["chr"],"align":["left"]},{"label":["odds"],"name":[14],"type":["chr"],"align":["left"]},{"label":["popularity"],"name":[15],"type":["chr"],"align":["left"]},{"label":["race_date"],"name":[16],"type":["chr"],"align":["left"]},{"label":["race_name"],"name":[17],"type":["chr"],"align":["left"]}],"data":[{"1":"1","2":"8","3":"11","4":"森安 弘昭","5":"01-01-01-01","6":"35.7","7":"2.00.7","8":"character(0)","9":"ヒダカハヤト","10":"牡8","11":"488","12":"-2","13":"大塚 栄三郎","14":"29","15":"10","16":"1994年1月5日","17":"第43回日刊スポーツ賞金杯（GIII）","_rn_":"1"},{"1":"2","2":"5","3":"6","4":"矢野 進","5":"06-06-04-03","6":"35.3","7":"2.00.8","8":"3/4馬身","9":"ステージチャンプ","10":"牡5","11":"462","12":"+14","13":"岡部 幸雄","14":"3.2","15":"1","16":"1994年1月5日","17":"第43回日刊スポーツ賞金杯（GIII）","_rn_":"2"},{"1":"3","2":"4","3":"4","4":"新関 力","5":"03-03-02-02","6":"35.8","7":"2.01.1","8":"1 3/4馬身","9":"マキノトウショウ","10":"牡5","11":"502","12":"+6","13":"的場 均","14":"6.9","15":"4","16":"1994年1月5日","17":"第43回日刊スポーツ賞金杯（GIII）","_rn_":"3"},{"1":"4","2":"8","3":"12","4":"大和田 稔","5":"02-02-03-03","6":"35.7","7":"2.01.1","8":"ハナ","9":"ペガサス","10":"牡5","11":"464","12":"+4","13":"安田 富男","14":"5.7","15":"2","16":"1994年1月5日","17":"第43回日刊スポーツ賞金杯（GIII）","_rn_":"4"},{"1":"5","2":"7","3":"9","4":"田中 和夫","5":"07-07-07-05","6":"35.8","7":"2.01.6","8":"3馬身","9":"シャマードシンボリ","10":"牡7","11":"520","12":"+4","13":"田中 剛","14":"29.6","15":"12","16":"1994年1月5日","17":"第43回日刊スポーツ賞金杯（GIII）","_rn_":"5"},{"1":"6","2":"3","3":"3","4":"中島 敏文","5":"09-10-10-09","6":"35.5","7":"2.01.7","8":"3/4馬身","9":"モンタミール","10":"牡7","11":"474","12":"+4","13":"蓑田 早人","14":"10.4","15":"6","16":"1994年1月5日","17":"第43回日刊スポーツ賞金杯（GIII）","_rn_":"6"}],"options":{"columns":{"min":{},"max":[10]},"rows":{"min":[10],"max":[10]},"pages":{}}}
  </script>
</div>

 以上です。次回はこのデータセットを使用して、分析を行っていきます。次回までには1994年からのデータを全てスクレイピングしてきます。

【追記（2018/6/10）】

上述したスクリプトを用いて、スクレイピングを行ったところエラーが出ました。どうやらレース結果の中には強風などで中止になったものも含まれているらしく、そこでエラーが出る様子（race_resultがcharacter(0)になってしまう）。なので、この部分を修正したスクリプトを以下で公開しておきます。こちらは私の PC環境では正常に作動しています。


```r
# rvestによる競馬データのwebスクレイピング

#install.packages("rvest")
#if (!require("pacman")) install.packages("pacman")
  install.packages("beepr")
  pacman::p_load(qdapRegex)
  library(rvest)
  library(stringr)
  library(dplyr)
  library(beepr)

# pathの設定
  setwd("C:/Users/assiy/Dropbox/競馬統計解析")

  for(year in 1994:2018){

  # yahoo競馬のレース結果一覧ページの取得
  for (k in 1:12){

    keiba.yahoo <- read_html(str_c("https://keiba.yahoo.co.jp/schedule/list/", year,"/?month=",k))
    race_url <- keiba.yahoo %>%
    html_nodes("a") %>%
    html_attr("href") # 全urlを取得

    # レース結果のをurlを取得
    race_url <- race_url[str_detect(race_url, pattern="result")==1] # 「result」が含まれるurlを抽出

    for (i in 1:length(race_url)){

    Sys.sleep(10)
    print(str_c("現在、", year, "年", k, "月", i,"番目のレースの保存中です"))

    race1 <- read_html(str_c("https://keiba.yahoo.co.jp",race_url[i])) # レース結果のurlを取得

    # レースが中止でなければ処理を実行
    if (identical(race1 %>%
    html_nodes(xpath = "//div[@class = 'resultAtt mgnBL fntSS']") %>%
    html_text(),character(0)) == TRUE){

    # レース結果をスクレイピング
    race_result <- race1 %>% html_nodes(xpath = "//table[@id = 'raceScore']") %>%
    html_table()
    race_result <- do.call("data.frame",race_result) # リストをデータフレームに変更
    colnames(race_result) <- c("order","frame_number","horse_number","horse_name/age","time/margin","passing_rank/last_3F","jockey/weight","popularity/odds","trainer") #　列名変更

    # 通過順位と上り3Fのタイム
    race_result <- dplyr::mutate(race_result,passing_rank=as.character(str_extract_all(race_result$`passing_rank/last_3F`,"(\\d{2}-\\d{2}-\\d{2}-\\d{2})|(\\d{2}-\\d{2}-\\d{2})|(\\d{2}-\\d{2})")))
    race_result <- dplyr::mutate(race_result,last_3F=as.character(str_extract_all(race_result$`passing_rank/last_3F`,"\\d{2}\\.\\d")))
    race_result <- race_result[-6]

    # タイムと着差
    race_result <- dplyr::mutate(race_result,time=as.character(str_extract_all(race_result$`time/margin`,"\\d\\.\\d{2}\\.\\d|\\d{2}\\.\\d")))
    race_result <- dplyr::mutate(race_result,margin=as.character(str_extract_all(race_result$`time/margin`,"./.馬身|.馬身|.[:space:]./.馬身|[ア-ン-]+")))
    race_result <- race_result[-5]

    # 馬名、馬齢、馬体重
    race_result <- dplyr::mutate(race_result,horse_name=as.character(str_extract_all(race_result$`horse_name/age`,"[ァ-ヴー・]+")))
    race_result <- dplyr::mutate(race_result,horse_age=as.character(str_extract_all(race_result$`horse_name/age`,"牡\\d+|牝\\d+|せん\\d+")))
    race_result <- dplyr::mutate(race_result,horse_weight=as.character(str_extract_all(race_result$`horse_name/age`,"\\d{3}")))
    race_result <- dplyr::mutate(race_result,horse_weight_change=as.character(str_extract_all(race_result$`horse_name/age`,"\\([\\+|\\-]\\d+\\)|\\([\\d+]\\)")))
    race_result$horse_weight_change <- sapply(rm_round(race_result$horse_weight_change, extract=TRUE), paste, collapse="")
    race_result <- race_result[-4]

    # ジョッキー
    race_result <- dplyr::mutate(race_result,jockey=as.character(str_extract_all(race_result$`jockey/weight`,"[ぁ-ん一-龠]+\\s[ぁ-ん一-龠]+|[:upper:].[ァ-ヶー]+")))
    race_result <- race_result[-4]

    # オッズと人気
    race_result <- dplyr::mutate(race_result,odds=as.character(str_extract_all(race_result$`popularity/odds`,"\\(.+\\)")))
    race_result <- dplyr::mutate(race_result,popularity=as.character(str_extract_all(race_result$`popularity/odds`,"\\d+[^(\\d+.\\d)]")))
    race_result$odds <- sapply(rm_round(race_result$odds, extract=TRUE), paste, collapse="")
    race_result <- race_result[-4]

    # レース情報
    race_date <- race1 %>% html_nodes(xpath = "//div[@id = 'raceTitName']/p[@id = 'raceTitDay']") %>%
    html_text()
    race_name <- race1 %>% html_nodes(xpath = "//div[@id = 'raceTitName']/h1[@class = 'fntB']") %>%
    html_text()

    race_result <- dplyr::mutate(race_result,race_date=as.character(str_extract_all(race_date,"\\d+年\\d+月\\d+日")))
    race_result <- dplyr::mutate(race_result,race_name=as.character(str_replace_all(race_name,"\\s","")))

    ## ファイル貯めるのかく
    if (k == 1 && i == 1 && year == 1994){
    dataset <- race_result
    } else {
    dataset <- rbind(dataset,race_result)
    } # if文2の終わり
    } # if文1の終わり
    } # iループの終わり
    } # kループの終わり
    beep()
    } # yearループの終わり

    write.csv(dataset,"race_result.csv", row.names = FALSE)
```


これを回すのに16時間かかりました（笑）データ数は想定していたよりは少なく、97939になりました。
