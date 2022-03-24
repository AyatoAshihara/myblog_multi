---
title: "Scraping past race results on yahoo horse racing on rvest (for the second time)"
author: admin
date: 2019-07-13T00:00:00Z
categories: ["競馬"]
tags: ["R","Web_scraping","preprocessing","SQL"]
draft: false
featured: false
slug: ["SQL"]
image:
  caption: ''
  focal_point: ""
  placement: 2
  preview_only: false
lastmod: ""
projects: []
summary: I found some data missing from the last data collection, so I scraped it again.
output: 
  blogdown::html_page:
    number_sections: false
    toc: true
---



For the second time, I'd like to drop past race results in rvest again. If you haven't seen the past articles, I suggest you look at that one first.

The reason I decided to take back the data this time is because I wanted to add more items to the explanatory variables when analyzing horse racing. So this time I created the program as an addition to the previous R script. The 14 new data items I added are as follows

1. grass or dirt.
2. right-handed or left-handed.
3. race conditions (good or slight)
4. weather
5. the color of the horse's coat (chestnut, deer hair, etc.)
6. horse owner
7. producers
8. place of origin
9. date of birth
10. the father's horse
11. the mother's horse
12. winnings up to that race (available from 2003)
13. jockey's weight.
14. increase or decrease in the weight of the jockey.

Actually, I haven't finished collecting data yet, and the R program has been running for a long time (I've been running it for about 3 days). However, the program itself is running tightly and I'll try to introduce the script. Maybe I'll write the results in a postscript.

## 1. Script



The first step is to call the package.


```r
# Web scraping of horse racing data by rvest

#install.packages("rvest")
#if (!require("pacman")) install.packages("pacman")
#install.packages("beepr")
#install.packages("RSQLite")
pacman::p_load(qdapRegex)
library(rvest)
library(stringr)
library(dplyr)
library(beepr)
library(RSQLite)
```

I'm pretty much warnning out, so I'm banning it and connecting to SQLite


```r
# warning prohibition
options(warn=-1)

# Connecting to SQLite
con = dbConnect(SQLite(), "horse_data.db", synchronous="off")
```

Since the odds are only available since 1994, the data is taken from 1994 up to the most recent date. yahoo horse racing has races organized by month, so the data is taken using that as a variable. Basically, you go to [List of race results for the relevant year and month](https://keiba.yahoo.co.jp/schedule/list/2018/?month=7) and then go to [Timetable for each day of the race](https://keiba.yahoo.co.jp/race/list/18020106/) for each day on that page. Since there are roughly a dozen or so races at each individual track, get the link and go to the [race results page](https://keiba.yahoo.co.jp/race/result/1802010601/) for each race. Then you will get the race results. The first step is to get a link to the timetable for each individual racecourse for each day.


```r
for(year in 1994:2019){
  start.time <- Sys.time() # calculate time
  # Retrieve the race results page on Yahoo!
  for (k in 1:12){ # K is for the month.
    
    tryCatch(
      {
        keiba.yahoo <- read_html(str_c("https://keiba.yahoo.co.jp/schedule/list/", year,"/?month=",k)) # Access to the list of race results for a given year and month
        Sys.sleep(2)
        race_lists <- keiba.yahoo %>%
          html_nodes("a") %>% 
          html_attr("href") # Retrieve all URLs
        
        # Get the list of races for each day by track
        race_lists <- race_lists[str_detect(race_lists, pattern="race/list/\\d+/")==1] # Extracts URLs containing "results".
      }
      , error = function(e){signal <- 1}
    )
```

Here, we only extract the links we get that contain the word result in the url. In essence, it is a link to the race tables of each racecourse. From here, we use the links to the race tables of the tracks to access that page and get the links to the pages that contain the results of all 12 races.


```r
    for (j in 1:length(race_lists)){ # where j is the link to the race table for the year in question.
      
      tryCatch(
        {
          race_list <- read_html(str_c("https://keiba.yahoo.co.jp",race_lists[j]))
          race_url <- race_list %>% html_nodes("a") %>% html_attr("href") # 全urlを取得
          
          # Get the URL of the race results
          race_url <- race_url[str_detect(race_url, pattern="result")==1] # Extracts URLs containing "results".
        }
        , error = function(e){signal <- 1}
      )
```

Now that we have the links to the results of each race, it's time to get the race results and the formatting part of the code. It's quite a long and complicated code. The race results are stored in the following table attributes, so we'll simply pull them first.


```r
      for (i in 1:length(race_url)){ # where i is the race that was held at the racecourse in question
        
        print(str_c(year, "/", k, "/",j, " group ", i," order"))
        
        tryCatch(
          {
            race1 <-  read_html(str_c("https://keiba.yahoo.co.jp",race_url[i])) # Get the URL of the race results
            signal <- 0
            Sys.sleep(2)
          }
          , error = function(e){signal <- 1}
        )
        
        # If the race is aborted or there are no errors in the process so far, run the process
        if (identical(race1 %>%
                      html_nodes(xpath = "//div[@class = 'resultAtt mgnBL fntSS']") %>%
                      html_text(),character(0)) == TRUE && signal == 0){
          
          # Scraping the race results
          race_result <- race1 %>% html_nodes(xpath = "//table[@id = 'raceScore']") %>%
            html_table()
          race_result <- do.call("data.frame",race_result) # Change the list to a data frame.
          
          colnames(race_result) <- c("order","frame_number","horse_number","horse_name/age","time/margin","passing_rank/last_3F","jockey/weight","popularity/odds","trainer") #　column renaming
```
If you just get a table, it will not be useful for analysis because of the following \n or multiple information in one cell. So, we need to mold the data into a form.  


```r
          # Passing order and time for 3 furlongs uphill
          race_result <- dplyr::mutate(race_result,passing_rank=as.character(str_extract_all(race_result$`passing_rank/last_3F`,"(\\d{2}-\\d{2}-\\d{2}-\\d{2})|(\\d{2}-\\d{2}-\\d{2})|(\\d{2}-\\d{2})")))
          race_result <- dplyr::mutate(race_result,last_3F=as.character(str_extract_all(race_result$`passing_rank/last_3F`,"\\d{2}\\.\\d")))
          race_result <- race_result[-6]
          
          # Time and Difference
          race_result <- dplyr::mutate(race_result,time=as.character(str_extract_all(race_result$`time/margin`,"\\d\\.\\d{2}\\.\\d|\\d{2}\\.\\d")))
          race_result <- dplyr::mutate(race_result,margin=as.character(str_extract_all(race_result$`time/margin`,"./.馬身|.馬身|.[:space:]./.馬身|[ア-ン-]+")))
          race_result$margin[race_result$order==1] <- "トップ"
          race_result$margin[race_result$margin=="character(0)"] <- "大差"
          race_result$margin[race_result$order==0] <- NA
          race_result <- race_result[-5]
          
          # Horse's name, age and weight
          race_result <- dplyr::mutate(race_result,horse_name=as.character(str_extract_all(race_result$`horse_name/age`,"[ァ-ヴー・]+")))
          race_result <- dplyr::mutate(race_result,horse_age=as.character(str_extract_all(race_result$`horse_name/age`,"牡\\d+|牝\\d+|せん\\d+")))
          race_result$horse_sex <- str_extract(race_result$horse_age, pattern = "牡|牝|せん")
          race_result$horse_age <- str_extract(race_result$horse_age, pattern = "\\d")
          race_result <- dplyr::mutate(race_result,horse_weight=as.character(str_extract_all(race_result$`horse_name/age`,"\\d{3}")))
          race_result <- dplyr::mutate(race_result,horse_weight_change=as.character(str_extract_all(race_result$`horse_name/age`,"\\([\\+|\\-]\\d+\\)|\\([\\d+]\\)")))
          race_result$horse_weight_change <- sapply(rm_round(race_result$horse_weight_change, extract=TRUE), paste, collapse="")
          race_result <- dplyr::mutate(race_result,brinker=as.character(str_extract_all(race_result$`horse_name/age`,"B")))
          race_result$brinker[race_result$brinker!="B"] <- "N"
          race_result <- race_result[-4]
          
          # jockey
          race_result <- dplyr::mutate(race_result,jockey=as.character(str_extract_all(race_result$`jockey/weight`,"[ぁ-ん一-龠]+\\s[ぁ-ん一-龠]+|[:upper:].[ァ-ヶー]+")))
          race_result <- dplyr::mutate(race_result,jockey_weight=as.character(str_extract_all(race_result$`jockey/weight`,"\\d{2}")))
          race_result$jockey_weight_change <- 0
          race_result$jockey_weight_change[str_detect(race_result$`jockey/weight`,"☆")==1] <- 1
          race_result$jockey_weight_change[str_detect(race_result$`jockey/weight`,"△")==1] <- 2
          race_result$jockey_weight_change[str_detect(race_result$`jockey/weight`,"△")==1] <- 3
          race_result <- race_result[-4]
          
          # Odds and popularity
          race_result <- dplyr::mutate(race_result,odds=as.character(str_extract_all(race_result$`popularity/odds`,"\\(.+\\)")))
          race_result <- dplyr::mutate(race_result,popularity=as.character(str_extract_all(race_result$`popularity/odds`,"\\d+[^(\\d+.\\d)]")))
          race_result$odds <- sapply(rm_round(race_result$odds, extract=TRUE), paste, collapse="")
          race_result <- race_result[-4]
```

Next, we'll import information other than the table we just retrieved. Specifically, race names, weather conditions, track conditions, dates, racecourses, etc. These information are listed at the top of the race results page.


```r
          # Race Information
          race_date <- race1 %>% html_nodes(xpath = "//div[@id = 'raceTitName']/p[@id = 'raceTitDay']") %>%
            html_text()
          race_name <- race1 %>% html_nodes(xpath = "//div[@id = 'raceTitName']/h1[@class = 'fntB']") %>%
            html_text()
          race_distance <- race1 %>% html_nodes(xpath = "//p[@id = 'raceTitMeta']") %>%
            html_text()
        
          race_result <- dplyr::mutate(race_result,race_date=as.character(str_extract_all(race_date,"\\d+年\\d+月\\d+日")))
          race_result$race_date <- str_replace_all(race_result$race_date,"年","/")
          race_result$race_date <- str_replace_all(race_result$race_date,"月","/")
          race_result$race_date <- as.Date(race_result$race_date)
          race_course <- as.character(str_extract_all(race_date,pattern = "札幌|函館|福島|新潟|東京|中山|中京|京都|阪神|小倉"))
          race_result$race_course <- race_course
          race_result <- dplyr::mutate(race_result,race_name=as.character(str_replace_all(race_name,"\\s","")))
          race_result <- dplyr::mutate(race_result,race_distance=as.character(str_extract_all(race_distance,"\\d+m")))
          race_type=as.character(str_extract_all(race_distance,pattern = "芝|ダート"))
          race_result$type <- race_type
          race_turn <- as.character(str_extract_all(race_distance,pattern = "右|左"))
          race_result$race_turn <- race_turn
          
          if(length(race1 %>% html_nodes(xpath = "//img[@class = 'spBg ryou']")) == 1){
            race_result$race_condition <- "良"
          } else if (length(race1 %>% 
                            html_nodes(xpath = "//img[@class = 'spBg yayaomo']")) == 1){
            race_result$race_condition <- "稍重"
          } else if (length(race1 %>%
                            html_nodes(xpath = "//img[@class = 'spBg omo']")) == 1){
            race_result$race_condition <- "重"
          } else if (length(race1 %>% 
                            html_nodes(xpath = "//img[@class = 'spBg furyou']")) == 1){
            race_result$race_condition <- "不良"
          } else race_result$race_condition <- "NA"
          
          if (length(race1 %>% html_nodes(xpath = "//img[@class = 'spBg hare']")) == 1){
            race_result$race_weather <- "晴れ"
          } else if (length(race1 %>% html_nodes(xpath = "//img[@class = 'spBg ame']")) == 1){
            race_result$race_weather <- "曇り"
          } else if (length(race1 %>% html_nodes(xpath = "//img[@class = 'spBg kumori']")) == 1){
            race_result$race_weather <- "雨"
          } else race_result$race_weather <- "その他"
```

The next step is to get information about each horse. In fact, the horse's name in the table we got earlier is a link, and if you follow the link, you can get [information about each horse] (https://keiba.yahoo.co.jp/directory/horse/2015105508/) (such as coat color and date of birth).


```r
          horse_url <- race1 %>% html_nodes("a") %>% html_attr("href") 
          horse_url <- horse_url[str_detect(horse_url, pattern="directory/horse")==1] # Extract only links to horse information.
          
          for (l in 1:length(horse_url)){
            tryCatch(
              {
                horse1 <-  read_html(str_c("https://keiba.yahoo.co.jp",horse_url[l]))
                Sys.sleep(0.5)
                horse_name <- horse1 %>% html_nodes(xpath = "//div[@id = 'dirTitName']/h1[@class = 'fntB']") %>% 
                  html_text()
                horse <- horse1 %>% html_nodes(xpath = "//div[@id = 'dirTitName']/ul") %>% 
                  html_text()
                race_result$colour[race_result$horse_name==horse_name] <- as.character(str_extract_all(horse,"毛色：.+")) 
                race_result$owner[race_result$horse_name==horse_name] <- as.character(str_extract_all(horse,"馬主：.+"))
                race_result$farm[race_result$horse_name==horse_name] <- as.character(str_extract_all(horse,"生産者：.+"))
                race_result$locality[race_result$horse_name==horse_name] <- as.character(str_extract_all(horse,"産地：.+"))
                race_result$horse_birthday[race_result$horse_name==horse_name] <- as.character(str_extract_all(horse,"\\d+年\\d+月\\d+日"))
                race_result$father[race_result$horse_name==horse_name] <- horse1 %>% html_nodes(xpath = "//td[@class = 'bloodM'][@rowspan = '4']") %>% html_text()
                race_result$mother[race_result$horse_name==horse_name] <- horse1 %>% html_nodes(xpath = "//td[@class = 'bloodF'][@rowspan = '4']") %>% html_text()
              }
              , error = function(e){
                race_result$colour[race_result$horse_name==horse_name] <- NA 
                race_result$owner[race_result$horse_name==horse_name] <- NA
                race_result$farm[race_result$horse_name==horse_name] <- NA
                race_result$locality[race_result$horse_name==horse_name] <- NA
                race_result$horse_birthday[race_result$horse_name==horse_name] <- NA
                race_result$father[race_result$horse_name==horse_name] <- NA
                race_result$mother[race_result$horse_name==horse_name] <- NA
                }
            )
          }
          
          race_result$colour <- str_replace_all(race_result$colour,"毛色：","")
          race_result$owner <- str_replace_all(race_result$owner,"馬主：","")
          race_result$farm <- str_replace_all(race_result$farm,"生産者：","")
          race_result$locality <- str_replace_all(race_result$locality,"産地：","")
          #race_result$horse_birthday <- str_replace_all(race_result$horse_birthday,"年","/")
          #race_result$horse_birthday <- str_replace_all(race_result$horse_birthday,"月","/")
          #race_result$horse_birthday <- as.Date(race_result$horse_birthday)
          
          race_result <- dplyr::arrange(race_result,horse_number) # arrange in order of precedence
```

The next step is to go and drop the amount of money you have won up to that race. You can access this by following the link marked [Runoffs] (https://keiba.yahoo.co.jp/race/denma/1802010601/) on the race results page. This is where you will find the prize money and you will get it.


```r
          yosou_url <- race1 %>% html_nodes("a") %>% html_attr("href") 
          yosou_url <- yosou_url[str_detect(yosou_url, pattern="denma")==1]
          
          if (length(yosou_url)==1){
          yosou1 <-  read_html(str_c("https://keiba.yahoo.co.jp",yosou_url)) 
          Sys.sleep(2)
          yosou <- yosou1 %>% html_nodes(xpath = "//td[@class = 'txC']") %>% as.character()
          prize <- yosou[grepl("万",yosou)==TRUE] %>% str_extract_all("\\d+万")
          prize <- t(do.call("data.frame",prize)) %>% as.character()
          race_result$prize <- prize
          race_result$prize <- str_replace_all(race_result$prize,"万","") %>% as.numeric()
          } else race_result$prize <- NA
```

We create a data frame called dataset to store the results of each race and store the data.


```r
          ## file storage
          if (k == 1 && i == 1 && j == 1){
            dataset <- race_result
          } else {
            dataset <- rbind(dataset,race_result)
          }
        }else
        {
          print("We couldn't save it.") 
        }
      }
    }
  }
  beep(3)
  write.csv(dataset,"race_result2.csv", row.names = FALSE)
  
  if (year == 1994){
    dbWriteTable(con, "race_result", dataset)
  } else {
    dbWriteTable(con, "temp", dataset)
    dbSendQuery(con, "INSERT INTO race_result select * from temp")
    dbSendQuery(con, "DROP TABLE temp")
  }
}
end.time <- Sys.time()
print(str_c("処理時間は",end.time-start.time,"です。"))
beep(5)

options(warn = 1)

dbDisconnect(con)
```

That's all. The data taken is as follows


```r
head(race_result)
```

```
##   order frame_number horse_number   trainer passing_rank last_3F   time
## 1    10            1            1   田中 剛        09-09    39.0 1.14.3
## 2    16            1            2 天間 昭一        11-11    40.3 1.15.7
## 3    15            2            3 田中 清隆        14-14    39.4 1.15.1
## 4     9            2            4 中舘 英二        08-08    39.1 1.14.3
## 5    12            3            5 根本 康広        11-11    39.0 1.14.4
## 6     4            3            6 杉浦 宏昭        04-04    38.4 1.13.2
##      margin         horse_name horse_age horse_sex horse_weight
## 1    アタマ     サトノジョニー         3        牡          512
## 2 3 1/2馬身       ツギノイッテ         3        牡          464
## 3     3馬身           ギュウホ         3        牡          444
## 4 2 1/2馬身 セイウンメラビリア         3        牝          466
## 5      クビ サバイバルトリック         3        牝          450
## 6    アタマ       ステイホット         3        牝          474
##   horse_weight_change brinker      jockey jockey_weight jockey_weight_change
## 1                 +30       N   松岡 正海            56                    0
## 2                  +8       N 西田 雄一郎            56                    0
## 3                  +8       N   杉原 誠人            56                    0
## 4                 +10       N   村田 一誠            54                    0
## 5                  -2       N 野中 悠太郎            51                    0
## 6                  -2       N   大野 拓弥            54                    0
##    odds popularity  race_date race_course       race_name race_distance   type
## 1  40.3         9  2019-01-05        中山 サラ系3歳未勝利         1200m ダート
## 2 340.9        16  2019-01-05        中山 サラ系3歳未勝利         1200m ダート
## 3 283.1        14  2019-01-05        中山 サラ系3歳未勝利         1200m ダート
## 4 299.7        15  2019-01-05        中山 サラ系3歳未勝利         1200m ダート
## 5  26.7         8  2019-01-05        中山 サラ系3歳未勝利         1200m ダート
## 6   2.4         1  2019-01-05        中山 サラ系3歳未勝利         1200m ダート
##   race_turn race_condition race_weather colour                           owner
## 1        右             良         晴れ   栗毛 株式会社 サトミホースカンパニー
## 2        右             良         晴れ 黒鹿毛                     西村 新一郎
## 3        右             良         晴れ   鹿毛           有限会社 ミルファーム
## 4        右             良         晴れ 青鹿毛                       西山 茂行
## 5        右             良         晴れ 黒鹿毛                       福田 光博
## 6        右             良         晴れ   栗毛                       小林 善一
##           farm   locality horse_birthday                 father
## 1   千代田牧場 新ひだか町  2016年1月29日         オルフェーヴル
## 2    織笠 時男     青森県  2016年4月17日 スクワートルスクワート
## 3    神垣 道弘 新ひだか町  2016年4月19日     ジャングルポケット
## 4  石郷岡 雅樹     新冠町  2016年4月21日     キンシャサノキセキ
## 5     原田牧場     日高町  2016年4月30日       リーチザクラウン
## 6 社台ファーム     千歳市  2016年3月13日     キャプテントゥーレ
##               mother prize
## 1 スパークルジュエル     0
## 2   エプソムアイリス     0
## 3     デライトシーン     0
## 4     ドリームシップ     0
## 5   フリーダムガール   180
## 6     ステイアライヴ   455
```


