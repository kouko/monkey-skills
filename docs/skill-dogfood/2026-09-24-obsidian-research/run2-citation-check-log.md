# Citation check log

NOTE: research/2026-09-24 日治時期鐵道建設與台灣城市發展——兼與朝鮮半島對照.md
PACKET: source-packet.md (544 lines, read in full)

Totals: 137 items checked. Tier-1 MATCH 122. Tier-1 non-MATCH 15: WRONG-SOURCE 9, NOT-IN-PACKET 4, MISMATCH 2, MATCH-with-wrong-URL-binding 0.
Escalated to tier 2 (had a cited URL): 13. Two more (#107, #131) have no cited URL, so tier 2 does not apply.
Final failures: 15 = NOT-IN-CITED-SOURCE 9, CONTRADICTED-BY-SOURCE 1, UNREACHABLE 3, unsourced / no URL 2.

Legend: T1 = tier-1 verdict (packet only). T2 = tier-2 verdict (fetch of the URL the note cites). "—" means not needed.

## A. Failures (all non-MATCH items)

| ID | line | [n] | item | T1 | T2 | fix |
|---|---|---|---|---|---|---|
| 31 | 90 | [3] | 《臺灣鐵道史》: line first planned via 南投, moved west to 彰化, never planned through 鹿港 | WRONG-SOURCE (packet lists it under 葉高華 in Angle 1 but attributes it to zh.wikipedia 鹿港鎮 in the verifier section) | NOT-IN-CITED-SOURCE. The mapstalk page has no 南投/彰化 routing. zh.wikipedia 鹿港鎮 has it, citing 臺灣鐵道史 (fetched, confirmed: 「從未有經過鹿港市區之規畫」) | Re-cite this sentence to zh.wikipedia 鹿港鎮 and add it to the source list; keep [3] for the three reasons. |
| 34 | 104 | [11] | Taipei station moved "1901" from 大稻埕 to north of the north-gate wall | WRONG-SOURCE (the year and 大稻埕 origin sit under a different URL in the packet) | NOT-IN-CITED-SOURCE for the year. [11] confirms the 1891 大稻埕 station and the move to the north-gate wall, but gives no year. tcmb.culture.tw id=188167 says 「明治34年（1901年）8月遷於現址」 (fetched, confirmed) | Add https://tcmb.culture.tw/zh-tw/detail?indexCode=Culture_Object&id=188167 as a source for 1901, or drop the year. |
| 42 | 105 | [15] | Taichung: front station = government offices and commerce; rear = warehouses, sugar mill, liquor plant | WRONG-SOURCE (packet: sugar/liquor/官署 come from a 報時光/聯合報 snippet, not StoryStudio) | NOT-IN-CITED-SOURCE. [15] has only the 臺灣倉庫會社 warehouse at the rear (and 綠川). time.udn.com/udntime/story/122835/9318232 confirms rear 帝國製糖廠 + 公賣局第五酒廠 + 鐵路倉庫, but did NOT show the front-side government/hospital/bank description | Re-cite the rear sugar/liquor part to the udn URL. Cut the "前站是官署與商業" clause or find a source for it. |
| 45 | 106 | [17] | Chiayi station is outside the city walls ("城外") | NOT-IN-PACKET (only the agent's own synthesis: "station outside or at the edge of the old city") | NOT-IN-CITED-SOURCE. [17] confirms the 1906 quake → wall remnants demolished → roundabouts, and says nothing on the station's location (fetched) | Remove "城外", or write "車站位置由本筆記推論" and drop the [17] cite from that cell. |
| 53 | 113 | [49] | "站前軸線的格局也因此延續下來" (station-front axes persisted because the planning law stayed in force) | NOT-IN-PACKET (packet only has the 1964 repeal of the 都市計畫令) | NOT-IN-CITED-SOURCE. [49] confirms legal continuity to 1964 and a general 「仍對至今的都市計畫影響深遠」, but does not link it to station-front layouts (fetched). The note's §8 also says no persistence study was found | Delete the sentence, or label it "我的推論（意見）". |
| 68 | 131 | [19] | 鹽水港製糖 moved its head office from 鹽水岸內 to 新營 after the mill was completed | WRONG-SOURCE (packet: from 新營糖廠, zh.wikipedia, not 臺灣糖業鐵路) | NOT-IN-CITED-SOURCE. The 臺灣糖業鐵路 page only mentions the 新營–岸內 line; nothing on the head-office move (fetched) | Re-cite to zh.wikipedia 新營糖廠 and add it to the source list. |
| 72 | 142 | [31] | 京釜線 was built by "民營的京釜鐵道會社趕在日俄戰爭期間完工" | WRONG-SOURCE (packet: a caveat in the verifier section, tied to [48]/DBpia, not [31]) | NOT-IN-CITED-SOURCE. [31] says only that 경부철도주식회사 was founded in 1901 as the operator; nothing on rushing for the war (fetched). [48] calls the line 半官半民, so "民營" is also too strong | Change to "京釜鐵道會社（半官半民）", cite [48], and drop the "趕在日俄戰爭期間完工" wording unless a source is found. |
| 78 | 155 | [33] | Daejeon was a quiet farm village called 한밭 before the railway | WRONG-SOURCE (the quote is in encykorea 「철도」 = [31]) | NOT-IN-CITED-SOURCE. [33] does not describe the village as 한적한 시골마을 (it only refers to 한밭마을 as a transit point). [31] has the exact quote (fetched, confirmed) | Change the cite to [31][51]. |
| 83 | 158 | [34] | Daejeon population 1915 = 6,061; 1932 = 33,843; 1935 = 39,061 | NOT-IN-PACKET (the packet has the figures but no URL binding; the Angle 4 report says they were not verified by reading a page) | NOT-IN-CITED-SOURCE. hsnews [34] gives 24,043 (1928) and 34,079 (1933) and the 1 Oct 1935 date, but not 6,061 / 33,843 / 39,061 (fetched). daejeon.go.kr menuSeq=1719 confirms 39,061 for 1935 only | Re-cite 39,061 to daejeon.go.kr/drh/…menuSeq=1719. Remove 6,061 and 33,843, or replace them with the hsnews figures (34,079 in 1933). |
| 87 | 161 | [35] | 鴨綠江鐵橋 opened in 1911 | WRONG-SOURCE (the packet gives 1911 in the verifier note, not tied to 北田) | UNREACHABLE for [35] (scanned J-STAGE PDF; fetch returned garbled binary). The 1911 date is not in [36] either (fetched) | Remove the year, or add a source that gives it. 北田's junction fact (footnote 7) stays cited to [35]. |
| 93 | 169 | [52] | 江景: river-trade role replaced by the railway hub | WRONG-SOURCE (packet: from unread search snippets) | CONTRADICTED-BY-SOURCE. [52] attributes the port's loss of function to a dike blocking the Geumgang estuary (「둑이 생기면서 뱃길이 막혀…」), not to the railway (fetched). The 1911 opening date in [52] is fine | Remove the "河運被鐵道樞紐取代" clause, or state the dike cause per [52] and treat the railway link as unverified. |
| 103 | 186 | [1][4] | 安平 listed among old ports replaced | WRONG-SOURCE (packet supports 安平 only via [6] (routes moved to 基隆/高雄) and [9] (land price 6→1.5)) | UNREACHABLE for [1] (PDF text layer not extractable). [4] not opened; the packet's table has no 安平 row | Change the cite for 安平 to [6][9], or drop 安平 from that cell. |
| 107 | 188 | none | "台中本來就是規劃中的省城"; "行政中心大多原地升格" | NOT-IN-PACKET (packet has only the book title 《從省城到臺中市》 and a general "administrative seat" remark) | — no cited URL | Add a cite, or mark it as the author's inference. |
| 131 | 243 | none | "其中 5 條修正了數字或措辭" | MISMATCH. The packet's verifier reports show corrections or caveats on well over 5 of the 14 claims: trunk-line A, B, D; economic/industrial A, C, D, E; Korea A, B, D, E. (14 claims, 3 verifiers, and 1 downgrade to Low all match.) | — no cited URL | Recount from the verifier reports, or write "多數條目有小幅修正". |
| 134 | 253 | none (packet: LSE blog) | Liu's study "用城鎮層級的資料比較有車站與沒有車站的地方" | MISMATCH. The packet says only "looks like an econometric study of connected versus unconnected towns"; it was blocked and none of its content was read | UNREACHABLE (LSE URL returned 403) | Hedge as "看起來是…（未能讀取）" or delete the method description. |

## B. Spot checks on MATCH items (fetched anyway; no change to verdicts)

- #30 line 84 [3]: bargaining, stations along lines between administrative centers, and the 北斗 (four river channels) and 麻豆 (widest part of 曾文溪) reasons are all on the page. CONFIRMED.
- #59/#61/#62 line 127 [23]: December 1912 "大致上完工", 0.35→3.35 km², and 林森西路 timber street are all on the page. CONFIRMED. Note that [23] says the sawmill was finished "隔年" (1913) while the note cites [24] for Dec 1914. [24] is the Forestry Agency page, which is the more specific source. Leave as is.
- #85 line 159 [34]: "1935年10月1日" is on the page. CONFIRMED.
- #88 line 161 [36]: April 1923 fire and the 1923 move are on the page. CONFIRMED.
- #73 line 143 [48]: the fetch confirms 軍用鐵道 (laid directly by the army) but did not show the 1906 / 1908 dates. The packet's own C1 gives 京義線 全線通車 1909 (from [31]). The packet's verifier accepted the note's dates. Residual doubt, not counted as a failure. Worth a manual look.
- #79 [51] and #71 [31] 445.6 km were not opened. They stay on tier-1 MATCH only.

## C. Full table of MATCH items (tier-1 MATCH; tier 2 not needed)

| ID | line | [n] | item |
|---|---|---|---|
| 1 | 22 | (none; supported by [1]) | 縱貫線 1908 通車 |
| 2 | 22 | (none; [35]) | 大田取代公州、新義州取代義州 |
| 3 | 22 | (none; [35]) | 朝鮮鐵路首先是通往滿洲的過境幹線 |
| 4 | 24 | [9] | 米價趨一致；車站地單產與地價上升幅度較大 |
| 5 | 24 | [11][16] | 商業重心移到車站前 |
| 6 | 24 | [32][35] | 幹線沿線新都市與道廳遷移 |
| 7 | 24 | [37][43] | 收奪論對上殖民地近代化論 |
| 8 | 44 | [1] | 各港各自對渡；主港帶次要港 |
| 9 | 46 | [1] | 清代只完成基隆到新竹 |
| 10 | 46 | [1] | 「成效非常有限，並不足以啟動資本主義發展」 |
| 11 | 48 | [8] | 1896 增田禮作勘測，「以軍事需求為重…近山之線路」 |
| 12 | 48 | [8][1] | 1899 長谷川重勘；「不惜迂迴彰化、員林」 |
| 13 | 48 | [8][2] | 「打狗直抵楠仔坑」；片倉：考量高雄未來發展 |
| 14 | 54 | [1] | 戴寶村 1988：舊港無鐵路、加速沒落 |
| 15 | 58 | [1] | 梧棲 1898 逾六成、1907 約五成（特別輸出入港間） |
| 16 | 59 | [1] | 1908 後梧棲地位不保；米改運大肚站、葫蘆墩站 |
| 17 | 60 | [1] | 汴仔頭戎克船 1904 10,800 → 1908 14 |
| 18 | 64 | [1] | 基隆約 1906 超過淡水成茶葉出口港 |
| 19 | 64 | [6] | 中國航線由淡水、安平改到基隆、高雄 |
| 20 | 70 | [4] | 台中列（8,025/11；24,605/4；70,069/6；101,272/6） |
| 21 | 71 | [4] | 高雄列（35,053/3；85,467/4；197,897/2） |
| 22 | 72 | [4] | 嘉義列（17,910/5；19,595/4；23,772/5；73,072/5；102,192/5） |
| 23 | 73 | [4] | 鹿港列（17,414/6；19,781/3；19,572/7；23,707/9；45,977/11） |
| 24 | 75 | [4] | 章英華、蔡勇美 1997；《市街庄概況》昭和 18 年 |
| 25 | 78 | [4] | 1905 以支廳為單位，鹿港第 3 被灌大 |
| 26 | 78 | [5] | 台中 1905 15,003 → 1943 102,083 |
| 27 | 80 | [4] | 鹿港人口增加但排名下滑 |
| 28 | 80 | [9] | 鹿港實質地價「不升反降」 |
| 29 | 80 | [2] | 片倉：中部重心由彰化、鹿港等轉到台中 |
| 30 | 84 | [3] | 葉高華 2015：傳說＋三項理由 |
| 32 | 90 | [8] | 選線標準可佐證 |
| 33 | 96 | [7] | 山線／海線；1917 滯貨；1919 開工；1922 通車 |
| 35 | 104 | [12] | 三線道路 1910–1913；1932 站前廣場 |
| 36 | 104 | [12] | 街廓以連接大稻埕與城內的東西向幹道為基準 |
| 37 | 104 | [13] | 日台居住分化「顯著」 |
| 38 | 105 | [14] | 縱貫線斜切既有市街 |
| 39 | 105 | [49] | 車站用地取代公園預定地 |
| 40 | 105 | [15] | 站前的綠川一帶 |
| 41 | 105 | [14] | 鐵路以北發展快；以南為第二次市區計畫新區 |
| 43 | 105 | (none) | 沒找到台中族群分區證據（packet 自身結論） |
| 44 | 106 | [17] | 1906 大地震後拆城牆殘蹟、改設圓環 |
| 46 | 106 | [16] | 中山路（站前到中央圓環） |
| 47 | 106 | [16] | 商業重心從東門圓環移到站前 |
| 48 | 106 | [16] | 大通多為日本人新店；二通「本島人街」 |
| 49 | 107 | [18] | 大正町通（今中山路）從車站通往大正公園 |
| 50 | 111 | [14] | 第一次市區計畫（1900）早於中部段完工；「有形的阻擋」 |
| 51 | 112 | [16] | 日本人「多」在大通開店，非嚴格隔離 |
| 52 | 113 | [49] | 1964《都市計畫法》廢止《臺灣都市計畫令》 |
| 54 | 119 | [19] | 糖鐵 2,964.6 / 2,337.5 / 627.1 公里 |
| 55 | 119 | [20] | 台鐵 1951 約 939.6 公里；約三倍 |
| 56 | 120 | [21] | 糖鐵營業線可與縱貫線轉乘 |
| 57 | 121 | [22] | 台車放射狀；1928 約 530 萬人次；多近百萬 |
| 58 | 121 | [22] | 「也難以充分發揮效用」 |
| 59 | 127 | [23] | 阿里山森林鐵道 1912 大致完工 |
| 60 | 127 | [24] | 貯木場與製材工場 1914 年 12 月落成 |
| 61 | 127 | [23] | 0.35 → 3.35 平方公里 |
| 62 | 127 | [23][25] | 林森路木材街；「木都」 |
| 63 | 128 | [28][29] | 1904 起填出鐵道部埋立地；四條線；濱線；哈瑪星 |
| 64 | 128 | [29] | 郡役所與街役場在哈瑪星；州廳在山下町 |
| 65 | 129 | [30] | 基隆車站在岸壁前、鐵軌延伸進港區 |
| 66 | 130 | [27] | 花蓮 1910 車站；1,678 → 逾 4,500 人 |
| 67 | 130 | [26] | 「非鐵道線上的聚落並無較大的變化」 |
| 69 | 133 | [25] | 「十分之一人口從事木業」；找不到原始統計 |
| 70 | 141 | [31] | 京仁線 1899，首條鐵路 |
| 71 | 142 | [31] | 京釜線 1905，445.6 公里 |
| 73 | 143 | [48] | 京義線 1906；1908 直通；軍用（見 §B 殘留疑慮） |
| 74 | 144 | [31] | 湖南線、京元線 1914；湖南線在大田分岔 |
| 75 | 146 | [31] | 日本以軍事行動為由主張鋪設 |
| 76 | 147 | [48] | 1917–1925 滿鐵；「宜統合支配」 |
| 77 | 151 | [35] | 北田：以確立內地至滿洲運輸路線為主要目的 |
| 79 | 155 | [51] | 朝鮮初期就有「한밭」地名 |
| 80 | 155 | [31] | 因京釜、湖南線分岔設站而成城 |
| 81 | 157 | [32] | 1904 設站；守備隊、駐在所、小學校 |
| 82 | 157 | [38] | 通車 4 年內 1,500 多家商店 |
| 84 | 159 | [32] | 1932 道廳自公州遷大田 |
| 85 | 159 | [33][34] | 1935 年 10 月 1 日升府 |
| 86 | 161 | [35] | 新義州位在京義線與滿洲鐵路接點 |
| 88 | 161 | [36] | 1923 道廳自義州遷新義州；4 月失火 |
| 89 | 163 | [35] | 北田：沿線新興、偏離路線停滯；公州／義州；忠州／尚州 |
| 90 | 167 | [39] | 鳥致院 1900 定線後成集散地 |
| 91 | 168 | [35] | 裡里、群山、木浦；1931 轉向後停滯 |
| 92 | 169 | [52] | 1911 湖南線通車，江景站開業 |
| 94 | 170 | [45] | 外道出生比例 38.5% / 31.6%；「結節點」 |
| 95 | 174 | [39] | 首爾新聞 2017；民俗博物館 2016；「地形險峻且繞行距離長」 |
| 96 | 174 | [40] | 「優先考慮軍事而非經濟效益」 |
| 97 | 178 | [41] | 朝鮮市街地計畫令：1934/6、目的、羅津、強制區劃、23 城、1962 |
| 98 | 178 | [49] | 台灣 1964 |
| 99 | 184 | [8] | 1899 軍事路線改經濟路線 |
| 100 | 184 | [35][48] | 朝鮮通往滿洲；滿鐵 1917–1925 |
| 101 | 185 | [6] | 南北縱貫線、兩端接兩港 |
| 102 | 185 | [31] | 釜山—首爾—新義州走廊；湖南、京元支線 |
| 104 | 187 | [4] | 台中、高雄、嘉義、基隆崛起 |
| 105 | 186 | [35] | 公州、義州、忠州、尚州 |
| 106 | 187 | [35][45] | 大田、新義州、鳥致院、裡里 |
| 108 | 188 | [32][36] | 公州→大田（1932）、義州→新義州（1923） |
| 109 | 189 | [19][20] | 糖鐵約 3,000 公里、約三倍 |
| 110 | 190 | [35][41] | 1930 年代北部礦工業與羅津崛起，南部農業據點停滯 |
| 111 | 191 | [3] | 龍脈說已被否定 |
| 112 | 191 | [39][40] | 公州儒生說已被否定 |
| 113 | 192 | [9] | 米價收斂、單產與地價計量研究 |
| 114 | 192 | [35][45][46] | 朝鮮以描述為主；只找到鐵路與三一運動的計量研究 |
| 115 | 193 | [10] | 台灣經濟學界「近代經濟成長」討論 |
| 116 | 193 | [37][50] | 收奪論對上近代化論 |
| 117 | 195 | [35] | 北田關鍵句 |
| 118 | 203 | [10] | 矢內原（1929）：土地調查、治安、交通建設 |
| 119 | 204 | [10] | 吳聰敏：許多人認為日本統治明顯促進經濟發展 |
| 120 | 206 | [9] | 米價 7.73/6.30 → 6.97/6.60 |
| 121 | 207 | [9] | 單產 p = 0.018 |
| 122 | 208 | [9] | 上等建地 p = 0.048；下等不顯著；聚集經濟與外部利益 |
| 123 | 214 | [37] | 「大動脈」；運入資本、軍隊與移民，運出原料、糧食、勞動力 |
| 124 | 214 | [42] | 國有地無償、民有地低價；米占貨運 14% → 46% |
| 125 | 215 | [43] | 李榮薰：社會間接資本擴充 |
| 126 | 215 | [50][44] | 批評：「以不實統計與局部近代要素誇大其詞」 |
| 127 | 216 | [42] | 鄭在貞：「付出高昂學費學習近代」 |
| 128 | 216 | [47] | 車明洙：鐵路整合國內外商品與要素市場 |
| 129 | 228 | [4][5] | 台中 1905：8,025 對 15,003 |
| 130 | 243 | (none) | 14 條說法、3 個查證代理、1 條降為 Low |
| 132 | 244 | (source list) | 搜尋語言 繁中 26／韓 18／日 6／英 2（我數過來源清單，吻合） |
| 133 | 244 | (none) | LSE 部落格 403、未採用 |
| 135 | 254 | (none) | J-STAGE 論文找到但未讀 |
| 136 | 255 | [12] | 越沢明 1987；嘉義市區改正碩士論文找到但未讀 |
| 137 | 258 | [3] | 葉高華指出車站沿行政中心連線分布 |
