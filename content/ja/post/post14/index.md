---
title: "10年物長期金利をフィッティングしてみる"
author: admin
date: 2019-07-16T00:00:00Z
categories: ["マクロ経済学"]
tags: ["R","時系列解析","金融"]
draft: false
featured: false
slug: ["long_term"]
image:
  caption: ''
  focal_point: ""
  placement: 2
  preview_only: false
lastmod: ""
projects: []
summary: 単なる思い付きです。
output: 
  blogdown::html_page:
    number_sections: false
    toc: true
---



おはこんばんにちは。とある理由で10年物長期金利のフィッティングを行いたいと思いました。というわけで、USデータを用いて解析していきます。まず、データを収集しましょう。`quantmod`パッケージを用いて、FREDからデータを落とします。`getsymbols(キー,from=開始日,src="FRED", auto.assign=TRUE)`で簡単にできちゃいます。ちなみにキーはFREDのHPで確認できます。

## 1. データ収集


```r
library(quantmod)

# data name collected
symbols.name <- c("10-Year Treasury Constant Maturity Rate","Effective Federal Funds Rate","
Consumer Price Index for All Urban Consumers: All Items","Civilian Unemployment Rate","3-Month Treasury Bill: Secondary Market Rate","Industrial Production Index","
10-Year Breakeven Inflation Rate","Trade Weighted U.S. Dollar Index: Broad, Goods","
Smoothed U.S. Recession Probabilities","Moody's Seasoned Baa Corporate Bond Yield","5-Year, 5-Year Forward Inflation Expectation Rate","Personal Consumption Expenditures")

# Collect economic data
symbols <- c("GS10","FEDFUNDS","CPIAUCSL","UNRATE","TB3MS","INDPRO","T10YIEM","TWEXBMTH","RECPROUSM156N","BAA","T5YIFRM","PCE")
getSymbols(symbols, from = '1980-01-01', src = "FRED", auto.assign = TRUE)
```

```
##  [1] "GS10"          "FEDFUNDS"      "CPIAUCSL"      "UNRATE"       
##  [5] "TB3MS"         "INDPRO"        "T10YIEM"       "TWEXBMTH"     
##  [9] "RECPROUSM156N" "BAA"           "T5YIFRM"       "PCE"
```

```r
macro_indicator <- merge(GS10,FEDFUNDS,CPIAUCSL,UNRATE,TB3MS,INDPRO,T10YIEM,TWEXBMTH,RECPROUSM156N,BAA,T5YIFRM,PCE)
rm(GS10,FEDFUNDS,CPIAUCSL,UNRATE,TB3MS,INDPRO,T10YIEM,TWEXBMTH,RECPROUSM156N,BAA,T5YIFRM,PCE,USEPUINDXD)
```

## 2. 月次解析パート

データは
[こちら](htmlwidget/macro_indicator.html)
から参照できます。では、推計用のデータセットを作成していきます。被説明変数は`10-Year Treasury Constant Maturity Rate(GS10)`です。説明変数は以下の通りです。

|  説明変数名  |  キー  |  代理変数  |
| ---- | ---- | ---- |
|  Federal Funds Rate  |  FEDFUNDS  |  短期金利  |
|  Consumer Price Index  |  CPIAUCSL  |  物価  |
|  Unemployment Rate  |  UNRATE  |  雇用関連  |
|  3-Month Treasury Bill  |  TB3MS  |  短期金利  |
|  Industrial Production Index  |  INDPRO  |  景気  |
|  Breakeven Inflation Rate  |  T10YIEM  |  物価  |
|  Trade Weighted Dollar Index  |  TWEXBMTH  |  為替  |
|  Recession Probabilities  |  RECPROUSM156N  |  景気  |
|  Moody's Seasoned Baa Corporate Bond Yield  |  BAA  |  リスクプレミアム  |
|  Inflation Expectation Rate  |  T5YIFRM  |  物価  |
|  Personal Consumption Expenditures  |  PCE  |  景気  |
|  Economic Policy Uncertainty Index  |  USEPUINDXD  |  政治  |

かなり適当な変数選択ではあるんですが、マクロモデリング的に長期金利ってどうやってモデル化するかというとちゃんとやってない場合が多いです。DSGEでは効率市場仮説に従って10年先までの短期金利のパスをリンクしたものと長期金利が等しくなると定式化するのが院生時代のモデリングでした（マクロファイナンスの界隈ではちゃんとやってそう）。そういうわけで、短期金利を説明変数に加えています。そして、短期金利に影響を与えるであろう物価にかかる指標も3つ追加しました。加えて、景気との相関が強いことはよく知られているので景気に関するデータも追加しました。これらはそもそもマクロモデルでは短期金利は以下のようなテイラールールに従うとモデリングすることが一般的であることが背景にあります。

$$
r_t = \rho r_{t-1} + \alpha \pi_{t} + \beta y_{t}
$$
ここで、$r_t$は政策金利（短期金利）、$\pi_t$はインフレ率、$y_t$はoutputです。$\rho, \alpha, \beta$はdeep parameterと呼ばれるもので、それぞれ慣性、インフレ率への金利の感応度、outputに対する感応度を表しています。$\rho=0,\beta=0$の時、$\alpha>=1$でなければ合理的期待均衡解が得られないことは「テイラーの原理」として有名です。
その他、Corporate bondとの裁定関係も存在しそうな`Moody's Seasoned Baa Corporate Bond Yield`も説明変数に追加しています。また、欲を言えば`VIX`指数と財政に関する指標を追加したいところです。財政に関する指数はQuateryかAnnualyなので今回のようなmonthlyの推計には使用することができません。この部分は最もネックなところです。なにか考え付いたら再推計します。

では、推計に入ります。今回は説明変数が多いので`lasso`回帰を行い、有効な変数を絞り込みたいと思います。また、比較のために`OLS`もやります。説明変数は被説明変数の1期前の値を使用します。おそらく、1期前でもデータの公表時期によっては翌月の推計に間に合わない可能性もありますが、とりあえずこれでやってみます。


```r
# make dataset
traindata <- na.omit(merge(macro_indicator["2003-01-01::2015-12-31"][,1],stats::lag(macro_indicator["2003-01-01::2015-12-31"][,-1],1)))
testdata  <- na.omit(merge(macro_indicator["2016-01-01::"][,1],stats::lag(macro_indicator["2016-01-01::"][,-1],1)))

# fitting OLS
trial1 <- lm(GS10~.,data = traindata)
summary(trial1)
```

```
## 
## Call:
## lm(formula = GS10 ~ ., data = traindata)
## 
## Residuals:
##     Min      1Q  Median      3Q     Max 
## -0.7593 -0.2182  0.0041  0.2143  0.7051 
## 
## Coefficients:
##                 Estimate Std. Error t value Pr(>|t|)    
## (Intercept)   15.0576773  4.3419245   3.468 0.000693 ***
## FEDFUNDS      -0.2075752  0.1413832  -1.468 0.144253    
## CPIAUCSL      -0.0750111  0.0204871  -3.661 0.000352 ***
## UNRATE        -0.2183796  0.0784608  -2.783 0.006109 ** 
## TB3MS          0.3031085  0.1393904   2.175 0.031310 *  
## INDPRO        -0.0705997  0.0263855  -2.676 0.008328 ** 
## T10YIEM        1.1476564  0.1758964   6.525 1.10e-09 ***
## TWEXBMTH      -0.0313911  0.0117338  -2.675 0.008338 ** 
## RECPROUSM156N -0.0103854  0.0021233  -4.891 2.66e-06 ***
## BAA            0.7802368  0.0858538   9.088 7.60e-16 ***
## T5YIFRM       -0.4529529  0.1881510  -2.407 0.017342 *  
## PCE            0.0009815  0.0002477   3.963 0.000116 ***
## ---
## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
## 
## Residual standard error: 0.2953 on 143 degrees of freedom
## Multiple R-squared:  0.9218,	Adjusted R-squared:  0.9158 
## F-statistic: 153.2 on 11 and 143 DF,  p-value: < 2.2e-16
```

自由度修正済み決定係数高めですね。2015/12/31までのモデルを使って、アウトサンプルのデータ(2016/01/01~)を予測し、平均二乗誤差を計算します。


```r
est.OLS.Y <- predict(trial1,testdata[,-1])
Y <- as.matrix(testdata[,1])
mse.OLS <- sum((Y - est.OLS.Y)^2) / length(Y)
mse.OLS
```

```
## [1] 0.2422673
```

次に`lasso`回帰です。Cross Validationを行い、$\lambda$を決める`glmnet`パッケージの`cv.glmnet`関数を使用します。


```r
# fitting lasso regression
library(glmnet)
trial2 <- cv.glmnet(as.matrix(traindata[,-1]),as.matrix(traindata[,1]),family="gaussian",alpha=1)
plot(trial2)
```

<img src="{{< blogdown/postref >}}index_files/figure-html/unnamed-chunk-4-1.png" width="672" />

```r
trial2$lambda.min
```

```
## [1] 0.001463052
```

```r
coef(trial2,s=trial2$lambda.min)
```

```
## 12 x 1 sparse Matrix of class "dgCMatrix"
##                          s1
## (Intercept)    8.1170282595
## FEDFUNDS       .           
## CPIAUCSL      -0.0370371311
## UNRATE        -0.1675017594
## TB3MS          0.1244417351
## INDPRO        -0.0554153857
## T10YIEM        1.1916137480
## TWEXBMTH      -0.0124760531
## RECPROUSM156N -0.0094119322
## BAA            0.7423502867
## T5YIFRM       -0.4664569086
## PCE            0.0004936828
```

`Unemployment Rate`、`3-Month Treasury Bill`、`Breakeven Inflation Rate、Moody's Seasoned Baa Corporate Bond Yield`、`Inflation Expectation Rate`の回帰係数が大きくなるという結果ですね。失業率以外は想定内の結果です。ただ、今回の結果を見る限り景気との相関は低そうです（逆向きにしか効かない？）。MSEを計算します。


```r
est.lasso.Y <- predict(trial2, newx = as.matrix(testdata[,-1]), s = trial2$lambda.min, type = 'response')
mse.lasso <- sum((Y - est.lasso.Y)^2) / length(Y)
mse.lasso
```

```
## [1] 0.1590115
```

`lasso`回帰のほうが良い結果になりました。`lasso`回帰で計算した予測値と実績値を時系列プロットしてみます。


```r
library(tidyverse)

ggplot(gather(data.frame(actual=Y[,1],lasso_prediction=est.lasso.Y[,1],OLS_prediction=est.OLS.Y,date=as.POSIXct(rownames(Y))),key=data,value=rate,-date),aes(x=date,y=rate, colour=data)) +
  geom_line() +
  scale_x_datetime(breaks = "6 month",date_labels = "%Y-%m") +
  scale_y_continuous(breaks=c(1,1.5,2,2.5,3,3.5),limits = c(1.25,3.5))
```

<img src="{{< blogdown/postref >}}index_files/figure-html/unnamed-chunk-6-1.png" width="672" />

方向感はいい感じです。一方で、2016年1月からや2018年12月以降の急激な金利低下は予測できていません。この部分については何か変数を考えるorローリング推計を実施する、のいずれかをやってみないと精度が上がらなそうです。

## 3. 日次解析パート

月次での解析に加えて日次での解析もやりたいとおもいます。日次データであればデータの公表は市場が閉まり次第の場合が多いので、いわゆる`jagged edge`の問題が起こりにくいと思います。まずは日次データの収集から始めます。


```r
# data name collected
symbols.name <- c("10-Year Treasury Constant Maturity Rate","Effective Federal Funds Rate","NASDAQ Composite Index","3-Month Treasury Bill: Secondary Market Rate","Economic Policy Uncertainty Index for United States","
10-Year Breakeven Inflation Rate","Trade Weighted U.S. Dollar Index: Broad, Goods","Moody's Seasoned Baa Corporate Bond Yield","5-Year, 5-Year Forward Inflation Expectation Rate")

# Collect economic data
symbols <- c("DGS10","DFF","NASDAQCOM","DTB3","USEPUINDXD","T10YIE","DTWEXB","DBAA","T5YIFR")
getSymbols(symbols, from = '1980-01-01', src = "FRED", auto.assign = TRUE)
```

```
## [1] "DGS10"      "DFF"        "NASDAQCOM"  "DTB3"       "USEPUINDXD"
## [6] "T10YIE"     "DTWEXB"     "DBAA"       "T5YIFR"
```

```r
NASDAQCOM.r <- ROC(na.omit(NASDAQCOM))
macro_indicator.d <- merge(DGS10,DFF,NASDAQCOM.r,DTB3,USEPUINDXD,T10YIE,DTWEXB,DBAA,T5YIFR)
rm(DGS10,DFF,NASDAQCOM,NASDAQCOM.r,DTB3,USEPUINDXD,T10YIE,DTWEXB,DBAA,T5YIFR)
```

次にデータセットを構築します。学習用と訓練用にデータを分けます。実際の予測プロセスを考え、2営業日前のデータを説明変数に用いています。


```r
# make dataset
traindata.d <- na.omit(merge(macro_indicator.d["1980-01-01::2010-12-31"][,1],stats::lag(macro_indicator.d["1980-01-01::2010-12-31"][,-1],2)))
testdata.d  <- na.omit(merge(macro_indicator.d["2010-01-01::"][,1],stats::lag(macro_indicator.d["2010-01-01::"][,-1],2)))

# fitting OLS
trial1.d <- lm(DGS10~.,data = traindata.d)
summary(trial1.d)
```

```
## 
## Call:
## lm(formula = DGS10 ~ ., data = traindata.d)
## 
## Residuals:
##      Min       1Q   Median       3Q      Max 
## -0.81961 -0.12380  0.00509  0.14514  0.72712 
## 
## Coefficients:
##               Estimate Std. Error t value Pr(>|t|)    
## (Intercept) -3.5168438  0.1664198 -21.132  < 2e-16 ***
## DFF          0.0770736  0.0217208   3.548 0.000403 ***
## NASDAQCOM   -0.4301865  0.4280568  -1.005 0.315121    
## DTB3         0.1137128  0.0238678   4.764 2.14e-06 ***
## USEPUINDXD  -0.0006591  0.0001073  -6.144 1.11e-09 ***
## T10YIE       0.6957403  0.0351666  19.784  < 2e-16 ***
## DTWEXB       0.0276208  0.0010896  25.350  < 2e-16 ***
## DBAA         0.2879946  0.0131335  21.928  < 2e-16 ***
## T5YIFR       0.3433321  0.0376058   9.130  < 2e-16 ***
## ---
## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
## 
## Residual standard error: 0.2167 on 1148 degrees of freedom
## Multiple R-squared:  0.8902,	Adjusted R-squared:  0.8894 
## F-statistic:  1163 on 8 and 1148 DF,  p-value: < 2.2e-16
```

依然決定係数は高めです。


```r
est.OLS.Y.d <- predict(trial1.d,testdata.d[,-1])
Y.d <- as.matrix(testdata.d[,1])
mse.OLS.d <- sum((Y.d - est.OLS.Y.d)^2) / length(Y.d)
mse.OLS.d
```

```
## [1] 0.8350614
```

次に`lasso`回帰です。`CV`で$\lambda$を決定。


```r
# fitting lasso regression
trial2.d <- cv.glmnet(as.matrix(traindata.d[,-1]),as.matrix(traindata.d[,1]),family="gaussian",alpha=1)
plot(trial2.d)
```

<img src="{{< blogdown/postref >}}index_files/figure-html/unnamed-chunk-10-1.png" width="672" />

```r
trial2.d$lambda.min
```

```
## [1] 0.001339007
```

```r
coef(trial2.d,s=trial2.d$lambda.min)
```

```
## 9 x 1 sparse Matrix of class "dgCMatrix"
##                        s1
## (Intercept) -3.4297225594
## DFF          0.0707532975
## NASDAQCOM   -0.3512778327
## DTB3         0.1204390843
## USEPUINDXD  -0.0006453775
## T10YIE       0.6894098221
## DTWEXB       0.0272773903
## DBAA         0.2831306290
## T5YIFR       0.3411269206
```

`libor`の係数値が0になりました。MSEは`OLS`の方が高い結果に。


```r
est.lasso.Y.d <- predict(trial2.d, newx = as.matrix(testdata.d[,-1]), s = trial2.d$lambda.min, type = 'response')
mse.lasso.d <- sum((Y.d - est.lasso.Y.d)^2) / length(Y.d)
mse.lasso.d
```

```
## [1] 0.8492769
```

予測値をプロットします。


```r
ggplot(gather(data.frame(actual=Y.d[,1],lasso_prediction=est.lasso.Y.d[,1],OLS_prediction=est.OLS.Y.d,date=as.POSIXct(rownames(Y.d))),key=data,value=rate,-date),aes(x=date,y=rate, colour=data)) +
  geom_line() +
  scale_x_datetime(breaks = "2 year",date_labels = "%Y-%m") +
  scale_y_continuous(breaks=c(1,1.5,2,2.5,3,3.5),limits = c(1.25,5))
```

<img src="{{< blogdown/postref >}}index_files/figure-html/unnamed-chunk-12-1.png" width="672" />

月次と同じく、`OLS`と`lasso`で予測値に差はほとんどありません。なかなかいい感じに変動を捉えることができていますが、2011年の`United States federal government credit-rating downgrades`による金利低下や2013年の景気回復に伴う金利上昇は捉えることができていません。日次の景気指標はPOSデータくらいしかないんですが、強いて言うなら最近使用した夜間光の衛星画像データなんかは使えるかもしれません。時間があればやってみます。とりあえず、いったんこれでこの記事は終わりたいと思います。ここまで読み進めていただき、ありがとうございました。
