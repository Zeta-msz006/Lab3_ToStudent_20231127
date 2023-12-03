# This file is part of OpenCV Zoo project.
# It is subject to the license terms in the LICENSE file found in the same directory.
#
# Copyright (C) 2021, Shenzhen Institute of Artificial Intelligence and Robotics for Society, all rights reserved.
# Third party copyrights are property of their respective owners.

import numpy as np
import cv2 as cv

class CRNN:
    def __init__(self, modelPath, backendId=0, targetId=0):
        self._model_path = modelPath
        self._backendId = backendId
        self._targetId = targetId

        self._model = cv.dnn.readNet(self._model_path)
        self._model.setPreferableBackend(self._backendId)
        self._model.setPreferableTarget(self._targetId)

        # load charset by the name of model
        if '_EN_' in self._model_path:
            self._charset = self._load_charset(self.CHARSET_EN_36)
        elif '_CH_' in self._model_path:
            self._charset = self._load_charset(self.CHARSET_CH_94)
        elif '_CN_' in self._model_path:
            self._charset = self._load_charset(self.CHARSET_CN_3944)
        else:
            print('Charset not supported! Exiting ...')
            exit()

        self._inputSize = [100, 32] # Fixed
        self._targetVertices = np.array([
            [0, self._inputSize[1] - 1],
            [0, 0],
            [self._inputSize[0] - 1, 0],
            [self._inputSize[0] - 1, self._inputSize[1] - 1]
        ], dtype=np.float32)

    @property
    def name(self):
        return self.__class__.__name__

    def _load_charset(self, charset):
        return ''.join(charset.splitlines())

    def setBackendAndTarget(self, backendId, targetId):
        self._backendId = backendId
        self._targetId = targetId
        self._model.setPreferableBackend(self._backendId)
        self._model.setPreferableTarget(self._targetId)

    def _preprocess(self, image, rbbox):
        # Remove conf, reshape and ensure all is np.float32
        vertices = rbbox.reshape((4, 2)).astype(np.float32)

        rotationMatrix = cv.getPerspectiveTransform(vertices, self._targetVertices)
        cropped = cv.warpPerspective(image, rotationMatrix, self._inputSize)

        # 'CN' can detect digits (0\~9), upper/lower-case letters (a\~z and A\~Z), and some special characters
        # 'CH' can detect digits (0\~9), upper/lower-case letters (a\~z and A\~Z), some Chinese characters and some special characters
        if 'CN' in self._model_path or 'CH' in self._model_path:
            pass
        else:
            cropped = cv.cvtColor(cropped, cv.COLOR_BGR2GRAY)

        return cv.dnn.blobFromImage(cropped, size=self._inputSize, mean=127.5, scalefactor=1 / 127.5)

    def infer(self, image, rbbox):
        # Preprocess
        inputBlob = self._preprocess(image, rbbox)

        # Forward
        self._model.setInput(inputBlob)
        outputBlob = self._model.forward()

        # Postprocess
        results = self._postprocess(outputBlob)

        return results

    def _postprocess(self, outputBlob):
        '''Decode charaters from outputBlob
        '''
        text = ''
        for i in range(outputBlob.shape[0]):
            c = np.argmax(outputBlob[i][0])
            if c != 0:
                text += self._charset[c - 1]
            else:
                text += '-'

        # adjacent same letters as well as background text must be removed to get the final output
        char_list = []
        for i in range(len(text)):
            if text[i] != '-' and (not (i > 0 and text[i] == text[i - 1])):
                char_list.append(text[i])
        return ''.join(char_list)

    CHARSET_EN_36 = '''0
1
2
3
4
5
6
7
8
9
a
b
c
d
e
f
g
h
i
j
k
l
m
n
o
p
q
r
s
t
u
v
w
x
y
z'''

    CHARSET_CH_94 = '''
0
1
2
3
4
5
6
7
8
9
a
b
c
d
e
f
g
h
i
j
k
l
m
n
o
p
q
r
s
t
u
v
w
x
y
z
A
B
C
D
E
F
G
H
I
J
K
L
M
N
O
P
Q
R
S
T
U
V
W
X
Y
Z
!
"
#
$
%
&
'
(
)
*
+
,
-
.
/
:
;
<
=
>
?
@
[
\
]
^
_
`
{
|
}
~'''

    CHARSET_CN_3944 = '''
H
O
K
I
T
E
A
酱
鸭
传
奇
J
N
G
Y
C
U
Q
蝦
兵
蟹
煲
这
是
可
以
先
吃
后
涮
的
干
锅
菜
加
盟
电
话
：
1
7
3
9
8
郑
州
总
店
雪
花
勇
闯
天
涯
虾
，
一
送
鱼
锡
纸
蛤
土
豆
粉
砂
米
线
牛
筋
面
刀
削
水
饺
吧
沙
拉
老
饭
盒
教
室
主
题
餐
厅
仁
馄
饨
重
庆
小
便
当
全
国
连
锁
4
0
-
6
5
2
人
快
量
贩
蓬
朗
御
茶
川
渝
捞
火
古
之
匠
今
七
西
域
羊
城
l
i
k
n
g
c
o
f
e
w
贵
阳
素
有
家
会
展
口
乐
三
惹
烤
肉
h
t
子
馆
常
盖
浇
兴
业
路
书
亦
燒
仙
草
L
:
德
啤
工
坊
杏
屋
高
桥
号
品
麻
辣
烫
检
官
.
千
翼
木
兰
画
食
上
汤
剁
馅
手
煮
时
尚
健
康
傲
椒
B
啵
条
脾
气
！
/
月
腾
讯
应
用
喵
泡
我
鲜
滚
给
你
看
客
来
香
汉
湘
本
地
炒
系
列
订
仔
肘
蹄
梅
扣
黄
焖
排
骨
炖
鸡
韓
金
利
串
舊
街
梨
村
座
经
济
实
惠
绿
色
炭
庐
蛙
忆
蓉
源
真
d
D
概
念
创
意
六
熏
各
种
精
美
y
疯
狂
世
界
杯
特
价
酒
元
瓶
沸
带
F
请
二
楼
自
动
升
降
烏
邦
嗦
味
风
货
团
外
卖
嘞
个
折
辛
束
舌
尖
中
包
浆
腐
r
P
a
u
丸
作
福
M
漫
蜜
冰
拌
匆
那
年
R
S
果
光
夹
馍
凉
皮
过
祖
南
山
風
景
堂
烘
培
龍
坎
半
婆
建
设
富
强
丽
菏
泽
省
安
港
竹
签
撩
只
为
好
生
活
抓
海
最
网
红
铁
统
®
功
夫
鱿
大
闻
就
知
遇
见
文
合
热
森
台
湾
卤
然
汁
甄
选
材
还
原
初
衷
*
洪
龙
公
酸
巴
乡
焦
烧
淘
成
都
眼
镜
优
菓
恋
V
化
糖
、
粥
田
螺
斓
X
爺
W
j
院
华
Z
蜊
北
京
刷
蝎
腿
梦
幻
奶
式
蛋
鍋
区
·
领
航
者
四
通
往
楚
河
停
车
场
凌
晨
点
杞
缘
王
集
唐
菠
萝
泰
板
鳳
凰
樓
名
壹
猪
晴
舍
犟
师
傅
飯
致
青
春
轰
炸
卡
里
身
厨
房
x
聚
鑫
阁
岛
纯
聘
专
长
庄
鄉
更
珍
固
新
岩
v
s
m
至
尊
比
萨
广
披
饮
管
理
限
司
p
幸
东
正
挞
少
女
克
装
童
哒
磨
厂
怼
纤
入
户
独
溜
共
享
滋
江
门
九
蒸
胜
盛
&
魔
爪
鹅
皇
（
）
友
甲
魚
首
烹
行
员
若
资
议
联
同
急
私
燕
儿
巢
鹏
记
腊
营
欢
迎
旗
舰
叫
了
做
故
铃
煎
饼
哥
力
五
谷
野
戈
厠
所
超
牌
冒
陳
陈
苕
爽
滑
启
秦
择
现
进
惊
喜
定
于
雅
膳
多
推
淇
淋
b
思
堡
偶
相
伴
呈
湯
绝
浏
'
刘
态
牧
万
达
和
番
丼
—
机
瘦
绵
柔
厉
蚝
娘
彩
百
事
调
韩
爱
喝
玩
放
肆
寿
净
配
髓
非
道
额
吉
招
商
杂
粮
筐
运
转
服
务
缤
灿
腕
楠
彤
学
橋
试
浩
减
薪
诚
霸
第
间
日
极
料
開
業
霏
星
期
分
秒
内
咨
询
。
樐
头
开
氏
渔
约
劳
保
礼
宏
武
佘
轻
奢
艺
井
隆
鐵
卷
染
焙
钵
马
牟
洋
芋
片
流
宽
心
位
清
潼
关
祥
背
凡
哈
尔
滨
珠
派
艾
让
变
得
样
玖
等
综
性
涵
粗
冠
記
肠
湖
财
贡
桃
杭
平
桂
林
煨
档
案
造
潮
汕
宗
单
县
鲁
舜
脆
酥
糕
仕
十
临
簋
宴
字
太
灌
薄
尝
址
晗
幢
购
梁
醉
皖
庭
白
肥
块
石
碗
颜
值
張
瘾
跷
脚
而
叁
蜀
橙
市
边
早
晚
云
吞
目
表
赵
烩
擀
蔬
找
回
游
刃
余
支
洗
吹
休
闲
简
撸
根
据
鸽
铜
亲
贝
纪
吕
豚
饅
悦
汇
油
无
制
在
寻
碳
馋
嘴
架
荣
斋
护
角
落
铺
臊
丝
围
柳
蛳
蒲
庙
视
荐
缃
想
呀
姜
母
起
泉
族
群
众
其
它
血
双
补
阴
润
不
禽
类
款
较
候
些
畅
脉
痰
疏
肝
帮
助
消
增
欲
尤
对
胃
畏
寒
很
效
秘
黑
嘿
佳
越
脑
桶
项
▪
|
榜
许
仿
或
酬
宾
指
买
赠
笃
鼎
盆
™
咕
咾
肚
识
栖
凤
渡
筒
彬
弟
醋
財
師
民
博
丁
扒
翅
墨
柠
檬
紫
薯
焗
芝
士
胸
图
妮
杀
菌
爹
尽
归
宁
粽
瑞
轩
午
陕
出
才
盘
植
甜
粒
神
舟
玻
璃
医
划
药
郡
毛
张
姐
留
满
下
兄
法
鋪
é
[
槑
]
言
密
帝
場
朴
寨
奉
z
什
顺
疆
馕
豫
怀
旧
验
昙
搞
圣
格
ǐ
à
隱
燙
状
居
饱
底
免
费
廣
點
專
門
语
叉
左
岸
发
乌
齐
冷
命
●
修
闸
飞
空
养
笼
興
银
套
東
吴
麺
館
¥
从
前
乙
弘
炝
夏
秋
冬
咖
啡
℃
©
莲
塘
哆
梓
依
哎
麦
泗
泾
瓯
胡
∣
歺
八
度
深
夜
旋
永
远
温
又
晶
溏
ä
盔
飘
劲
旺
楸
良
譜
餅
苏
莎
足
宵
与
楊
國
莱
卜
炊
挑
剔
存
错
方
程
解
能
堆
洲
诗
玛
渴
脖
丛
狼
翁
姓
葫
芦
沾
葵
の
咔
粹
弥
乖
悠
茗
别
走
柒
榨
咥
虹
沏
桔
叔
贴
办
充
崎
鮮
属
彭
浦
町
郎
°
悟
惑
科
英
育
岁
幼
园
慢
摆
_
狐
狸
典
暴
帥
尾
琼
見
望
烟
坚
鸳
鸯
直
校
饪
承
们
么
￥
份
宇
炉
峰
乃
趣
代
刨
抖
音
占
谜
答
熟
控
蕾
节
社
您
《
羅
茉
瀞
憨
尼
丰
镇
酿
避
抢
突
破
杰
姆
波
观
澜
庫
舒
谁
短
島
爷
码
每
欧
注
册
标
腸
奈
熊
粵
吳
衢
雄
际
葱
柱
压
陪
器
厘
柴
席
饿
俏
汽
站
霜
荟
禾
咘
臭
夷
肖
微
组
刺
拼
打
信
步
!
说
囍
智
藍
鹿
巷
顾
勃
頭
帕
徐
渣
嗨
鲍
抽
莊
胗
耳
栈
葑
谊
李
够
歪
到
杜
绪
始
“
”
编
感
谢
阿
妹
抄
屿
旁
钟
糰
鷄
觉
队
明
没
幺
罗
恭
發
溢
圆
筵
鲩
斤
噜
府
雕
牦
津
間
粤
义
驾
嫩
眷
苔
怡
逍
遥
即
把
季
鹃
妈
烙
淡
嘟
班
散
磐
稣
耍
芽
昌
粿
鼓
姑
央
告
翔
迦
缆
怪
俗
菩
宥
酵
男
顿
蚂
蚁
q
緑
瑩
養
滿
接
立
勤
封
徽
酷
(
慕
曹
吊
咸
矿
黛
刻
呗
布
袋
钝
丘
逗
窗
吾
塔
坡
周
雙
朝
末
如
杨
淮
摄
影
翻
窝
物
椰
荞
搅
陇
收
两
倍
狮
伊
後
晖
長
箐
豪
耀
漢
釜
宮
次
掌
斯
朋
针
菇
蚬
拍
雒
陽
漿
麵
條
部
←
柜
驴
证
票
账
汗
汆
稍
戏
菋
卫
匹
栋
馨
肯
迪
邢
梯
容
嘉
莞
袁
锦
遮
雨
篷
腰
肺
剡
乾
,
翰
蔚
刁
藤
帅
傳
维
笔
历
史
】
适
煌
倾
沧
姬
训
邵
诺
敢
质
益
佬
兼
职
盅
诊
扬
速
宝
褚
糁
钢
松
婚
秀
盐
及
個
飲
绍
槿
觅
逼
兽
》
吐
右
久
闺
祝
贺
啦
瓦
甏
探
辰
碚
芳
灣
泷
饰
隔
帐
飮
搜
時
宫
蘭
再
糊
仓
稻
玉
印
象
稀
拴
桩
餃
贾
贱
球
萌
撕
脂
肪
层
晋
荷
钱
潍
失
孜
提
供
具
洛
涂
叠
豊
积
媒
级
纷
巧
瓜
苹
琥
珀
蜂
柚
莉
爆
龄
饸
饹
郞
嫡
億
姚
繁
监
督
示
佰
汍
%
甘
蔗
喻
骄
基
因
匙
评
侠
赢
交
歡
待
馒
产
倡
导
低
茂
沐
熙
延
丧
受
确
睡
蓝
未
賣
電
話
农
札
岗
树
赖
琪
驻
辉
软
防
盗
隐
形
纱
灶
扎
环
禁
止
吸
萬
昆
几
跳
媳
婦
坛
<
>
拿
妖
协
朱
住
宿
魅
照
碰
滴
何
贤
棒
持
啊
赛
版
帆
順
狗
情
+
洞
奋
斗
亨
叶
涛
铝
范
汀
號
律
價
鞭
肩
#
愚
奥
脯
沁
奚
魏
批
租
宠
炲
横
沥
彪
投
诉
犀
去
屠
鲅
~
俱
徒
鴻
劉
迷
荤
威
曜
連
鎖
馳
载
添
筑
陵
佐
敦
＞
郭
厢
祛
茄
堰
漂
亮
爅
虎
膀
叼
猫
藏
陶
鲈
栏
…
考
冲
胖
裕
沃
挂
报
兔
胶
臨
附
处
嫂
萃
幂
吻
聪
糯
糍
棋
烓
脊
衡
亚
副
肤
荆
榴
绚
黔
圈
纳
课
逸
宜
=
烊
姨
施
救
贸
啥
也
贯
雷
呆
棠
伙
岐
宛
媽
寸
澳
已
還
兒
Ⅱ
凯
株
藕
闽
窖
瀘
售
索
体
型
樂
琅
琊
夺
扩
)
诱
滩
浓
要
芹
君
反
复
羔
追
演
唱
過
綫
乳
涩
芒
露
蒙
羯
励
志
嵊
閒
罐
佛
墙
頁
坐
眯
预
華
廉
释
必
随
逐
引
究
爸
灵
勺
岂
俵
廷
苗
岭
将
來
泛
朵
維
園
廳
圳
伦
寶
付
仅
減
谦
硕
抚
慶
雞
郝
计
熱
杖
亭
喱
惜
莒
另
陆
拾
伍
谈
嚼
娅
翟
別
颈
邮
弄
•
扇
哦
吼
耶
宅
帽
魂
搭
笨
映
拨
烂
馈
胎
溶
\
善
销
难
忘
斑
噢
錫
娟
語
哨
筷
摊
均
椅
改
换
跟
帖
勾
缅
孙
啪
栗
着
漁
吓
易
漲
靖
枸
馬
昇
當
麥
妆
塑
魯
鎮
吗
魁
丹
杈
技
术
泼
零
忙
漾
創
攀
郫
抿
稼
假
循
泳
池
膨
巨
歧
愛
鵝
悉
灯
激
踪
细
會
舔
愿
們
衹
令
浔
丨
酉
惦
耕
×
闪
經
玺
芯
襄
賦
予
學
苑
托
丢
赔
ā
聽
濤
浮
伯
兑
币
治
愈
盱
眙
漏
夕
搏
由
完
切
罕
息
燃
叙
萍
碑
腌
衣
害
己
患
浙
闫
｜
芈
谣
戴
錦
謝
恩
芊
拇
矾
政
锣
跃
钥
寺
驼
芙
插
恒
咪
禄
摩
轮
譚
鴨
戊
申
丙
邊
唯
登
困
貢
誉
賀
认
准
妃
潜
旨
死
桌
尧
箱
届
获
顶
柿
臂
蓮
凭
慵
懒
醇
籍
静
淌
此
甚
绣
渌
呢
问
抹
弹
捷
邱
旦
曉
艳
雲
研
守
鼻
¦
揽
含
沂
听
帛
端
兆
舆
谐
帘
笑
寅
【
車
@
＆
胪
臻
蘆
衙
餌
①
鉴
敬
枝
沈
衔
蝉
芜
烈
库
椿
稳
’
豌
亿
缙
獨
菊
沤
迟
忧
沫
伟
靠
并
互
晓
枫
窑
芭
夯
鸿
無
烦
恼
闖
贞
鳥
厦
抱
歐
藝
廖
振
腦
舖
酪
碎
浪
荔
巫
撈
醬
段
昔
潘
Λ
禧
妻
瓢
柏
郁
暹
兮
娃
敏
進
距
离
倪
征
咱
继
责
任
銅
啖
赞
菲
蛇
焰
娜
芮
坦
磅
薛
緣
乔
拱
骚
扰
約
喷
驢
仨
纬
臘
邳
终
喏
扫
除
恶
争
率
‘
肃
雀
鈴
贼
绕
笋
钩
勒
翠
黎
董
澄
境
采
拳
捆
粄
诸
暨
榧
葛
親
戚
访
股
融
潤
寄
递
藩
滇
湛
他
篓
普
撞
莅
但
沟
暑
促
玲
腩
碼
偏
楹
嘎
洒
抛
危
险
损
负
銘
黃
燜
說
杆
称
蹭
聊
妙
滕
曦
肴
萧
颗
剂
義
锋
授
权
著
茴
蒝
侬
顏
菁
擦
鞋
庞
毕
谱
樱
→
綦
舞
蹈
躁
渠
俐
涧
馀
潇
邻
须
藻
纺
织
军
沅
豐
爐
韭
棚
綿
麯
剑
娱
链
锤
炼
献
晟
章
謎
数
侯
她
疗
途
篇
则
邓
赐
閣
對
猩
邑
區
鬼
莫
沪
淼
赤
混
沌
需
求
痛
绮
琦
荃
熳
佑
Á
ō
現
専
卢
譽
缠
曾
鸣
琴
汊
濮
哇
哩
唝
曲
坂
呼
莴
怕
蒋
伞
炙
燻
瑧
冈
讲
硬
详
鹵
摇
偃
嵩
严
谨
′
剥
穗
榮
禹
颐
局
刚
▕
暖
漠
炎
頤
樟
？
储
移
缕
艰
袍
瑪
麗
参
䬺
趁
呦
霖
饵
溪
孔
澤
袜
蔓
熠
显
屏
缇
寇
亞
坑
槟
榔
絳
驿
歹
匾
猴
旭
竞
­
唛
介
习
涡
寓
掉
蘸
愉
佼
ǒ
納
∶
革
嚸
募
螃
鲢
俤
扁
寳
辽
∧
厚
裤
扯
屯
废
挪
辘
碉
歇
漓
腻
捣
孩
烁
整
按
Ⓡ
眉
脸
痣
粑
序
穿
樊
玮
★
扑
渊
醴
瑶
農
檔
憩
霊
赫
呜
～
备
説
莓
钻
播
冻
紅
菽
喪
埔
壽
❤
籽
咻
籣
尹
潭
穆
壮
使
霄
蔵
浒
岳
熘
臺
殷
孤
邂
逅
厕
郸
铭
莆
抻
虽
倦
怠
矣
茵
垂
殿
鄂
嗑
续
钦
党
鲫
蔡
侧
割
彰
凝
熬
叕
純
谛
籠
宋
峡
俩
雜
跑
⑧
焼
－
逢
澧
舵
异
冯
战
决
棍
；
﹣
丑
妇
焉
芷
楂
坞
壳
馐
帜
旅
鳯
簡
凍
秜
结
咩
丫
稠
暗
缔
乎
被
狠
皲
豉
崇
渭
担
鹤
製
蛎
笛
奔
赴
盼
鳌
拜
络
灸
膜
刮
痧
毒
萊
陂
濑
唇
抵
押
置
馇
泌
尿
傻
像
孃
陣
靓
规
企
矮
凳
贰
兎
庵
質
阅
读
◆
练
墩
曼
呱
泓
耐
磁
枣
罉
浴
氧
洱
鳅
線
炳
顽
符
倌
泥
郊
柯
餘
巍
论
沽
荘
奕
啃
髙
○
芬
苟
且
阆
確
獅
匣
睫
牙
戒
俊
阜
遵
爵
遗
捧
仑
构
豬
挡
弓
蠔
旬
鱻
镖
燚
歌
壁
啫
饷
仰
韶
勞
軒
菒
炫
廊
塞
脏
堤
浅
辈
靡
裙
尺
廚
向
磊
咬
皓
卿
懂
葉
廿
芸
賴
埠
應
碟
溧
訂
選
睦
举
钳
哟
霍
扞
侣
營
龟
钜
埭
が
搽
螞
蟻
娚
蒜
厝
垵
☎
捌
倒
骑
Ξ
谋
黍
侍
赏
扮
忱
蘑
洁
嘆
闹
谭
鶏
種
φ
坤
麓
麒
麟
喂
琳
Ⓑ
趙
總
這
奖
取
拔
錯
仉
缸
廟
暢
腔
卓
腱
朙
紹
莹
缺
抺
睿
氣
该
貼
妍
拆
穇
箩
希
廰
祗
盲
坝
骆
熄
蛮
賓
馮
尋
泊
孫
槁
亖
俯
浣
婴
锨
馥
闷
梆
▫
姥
哲
录
甫
床
嬌
烎
梵
枪
乍
璜
羌
崂
穷
榕
聲
喚
駕
晕
嬷
箕
婧
盧
楓
柃
差
「
」
佶
唔
壕
歆
盏
擂
睇
巾
查
淖
哪
沣
赣
優
諾
礁
努
畔
疙
瘩
握
叮
栙
甑
嶺
涌
透
钓
斜
搬
迁
妨
借
仍
鳕
瓷
绘
餠
á
ǎ
祈
邨
醒
闵
砖
锹
咀
綠
幕
忠
雾
覓
靜
擔
篮
杉
势
薇
甬
频
般
仲
蘇
鸟
卞
憾
資
駱
蝶
為
仟
耗
莘
涉
昕
盈
熹
觀
瑭
湃
兢
淞
䒩
結
柗
鲤
糟
粕
塗
簽
怎
桐
皆
羽
盯
氽
晏
液
镀
珂
悸
∙
桑
夢
楽
剩
纵
逝
欺
統
飛
姣
俄
揪
薡
幅
蓋
︳
屉
㕔
а
铸
韦
銀
檀
击
伿
隍
『
』
芥
☆
声
跆
肋
榭
牵
棧
網
愁
嗏
嵗
巡
稚
貴
買
恰
㸆
捻
玫
瑰
炕
梧
餡
锌
焱
驰
堽
邯
珑
尕
宰
栓
喃
殊
燊
慈
羴
逃
脱
邹
檐
碌
页
荠
券
題
龚
肌
蕉
囬
肫
坪
沉
淀
斌
鳝
核
喳
剃
昭
｛
｝
坏
烜
媛
猛
桓
欣
碁
竭
堇
↑
扛
罄
栾
鲶
鍕
崔
橘
携
丈
射
梗
檸
疼
卑
捉
障
裏
遍
蓓
析
許
虫
坨
馔
窄
姫
噤
係
湿
汐
鳜
船
崽
＋
例
灼
祿
腥
峭
酌
喽
件
郏
栀
鲨
寫
與
诈
斥
炮
稿
懿
掂
鹭
乱
恬
婷
苦
埃
珊
禅
裹
圃
鹌
鹑
û
澡
囧
阡
靑
警
牢
嘱
鳞
浃
贷
慧
翊
讨
碧
剪
陌
冀
砵
迅
鹰
竟
召
敌
鯡
蒌
蒿
扶
③
誘
嘻
輪
嬢
瓮
絲
嚣
荀
莽
鄧
咋
勿
佈
洽
羹
模
貨
粱
凈
腹
鄭
署
儒
隧
鉢
茫
蔻
í
ó
裴
偉
Θ
祎
褥
殖
湫
瀚
貓
汪
紙
極
伤
灰
團
橄
榄
拽
响
貌
傣
舂
斩
飨
执
諸
蒂
嘣
葡
渤
惺
驛
戰
箬
俭
瀏
嫦
琵
琶
咿
吖
舱
韵
揭
祁
將
軍
吟
彼
岚
绒
煤
淝
歸
锐
嗯
傾
甩
瞳
睁
鳗
遜
嗲
虚
娴
碱
呷
{
哚
兜
喇
叭
燦
逻
匪
槐
撒
写
踩
踏
霞
喫
返
赚
拓
動
觞
鲽
鐘
闰
扳
沖
賈
璐
煸
棵
峪
π
憶
齋
娇
穎
嫁
玥
胚
喊
阻
餓
截
孵
屎
爾
莳
倔
娄
祸
`
姿
稽
戌
缪
ī
糠
痴
猎
嬉
柑
鞍
兹
凼
舅
褐
醪
仪
氷
單
丞
碛
绽
袂
檢
瀾
饃
孖
雍
ò
螄
涤
茨
寮
近
辜
茅
孟
累
宣
樹
鷹
膝
臉
襪
嘢
嵐
▲
璇
竺
気
迈
糐
挥
瑜
伽
"
裳
纹
潯
幾
朔
枊
釀
劝
俺
粢
馓
胥
拥
嘶
達
蝴
昱
ホ
ル
モ
ニ
颂
噫
否
笙
绎
俞
泵
测
耿
揚
犇
锄
卧
炯
烽
橡
操
齊
隴
宀
荥
滙
贪
関
垦
↓
麽
暧
匯
恨
叽
断
鮪
椎
病
迹
禺
搓
瀛
唤
埕
愤
怒
拐
狱
垅
绅
設
計
書
楷
鮨
邪
郴
盞
榆
恺
樵
煙
舫
翡
砸
叹
縣
璞
禮
獻
似
吆
嘛
灭
擇
夥
ē
曰
蜗
櫻
▏
鑪
鯊
視
淄
钰
〝
〞
報
退
壶
鳴
拒
旱
鼠
蕴
峧
赶
咏
寬
渎
靣
卟
宙
趟
負
镫
讷
迭
彝
樣
輕
却
覆
庖
扉
聖
喬
瞻
瞿
箭
胆
ε
韧
誌
既
淳
饞
ě
圍
墟
俚
翕
貂
畜
緹
搄
旮
旯
寂
寞
詹
茜
鉄
絕
泸
嬤
允
炘
骏
侑
晒
玄
粧
糘
毫
幽
攸
愧
侨
衰
ぉ
に
き
ぃ
炽
倉
斛
領
盾
窜
鲷
瓏
媚
爲
裸
窦
虞
處
魷
}
羡
冕
祺
裁
粶
䬴
嚟
辆
撮
隋
＇
勝
梭
茸
咭
崟
滷
緻
沩
颠
诠
珺
拙
察
≡
辅
父
雁
裱
瞄
漖
鯨
略
橱
帼
棉
濠
蕃
ǔ
崮
阮
勋
苍
喔
猜
箔
è
雏
睐
袭
皋
彻
売
垚
咯
凑
汴
纽
巩
宸
墅
茏
裡
昧
飽
坯
濟
└
┐
懷
霾
´
閑
茹
闳
湶
鈣
圓
昊
眞
標
凖
皱
箍
筹
孬
唠
輝
输
綺
驭
哼
匡
偵
蝇
運
漟
乘
Ē
卉
邴
謠
怿
亁
棱
呐
湄
莜
阶
堔
炜
邀
笠
遏
犯
罪
栢
餛
亀
苓
膏
伸
?
阪
委
妯
娌
仝
咧
鍚
▼
遠
摑
滘
颁
ʌ
锈
佤
佗
卌
É
↙
蔺
汰
塍
認
鳟
畿
耦
吨
䒕
茬
枼
饕
涼
烀
汶
齿
貳
沱
楞
屹
掺
挢
荻
偷
辶
饌
泮
喧
某
聂
夾
吁
鎬
谅
鞘
泪
佩
㎡
鐡
犊
漳
睢
粘
輔
爬
濃
し
ん
い
ち
ょ
く
ど
ぅ
戍
咚
蒡
惯
隣
沭
撇
妞
筛
昵
赁
震
欠
涞
從
靚
绥
俑
熔
曙
侗
√
仗
袖
饶
辫
琉
鴿
裂
缝
灞
崖
炑
昝
┌
┘
邕
趴
踢
迩
浈
挚
聆
犁
陝
滾
彎
問
癮
砚
ú
瀧
吮
毓
劵
槽
黒
忍
畈
姊
沛
忽
摘
燍
♡
汝
贛
叻
甸
乞
丐
践
嗞
㥁
斐
圖
祯
牤
攻
弯
幹
杠
苞
滤
筆
練
鞑
ˊ
萤
榶
叨
轨
耒
嚮
┃
漪
剛
键
弋
彦
瘋
词
敖
鸦
秧
囚
绾
镶
濂
↘
豁
煒
萄
珲
緋
昂
瀨
缓
疲
替
汥
殡
葬
靳
揉
闭
睛
偘
佚
$
;
^'''
