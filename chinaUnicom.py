# -*- coding: utf-8 -*-
"""
中国联通 Python 版 v1.0.8

包含以下功能:
1. 首页签到 (话费红包/积分)
2. 联通祝福 (各类抽奖)
3. 天天领现金 (每日打卡/立减金)
4. 权益超市 (任务/抽奖/浇水/领奖/全局库存缓存)
5. 安全管家 (日常任务/积分领取)
6. 联通云盘 (签到/AI互动/文件上传/抽奖活动/重复清理)
7. 联通阅读 (自动获取书籍/心跳阅读/抽奖/查红包)
8. 联通爱听 (积分任务/自动签到/阅读挂机/分享任务)
9. 沃云手机 (签到/任务/抽奖)
10. 区域专区 (自动识别安徽超级星期五/辽宁福利魔方/新疆/河南/云南执行特有任务)

更新说明:

### 20261006 (移植自上游 v1.2.0)
- 联通云盘「海岛逐浪应援」：新增**第3步「芒果 AI 入戏」视频制作**（`island_ai_video`）——
  云盘 token 换 ticket → mgtv 登录 → 提交模板生成视频。
  · 「照片识别失败」= 芒果对同一素材的短时频控（多账号连跑只有第 1 个通过）→ 等待后重试；
  · 响应为空 / 非 JSON（多账号连跑偶发）→ 同样等待后重试；
  · 「权益扣减失败」→ 先 offlineSubscribe 领权益再重试一次。
  开关 `UNICOM_ISLAND_AI_ENABLE`（默认开）；模板/素材用 `UNICOM_ISLAND_AI_TEMPLATE_ID` /
  `UNICOM_ISLAND_AI_IMG_FID` 覆盖；重试用 `UNICOM_ISLAND_AI_RETRY_TIMES`(默认2) /
  `UNICOM_ISLAND_AI_RETRY_WAIT`(默认40秒)。
- 联通爱听：新增**「签到」类任务处理**（`jf_sign`）—— 签到走 `uasptask/sign`，其余仍走 `jftask/toFinish`。
  ⚠️ 原脚本把签到任务从待办里过滤掉却没有处理分支，导致爱听签到任务从不执行。
- ⚠️ **未移植「乘风活动」**：上游 v1.1.2 起已移除（活动已于 2026-06 下线），本版不引入。

### 20261006
v1.0.9: (移植自上游 v1.1.2)
- 签到区：新增「月签有礼」自动领取 —— 六宫格转盘月度签到奖励
  (`sixPalaceGridTurntableLottery/floor/getMonthSign` 查列表 →
   `task/getTaskReward` 逐条领奖，taskType=30)，查询模式下只统计「可领取/已领取」数量。

### 20260917
v1.0.8: (本次实测抓包)
- 签到区-任务中心：重写任务遍历，新增 taskType=3「抽奖类」任务支持（先 completeTask 触发抽奖 → 再 getTaskReward 领奖）。
  旧版只处理 taskType=5，导致「抽视频会员」这类抽奖任务永远停在「立即抽奖」不自动完成。
- 签到区-任务中心：任务列表改为 type=1 与 type=2 双列表合并去重；领奖遇 0329「活动火爆」自动重试 4 次。
- 签到区-任务中心：taskType=8（前往新浪微博签到 / 前往百度地图签到）实测 completeTask 恒定返回
  0305「任务完成失败」，需在第三方 App 内实际签到，脚本改为明确提示"需第三方App完成"而非误报失败。
- 签到区-v2：1G流量日包改为先读 doTask/getTaskInfo 判断「看视频」状态，避免重复做任务；
  finishVideo/getPrize 遇「【050】前方网络拥堵」自动重试 3 次。
- 签到区-v2：实测 m.client.10010.com/growth/* 与 /dailylottery/* 已 302 跳转 /error/busy1.html
  （沃之树浇水、金币抽奖接口已下线），日志提示由"需登录态"更正为"接口已下线"。
- 权益超市：中奖记录推送口径改为「本月全部 + 上月距今 5 天内的」，其余（含上月早期、更早月份）一律不推送
  （旧逻辑取"上月前 2 条"，在跨月无记录时会错抓到 6 月之类的旧数据）。
  即：9 月 17 日跑 → 8 月记录全部不显示；9 月 1 日跑 → 显示 8/27~8/31（上月最后 5 天）。
- 权益超市：**本月所得**相关推送改为红色（表头「抽奖记录(本月 …)」行 + 本月中奖记录行 + "本月话费累计"行），
  用 `<font color="#ff0000">`（与话费资产行同款写法）；上月最后 5 天的记录行保持普通色。
- 资产查询：新增「流量查询」(`enable_flow`)，跟在话费余额后面输出
  **主卡套餐 + 账户流量合计 + 各号码(主卡/副卡/亲情卡)用量 + 流量包明细 + 剩余可用**，
  整块走**红色推送**（与话费行同款 `<font color="#ff0000">`）。
  接口 `servicequerybusiness/operationservice/queryOcsPackageFlowLeftContentRevisedInJune`
  （`queryOcsPackageFlowLeftContent` 备用，只有 summary 没有分号明细）。
- 修复：话费余额行同时传了 `notify=True` 和 `notify_html`，导致每条推送里重复出现两遍
  （一红一黑）。`log()` 里这两个参数是两条独立入队分支，现在只传 `notify_html`。

### 20260331
v1.0.7:
- 区域专区：新增安徽联通"超级星期五"抢红包，支持自定义面额。
- 联通爱听：修复积分弹窗空响应导致脚本崩溃。

### 20260326
v1.0.6:
- 区域专区：新增辽宁联通"福利魔方"自动化签到与资产明细展示。
- 安全管家：重构接入最新多类拦截选项及助手安全积分获取通道。
- 权益超市：增加查抢话费记录 `receiveTime` 空值防报错处理。

### 20260322
v1.0.5:
- 云盘：1GB上传任务改用秒传(quickTransfer)，无需真实上传文件，几秒完成。
- 权益超市：接入会员中心浏览积分任务，并拆分独立子开关。
- 区域专区：接入新疆每月抽奖新版 `themeAct` 链路。
- 会员中心：补充页面预热、状态轮询和领奖兜底，提升成功率。
- 日志：更新版本号，精简更新说明与启动输出。

### 20260321
v1.0.3:
- 云盘：整合实时任务、家乡打卡抽奖、上传/清理与容错优化。
- 权益超市：恢复浇花签名并对齐 H5 请求头。
- 联通爱听：补齐 `jftask` 签名头。
- 区域专区：新增云南生活任务。

配置说明:
1. 账号变量 (chinaUnicomCookie):
   赋值方式有三种:
   a. 填账号密码 (自动获取Token - 推荐):
      export chinaUnicomCookie="18600000000#123456"
   b. 填Token#AppId (免密模式 - 推荐):
      export chinaUnicomCookie="a3e4c1ff2xxxxxxxxx#912d30xxxxxx"
   c. 仅填Token (旧模式):
      export chinaUnicomCookie="a3e4c1ff2xxxxxxxxx"
   (多账号用 & 或 换行 隔开)

2. 代理设置 (可选):
   export UNICOM_PROXY_API="你的代理提取链接" (支持 JSON/TXT 格式，自动识别)
   export UNICOM_PROXY_TYPE="socks5" (可选 http 或 socks5，默认 socks5)

3. 话费优先设置:
   export UNICOM_GRAB_AMOUNT="5"           : (可选) 抢兑单面额 (兼容旧写法, 等价于 UNICOM_GRAB_AMOUNTS)
   export UNICOM_GRAB_AMOUNTS="18,10,5,3,1": (可选) 抢兑面额池, 逗号分隔, 降序=优先抢大额.
                                             库存不足会自动降级到下一档; 默认 "5"
   export UNICOM_GRAB_FALLBACK="1"         : (可选) 1=有库存的档位都抢光时, 无库存档也试一次; 0=关闭
   export UNICOM_GRAB_ATTEMPTS="8"         : (可选) 整点开抢瞬间单档最大冲击次数 (非整点自动降为2次防风控)
   export UNICOM_GRAB_MONTHLY_MAX="1"      : (可选) 每月最多成功抢兑几张话费券; 默认 1 = 本月已抢到就跳过抢兑
                                             (抢多张也用不上, 白白消耗兑换币); 0 = 不限, 恢复旧行为

4. 特殊功能设置:
   export UNICOM_TEST_MODE="query"        : (可选) 仅查询模式，跳过任务执行只查询资产
   export UNICOM_AH_FRIDAY_AMOUNT="50"    : (可选) 安徽超级星期五抢红包面额 (如50=抢50元红包, 不填则不执行)

定时规则建议 (Cron) — 🔺话费优先:
0 58 9,17 * * * (抢话费券: 每天 10:00 / 18:00 两场, 提前2分钟启动, 脚本自动精准等待整点)
0 58 9 * * 5   (安徽超级星期五: 需设置 UNICOM_AH_FRIDAY_AMOUNT，每周五9:58启动)
0 7,20 * * *   (日常: 每天7点/20点各跑一次, 覆盖签到/任务中心/话费红包, 且顺带捡漏话费券)

话费入口说明 (2026-09-17 实测):
   ① 签到区话费红包  = 唯一"真话费"资产, 由签到区任务中心浏览类任务累积 (每任务 0.01~0.03元)
   ② 抢兑话费券      = 1/3/5/10/18元 话费充值抵扣券, 兑换币 100=1元, 需在联通APP充值50元+才可抵扣
   ③ 其它模块 (权益超市抽奖/沃云手机积分/云盘抽奖/天天领现金) 奖池内均无话费, 不必指望

账户明细推送口径 (2026-10-06 改):
   兑换记录只打印/推送【本月】的条目; 9 月及更早的记录不再输出 (避免往月记录反复占用推送)

From: YaoHuo8648
Email: zheyizzf@188.com
Update: 2026.03.31
"""
import os
import sys
import json
import time
import random
import re
import hashlib
import hmac
import base64
# 自动检查并安装依赖
def _ensure_deps():
    missing = []
    try: import requests
    except: missing.append("requests")
    try: from Crypto.Cipher import AES
    except: missing.append("pycryptodome")
    if missing:
        print(f"正在安装依赖: {', '.join(missing)} ...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
        print("依赖安装完成")
_ensure_deps()
import logging
import requests
import uuid
import string
import tempfile
from datetime import datetime, timedelta
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass
from urllib.parse import urlparse, parse_qs, urlencode, unquote, quote
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad, unpad
# ========================================
# 全局配置 (globalConfig)
# true=开启, false=关闭
# ========================================
globalConfig = {
    # --- 1. 功能总开关 (True=开启, False=关闭) ---
    "enable_sign": True,          # 首页签到 (🔺总开关, 含签到/任务/抢话费券)
    "enable_ttlxj": True,         # 天天领现金
    "enable_ttxc": True,         # 通通乡村 (碳能量/签到/农场任务)
    "enable_ltzf": True,          # 联通祝福
    "enable_woread": True,        # 联通阅读
    "enable_security": True,      # 安全管家
    "enable_ltyp": True,          # 联通云盘
    "enable_market": True,        # 权益超市 (🔺总开关, 必须开启内部功能才能运行)
    "enable_aiting": True,        # 联通爱听
    "enable_wostore": True,       # 沃云手机
    "enable_regional": True,      # 区域专区
    "enable_flow": True,          # 流量查询 (主卡套餐总用量 + 各副卡/亲情卡用量)
    "enable_islandwaves": True,   # 披荆斩棘2026·海岛逐浪应援 (云盘活动: 转存海报/签到/抽奖)
    "enable_cloud_benefit": True, # 云盘「不限次数」权益活动 (39 权益大放送-山东海南 / 41 权益放送-上海重庆)

    # --- ✅ 签到区内部细分开关 ---
    "sign_config": {
        "run_grab_coupon": True,  # True = 开启抢话费券 (每天 10:00 / 18:00 两场, 面额由 UNICOM_GRAB_AMOUNTS 决定)
    },

    # --- 🛒 权益超市内部细分开关 (按需修改到这里) ---
    "market_config": {
        "run_water": False,        # False = 关闭浇水
        "run_task": True,         # False = 关闭做任务(浏览/分享)
        "run_member_center": True, # False = 关闭浏览会员中心得积分
        "run_draw": True,         # True  = 开启抽奖
        "run_claim": True,       # True  = 开启自动领奖(建议开启, 不领白不领)
    },

    # --- 🏷️ 区域专区内部细分开关 ---
    "regional_config": {
        "run_ah_friday": True,    # True = 开启安徽超级星期五 (需配合 UNICOM_AH_FRIDAY_AMOUNT 设置面额)
    },

    # --- 2. 设备ID配置 ---
    "refresh_device_id": False,   # False:使用缓存ID, True:强制刷新
}
COMMON_CONSTANTS = {
    "UA": "Dalvik/2.1.0 (Linux; U; Android 12; Mi 10 Pro MIUI/21.11.3);unicom{version:android@11.0802}",
    "MARKET_UA": "Dalvik/2.1.0 (Linux; U; Android 12; Mi 10 Pro MIUI/21.11.3);unicom{version:android@11.0802}",
    "MARKET_H5_UA": "Mozilla/5.0 (Linux; Android 10; MI 8 Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/143.0.7499.146 Mobile Safari/537.36; unicom{version:android@11.0802,desmobile:0};devicetype{deviceBrand:Xiaomi,deviceModel:MI 8}",
    "APP_VERSION": "android@11.0802",
}
MARKET_MEMBER_CENTER_PAGE_ID = "s782351687947921408"
MARKET_MEMBER_CENTER_DISTRIBUTE_ID = "D1161369893988319232"
MARKET_MEMBER_CENTER_PARTNERS_ID = "1703"
MARKET_MEMBER_CENTER_CLIENT_TYPE = "marketUnicom"
MARKET_MEMBER_CENTER_TASK_CODE = "s769153426294495232"
XJ_ACTIVITY_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
XJ_ACTIVITY_YEAR = os.environ.get("XJ_ACTIVITY_YEAR", str(datetime.now().year))
XJ_ACTIVITY_MONTH = os.environ.get("XJ_ACTIVITY_MONTH", XJ_ACTIVITY_MONTHS[datetime.now().month - 1])
XJ_ACTIVITY_ID = f"{XJ_ACTIVITY_MONTH}{XJ_ACTIVITY_YEAR}Act"
XJ_MONTHLY_DRAW_ATTEMPT_COUNT = max(int(os.environ.get("UNICOM_ATTEMPT_COUNT", "1") or "1"), 1)
XJ_USER_AGENT = os.environ.get(
    "XJ_USER_AGENT",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_2 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Mobile/15E148 unicom{version:iphone_c@12.0701};ltst;OSVersion/16.2"
)
UNICOM_CLOUD_UPLOAD_TIMEOUT = int(os.environ.get("UNICOM_CLOUD_UPLOAD_TIMEOUT", "120") or "120")
UNICOM_CLOUD_UPLOAD_PROGRESS_BYTES = int(os.environ.get("UNICOM_CLOUD_UPLOAD_PROGRESS_BYTES", "6376590") or "6376590")
# 云盘 /activity/lottery 抽奖验签密钥 (body 内 HMAC-SHA256 签名, 必须先取 getTimestamp 的 nonce)
CLOUD_LOTTERY_SECRET = os.environ.get("UNICOM_CLOUD_LOTTERY_SECRET", "s8Hf3LqP9xN2vM5bR7tY1wZ4cA6eG0K")
CLOUD_LOTTERY_TS_KEY = os.environ.get("UNICOM_CLOUD_LOTTERY_TS_KEY", "activity:lottery")

# ---------- 云盘「不限次数」权益活动 (2026-09-19 接入) ----------
# 已实测的两个活动: 39 = Mzk= (权益大放送-山东海南) / 41 = NDE= (权益放送-上海重庆)
# 特征: /activity/lottery/lottery-times 恒返回 result:-1 (=不限次数), 每抽必中
#       奖品为「5G宽视界」包月卡类权益 (prizeType=10, 带 benefitDesc / pathUseNotice)
# ⚠️ 原 draw_lottery_cloud() 把 -1 当作"没有次数"直接 return, 所以这两个活动一直没被抽到
CLOUD_BENEFIT_ENABLE = os.environ.get("UNICOM_CLOUD_BENEFIT_ENABLE", "1").strip().lower() not in ("0", "false", "no", "off", "")
# 每个权益活动抽几次 (不限次数活动, 默认 3 次以免刷太狠)
CLOUD_BENEFIT_DRAW_TIMES = max(int(os.environ.get("UNICOM_CLOUD_BENEFIT_DRAW_TIMES", "3") or "3"), 0)
# 抽奖间隔秒数
CLOUD_BENEFIT_INTERVAL = float(os.environ.get("UNICOM_CLOUD_BENEFIT_INTERVAL", "1.2") or "1.2")
# 留空 = 自动发现(探测存活活动里 times<0 的); 也可手填, 逗号分隔的 base64 活动码, 如 "Mzk=,NDE="
CLOUD_BENEFIT_ACTIVITY_IDS = [x.strip() for x in os.environ.get(
    "UNICOM_CLOUD_BENEFIT_ACTIVITY_IDS", "").replace("，", ",").split(",") if x.strip()]

# ---------- 披荆斩棘2026 · 海岛逐浪应援 (联通云盘活动, 2026-09-18 接入) ----------
# 活动页: https://panservice.mail.wo.cn/h5/activitymobile/cmf2026/share?activityId=NDA=&touchpoint=300500030006
ISLAND_WAVES_BASE = "https://panservice.mail.wo.cn"
# ⚠️ activityId 就是 URL 里那个 base64 串, 原样传, 不要解成 40
ISLAND_WAVES_ACT_ID = os.environ.get("UNICOM_ISLANDWAVES_ACT_ID", "NDA=")
# getTimestamp 的活动专属 key (与云盘抽奖的 activity:lottery 不同)
ISLAND_WAVES_TS_KEY = os.environ.get("UNICOM_ISLANDWAVES_TS_KEY", "activity:island:activate")
ISLAND_WAVES_TOUCHPOINT = os.environ.get("UNICOM_ISLANDWAVES_TOUCHPOINT", "300500030006")
# ⚠️ 第1关「转存海报」要把登顶值永久助力给某位哥哥(官方原文: 不可更改哥哥及取消共享),
#    所以这里只能由用户自己选定; 留空则跳过第1关(签到会因未过第一关而失败)
ISLAND_WAVES_TARGET = os.environ.get("UNICOM_ISLANDWAVES_TARGET", "余文乐")

# 通通乡村 (epay 碳能量小游戏: 签到/任务/农场)
TTXC_BASE_URL = "https://epay.10010.com/cu-ca-game-front"
TTXC_APP_BASE_URL = "https://epay.10010.com/cu-ca-app-front"
TTXC_CHANNEL = "225"
TTXC_REFERER = "https://epay.10010.com/cu-ca-game-web/index.html?channel=qdqp"
TTXC_GARBAGE_WAIT_SECONDS = int(os.environ.get("UNICOM_TTXC_GARBAGE_WAIT", "28") or "28")
TTXC_GROW_MAX_CHARGE_PER_LAND = int(os.environ.get("UNICOM_TTXC_GROW_MAX_CHARGE_PER_LAND", "20") or "20")
TTXC_HARVEST_WAIT_SECONDS = int(os.environ.get("UNICOM_TTXC_HARVEST_WAIT", "3") or "3")
TTXC_NEWBIE_STEPS = ["G01", "G02", "G03", "G03_2", "G04", "G05", "G09", "G10", "G11", "G12"]
# ============ 沃云手机 (uphone.wostore.cn / h5forphone.wostore.cn) ============
# 活动码按月轮换, 默认值为 2026-09 实测存活的 4 个码; 运行时用 wostore_discover_live_codes() 自动发现
WOSTORE_CLOUD_TIMEOUT = int(os.environ.get("UNICOM_WOSTORE_TIMEOUT", "20") or "20")
WOSTORE_CLOUD_SIGN_CODE = os.environ.get("UNICOM_WOSTORE_SIGN_CODE", "Points_Sign_2507")
WOSTORE_CLOUD_ACTIVITY_CODES = [x.strip() for x in os.environ.get(
    "UNICOM_WOSTORE_ACTIVITY_CODES", "Points_Obtain_2507").split(",") if x.strip()]
WOSTORE_LOTTERY_ACTIVITY_CODES = [x.strip() for x in os.environ.get(
    "UNICOM_WOSTORE_LOTTERY_ACTIVITY_CODES", "HD2026062200218").split(",") if x.strip()]
WOSTORE_POINTS_ACT_CODE = os.environ.get("UNICOM_WOSTORE_POINTS_ACT_CODE", "Points_Exchange_2507")
WOSTORE_CLOUD_LOGIN_ACTIVITY_ID = os.environ.get("UNICOM_WOSTORE_LOGIN_ACTIVITY_ID", "HD2026062200218")
# 积分兑换: 逗号分隔 goodsId; 留空 = 只打印可兑换菜单, 不自动兑换
WOSTORE_EXCHANGE_ENABLE = os.environ.get("UNICOM_WOSTORE_EXCHANGE_ENABLE", "1").strip() not in ("0", "false", "False", "")
WOSTORE_EXCHANGE_GOODS = [x.strip() for x in os.environ.get("UNICOM_WOSTORE_EXCHANGE_GOODS", "").split(",") if x.strip()]
WOSTORE_EXCHANGE_KEEP_POINTS = int(os.environ.get("UNICOM_WOSTORE_EXCHANGE_KEEP", "0") or "0")
WOCARE_CONSTANTS = {
	"serviceLife": "wocareMBHServiceLife1",
	"anotherApiKey": "beea1c7edf7c4989b2d3621c4255132f",
	"anotherEncryptionKey": "f4cd4ffeb5554586acf65ba7110534f5",
	"minRetries": "1"
}
WOCARE_ACTIVITIES = [
	{"name": "星座配对", "id": 2},
	{"name": "大转盘", "id": 3},
	{"name": "盲盒抽奖", "id": 4}
]
AITING_BASE_URL = "https://pcc.woread.com.cn"
AITING_SIGN_KEY_APPKEY = "7ZxQ9rT3wE5sB2dF"
AITING_SIGN_KEY_API = "woread!@#qwe1234"
AITING_SIGN_KEY_REQUERTID = "46iCw24ewAZbNkK6"
AITING_CLIENT_KEY = "1"
AITING_AES_KEY = "j2K81755sxV12wFx"
AITING_AES_IV = "16-Bytes--String"
WOREAD_KEY = "woreadst^&*12345"
ADDREADTIME_AES_KEY = "UNS#READDAY39COM"
YUNNAN_LIFE_BASE_URL = "https://wsm.wx.yn10010.com"
YUNNAN_LIFE_ACT_ID = "47191519589909"
YUNNAN_LIFE_SIGN_SALT = "ltynsh@sd23kjkgj2mbnfa0"
YUNNAN_LIFE_ACCESS_KEY = "ltynsh"
YUNNAN_LIFE_TO_URL = "https://wsm.wx.yn10010.com/micropage/orderPages/newYear/2025newYearsDay?channelId=1001010"
YUNNAN_LIFE_TASKS = [
    {"taskName": "每日签到", "taskCode": "DAILY_SIGN"},
    {"taskName": "浏览年终大回馈,好礼多多", "taskCode": "BROWSE_5TOWNS"},
]
GRAB_AMOUNT = os.environ.get("UNICOM_GRAB_AMOUNT", "5")


def parse_grab_amounts(raw, default=("5",)):
    """解析抢兑面额列表: '5' / '5,10' / '5 10' / '5;10' -> [5,10] (降序, 去重)"""
    if raw is None or str(raw).strip() == "":
        raw = ",".join(default)
    out = []
    for part in re.split(r"[,;\s|/]+", str(raw)):
        part = part.strip()
        if part.isdigit():
            v = int(part)
            if v > 0 and v not in out:
                out.append(v)
    return sorted(out, reverse=True)


# 抢兑可接受的面额池 (降序=优先抢大额; 库存不足时自动降级)
GRAB_AMOUNTS = parse_grab_amounts(os.environ.get("UNICOM_GRAB_AMOUNTS", ""), (str(GRAB_AMOUNT),))
GRAB_FALLBACK = os.environ.get("UNICOM_GRAB_FALLBACK", "1").strip().lower() not in ("0", "false", "no")
# 抢兑场次开始后仍可尝试的秒数 (窗口内随时可抢, 但库存先到先得)
GRAB_WINDOW_GRACE = int(os.environ.get("UNICOM_GRAB_WINDOW_GRACE", "30") or "30")
# 单档面额最大冲击次数
GRAB_ATTEMPTS = int(os.environ.get("UNICOM_GRAB_ATTEMPTS", "8") or "8")


def _env_int(name, default):
    """读整型环境变量: 未设置/空 -> default; 非法 -> default"""
    v = os.environ.get(name)
    if v is None or str(v).strip() == "":
        return default
    try:
        return int(str(v).strip())
    except Exception:
        return default

# ---------- 海岛逐浪应援 · 第3步「芒果 AI 入戏」(移植自上游 v1.2.0) ----------
# 模板与素材 FID 是海岛逐浪活动专用（已下线的乘风用的是另一套）
ISLAND_AI_ENABLE = os.environ.get("UNICOM_ISLAND_AI_ENABLE", "1").strip() not in ("0", "false", "False", "")
ISLAND_AI_TEMPLATE_ID = os.environ.get("UNICOM_ISLAND_AI_TEMPLATE_ID", "2097593536866250752")
ISLAND_AI_IMG_FID = os.environ.get(
    "UNICOM_ISLAND_AI_IMG_FID",
    "pKPC6_6Z2fplLfkZ/vMTfjpZKo/VOKdkYe5CIZtnnkh1R1BrpUdK+X6YenhkNURCorNuZf",
)
ISLAND_AI_MGTV_BASE = os.environ.get("UNICOM_ISLAND_AI_MGTV_BASE", "https://mgcact.api.mgtv.com")
# 芒果侧对同一素材有短时频控（多账号连跑时只有第 1 个通过）→ 失败后等待重试
# 设 UNICOM_ISLAND_AI_RETRY_TIMES=0 可关掉这个兜底
ISLAND_AI_RETRY_TIMES = max(0, _env_int("UNICOM_ISLAND_AI_RETRY_TIMES", 2))
ISLAND_AI_RETRY_WAIT = max(0, _env_int("UNICOM_ISLAND_AI_RETRY_WAIT", 40))


# 每月最多成功抢兑几张话费券 (0 = 不限; 默认 1 = 本月已抢到就跳过, 免得白费兑换币)
GRAB_MONTHLY_MAX = _env_int("UNICOM_GRAB_MONTHLY_MAX", 1)
AH_FRIDAY_AMOUNT = os.environ.get("UNICOM_AH_FRIDAY_AMOUNT", "")
AH_FRIDAY_BASE_URL = "http://123.138.11.116:8080"
AH_FRIDAY_SECKILL_TIMES = int(os.environ.get("UNICOM_AH_FRIDAY_TIMES", "50") or "50")
AH_FRIDAY_INTERVAL = float(os.environ.get("UNICOM_AH_FRIDAY_INTERVAL", "0.3") or "0.3")
UNICOM_TOKEN_CACHE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "unicom_token_cache.json")
if "UNICOM_PROXY_API" not in os.environ:
    os.environ.pop("http_proxy", None)
    os.environ.pop("https_proxy", None)
    os.environ.pop("HTTP_PROXY", None)
    os.environ.pop("HTTPS_PROXY", None)
LOGIN_PUB_KEY = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDc+CZK9bBA9IU+gZUOc6FUGu7yO9WpTNB0PzmgFBh96Mg1WrovD1oqZ+eIF4LjvxKXGOdI79JRdve9NPhQo07+uqGQgE4imwNnRx7PFtCRryiIEcUoavuNtuRVoBAm6qdB0SrctgaqGfLgKvZHOnwTjyNqjBUxzMeQlEC2czEMSwIDAQAB
-----END PUBLIC KEY-----"""

def mask_str(s):
    try:
        s = str(s)
        if len(s) == 11 and s.isdigit():
            return s[:3] + "****" + s[7:]
        elif s.startswith("enc_"):
            return s
        elif len(s) > 11:
            return s[:6] + "******" + s[-6:]
        return s
    except:
        return s


def safe_int(value, default=0):
    try:
        return int(str(value).strip())
    except Exception:
        return default


def pretty_json(data):
    """格式化 JSON 便于日志输出"""
    try:
        return json.dumps(data, ensure_ascii=False, indent=2, default=str)
    except Exception:
        return str(data)


def response_summary(data):
    """从接口响应里提取可读的错误摘要"""
    if not isinstance(data, dict):
        return str(data)
    meta = data.get("meta")
    source = meta if isinstance(meta, dict) else data
    code = source.get("code") or source.get("resultCode") or source.get("rsp_code")
    msg = (source.get("message") or source.get("msg") or source.get("desc")
           or source.get("resultMsg") or source.get("rsp_desc"))
    if msg:
        return str(msg)
    if code:
        return "接口返回异常(%s)" % code
    return "接口返回异常"


def format_flow(value, unit="MB"):
    """流量数值格式化: 30720(MB) -> 30.00GB, 723.85(MB) -> 723.85MB"""
    try:
        val = float(str(value).strip())
    except Exception:
        return str(value)
    if str(unit or "MB").strip().upper() == "KB":
        val = val / 1024.0
    if abs(val) >= 1024:
        return "%.2fGB" % (val / 1024.0)
    return "%.2fMB" % val


def wostore_month_variants(code, prefix, span=2):
    """由 Points_Obtain_2507 这类月度码生成相邻月份的候选码"""
    m = re.search(r"(\d{2})(\d{2})$", str(code or ""))
    if not m:
        return [code] if code else []
    yy, mm = int(m.group(1)), int(m.group(2))
    out = []
    for d in range(0, span + 1):
        for sign in ((0,) if d == 0 else (-d, d)):
            t = yy * 12 + (mm - 1) + sign
            y2, m2 = divmod(t, 12)
            out.append("%s%02d%02d" % (prefix, y2, m2 + 1))
    return out

class FailoverSession:
    """包装 requests.Session，自动为所有请求添加代理故障转移"""
    RETRIABLE_KEYWORDS = ("Max retries exceeded", "timed out", "connection", "SOCKS", "ProxyError", "ConnectionError")

    def __init__(self, session, owner):
        self._session = session
        self._owner = owner  # UserService 实例引用

    def __getattr__(self, name):
        return getattr(self._session, name)

    def _should_failover(self, err_msg):
        if not os.environ.get("UNICOM_PROXY_API"):
            return False
        err_lower = err_msg.lower()
        return any(kw.lower() in err_lower for kw in self.RETRIABLE_KEYWORDS)

    def _has_streaming_payload(self, kwargs):
        if kwargs.get("files"):
            return True
        data = kwargs.get("data")
        return hasattr(data, "read")

    def request(self, method, url, **kwargs):
        try:
            return self._session.request(method, url, **kwargs)
        except Exception as e:
            if self._should_failover(str(e)):
                self._owner.log(f"⚠️ [自动故障转移] {url} 请求异常: {e}")
                self._owner.failover_proxy()
                if self._has_streaming_payload(kwargs):
                    raise
                return self._session.request(method, url, **kwargs)
            raise

    def get(self, url, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self.request("POST", url, **kwargs)

class UserService:
    def __init__(self, index, config_str):
        self.index = index
        self.valid = False
        self.notify_logs = []
        # 本机是不是主卡: None=未判定, True=主卡, False=副卡/亲情卡
        # 由 queryFlowUsage() 在流量接口里判定; do_notify() 用它把主卡账号整段排到推送最前
        self.is_main_card = None
        raw_session = requests.Session()
        import socket

        class SourceAddressAdapter(HTTPAdapter):

            def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
                pool_kwargs['source_address'] = ('0.0.0.0', 0)
                super(SourceAddressAdapter, self).init_poolmanager(connections, maxsize, block, **pool_kwargs)

            def get_connection(self, url, proxies=None):
                return super(SourceAddressAdapter, self).get_connection(url, proxies)
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        adapter = SourceAddressAdapter(max_retries=retries)
        raw_session.mount('http://', adapter)
        raw_session.mount('https://', adapter)
        raw_session.headers.update({
            "User-Agent": COMMON_CONSTANTS["UA"],
            "Connection": "keep-alive"
        })
        raw_session.verify = False
        import urllib3
        urllib3.disable_warnings()
        self.session = FailoverSession(raw_session, self)
        self.account_mobile = ""
        self.mobile = ""
        self.account_password = ""
        self.token_online = ""
        self.token_refresh = ""
        self.cookie = ""
        self.appId = ""
        self.city_info = []
        self.last_read_submission_time = 0
        if globalConfig.get("refresh_device_id", False):
            self.uuid = str(uuid.uuid4()).replace('-', '')
        else:
            self.uuid = os.environ.get("chinaUnicomUuid") or str(uuid.uuid4()).replace('-', '')
        self.unicomTokenId = self.random_string(32)
        self.tokenId_cookie = "chinaunicom-" + self.random_string(32, string.ascii_uppercase + string.digits)
        self.ecs_token = ""
        self.rptId = ""
        self.sec_ai_share_key = ""
        self.sec_share_task_code = ""
        self.sec_share_task_name = "联通助理-分享AI助手对话"
        self.sec_pending_claim_tasks = {}
        self.init_account(config_str)

    def _parse_proxy_response(self, text):
        """解析代理API响应，支持JSON和文本格式，提取ip/port/user/pass"""
        text = text.strip()

        def extract(d):
            if not d or not d.get('ip') or not d.get('port'):
                return None
            return {
                'ip': str(d['ip']),
                'port': int(d['port']),
                'user': str(d.get('account') or d.get('user') or ''),
                'pass': str(d.get('password') or d.get('pass') or '')
            }
        try:
            json_start = text.find('{')
            json_end = text.rfind('}')
            if json_start != -1 and json_end != -1:
                data = json.loads(text[json_start:json_end + 1])
                if data.get('ip') and data.get('port'):
                    return extract(data)
                if data.get('data'):
                    inner = data['data']
                    if isinstance(inner, dict) and inner.get('list') and isinstance(inner['list'], list) and len(inner['list']) > 0:
                        return extract(inner['list'][0])
                    if isinstance(inner, list) and len(inner) > 0:
                        return extract(inner[0])
                    if isinstance(inner, dict) and inner.get('ip'):
                        return extract(inner)
                if data.get('result') and isinstance(data['result'], dict) and data['result'].get('ip'):
                    return extract(data['result'])
        except:
            pass
        m = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})[:\s\t]+(\d{1,5})', text)
        if m:
            return {'ip': m.group(1), 'port': int(m.group(2)), 'user': '', 'pass': ''}
        return None

    def configure_proxy(self):
        proxy_api = os.environ.get("UNICOM_PROXY_API")
        if not proxy_api:
            return
        proxy_type = os.environ.get("UNICOM_PROXY_TYPE", "socks5").lower()
        max_retries = 5
        for attempt in range(1, max_retries + 1):
            try:
                if attempt > 1:
                    self.log(f"🔄 [第{attempt}次] 重试获取代理IP ({proxy_type})...")
                    time.sleep(2)
                else:
                    self.log(f"正在获取代理IP (模式: {proxy_type})...")
                res = requests.get(proxy_api, timeout=10)
                if res.status_code != 200:
                    self.log(f"⚠️ 获取代理失败: HTTP {res.status_code}")
                    continue
                proxy_info = self._parse_proxy_response(res.text)
                if not proxy_info:
                    preview = res.text[:100] + "..." if len(res.text) > 100 else res.text
                    self.log(f"❌ 提取失败: 无法识别代理格式 (内容: {preview})")
                    continue
                ip, port = proxy_info['ip'], proxy_info['port']
                user, pwd = proxy_info['user'], proxy_info['pass']
                if user and pwd:
                    proxy_url = f"{proxy_type}://{quote(user)}:{quote(pwd)}@{ip}:{port}"
                    log_msg = f"{proxy_type}://***:***@{ip}:{port}"
                else:
                    proxy_url = f"{proxy_type}://{ip}:{port}"
                    log_msg = proxy_url
                self.log(f"🔍 提取成功: {log_msg}")
                test_proxies = {"http": proxy_url, "https": proxy_url}
                try:
                    requests.get("https://www.baidu.com", proxies=test_proxies, timeout=3)
                    self.session.proxies.update(test_proxies)
                    self.log("✅ 代理连通性测试通过")
                    return
                except Exception as te:
                    self.log(f"⚠️ 代理测试失败: {te}")
            except Exception as e:
                self.log(f"❌ 请求代理API异常: {e}")
        self.log(f"🚫 重试{max_retries}次均失败，回退至本地IP")

    def failover_proxy(self):
        proxy_api = os.environ.get("UNICOM_PROXY_API")
        if not proxy_api:
            return False
        self.log("⚠️ [故障转移] 检测到网络不稳定，正在检查当前代理是否存活...")
        try:
            requests.get("https://www.baidu.com", proxies=self.session.proxies, timeout=3)
            self.log("✅ [故障转移] 经测试当前IP仍有效，继续复用，暂不提取新IP。")
            time.sleep(1)
            return True
        except Exception as e:
            self.log(f"❌ [故障转移] 当前代理已失效 ({e})，准备更换新IP...")
        time.sleep(2)
        self.configure_proxy()
        return True

    def init_account(self, config_str):
        parts = config_str.split('#')
        if len(parts) >= 2 and len(parts[0]) == 11 and parts[0].isdigit() and len(parts[1]) < 50:
             self.account_mobile = parts[0]
             self.account_password = parts[1]
        else:
            self.token_online = parts[0].strip()
            if len(self.token_online) == 11 and self.token_online.isdigit():
                self.account_mobile = self.token_online
                self.token_online = "" # Reset, allow load_token_from_cache to fill it
                self.log(f"识别到纯手机号模式: {mask_str(self.account_mobile)}")
            if len(parts) > 1:
                 self.appId = parts[1].strip()
            if len(parts) > 2 and parts[2]:
                potential_mobile = parts[2].strip()
                if potential_mobile.isdigit() and len(potential_mobile)==11:
                    self.account_mobile = potential_mobile
        self.unicomTokenId = str(uuid.uuid4()).replace('-', '') # simplified
        self.tokenId_cookie = "chinaunicom-" + str(uuid.uuid4()).replace('-', '').upper() # simplified
        self.cookie_string = f"TOKENID_COOKIE={self.tokenId_cookie}; UNICOM_TOKENID={self.unicomTokenId}; sdkuuid={self.unicomTokenId}"
        self.update_session_cookies()

    def update_session_cookies(self):
        if self.cookie_string:
            cookies = {}
            for item in self.cookie_string.split(';'):
                if '=' in item:
                    k, v = item.split('=', 1)
                    cookies[k.strip()] = v.strip()
            self.session.cookies.update(cookies)
        extra_cookies = {}
        if self.token_online:
            extra_cookies['token_online'] = self.token_online
        if self.appId:
            extra_cookies['appId'] = self.appId
        if extra_cookies:
            self.session.cookies.update(extra_cookies)

    def log(self, msg, notify=False, notify_html=None):
        prefix = f"账号[{self.index}]"
        full_msg = f"{prefix}{msg}"
        log_line = f"[{datetime.now().strftime('%H:%M:%S')}] {full_msg}"
        print(log_line)
        if notify:
            self.notify_logs.append(str(msg))
        if notify_html:
            self.notify_logs.append(str(notify_html))

    def request_direct(self, method, url, **kwargs):
        session = requests.Session()
        session.trust_env = False
        session.verify = False
        try:
            return session.request(method, url, **kwargs)
        finally:
            session.close()

    def rsa_encrypt(self, val):
        self.log(f"正在进行 RSA 加密...")
        try:
             random_str = ''.join(str(random.randint(0, 9)) for _ in range(6))
             text = str(val) + random_str
             data = text.encode('utf-8')
             key_pem = LOGIN_PUB_KEY.encode()
             recipient_key = RSA.import_key(key_pem)
             cipher_rsa = PKCS1_v1_5.new(recipient_key)
             enc_data = cipher_rsa.encrypt(data)
             return base64.b64encode(enc_data).decode('utf-8')
        except Exception as e:
            self.log(f"RSA加密失败: {str(e)}")
            return ""

    def generate_appid(self):

        def rnd(): return str(random.randint(0, 9))
        return (f"{rnd()}f{rnd()}af"
                f"{rnd()}{rnd()}ad"
                f"{rnd()}912d306b5053abf90c7ebbb695887bc"
                f"870ae0706d573c348539c26c5c0a878641fcc0d3e90acb9be1e6ef858a"
                f"59af546f3c826988332376b7d18c8ea2398ee3a9c3db947e2471d32a49") + rnd() + rnd()

    def unicom_login(self):
        self.log(f"正在使用账号 {mask_str(self.account_mobile)} 进行登录...")
        if not self.appId:
            self.appId = self.generate_appid()
            self.log(f"生成临时 AppId: {self.appId[:15]}...")
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            payload = {
                "version": COMMON_CONSTANTS["APP_VERSION"],
                "mobile": self.rsa_encrypt(self.account_mobile),
                "reqtime": timestamp,
                "deviceModel": "Android",
                "netWay": "Wifi",
                "isR4": "0",
                "password": self.rsa_encrypt(self.account_password),
                "appId": self.appId
            }
            url = "https://m.client.10010.com/mobileService/login.htm"
            res = self.session.post(url, data=payload)
            result = res.json()
            if result.get('code') in ['0', '0000']:
                if result.get('token_online'):
                    self.token_online = result['token_online']
                    self.log("✅ 登录接口验证通过")
                    return True
                else:
                    self.log("❌ 登录响应中未找到 token_online")
            else:
                self.log(f"❌ 登录失败: {result.get('desc')} (Code: {result.get('code')})")
        except Exception as e:
            self.log(f"❌ 登录过程异常: {str(e)}")
        return False

    def request(self, method, url, **kwargs):
        try:
            current_cookies = self.session.cookies.get_dict()
            if self.cookie_string:
                for item in self.cookie_string.split(';'):
                    if '=' in item:
                        k, v = item.split('=', 1)
                        current_cookies[k.strip()] = v.strip()
            cookie_header = "; ".join([f"{k}={v}" for k, v in current_cookies.items()])
            if cookie_header:
                if 'headers' not in kwargs:
                    kwargs['headers'] = {}
                kwargs['headers']['Cookie'] = cookie_header
            timeout = kwargs.get('timeout', 10)
            if 'timeout' in kwargs: del kwargs['timeout']
            response = self.session.request(method, url, timeout=timeout, **kwargs)
            if response.status_code >= 400:
                self.log(f"请求 {url} 返回状态码 {response.status_code}")
            return response
        except Exception as e:
            self.log(f"请求 {url} 异常: {str(e)}")
            return None

    def load_token_from_cache(self):
        if not self.account_mobile:
            return False
        if not os.path.exists(UNICOM_TOKEN_CACHE_PATH):
            return False
        try:
            with open(UNICOM_TOKEN_CACHE_PATH, 'r', encoding='utf-8') as f:
                cache = json.load(f)
            user_cache = cache.get(self.account_mobile)
            if user_cache and user_cache.get('token_online'):
                if (datetime.now().timestamp() * 1000) - user_cache.get('timestamp', 0) < 12 * 60 * 60 * 1000:
                    self.token_online = user_cache['token_online']
                    self.appId = user_cache.get('appId', self.appId)
                    self.city_info = user_cache.get('city_info', [])
                    self.update_session_cookies()
                    self.log(f"♻️ [缓存复用] 成功加载本地 Token ({user_cache.get('time')})")
                    return True
        except Exception as e:
            pass
        return False

    def save_token_to_cache(self):
        if not self.account_mobile:
            return
        cache = {}
        if os.path.exists(UNICOM_TOKEN_CACHE_PATH):
             try:
                with open(UNICOM_TOKEN_CACHE_PATH, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
             except: pass
        now = datetime.now()
        cache[self.account_mobile] = {
            "token_online": self.token_online,
            "appId": self.appId,
            "city_info": getattr(self, 'city_info', []),
            "cookieString": "",
            "timestamp": int(now.timestamp() * 1000),
            "time": now.strftime('%Y-%m-%d %H:%M:%S')
        }
        try:
            with open(UNICOM_TOKEN_CACHE_PATH, 'w', encoding='utf-8') as f:
                json.dump(cache, f, indent=2, ensure_ascii=False)
            self.log("💾 [缓存保存] Token 已写入本地文件")
        except Exception as e:
            self.log(f"❌ 保存缓存失败: {str(e)}")

    def get_city_info(self):
        try:
            url = "https://m.client.10010.com/mobileService/business/get/getCity"
            res = self.session.post(url, data={}, timeout=10).json()
            if res.get('code') == '200' and res.get('list'):
                 self.city_info = res.get('list')
                 return True
            return False
        except:
            return False

    def queryRemain(self):
        try:
            if not self.ecs_token:
                if not self.onLine():
                    self.log("❌ 无法获取 ecs_token，跳过查询")
                    return
            self.log("==== 资产查询 ====")
            self.log("正在查询套餐余量...")
            url = "https://m.client.10010.com/servicequerybusiness/balancenew/accountBalancenew.htm"
            headers = {
                "User-Agent": COMMON_CONSTANTS["MARKET_UA"],
                "Cookie": f"ecs_token={self.ecs_token}"
            }
            res = self.request("get", url, headers=headers)
            if not res: return
            result = res.json()
            if result.get('code') == '0000':
                current_balance = "0.00"
                real_time_fee = "0.00"
                if result.get('curntbalancecust'):
                    current_balance = str(result['curntbalancecust'])
                if result.get('realfeecust'):
                    real_time_fee = str(result['realfeecust'])
                fee_line = f"💰 [资产-话费] 当前余额: {current_balance}元, 实时话费: {real_time_fee}元"
                # 只传 notify_html: notify=True 和 notify_html 是两条独立入队分支, 同时传会重复推两遍
                self.log(fee_line, notify_html=f'<font color="#ff0000">{fee_line}</font>')
                pkg_list = result.get('realTimeFeeSpecialFlagThree', [])
                if pkg_list and isinstance(pkg_list, list):
                    self.log(f"    📋 [套餐详情]:", notify=True)
                    for item in pkg_list:
                        sub_items = item.get('subItems', [])
                        if sub_items:
                            for sub in sub_items:
                                bill = sub.get('bill', {})
                                if bill:
                                    name = bill.get('integrateitem', '未知项')
                                    fee = bill.get('realfee', '0.00')
                                    self.log(f"       - {name}: {fee}元", notify=True)
            else:
                msg = result.get('desc') or result.get('msg') or "未知错误"
                self.log(f"套餐余量查询失败: {msg}")
        except Exception as e:
            self.log(f"queryRemain 异常: {str(e)}")
        finally:
            # 🔺 流量查询 (话费之后第二个资产项)
            if globalConfig.get("enable_flow", True):
                try:
                    self.queryFlowUsage()
                except Exception as e:
                    self.log(f"流量查询异常: {e}")

    def queryFlowUsage(self):
        """流量查询 (2026-09-17 实测存活):
        主卡套餐总用量 + 各号码(副卡/亲情卡)用量 + 流量包明细

        接口: POST m.client.10010.com/servicequerybusiness/operationservice/queryOcsPackageFlowLeftContentRevisedInJune
          - resources[0].userResource        = 账户流量总用量
          - resources[*].details[*]           = 各流量包 {feePolicyName, addUpItemName, use, total, usedPercent, elemType}
                                               elemType=3 流量 / elemType=1 语音(单位分钟, 不参与汇总)
          - resources[*].details[*].viceCardlist[] = ⭐ 各号码用量 {usernumber, use, currentLoginFlag, viceCardflag}
                                               currentLoginFlag=1 → 当前登录号 (唯一可靠的按号用量来源)
          - summary.freeFlow                 = 剩余可用流量
          - canuseFlowAllUnit                = 单位 (MB)
        ⚠️ 坑: 顶层 `viceCardList`(带 use) **时有时无**(同一账号两次调用都可能不一样),
           顶层 `viceCardLits`(联通自己拼错的)只有 number/secretNumber/numberFlag, **没有用量**。
           所以按号用量必须从 `details[*].viceCardlist` 累加, 不要读顶层。
        ⚠️ 该接口是"共享池"口径: 主卡/副卡/亲情卡同属一个账户, 所以
           3 个不同号码的 CK 会拿到**同一份**成员用量 (这也解释了此前
           "余额/话费红包三号一致"的现象 —— 很可能是共享账户, 未必是串号)。
        """
        def _push(text):
            """流量行统一红色推送 (notify 与 notify_html 是两个独立入队分支, 只能传一个)"""
            self.log(text, notify_html=f'<font color="#ff0000">{text}</font>')

        try:
            if not self.ecs_token:
                if not self.onLine():
                    self.log("📶 流量查询: 无 ecs_token, 跳过")
                    return
            url = ("https://m.client.10010.com/servicequerybusiness/operationservice/"
                   "queryOcsPackageFlowLeftContentRevisedInJune")
            headers = {
                "User-Agent": COMMON_CONSTANTS["UA"],
                "Cookie": f"ecs_token={self.ecs_token}",
            }
            res = self.request("post", url, data={}, headers=headers)
            if not res:
                self.log("📶 流量查询: 无响应")
                return
            data = res.json()
            if data.get("code") != "0000":
                self.log(f"📶 流量查询失败: {response_summary(data)}")
                return

            unit = data.get("canuseFlowAllUnit") or "MB"
            pkg = data.get("packageName") or "未知套餐"

            # 收集所有流量明细 (elemType=3 才是流量; elemType=1 是语音, 单位是分钟)
            flow_items = []
            for group in (data.get("resources") or []):
                for it in (group.get("details") or []):
                    if str(it.get("elemType")) == "3":
                        flow_items.append(it)
            total_used = (data.get("resources") or [{}])[0].get("userResource")

            # 1) 先汇总各号码用量 + 判定"本机是不是主卡"
            #    (顶层 viceCardList 时有时无, 顶层 viceCardLits 只有号码没有用量, 都不可靠)
            #    viceCardflag=1 是该账户的主卡(实测三个号调用结果恒定), currentLoginFlag=1 是本机
            agg, order, meta = {}, [], {}
            for it in flow_items:
                for m in (it.get("viceCardlist") or []):
                    num = str(m.get("usernumber") or "")
                    if not num:
                        continue
                    if num not in agg:
                        agg[num] = 0.0
                        meta[num] = {"main": False, "login": False}
                        order.append(num)
                    try:
                        agg[num] += float(str(m.get("use") or 0).strip())
                    except Exception:
                        pass
                    if safe_int(m.get("viceCardflag"), 0) == 1:
                        meta[num]["main"] = True
                    if safe_int(m.get("currentLoginFlag"), 0) == 1:
                        meta[num]["login"] = True

            # 1.1) 🔺 流量明细只在主卡推送: 本机是副卡/亲情卡 → 静默跳过(只留控制台日志, 不进推送)
            #      实测: 副卡(亲情卡/5G副卡套餐) 本机 viceCardflag=0 → 跳过
            #            主卡(腾讯大王卡)       本机 viceCardflag=1 → 正常推送
            #      兜底: 拿不到 currentLoginFlag(单卡户/字段缺失) 时照常显示, 不误杀
            login_nums = [n for n in order if meta[n]["login"]]
            if login_nums:
                # 记下本机身份, 供 do_notify() 把主卡账号整段排到推送最前
                self.is_main_card = any(meta[n]["main"] for n in login_nums)
            if login_nums and not self.is_main_card:
                self.log(f"📶 [流量] 本机({login_nums[0]})为副卡, 流量明细统一在主卡推送, 此处跳过")
                return

            _push(f"📶 [流量] 主卡套餐: {pkg} | 账户流量合计 {format_flow(total_used, unit)}")

            if order:
                order.sort(key=lambda n: 0 if meta[n]["main"] else (1 if meta[n]["login"] else 2))
                _push(f"   👥 各号码流量用量 (共 {len(order)} 个):")
                for num in order:
                    tags = []
                    if meta[num]["main"]:
                        tags.append("主卡")
                    if meta[num]["login"]:
                        tags.append("本机")
                    tag = f" ({'/'.join(tags)})" if tags else ""
                    _push(f"       - {num}{tag}: {format_flow(agg[num], unit)}")

            # 2) 流量包明细
            if flow_items:
                _push("   📋 流量包明细:")
                for it in flow_items:
                    name = it.get("feePolicyName") or it.get("addUpItemName") or "未知流量包"
                    try:
                        tot_f = float(str(it.get("total")).strip())
                    except Exception:
                        tot_f = 0.0
                    if tot_f <= 0:
                        desc = f"已用 {format_flow(it.get('use'), unit)} (不限量/达量限速)"
                    else:
                        desc = (f"{format_flow(it.get('use'), unit)} / {format_flow(tot_f, unit)}"
                                f" (已用 {it.get('usedPercent')}%)")
                    _push(f"       - {name}: {desc}")

            # 3) 剩余可用
            try:
                free = float(str((data.get("summary") or {}).get("freeFlow")).strip())
                if free > 0:
                    _push(f"   ✅ 剩余可用流量: {format_flow(free, unit)}")
            except Exception:
                pass
        except Exception as e:
            self.log(f"queryFlowUsage 异常: {e}")

    def derive_android_id(self):
        """按账号派生稳定的 androidId（16 位 hex）。

        历史上这里是写死的一个固定值，导致所有账号共用同一个设备指纹。
        现在按 手机号 -> token -> uuid 的优先级取种子做 md5，首次算完即缓存，
        保证同一账号在整个进程生命周期内稳定，不同账号互相独立。
        """
        cached = getattr(self, "_derived_android_id", "")
        if cached:
            return cached
        seed = ((self.account_mobile or "").strip()
                or (self.token_online or "").strip()
                or (self.uuid or "").strip())
        if not seed:
            seed = str(uuid.uuid4()).replace("-", "")
        aid = hashlib.md5(("unicom-android-" + seed).encode("utf-8")).hexdigest()[:16]
        self._derived_android_id = aid
        return aid

    def onLine(self):
        if not self.token_online:
             self.log("❌ 缺少 token_online，无法执行 onLine")
             return False
        try:
            url = "https://m.client.10010.com/mobileService/onLine.htm"
            data = {
                'isFirstInstall': '1',
                'netWay': 'Wifi',
                'version': 'android@11.0000',
                'token_online': self.token_online,
                'provinceChanel': 'general',
                'deviceModel': 'ALN-AL10',
                'step': 'dingshi',
                'androidId': self.derive_android_id(),
                'reqtime': int(time.time() * 1000)
            }
            if self.appId:
                data['appId'] = self.appId
            res = self.request('post', url, data=data)
            if not res: return False
            result = res.json()
            code = result.get('code')
            if code == '0' or code == 0:
                self.valid = True
                desmobile = result.get('desmobile', '')
                if len(desmobile) == 11 and desmobile.isdigit():
                    self.account_mobile = desmobile
                    self.mobile = desmobile
                elif desmobile.startswith("enc_"):
                     if not self.account_mobile:
                          self.log("⚠️ 注意: 服务端返回了加密手机号且未配置本地手机号")
                self.log("登录成功")
                self.city_info = result.get('list', [])
                self.ecs_token = result.get('ecs_token')
                return True
            else:
                self.log(f"登录失败[{code}]: {result.get('msg')}")
                return False
        except Exception as e:
            self.log(f"onLine 异常: {str(e)}")
            return False

    def gettaskip(self):
        orderId = self.random_string(32).upper()
        try:
            url = "https://m.client.10010.com/taskcallback/topstories/gettaskip"
            data = {
                "mobile": self.account_mobile,
                "orderId": orderId
            }
            self.request("post", url, data=data)
        except Exception as e:
            pass
        return orderId

    def sign_getContinuous(self, is_query_only=False):
        try:
            url = "https://activity.10010.com/sixPalaceGridTurntableLottery/signin/getContinuous"
            params = {
                "taskId": "",
                "channel": "wode",
                "imei": self.uuid
            }
            res = self.request("get", url, params=params)
            if not res: return
            result = res.json()
            code = result.get('code')
            if code == "0000":
                todayIsSignIn = result.get('data', {}).get('todayIsSignIn', 'n')
                self.log(f"签到区今天{'已' if todayIsSignIn == 'y' else '未'}签到", notify=True)
                if todayIsSignIn == 'y':
                    pass
                else:
                    if not is_query_only:
                        time.sleep(1)
                        self.sign_daySign()
                    else:
                        self.log("签到区: [查询模式] 跳过自动打卡")
            else:
                self.log(f"签到区查询签到状态失败[{code}]: {result.get('desc', '')}")
        except Exception as e:
            self.log(f"sign_getContinuous 异常: {str(e)}")

    def sign_daySign(self):
        try:
            url = "https://activity.10010.com/sixPalaceGridTurntableLottery/signin/daySign"
            res = self.request("post", url, data={})
            if not res: return
            result = res.json()
            code = result.get('code')
            if code == "0000":
                data = result.get('data', {})
                msg = f"签到区签到成功: [{data.get('statusDesc', '')}]{data.get('redSignMessage', '')}"
                self.log(msg)
            elif code == "0002" and "已经签到" in result.get('desc', ''):
                self.log("签到区签到成功: 今日已完成签到！")
            else:
                self.log(f"签到区签到失败[{code}]: {result.get('desc', '')}")
        except Exception as e:
            self.log(f"sign_daySign 异常: {str(e)}")

    def sign_getTelephone(self, is_initial=False, silent=False):
        try:
            url = "https://act.10010.com/SigninApp/convert/getTelephone"
            res = self.request("post", url, data={})
            if not res: return None
            result = res.json()
            status = result.get('status')
            if status == "0000" and result.get('data'):
                tel_val = result['data'].get('telephone', 0)
                try:
                    current_amount = float(tel_val)
                except:
                    current_amount = 0.0
                if silent:
                    return current_amount
                if is_initial:
                    msg = f"签到区-话费红包: 运行前总额 {current_amount:.2f}元"
                    self.sign_initial_amount = current_amount
                else:
                    if hasattr(self, 'sign_initial_amount'):
                        increase = current_amount - self.sign_initial_amount
                        self.log(f"签到区-话费红包: 本次运行增加 {increase:.2f}元", notify=True)
                    msg = f"签到区-话费红包: 总额 {current_amount:.2f}元"
                    exp_val = result['data'].get('needexpNumber', 0)
                    try:
                        exp_num = float(exp_val)
                    except:
                        exp_num = 0.0
                    if exp_num > 0:
                        msg += f"，其中 {result['data'].get('needexpNumber', '0')}元 将于 {result['data'].get('month', '')}月底到期"
                self.log(msg, notify=not is_initial)
                return current_amount
            else:
                if not silent:
                    self.log(f"签到区查询话费红包失败[{status}]: {result.get('msg', '')}")
                return None
        except Exception as e:
            if not silent:
                self.log(f"sign_getTelephone 异常: {str(e)}")
            return None

    def sign_task_center_fetch(self):
        """拉取任务中心全量任务 (type=1 与 type=2 合并去重, 0329 重试)"""
        url = "https://activity.10010.com/sixPalaceGridTurntableLottery/task/taskList"
        headers = {"Referer": "https://img.client.10010.com/"}
        all_tasks, seen = [], set()
        for t in ("1", "2"):
            for attempt in range(3):
                res = self.request("get", url, params={"type": t}, headers=headers, timeout=10)
                if not res:
                    break
                try:
                    result = res.json()
                except Exception:
                    break
                code = result.get('code')
                desc = str(result.get('desc', ''))
                if code == "0329" or "火爆" in desc:
                    time.sleep(3 + attempt * 2)
                    continue
                if code != "0000":
                    if t == "1":
                        self.log(f"签到区-任务中心: 获取任务列表失败[{code}]: {desc}")
                    break
                data = result.get('data', {}) or {}
                rows = list(data.get('taskList') or [])
                for tag in (data.get('tagList') or []):
                    rows += list(tag.get('taskDTOList') or [])
                for x in rows:
                    if not x:
                        continue
                    tid = x.get('id')
                    if tid and tid not in seen:
                        seen.add(tid)
                        all_tasks.append(x)
                break
        return all_tasks

    def sign_getTaskList(self):
        """任务中心自动完成: 领奖 → 抽奖类(taskType=3) → 浏览类(taskType=5) → 第三方类(taskType=8)"""
        TASK_TYPE_NAMES = {"3": "抽奖类", "5": "浏览类", "8": "第三方App"}
        try:
            fail_ids = set()
            for _ in range(25):
                all_tasks = self.sign_task_center_fetch()
                if not all_tasks:
                    self.log("签到区-任务中心: 当前无任何任务。")
                    return
                # 1) 可领奖 (taskState=0)
                cand = next((t for t in all_tasks if str(t.get('taskState')) == '0'
                             and t.get('id') not in fail_ids), None)
                if cand:
                    self.log(f"签到区-任务中心: 发现可领取奖励的任务 [{cand.get('taskName')}]")
                    if not self.sign_getTaskReward(cand.get('id')):
                        fail_ids.add(cand.get('id'))
                    time.sleep(2)
                    continue
                # 2) 抽奖类任务 (taskType=3, 需先 completeTask 再领奖)
                cand = next((t for t in all_tasks if str(t.get('taskState')) == '1'
                             and str(t.get('taskType')) == '3' and t.get('id') not in fail_ids), None)
                if cand:
                    self.log(f"签到区-任务中心: 开始抽奖类任务 [{cand.get('taskName')}]")
                    if not self.sign_drawTaskFromList(cand):
                        fail_ids.add(cand.get('id'))
                    time.sleep(3)
                    continue
                # 3) 浏览/分享类任务 (taskType=5)
                cand = next((t for t in all_tasks if str(t.get('taskState')) == '1'
                             and str(t.get('taskType')) == '5' and t.get('id') not in fail_ids), None)
                if cand:
                    self.log(f"签到区-任务中心: 开始执行任务 [{cand.get('taskName')}]")
                    if not self.sign_doTaskFromList(cand):
                        fail_ids.add(cand.get('id'))
                    time.sleep(3)
                    continue
                # 4) 需第三方App完成的签到任务 (taskType=8) - 脚本无法代做
                third = [t for t in all_tasks if str(t.get('taskState')) == '1'
                         and str(t.get('taskType')) == '8' and t.get('id') not in fail_ids]
                if third:
                    names = "、".join(str(t.get('taskName') or '') for t in third)
                    self.log(f"签到区-任务中心: [{names}] 需前往第三方App完成, 脚本无法代做, 已跳过")
                self.log("签到区-任务中心: 所有可执行任务处理完毕。")
                return
            self.log("签到区-任务中心: 达到最大尝试次数, 结束本轮。")
        except Exception as e:
            self.log(f"sign_getTaskList 异常: {str(e)}")

    def sign_doTaskFromList(self, task):
        """浏览/分享类任务 (taskType=5): 访问 url 后提交完成. 返回是否成功"""
        try:
            if task.get('url') and task['url'] != '1' and task['url'].startswith('http'):
                 self.request("get", task['url'], headers={"Referer": "https://img.client.10010.com/"})
                 self.log(f"签到区-任务中心: 浏览页面 [{task.get('taskName')}]")
                 time.sleep(random.uniform(5, 7))
            orderId = self.gettaskip()
            url = "https://activity.10010.com/sixPalaceGridTurntableLottery/task/completeTask"
            params = {
                "taskId": task.get('id'),
                "orderId": orderId,
                "systemCode": "QDQD"
            }
            res = self.request("get", url, params=params)
            if not res: return False
            result = res.json()
            code = result.get('code')
            if code == "0000":
                self.log(f"签到区-任务中心: ✅ 任务 [{task.get('taskName')}] 已完成")
                return True
            self.log(f"签到区-任务中心: ❌ 任务 [{task.get('taskName')}] 完成失败[{code}]: {result.get('desc', '未知错误')}")
            return False
        except Exception as e:
             self.log(f"sign_doTaskFromList 异常: {str(e)}")
             return False

    def sign_drawTaskFromList(self, task):
        """抽奖类任务 (taskType=3): 先 completeTask 触发抽奖, 再领取奖励. 返回是否成功"""
        try:
            orderId = self.gettaskip()
            url = "https://activity.10010.com/sixPalaceGridTurntableLottery/task/completeTask"
            res = self.request("get", url, params={
                "taskId": task.get('id'),
                "orderId": orderId,
                "systemCode": "QDQD"
            })
            if not res:
                return False
            result = res.json()
            code = result.get('code')
            if code == "0000":
                self.log(f"签到区-任务中心: ✅ 抽奖任务 [{task.get('taskName')}] 已完成, 转入领奖")
                return True
            if code in ("0311", "0305"):
                # 0311=任务状态异常(可能已在待领取), 0305=需第三方App完成
                self.log(f"签到区-任务中心: 抽奖任务 [{task.get('taskName')}] 状态异常[{code}]: {result.get('desc', '')}")
                return True
            self.log(f"签到区-任务中心: ❌ 抽奖任务 [{task.get('taskName')}] 完成失败[{code}]: {result.get('desc', '未知错误')}")
            return False
        except Exception as e:
            self.log(f"sign_drawTaskFromList 异常: {str(e)}")
            return False

    def sign_getTaskReward(self, task_id, retries=4):
        """领取任务奖励 (0329 活动火爆自动重试). 返回是否成功"""
        try:
            url = "https://activity.10010.com/sixPalaceGridTurntableLottery/task/getTaskReward"
            for i in range(max(1, retries)):
                res = self.request("get", url, params={"taskId": task_id})
                if not res:
                    return False
                try:
                    result = res.json()
                except Exception:
                    return False
                code = result.get('code')
                if code == "0000":
                    data = result.get('data', {}) or {}
                    inner = str(data.get('code') or '')
                    if inner in ("0000", ""):
                        prize = data.get('prizeName') or data.get('prizeNameRed') or data.get('statusDesc') or "已领取"
                        self.log(f"签到区-任务中心: 🎁 领取奖励成功 [{prize}]", notify=True)
                        return True
                    desc = result.get('desc') or data.get('desc') or data.get('statusDesc') or ''
                    if inner == "0329" or "火爆" in str(desc):
                        if i < retries - 1:
                            time.sleep(3 + i * 2)
                            continue
                    self.log(f"签到区-任务中心: 领取奖励失败[{inner}]: {desc}")
                    return False
                self.log(f"签到区-任务中心: 领取奖励失败[{code}]: {result.get('desc', '')}")
                return False
            self.log(f"签到区-任务中心: 领取奖励多次重试仍繁忙, 下次运行再领")
            return False
        except Exception as e:
            self.log(f"sign_getTaskReward 异常: {str(e)}")
            return False

    @staticmethod
    def sign_grab_parse_amount(name):
        """从奖品名解析面额: '5元话费充值抵扣券' -> 5.0"""
        if not name:
            return None
        m = re.search(r'(\d+(?:\.\d+)?)\s*元', str(name))
        return float(m.group(1)) if m else None

    @staticmethod
    def sign_grab_parse_time(val):
        """兼容 '2026-09-17 10:00:00' / '2026/09/17 10:00' / '10:00' 三种写法"""
        if not val:
            return None
        val = str(val).strip()
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S",
                    "%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M"):
            try:
                return datetime.strptime(val, fmt)
            except Exception:
                continue
        try:
            t = datetime.strptime(val, "%H:%M")
            return datetime.now().replace(hour=t.hour, minute=t.minute, second=0, microsecond=0)
        except Exception:
            return None

    def sign_grab_probe_pool(self):
        """读取抢兑奖品池, 归集为候选列表. 只读, 不消耗任何资产"""
        url = "https://act.10010.com/SigninApp/new_convert/prizeList"
        headers = {"Origin": "https://img.client.10010.com"}
        cands = []
        try:
            res = self.request("post", url, headers=headers)
            if not res:
                return cands
            data = res.json()
            if data.get('status') != "0000":
                self.log(f"⚔️ [抢兑] 奖品池查询失败[{data.get('status')}]: {data.get('msg', '')}")
                return cands
            tabs = (data.get('data', {}).get('datails', {}) or {}).get('tabItems', []) or []
            for tab in tabs:
                sess_start = self.sign_grab_parse_time(tab.get('time'))
                for item in (list(tab.get('timeLimitQuanListData') or []) + list(tab.get('quanListData') or [])):
                    name = item.get('product_name', '') or ''
                    amount = self.sign_grab_parse_amount(name)
                    if amount is None or not any(k in name for k in ("话费", "充值", "抵扣券")):
                        continue
                    try:
                        stock = int(item.get('stockSurplus') or 0)
                    except Exception:
                        stock = 0
                    cands.append({
                        "id": item.get('product_id'),
                        "name": name,
                        "amount": amount,
                        "typeCode": item.get('type_code') or '0',
                        "stock": stock,
                        "cost": item.get('eb_count'),
                        "sessStart": sess_start,
                        "sessState": str(tab.get('state') or ''),
                        "endTime": self.sign_grab_parse_time(item.get('endTime')),
                    })
        except Exception as e:
            self.log(f"⚔️ [抢兑] 获取奖品池异常: {e}")
        return cands

    def sign_grab_execute(self, candidate, attempts=2, interval=0.5):
        """抢兑单档. 返回状态串:
        ok=成功  closed=场次未开/规则上限  ratelimit=触发风控  nostock=无库存  fail=其它失败  """
        headers = {
            "Origin": "https://img.client.10010.com",
            "Referer": "https://img.client.10010.com/",
            "X-Requested-With": "com.sinovatech.unicom.ui",
        }
        label = f"{candidate['amount']:g}元话费券"
        last = "fail"
        for i in range(1, max(1, attempts) + 1):
            try:
                res = self.request("post", "https://act.10010.com/SigninApp/convert/prizeConvert",
                                   data={"product_id": candidate['id'], "typeCode": candidate['typeCode']},
                                   headers=headers)
                if not res:
                    last = "fail"
                    time.sleep(interval)
                    continue
                result = res.json()
                uuid_val = (result.get('data') or {}).get('uuid')
                if result.get('status') != "0000" or not uuid_val:
                    msg = str(result.get('msg') or result.get('message') or '')
                    if any(k in msg for k in ("频繁操作", "网络环境")):
                        self.log(f"🚫 [抢兑] {label} 触发风控: {msg}")
                        return "ratelimit"
                    if any(k in msg for k in ("火爆", "上限", "结束", "未开始")):
                        return "closed"
                    self.log(f"❌ [抢兑] {label} 第{i}次提交被拒: "
                             f"{msg or json.dumps(result, ensure_ascii=False)[:120]}")
                    last = "fail"
                    time.sleep(interval)
                    continue
                # 查工单最终结果
                for _ in range(3):
                    time.sleep(0.8)
                    check = self.request("post", "https://act.10010.com/SigninApp/convert/prizeConvertResult",
                                         data={"uuid": uuid_val}, headers=headers)
                    if not check:
                        continue
                    final = check.json()
                    if final.get('status') == "0000":
                        self.log(f"🎉🎉🎉 [抢兑成功] 已抢到 {candidate['name']}! "
                                 f"(消耗 {candidate.get('cost')} 兑换币; 券有效期至 9/30, "
                                 f"需在中国联通APP充值50元+才可抵扣)", notify=True)
                        return "ok"
                    d = final.get('data') or {}
                    err = str(d.get('errorCode') or '')
                    msg = str(final.get('msg') or '')
                    rule = str((d.get('rightBtn') or {}).get('name') or '')
                    if any(k in msg for k in ("频繁操作", "网络环境")):
                        self.log(f"🚫 [抢兑] {label} 触发风控: {msg}")
                        return "ratelimit"
                    if "库存" in msg or "不足" in msg or "抢光" in msg:
                        self.log(f"📉 [抢兑] {label} 无库存: {msg}")
                        return "nostock"
                    if err in ("", "10013") and ("火爆" in msg or "上限" in rule or "结束" in msg):
                        last = "closed"
                        break
                    self.log(f"💔 [抢兑] {label} 第{i}次失败: status={final.get('status')} "
                             f"code={err or '-'} msg={msg} {rule}")
                    last = "fail"
                    break
                time.sleep(interval)
            except Exception as e:
                self.log(f"❌ [抢兑] {label} 第{i}次异常: {e}")
                last = "fail"
                time.sleep(interval)
        return last

    def sign_grab_month_count(self):
        """统计「本月」已成功抢兑的话费券张数 (只读查询, 不消耗任何资产).
        返回 >=0: 统计到的张数; 返回 -1: 查询失败 (调用方按 fail-open 处理, 照常抢)."""
        try:
            url = "https://act.10010.com/SigninApp/convert/phoneDetails"
            form = {"log_type": "1", "number": "1", "list_num": ""}
            headers = {"Origin": "https://img.client.10010.com"}
            res = self.request("post", url, data=form, headers=headers)
            if not res:
                return -1
            result = res.json()
            if result.get('status') != '0000':
                self.log(f"⚠️ [抢兑] 本月兑换记录查询失败[{result.get('status')}]: "
                         f"{result.get('msg', '')} —— 无法判断本月是否已抢, 按保守策略照常抢")
                return -1
            month = datetime.now().strftime('%Y-%m')
            cnt = 0
            for item in (result.get('data', {}).get('detailedBO') or []):
                remark = str(item.get('remark') or '')
                buss = str(item.get('from_bussname') or '')
                if "兑换" not in remark and "兑换" not in buss:
                    continue
                if not any(k in remark for k in ("话费", "充值", "抵扣券")):
                    continue
                t = ""
                for k in ("order_time", "createTime", "receiveTime", "time"):
                    if item.get(k):
                        t = str(item.get(k)).replace('/', '-')
                        break
                if not t.startswith(month):
                    continue
                cnt += 1
            return cnt
        except Exception as e:
            self.log(f"⚠️ [抢兑] 本月兑换记录查询异常: {e} —— 按保守策略照常抢")
            return -1

    def sign_grabCoupon(self):
        """话费券抢兑: 自动选场次 + 面额优先 + 库存降级 + 风控自保(命中即全线收手)"""
        sc = globalConfig.get("sign_config", {})
        if not sc.get("run_grab_coupon", False):
            return
        # ── 月度限额: 本月已抢到就不抢了 (多抢也用不上, 白白消耗兑换币) ──
        if GRAB_MONTHLY_MAX > 0:
            got = self.sign_grab_month_count()
            if got >= GRAB_MONTHLY_MAX:
                self.log(f"⏭️ [抢兑] 本月已抢到 {got} 张话费券 (限额 {GRAB_MONTHLY_MAX} 张/月), "
                         f"跳过抢兑 —— 多抢也用不上, 省下兑换币", notify=True)
                return
            if got >= 0:
                self.log(f"⚔️ [抢兑] 本月已抢 {got} 张 (限额 {GRAB_MONTHLY_MAX} 张/月), 继续抢")
        amounts = list(GRAB_AMOUNTS) or [int(GRAB_AMOUNT)]
        self.log(f"⚔️ [抢兑阶段] 目标面额: {'/'.join(str(a) for a in amounts)}元 话费券")

        cands = self.sign_grab_probe_pool()
        if not cands:
            self.log("⚔️ [抢兑] 奖品池无话费券, 跳过")
            return

        # ── 1) 场次归集 (实测每天 10:00-14:00 / 18:00-22:00 两场) ──
        sessions = {}
        for c in cands:
            sessions.setdefault(c["sessStart"], []).append(c)
        now = datetime.now()
        active, future, past = [], [], []
        for st, items in sessions.items():
            if not st:
                past.append((st, items))
                continue
            ends = [i["endTime"] for i in items if i["endTime"]] or [st]
            if st <= now < max(ends):
                active.append((st, items))
            elif st > now:
                future.append((st, items))
            else:
                past.append((st, items))
        if active:
            sess_start, items = max(active, key=lambda x: x[0])
            self.log(f"🎯 [抢兑] 场次进行中 (开抢 {sess_start:%m-%d %H:%M})")
        elif future:
            sess_start, items = min(future, key=lambda x: x[0])
            self.log(f"🎯 [抢兑] 下一场 {sess_start:%m-%d %H:%M}")
        elif past:
            sess_start, items = max(past, key=lambda x: x[0] or datetime.min)
            self.log(f"🎯 [抢兑] 场次已过 ({sess_start:%m-%d %H:%M}), 尝试捡漏")
        else:
            self.log("⚔️ [抢兑] 未解析到场次时间, 跳过")
            return

        # ── 2) 选档: 面额优先级 > 有库存优先 ──────────────────
        def rank(c):
            try:
                idx = amounts.index(int(c["amount"]))
            except ValueError:
                idx = len(amounts) + 1
            return (0 if c["stock"] > 0 else 1, idx, -c["amount"])

        ranked = sorted(items, key=rank)
        self.log("📋 [抢兑] 可选档位: " + ", ".join(
            f"{c['amount']:g}元(库存{c['stock']})" for c in ranked))
        pick = [c for c in ranked if c["stock"] > 0] or (ranked if GRAB_FALLBACK else [])
        if not pick:
            self.log("⚔️ [抢兑] 全部档位无库存, 跳过")
            return

        # ── 3) 等到开抢; 决定冲击强度 ─────────────────────────
        burst = False
        if sess_start and sess_start > now:
            wait_seconds = (sess_start - datetime.now()).total_seconds()
            if wait_seconds > 300:
                self.log(f"⏳ [抢兑] 距开抢还有 {wait_seconds:.0f}s (>5min), 本轮不等待; "
                         f"请把定时设在 09:58 / 17:58")
                return
            self.log(f"⏳ [抢兑] 等待开抢... (剩余 {wait_seconds:.1f}s)")
            while (sess_start - datetime.now()).total_seconds() > 0.3:
                time.sleep(0.2)
            burst = True
        elif sess_start:
            lag = (now - sess_start).total_seconds()
            self.log(f"⏳ [抢兑] 场次已开 {lag/60:.0f} 分钟, 轻探模式 (避免触发风控)")
        attempts = GRAB_ATTEMPTS if burst else 2

        # ── 4) 逐档冲击; 命中「风控/已结束」立即全线收手 ──────
        for cand in pick:
            st = self.sign_grab_execute(cand, attempts=attempts, interval=0.4 + random.random() * 0.3)
            if st == "ok":
                return
            if st == "ratelimit":
                self.log("🚫 [抢兑] 已触发风控, 本轮全线收手 (继续操作会拿不到奖励), 下个场次再试")
                return
            if st == "closed":
                self.log(f"🚫 [抢兑] 服务端返回「场次未开/兑换上限」, 本场已关闭, 全线收手 "
                         f"(若在 10:00/18:00 整点前后仍如此, 说明该号当前无兑换资格)")
                return
            if st == "nostock":
                self.log(f"📉 [抢兑] {cand['amount']:g}元券无库存, 自动降级下一档")
                continue
            self.log(f"💔 [抢兑] {cand['amount']:g}元券未抢到, 降级下一档")
        self.log(f"💔 [抢兑] {len(pick)} 个档位全部未抢到, 下次场次再试")

    def sign_huafei_summary(self):
        """话费资产汇总 (优先推送): 话费红包余额 + 临期提醒"""
        try:
            res = self.request("post", "https://act.10010.com/SigninApp/convert/getTelephone", data={})
            if not res:
                return
            j = res.json()
            if j.get('status') != "0000" or not j.get('data'):
                return
            d = j['data']
            bal = float(d.get('telephone') or 0)
            exp = float(d.get('needexpNumber') or 0)
            msg = f"💰 [话费] 签到区话费红包余额 {bal:.2f}元"
            if exp > 0:
                msg += f" (⚠️ 其中 {exp:.2f}元 将于 {d.get('month', '')}月底过期)"
            self.log(msg, notify=True)
            self.sign_initial_amount = bal
        except Exception as e:
            self.log(f"话费汇总异常: {e}")



    def get_wocare_body(self, apiCode, requestData={}):
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S') + str(int(datetime.now().microsecond / 1000)).zfill(3)
        encodedContent = base64.b64encode(json.dumps(requestData, separators=(',', ':')).encode('utf-8')).decode('utf-8')
        body = {
            "version": WOCARE_CONSTANTS["minRetries"],
            "apiCode": apiCode,
            "channelId": WOCARE_CONSTANTS["anotherApiKey"],
            "transactionId": timestamp + self.random_string(6, "0123456789"),
            "timeStamp": timestamp,
            "messageContent": encodedContent
        }
        params_array = []
        for key in sorted(body.keys()):
            params_array.append(f"{key}={body[key]}")
        params_array.append(f"sign={WOCARE_CONSTANTS['anotherEncryptionKey']}")
        sign_str = "&".join(params_array)
        body["sign"] = hashlib.md5(sign_str.encode('utf-8')).hexdigest()
        return body

    def wocare_api(self, apiCode, requestData={}):
        try:
            url = f"https://wocare.unisk.cn/api/v1/{apiCode}"
            body = self.get_wocare_body(apiCode, requestData)
            res = self.request("post", url, data=body)
            if not res: return None
            result = res.json()
            if result.get("messageContent"):
                try:
                    content = result["messageContent"]
                    content = content.replace('\n', '').replace('\r', '').replace(' ', '')
                    content = content.replace('-', '+').replace('_', '/')
                    missing_padding = len(content) % 4
                    if missing_padding:
                        content += '=' * (4 - missing_padding)
                    try:
                        decoded_bytes = base64.b64decode(content)
                        decoded_str = decoded_bytes.decode('utf-8')
                    except UnicodeDecodeError:
                        decoded_str = decoded_bytes.decode('utf-8', errors='replace')
                    except Exception as e:
                        decoded_str = "{}"
                    try:
                        decoded = json.loads(decoded_str, strict=False)
                    except:
                        decoded_str = re.sub(r'[\x00-\x1f\x7f]', '', decoded_str)
                        try:
                            decoded = json.loads(decoded_str, strict=False)
                        except:
                            decoded = {}
                    if isinstance(decoded, dict):
                        if "data" in decoded:
                            result["data"] = decoded["data"]
                        else:
                            result["data"] = decoded
                        if "resultMsg" in decoded:
                            result["resultMsg"] = decoded["resultMsg"]
                        if "resultCode" in decoded:
                            result["resultCode"] = decoded["resultCode"]
                except Exception as e:
                    self.log(f"联通祝福: 解析返回失败: {str(e)}")
            return result
        except Exception as e:
            self.log(f"wocare_api 异常: {str(e)}")
            return None

    def wocare_getToken(self, ticket):
        try:
            url = "https://wocare.unisk.cn/mbh/getToken"
            params = {
                "channelType": WOCARE_CONSTANTS["serviceLife"],
                "type": "02",
                "ticket": ticket,
                "version": COMMON_CONSTANTS["APP_VERSION"],
                "timestamp": datetime.now().strftime('%Y%m%d%H%M%S') + str(int(datetime.now().microsecond / 1000)).zfill(3),
                "desmobile": self.account_mobile,
                "num": "0",
                "postage": self.random_string(32),
                "homePage": "home",
                "duanlianjieabc": "qAz2m",
                "userNumber": self.account_mobile
            }
            res = self.session.get(url, params=params, allow_redirects=False, timeout=15)
            if res.status_code == 302:
                location = res.headers.get("Location", "")
                if location:
                    parsed = urlparse(location)
                    sid = parse_qs(parsed.query).get("sid", [None])[0]
                    if not sid:
                        sid = parse_qs(parsed.query).get("uuid", [None])[0]
                        if sid:
                            self.log(f"联通祝福: 未找到sid，使用uuid替代: {sid}")
                    if sid:
                        self.wocare_sid = sid
                        return self.wocare_loginmbh()
                    else:
                        self.log(f"联通祝福: 没有获取到sid或uuid, Location: {location}")
                else:
                    self.log("联通祝福: 没有获取到location")
            else:
                self.log(f"联通祝福: 获取sid失败[{res.status_code}]")
        except Exception as e:
            self.log(f"wocare_getToken 异常: {str(e)}")
        return False

    def wocare_loginmbh(self):
        try:
            apiCode = "loginmbh"
            requestData = {
                "sid": self.wocare_sid,
                "channelType": WOCARE_CONSTANTS["serviceLife"],
                "apiCode": apiCode
            }
            result = self.wocare_api(apiCode, requestData)
            if not result: return False
            responseResult = result
            resultCode = responseResult.get("resultCode", "-1")
            if resultCode == "0000":
                self.wocare_token = responseResult.get("data", {}).get("token")
                self.log("联通祝福: 登录成功")
                return True
            else:
                msg = responseResult.get("resultMsg") or responseResult.get("resultDesc") or ""
                self.log(f"联通祝福: 登录失败[{resultCode}]: {msg}")
        except Exception as e:
            self.log(f"wocare_loginmbh 异常: {str(e)}")
        return False

    def wocare_getDrawTask(self, activity):
        try:
            apiCode = "getDrawTask"
            requestData = {
                "token": self.wocare_token,
                "channelType": WOCARE_CONSTANTS["serviceLife"],
                "type": activity["id"],
                "apiCode": apiCode
            }
            result = self.wocare_api(apiCode, requestData)
            responseResult = result if result else {}
            resultCode = responseResult.get("resultCode", "-1")
            if resultCode == "0000":
                taskList = responseResult.get("data", {}).get("taskList", []) or []
                if not taskList:
                    pass
                else:
                    self.log(f"联通祝福: [{activity['name']}] 查询到 {len(taskList)} 个任务")
                    for task in taskList:
                        ts = task.get("taskStatus")
                        if str(ts) == "0" or not ts:
                            self.wocare_completeTask(activity, task)
            else:
                msg = responseResult.get("resultMsg") or responseResult.get("resultDesc") or ""
                self.log(f"联通祝福: [{activity['name']}]查询任务失败[{resultCode}]: {msg}")
        except Exception as e:
            self.log(f"wocare_getDrawTask 异常: {str(e)}")

    def wocare_completeTask(self, activity, task, taskStep="1"):
        try:
            taskTitle = task.get("title", "")
            action = "领取任务" if taskStep == "1" else "完成任务"
            apiCode = "completeTask"
            requestData = {
                "token": self.wocare_token,
                "channelType": WOCARE_CONSTANTS["serviceLife"],
                "task": task.get("id"),
                "taskStep": taskStep,
                "type": activity["id"],
                "apiCode": apiCode
            }
            result = self.wocare_api(apiCode, requestData)
            responseResult = result if result else {}
            resultCode = responseResult.get("resultCode", "-1")
            if resultCode == "0000":
                self.log(f"联通祝福: {action}[{taskTitle}]成功")
                if taskStep == "1":
                    time.sleep(1)
                    self.wocare_completeTask(activity, task, "4")
            else:
                msg = responseResult.get("resultMsg") or responseResult.get("resultDesc") or ""
                self.log(f"联通祝福: [{activity['name']}]{action}[{taskTitle}]失败[{resultCode}]: {msg}")
        except Exception as e:
            self.log(f"wocare_completeTask 异常: {str(e)}")

    def wocare_getSpecificityBanner(self):
        try:
            apiCode = "getSpecificityBanner"
            requestData = {
                "token": self.wocare_token,
                "apiCode": apiCode
            }
            result = self.wocare_api(apiCode, requestData)
            responseResult = result if result else {}
            resultCode = responseResult.get("resultCode", "-1")
            if resultCode == "0000":
                bannerList = responseResult.get("data", []) or []
                if not bannerList:
                    self.log(f"联通祝福: 获取动态 Banner 列表为空，接口明细: {responseResult}")
                for banner in bannerList:
                    if str(banner.get("activityStatus")) == "0" and str(banner.get("isDeleted")) == "0":
                        self.wocare_getDrawTask(banner)
                        self.wocare_loadInit(banner)
            else:
                msg = responseResult.get("resultMsg") or responseResult.get("resultDesc", "")
                self.log(f"联通祝福: 进入活动失败[{resultCode}]: {msg}")
        except Exception as e:
            self.log(f"wocare_getSpecificityBanner 异常: {str(e)}")

    def wocare_loadInit(self, activity):
        try:
            apiCode = "loadInit"
            requestData = {
                "token": self.wocare_token,
                "channelType": WOCARE_CONSTANTS["serviceLife"],
                "type": activity["id"],
                "apiCode": apiCode
            }
            result = self.wocare_api(apiCode, requestData)
            responseResult = result if result else {}
            resultCode = responseResult.get("resultCode", "-1")
            if resultCode == "0000":
                responseData = responseResult.get("data", {}) or {}
                activeModuleGroupId = responseData.get("zActiveModuleGroupId")
                drawCount = 0
                aid = activity["id"]
                if aid == 2:
                    isPartake = responseData.get("data", {}).get("isPartake") or 0
                    if not isPartake:
                        drawCount = 1
                elif aid == 3:
                    drawCount = int(responseData.get("raffleCountValue", 0) or 0)
                elif aid == 4:
                    drawCount = int(responseData.get("mhRaffleCountValue", 0) or 0)
                if drawCount > 0:
                     self.log(f"联通祝福: [{activity['name']}] 可抽奖次数 {drawCount}")
                else:
                     self.log(f"联通祝福: [{activity['name']}] 今日已无抽奖机会")
                while drawCount > 0:
                    time.sleep(2)
                    self.wocare_luckDraw(activity, activeModuleGroupId)
                    drawCount -= 1
            else:
                msg = responseResult.get("resultMsg") or responseResult.get("resultDesc") or ""
                self.log(f"联通祝福: [{activity['name']}]查询活动失败[{resultCode}]: {msg}")
        except Exception as e:
            self.log(f"wocare_loadInit 异常: {str(e)}")

    def wocare_luckDraw(self, activity, activeModuleGroupId):
        try:
            apiCode = "luckDraw"
            requestData = {
                "token": self.wocare_token,
                "channelType": WOCARE_CONSTANTS["serviceLife"],
                "zActiveModuleGroupId": activeModuleGroupId,
                "type": activity["id"],
                "apiCode": apiCode
            }
            result = self.wocare_api(apiCode, requestData)
            responseResult = result if result else {}
            resultCode = responseResult.get("resultCode", "-1")
            if resultCode == "0000":
                resultData = responseResult.get("data", {}) or {}
                drawResultCode = resultData.get("resultCode", "-1")
                if drawResultCode == "0000":
                    prize = resultData.get("data", {}).get("prize", {})
                    prizeName = prize.get("prizeName", "")
                    prizeDesc = prize.get("prizeDesc", "")
                    self.log(f"联通祝福: [{activity['name']}]抽奖: {prizeName}[{prizeDesc}]", notify=True)
                else:
                    msg = responseResult.get("resultMsg") or responseResult.get("resultDesc") or ""
                    if msg.lower() == "success":
                        self.log(f"联通祝福: [{activity['name']}] 未中奖 (继续努力)")
                    else:
                        self.log(f"联通祝福: [{activity['name']}] 抽奖并未中奖: {msg}")
            else:
                msg = responseResult.get("resultMsg") or responseResult.get("resultDesc") or ""
                if msg.lower() == "success":
                    self.log(f"联通祝福: [{activity['name']}] 未中奖 (继续努力)")
                else:
                    self.log(f"联通祝福: [{activity['name']}] 抽奖异常[{resultCode}]: {msg}")
        except Exception as e:
            self.log(f"wocare_luckDraw 异常: {str(e)}")

    def parse_jwt_payload(self, token):
        try:
            payload = token.split('.')[1]
            padding = len(payload) % 4
            if padding:
                payload += '=' * (4 - padding)
            payload = payload.replace('-', '+').replace('_', '/')
            decoded_bytes = base64.b64decode(payload)
            return json.loads(decoded_bytes.decode('utf-8'))
        except Exception as e:
            self.log(f"JWT Decode Error: {e}")
            return {}

    def generate_market_signature_headers(self, user_token, query_string="", json_body=""):
        try:
            token = user_token.replace('Bearer ', '')
            payload = self.parse_jwt_payload(token)
            login_id = payload.get('loginId', '')
            app_secret = hashlib.md5(f"al:ak:{login_id}".encode('utf-8')).hexdigest()
            nonce = str(uuid.uuid4())
            message = f"{login_id}{app_secret}{nonce}{query_string or ''}{json_body or ''}"
            signature = base64.b64encode(
                hmac.new(
                    app_secret.encode('utf-8'),
                    message.encode('utf-8'),
                    digestmod=hashlib.sha256
                ).digest()
            ).decode('utf-8')
            return {
                'X-User-Id': login_id,
                'X-Nonce': nonce,
                'X-Timestamp': str(int(time.time() * 1000)),
                'X-Signature': signature,
                'Content-Type': 'application/json'
            }
        except Exception as e:
            self.log(f"Signature Generation Error: {e}")
            return {}

    def generate_market_watering_signature_headers(self, user_token, xbsosjl, login_id, request_ts):
        try:
            message = f"td:433:tp{xbsosjl}td:334:et{login_id}td:334:et{request_ts}td:334:et"
            signature = base64.b64encode(
                hmac.new(
                    str(login_id).encode('utf-8'),
                    message.encode('utf-8'),
                    digestmod=hashlib.sha256,
                ).digest()
            ).decode('utf-8')
            return {'X-Signature': signature}
        except Exception as e:
            self.log(f"Market Watering Signature Error: {e}")
            return {}

    def get_market_headers(self, user_token):
        return {
            'User-Agent': COMMON_CONSTANTS['MARKET_UA'],
            'Authorization': f"Bearer {user_token}",
            'Content-Type': 'application/json',
            'X-Requested-With': 'com.sinovatech.unicom.ui'
        }

    def market_get_ticket(self):
        self.log("权益超市: 正在获取 ticket...")
        target_url = "https://contact.bol.wo.cn/market"
        res = self.openPlatLineNew(target_url)
        if res and 'ticket' in res:
            self.log("权益超市: 获取ticket成功")
            return res['ticket']
        self.log("权益超市: 获取ticket失败")
        return None

    def market_get_user_token(self, ticket):
        url = f"https://backward.bol.wo.cn/prod-api/auth/marketUnicomLogin?ticket={ticket}"
        headers = {
            'User-Agent': COMMON_CONSTANTS['MARKET_UA'],
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
        }
        for attempt in range(1, 4):
            try:
                self.log(f"权益超市: 正在获取 userToken...{f' (第{attempt}次重试)' if attempt > 1 else ''}")
                res = self.session.post(url, headers=headers, timeout=30).json()
                if res.get('code') == 200:
                    user_token = res.get('data', {}).get('token')
                    if user_token:
                        self.log("权益超市: 获取userToken成功")
                        return user_token
                self.log(f"权益超市: 获取userToken失败: {res.get('msg')}")
            except Exception as e:
                self.log(f"权益超市: 获取userToken异常: {e}")
            if attempt < 3:
                self.log(f"权益超市: 等待5秒后重试...")
                time.sleep(5)
        return None

    def query_market_watering_status(self, user_token):
        try:
            status_url = "https://backward.bol.wo.cn/prod-api/promotion/activityTask/getMultiCycleProcess?activityId=13"
            headers = self.get_market_headers(user_token)
            res = self.session.get(status_url, headers=headers).json()
            if res.get('code') == 200:
                data = res.get('data', {})
                triggered_time = data.get('triggeredTime', 0)
                trigger_time = data.get('triggerTime', 0)
                create_date = data.get('createDate', '')
                self.log(f"权益超市-浇花当前状况: 进度 {triggered_time}/{trigger_time}", notify=True)
                if triggered_time >= trigger_time:
                    self.log("权益超市-浇花: 🌟 您有鲜花权益待领取! (连续浇花已满) 🌟", notify=True)
                else:
                    today_str = datetime.now().strftime('%Y-%m-%d')
                    last_watered = create_date.split(' ')[0] if create_date else ''
                    if today_str == last_watered:
                        self.log(f"权益超市-浇花: 今日已浇水 (最后: {create_date})", notify=True)
                    else:
                        self.log("权益超市-浇花: 今日尚未浇水。")
            else:
                self.log(f"权益超市-浇花查验: 查询状态失败: {res.get('msg')}")
        except Exception as e:
            self.log(f"权益超市-浇花查验: 异常: {e}")

    def market_watering_task(self, user_token):
        self.log("权益超市: 浇花任务开始...")
        try:
            status_url = "https://backward.bol.wo.cn/prod-api/promotion/activityTask/getMultiCycleProcess?activityId=13"
            headers = self.get_market_headers(user_token)
            res = self.session.get(status_url, headers=headers).json()
            if res.get('code') != 200:
                self.log(f"权益超市-浇花: ❌ 失败: 获取状态失败: {res.get('msg')}", notify=True)
                return
            data = res.get('data', {})
            before_triggered = safe_int(data.get('triggeredTime', 0))
            trigger_time = safe_int(data.get('triggerTime', 0))
            create_date = data.get('createDate', '')
            today_str = datetime.now().strftime('%Y-%m-%d')
            last_watered = create_date.split(' ')[0] if create_date else ''
            if today_str == last_watered:
                self.log(f"权益超市-浇花: 今日已浇水 ({before_triggered}/{trigger_time})", notify=True)
                return
            if before_triggered >= trigger_time:
                self.log(f"权益超市-浇花: 🌟 已达领奖条件 ({before_triggered}/{trigger_time})", notify=True)
                return
            token = user_token.replace('Bearer ', '')
            payload = self.parse_jwt_payload(token)
            login_id = payload.get('loginId', '')
            if not login_id:
                self.log("权益超市-浇花: ❌ 失败: 无法获取登录标识", notify=True)
                return
            xbsosjl = "Y1mN8fNYktY0"
            request_ts = str(int(time.time() * 1000))
            query_string = f"xbsosjl={xbsosjl}&timeVerRan={request_ts}&diceid={login_id}"
            watering_url = f"https://backward.bol.wo.cn/prod-api/promotion/activityTaskShare/checkWatering?{query_string}"
            req_headers = {
                'Authorization': f"Bearer {token}",
                'X-Signature': self.generate_market_watering_signature_headers(
                    user_token, xbsosjl, login_id, request_ts
                ).get('X-Signature', ''),
                'User-Agent': COMMON_CONSTANTS['MARKET_H5_UA'],
                'Content-Type': 'application/json',
                'Origin': 'https://contact.bol.wo.cn',
                'Referer': 'https://contact.bol.wo.cn/',
                'X-Requested-With': 'com.sinovatech.unicom.ui',
                'Accept': '*/*',
            }
            water_res = self.session.post(watering_url, headers=req_headers, data="{}").json()
            if water_res.get('code') != 200:
                self.log(f"权益超市-浇花: ❌ 失败: {water_res.get('msg')}", notify=True)
                return
            time.sleep(1)
            check_res = self.session.get(status_url, headers=headers).json()
            if check_res.get('code') != 200:
                self.log(
                    f"权益超市-浇花: ✅ 浇水成功 (当前进度约 {before_triggered}/{trigger_time}，APP 可能稍后刷新)",
                    notify=True
                )
                return
            check_data = check_res.get('data', {})
            after_triggered = safe_int(check_data.get('triggeredTime', before_triggered))
            after_trigger_time = safe_int(check_data.get('triggerTime', trigger_time)) or trigger_time
            if after_triggered != before_triggered:
                self.log(
                    f"权益超市-浇花: ✅ 浇水成功 ({before_triggered}/{after_trigger_time} → {after_triggered}/{after_trigger_time})",
                    notify=True
                )
                return
            self.log(
                f"权益超市-浇花: ✅ 浇水成功 (当前进度约 {before_triggered}/{trigger_time}，APP 可能稍后刷新)",
                notify=True
            )
        except Exception as e:
            self.log(f"权益超市-浇花: ❌ 失败: {e}", notify=True)

    def market_get_raffle(self, user_token):
        self.log("权益超市: 正在查询奖品池...")
        try:
            timestamp = int(time.time() * 1000)
            query_string = f"id=12&timeVerRan={timestamp}"
            json_body = "{}"
            sig_headers = self.generate_market_signature_headers(user_token, query_string, json_body)
            url = f"https://backward.bol.wo.cn/prod-api/promotion/home/raffleActivity/prizeList?{query_string}"
            headers = self.get_market_headers(user_token)
            headers.update(sig_headers)
            headers['Referer'] = 'https://contact.bol.wo.cn/market'
            headers['Origin'] = 'https://contact.bol.wo.cn'
            res = self.session.post(url, headers=headers, data=json_body).json()
            if res.get('code') == 200 and isinstance(res.get('data'), list):
                keywords = ['月卡', '月会员', '月度', 'VIP月', '一个月', '周卡']
                exclude = ['5G宽视界', '沃视频']
                live_prizes = []
                for p in res['data']:
                    vip_prob = float(p.get('probabilityVip') or p.get('newVipProbability') or 0)
                    norm_prob = float(p.get('probability') or 0)
                    name = p.get('name', '')
                    daily_limit = int(p.get('dailyPrizeLimit') or 0)
                    match = any(k in name for k in keywords)
                    not_excluded = not any(e in name for e in exclude)
                    has_stock = daily_limit > 0
                    has_chance = norm_prob > 0 or vip_prob > 0
                    if match and not_excluded and has_stock and has_chance:
                        live_prizes.append(p)
                        total_limit = int(p.get('quantity') or 0)
                        self.log(f"权益超市: 【{name}】监测到放水 (日库存:{daily_limit}, 总库存:{total_limit}, 普通概率:{(norm_prob * 100):.4f}%, VIP概率:{(vip_prob * 100):.4f}%)")
                if live_prizes:
                    return True
            self.log("权益超市: 📢 未监测到高价值权益放水")
            return False
        except Exception as e:
            self.log(f"权益超市: 查询奖品池异常: {e}")
            return False

    def market_get_raffle_count(self, user_token):
        try:
            timestamp = int(time.time() * 1000)
            query_string = f"id=12&channel=unicomTab&timeVerRan={timestamp}"
            json_body = "{}"
            sig_headers = self.generate_market_signature_headers(user_token, query_string, json_body)
            url = f"https://backward.bol.wo.cn/prod-api/promotion/home/raffleActivity/getUserRaffleCountExt?{query_string}"
            headers = self.get_market_headers(user_token)
            headers.update(sig_headers)
            headers['Referer'] = 'https://contact.bol.wo.cn/market'
            headers['Origin'] = 'https://contact.bol.wo.cn'
            res = self.session.post(url, headers=headers, data=json_body).json()
            count = 0
            if res.get('code') == 200:
                data = res.get('data')
                if isinstance(data, dict):
                    count = int(data.get('raffleCount') or 0)
                else:
                    count = int(data or 0)
            if count > 0:
                self.log(f"权益超市: ✅ 当前抽奖次数: {count}")
                for i in range(count):
                    self.log(f"权益超市: 🎯 第 {i+1} 次抽奖...")
                    if not self.market_user_raffle(user_token):
                        break
                    time.sleep(3 + random.random() * 2)
            else:
                self.log("权益超市: 当前无抽奖次数")
        except Exception as e:
            self.log(f"权益超市: 查询抽奖次数异常: {e}")

    def market_user_raffle(self, user_token):
        try:
            timestamp = int(time.time() * 1000)
            query_string = f"id=12&channel=unicomTab&timeVerRan={timestamp}"
            json_body = "{}"
            sig_headers = self.generate_market_signature_headers(user_token, query_string, json_body)
            url = f"https://backward.bol.wo.cn/prod-api/promotion/home/raffleActivity/userRaffle?{query_string}"
            headers = self.get_market_headers(user_token)
            headers.update(sig_headers)
            headers['Referer'] = 'https://contact.bol.wo.cn/market'
            res = self.session.post(url, headers=headers, data=json_body).json()
            if res.get('code') == 200:
                data = res.get('data', {})
                prize_name = data.get('prizesName', '')
                message = data.get('message') or res.get('msg') or ""
                if prize_name and "谢谢参与" not in prize_name:
                    self.log(f"权益超市: 🎉 抽奖成功: {prize_name}", notify=True)
                    return True
                self.log(f"权益超市: 💨 未中奖: {message}", notify=True)
                return True
            self.log(f"权益超市: 抽奖失败: {res.get('msg')}")
            return False
        except Exception as e:
            self.log(f"权益超市: 抽奖异常: {e}")
            return False

    def market_get_all_tasks(self, ecs_token, user_token):
        url = "https://backward.bol.wo.cn/prod-api/promotion/activityTask/getAllActivityTasks?activityId=12"
        headers = {
            "Authorization": f"Bearer {user_token}",
            "User-Agent": COMMON_CONSTANTS["MARKET_UA"],
            "Origin": "https://contact.bol.wo.cn",
            "Referer": "https://contact.bol.wo.cn/",
            "Cookie": f"ecs_token={ecs_token}"
        }
        for attempt in range(1, 4):
            try:
                self.log(f"权益超市: 正在获取任务列表...{f' (第{attempt}次重试)' if attempt > 1 else ''}")
                res = self.session.get(url, headers=headers, timeout=15).json()
                if res.get('code') == 200:
                    tasks = res.get('data', {}).get('activityTaskUserDetailVOList', [])
                    self.log(f"权益超市: 成功获取到 {len(tasks)} 个任务")
                    return tasks
                self.log(f"权益超市: 查询任务列表失败: {res.get('msg')}")
            except Exception as e:
                self.log(f"权益超市: 获取任务列表异常: {e}")
            if attempt < 3:
                self.log("权益超市: 等待5秒后重试...")
                time.sleep(5)
        return []

    def market_do_share_list(self, share_list, user_token):
        self.log("权益超市: 开始执行任务...")
        for task in share_list:
            name = task.get('name', '')
            param = task.get('param1', '')
            trigger_time = task.get('triggerTime', 0)
            triggered_time = task.get('triggeredTime', 0)
            if any(k in name for k in ["购买", "秒杀"]):
                 self.log(f"权益超市: 🚫 {name} [跳过]")
                 continue
            if triggered_time >= trigger_time:
                 self.log(f"权益超市: ✅ {name} [已完成]")
                 continue
            url = ""
            if any(k in name for k in ["浏览", "查看"]):
                url = f"https://backward.bol.wo.cn/prod-api/promotion/activityTaskShare/checkView?checkKey={param}"
            elif "分享" in name:
                url = f"https://backward.bol.wo.cn/prod-api/promotion/activityTaskShare/checkShare?checkKey={param}"
            if url:
                try:
                    headers = {
                        "Authorization": f"Bearer {user_token}",
                        "User-Agent": COMMON_CONSTANTS["MARKET_UA"],
                        "Origin": "https://contact.bol.wo.cn",
                        "Referer": "https://contact.bol.wo.cn/"
                    }
                    res = self.session.post(url, json={}, headers=headers, timeout=15).json()
                    if res.get('code') == 200:
                        self.log(f"权益超市: ✅ {name} [执行成功]")
                    else:
                        self.log(f"权益超市: ❌ {name} [执行失败]: {res.get('msg')}")
                except Exception as e:
                    self.log(f"权益超市: ❌ {name} [执行异常]: {e}")
            time.sleep(2)

    def market_get_points_ticket(self, user_token):
        try:
            res = self.session.get(
                "https://backward.bol.wo.cn/prod-api/auth/getTicket?channel=pointsPlatform",
                headers={
                    "Authorization": f"Bearer {user_token}",
                    "User-Agent": COMMON_CONSTANTS["MARKET_UA"],
                },
                timeout=15,
            ).json()
            if res.get("code") == 200 and res.get("data"):
                return res.get("data")
            self.log(f"权益超市-会员中心: 获取 points ticket 失败: {res.get('msg') or res}")
        except Exception as e:
            self.log(f"权益超市-会员中心: 获取 points ticket 异常: {e}")
        return None

    def market_member_center_base_headers(self, points_ticket):
        referer = (
            f"https://m.jf.10010.com/ts-mobile/well/{MARKET_MEMBER_CENTER_PAGE_ID}"
            f"?distributeId={MARKET_MEMBER_CENTER_DISTRIBUTE_ID}"
            f"&partnersId={MARKET_MEMBER_CENTER_PARTNERS_ID}"
            f"&clientType={MARKET_MEMBER_CENTER_CLIENT_TYPE}"
            f"&ticket={points_ticket}"
        )
        return {
            "origin": "https://m.jf.10010.com",
            "clienttype": MARKET_MEMBER_CENTER_CLIENT_TYPE,
            "ticket": points_ticket,
            "partnersid": MARKET_MEMBER_CENTER_PARTNERS_ID,
            "content-type": "application/json;charset=UTF-8",
            "pageid": MARKET_MEMBER_CENTER_PAGE_ID,
            "Accept": "application/json, text/plain, */*",
            "Referer": referer,
            "User-Agent": COMMON_CONSTANTS["MARKET_H5_UA"],
            "X-Requested-With": "com.sinovatech.unicom.ui",
        }

    def market_get_secret_key_jf(self, points_ticket):
        if (
            getattr(self, "market_jf_secretKey", None)
            and getattr(self, "market_jf_ticket", None) == points_ticket
        ):
            return self.market_jf_secretKey
        try:
            res = self.session.get(
                "https://m.jf.10010.com/jf-external-application/jftask/getSecretKey",
                headers=self.market_member_center_base_headers(points_ticket),
                timeout=10,
            ).json()
            secret = res.get("data", {}).get("secretKey")
            if res.get("code") == "0000" and secret:
                self.market_jf_ticket = points_ticket
                self.market_jf_secretKey = secret.encode("utf-8")
                return self.market_jf_secretKey
            self.log(f"权益超市-会员中心: getSecretKey 失败: {res}")
        except Exception as e:
            self.log(f"权益超市-会员中心: getSecretKey 异常: {e}")
        return None

    def market_build_signature_headers_jf(self, points_ticket):
        secret_key = self.market_get_secret_key_jf(points_ticket)
        if not secret_key:
            return {}
        request_ts = str(round(time.time() * 1000))
        nonce = ''.join(random.choices('0123456789abcdefghijklmnopqrstuvwxyz', k=8))
        signature = hmac.new(
            secret_key,
            f"{nonce}{request_ts}".encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return {
            "x-request-timestamp": request_ts,
            "x-request-nonce": nonce,
            "x-request-signature": signature,
        }

    def market_member_center_headers(self, points_ticket, with_sign=False):
        headers = self.market_member_center_base_headers(points_ticket)
        if with_sign:
            headers.update(self.market_build_signature_headers_jf(points_ticket))
        return headers

    def market_prepare_member_center_context(self, points_ticket):
        signed_headers = self.market_member_center_headers(points_ticket, with_sign=True)
        try:
            self.session.post(
                "https://m.jf.10010.com/jf-external-application/page/query",
                json={
                    "activityId": MARKET_MEMBER_CENTER_PAGE_ID,
                    "distributeId": MARKET_MEMBER_CENTER_DISTRIBUTE_ID,
                    "partnersId": MARKET_MEMBER_CENTER_PARTNERS_ID,
                },
                headers=signed_headers,
                timeout=10,
            )
        except Exception as e:
            self.log(f"权益超市-会员中心: page/query 预热异常: {e}")
        try:
            self.session.post(
                "https://m.jf.10010.com/jf-external-application/jftask/userInfo",
                json={},
                headers=self.market_member_center_headers(points_ticket, with_sign=True),
                timeout=10,
            )
        except Exception as e:
            self.log(f"权益超市-会员中心: userInfo 预热异常: {e}")

    def market_member_center_finish_code(self, task):
        return safe_int(task.get("finish", task.get("status", 0)), 0)

    def market_member_center_finish_text(self, task):
        finish_text = str(task.get("finishText", "")).strip()
        if finish_text:
            return finish_text
        return {
            0: "未完成",
            99: "待领取",
            100: "已领取",
        }.get(self.market_member_center_finish_code(task), "未知状态")

    def market_query_member_center_task(self, points_ticket):
        try:
            res = self.session.post(
                "https://m.jf.10010.com/jf-external-application/jftask/taskDetail",
                json={},
                headers=self.market_member_center_headers(points_ticket, with_sign=True),
                timeout=10,
            ).json()
            if res.get("code") != "0000":
                self.log(f"权益超市-会员中心: 查询任务失败: {res}")
                return None
            task_list = res.get("data", {}).get("taskDetail", {}).get("taskList", [])
            return next(
                (task for task in task_list if str(task.get("taskCode")) == MARKET_MEMBER_CENTER_TASK_CODE),
                None,
            )
        except Exception as e:
            self.log(f"权益超市-会员中心: 查询任务异常: {e}")
            return None

    def market_wait_member_center_task_state(self, points_ticket, expected_codes, attempts=4, delay=2):
        task = None
        for idx in range(1, attempts + 1):
            task = self.market_query_member_center_task(points_ticket)
            if task:
                finish_code = self.market_member_center_finish_code(task)
                finish_text = self.market_member_center_finish_text(task)
                text_matches = (
                    (finish_text == "待领取" and 99 in expected_codes)
                    or (finish_text == "已领取" and 100 in expected_codes)
                )
                if finish_code in expected_codes or text_matches:
                    return task
                self.log(
                    f"权益超市-会员中心: 第{idx}次回查状态 {finish_text}/{finish_code}，"
                    f"本月进度 {safe_int(task.get('finishCount'), 0)}/{safe_int(task.get('needCount'), 0)}"
                )
            if idx < attempts:
                time.sleep(delay)
                self.market_prepare_member_center_context(points_ticket)
        return task

    def market_mark_member_center_browse_done(self, user_token, task_fix_id):
        try:
            headers = {
                "Authorization": f"Bearer {user_token}",
                "Origin": "https://contact.bol.wo.cn",
                "Referer": "https://contact.bol.wo.cn/",
                "Content-Type": "application/json",
                "Accept": "*/*",
                "User-Agent": COMMON_CONSTANTS["MARKET_H5_UA"],
                "X-Requested-With": "com.sinovatech.unicom.ui",
            }
            detail = self.session.get(
                f"https://backward.bol.wo.cn/prod-api/promotion/activityTask/getActivityTaskDetailByFixId?taskFixId={task_fix_id}",
                headers=headers,
                timeout=10,
            ).json()
            if detail.get("code") != 200:
                self.log(f"权益超市-会员中心: 获取任务详情失败: {detail.get('msg') or detail}")
                return False
            task_data = detail.get("data") or {}
            check_key = task_data.get("param1")
            wait_seconds = max(safe_int(task_data.get("content"), 17), 15)
            if not check_key:
                self.log("权益超市-会员中心: 未拿到 checkKey，跳过浏览任务")
                return False
            self.log(f"权益超市-会员中心: 模拟浏览会员中心 {wait_seconds} 秒")
            time.sleep(wait_seconds)
            check = self.session.post(
                f"https://backward.bol.wo.cn/prod-api/promotion/activityTaskShare/checkView?checkKey={check_key}",
                json={},
                headers=headers,
                timeout=10,
            ).json()
            if check.get("code") == 200 and check.get("data") is True:
                self.log("权益超市-会员中心: 浏览完成，任务已进入待领取")
                return True
            self.log(f"权益超市-会员中心: checkView 失败: {check.get('msg') or check}")
        except Exception as e:
            self.log(f"权益超市-会员中心: 浏览任务异常: {e}")
        return False

    def market_receive_member_center_points(self, points_ticket):
        try:
            res = self.session.post(
                "https://m.jf.10010.com/jf-external-application/jfmarkettask/receive",
                json={"taskCode": MARKET_MEMBER_CENTER_TASK_CODE},
                headers=self.market_member_center_headers(points_ticket, with_sign=True),
                timeout=10,
            ).json()
            if res.get("code") == "0000":
                score = res.get("data", {}).get("score", "未知积分")
                title = res.get("data", {}).get("title", "领取成功")
                self.log(f"权益超市-会员中心: ✅ {title}，获得 {score}", notify=True)
                return True
            self.log(f"权益超市-会员中心: 领取失败: {res.get('msg') or res}")
        except Exception as e:
            self.log(f"权益超市-会员中心: 领取异常: {e}")
        return False

    def market_member_center_task(self, user_token):
        self.log("权益超市-会员中心: 开始检查浏览任务")
        points_ticket = self.market_get_points_ticket(user_token)
        if not points_ticket:
            return
        self.market_prepare_member_center_context(points_ticket)
        task = self.market_query_member_center_task(points_ticket)
        if not task:
            self.log("权益超市-会员中心: 未找到目标任务")
            return
        finish_code = self.market_member_center_finish_code(task)
        finish_text = self.market_member_center_finish_text(task)
        finish_count = safe_int(task.get("finishCount"), 0)
        need_count = safe_int(task.get("needCount"), 0)
        self.log(
            f"权益超市-会员中心: 当前状态 {finish_text}/{finish_code}，"
            f"本月进度 {finish_count}/{need_count}"
        )
        if finish_count >= need_count:
            self.log("权益超市-会员中心: 本月次数已达上限")
            return
        if finish_code == 100 or finish_text == "已领取":
            self.log("权益超市-会员中心: 今日已领取，跳过")
            return
        if finish_code == 0 or finish_text == "未完成":
            jump_url = str(task.get("jumpUrl", "")).strip()
            match = re.search(r"taskFixId=(\d+)", jump_url)
            task_fix_id = match.group(1) if match else "90"
            if not self.market_mark_member_center_browse_done(user_token, task_fix_id):
                return
            self.market_prepare_member_center_context(points_ticket)
            task = self.market_wait_member_center_task_state(points_ticket, {99, 100}, attempts=4, delay=2)
            if not task:
                return
            finish_code = self.market_member_center_finish_code(task)
            finish_text = self.market_member_center_finish_text(task)
            self.log(
                f"权益超市-会员中心: 浏览后状态 {finish_text}/{finish_code}，"
                f"本月进度 {safe_int(task.get('finishCount'), 0)}/{safe_int(task.get('needCount'), 0)}"
            )
        if finish_code == 99 or finish_text == "待领取":
            self.market_receive_member_center_points(points_ticket)
        elif finish_code != 100:
            self.log("权益超市-会员中心: 状态未及时刷新，尝试直接领奖兜底")
            if self.market_receive_member_center_points(points_ticket):
                return
            self.log("权益超市-会员中心: 直接领奖兜底失败，跳过")

    def market_task(self, is_query_only=False):
        self.log("==== 权益超市 ====")
        ticket = self.market_get_ticket()
        if not ticket:
            return
        user_token = self.market_get_user_token(ticket)
        if not user_token:
            return
        if is_query_only:
            #self.query_market_watering_status(user_token)
            self.query_market_raffle_records(user_token)
            self.query_phone_recharge_records(user_token)
            return
        mc = globalConfig.get("market_config", {})
        if mc.get("run_water", True):
            self.market_watering_task(user_token)
            time.sleep(2)
        else:
            self.log("权益超市-浇水: ⏭️ 已被总开关关闭，跳过")
        if mc.get("run_task", True):
            if hasattr(self, 'ecs_token'):
                share_list = self.market_get_all_tasks(self.ecs_token, user_token)
                if share_list:
                    self.market_do_share_list(share_list, user_token)
            else:
                 self.log("权益超市: 缺 ecs_token, 跳过通用任务列表")
        else:
            self.log("权益超市-做任务: ⏭️ 已被总开关关闭，跳过")
        if mc.get("run_member_center", True):
            time.sleep(2)
            self.market_member_center_task(user_token)
        else:
            self.log("权益超市-会员中心: ⏭️ 已被子开关关闭，跳过")
        if mc.get("run_draw", True):
            if self.market_get_raffle(user_token):
                self.market_get_raffle_count(user_token)
        else:
            self.log("权益超市-抽奖: ⏭️ 已被总开关关闭，跳过")
        if mc.get("run_claim", False):
            self.log("权益超市-领奖: 自动领奖已开启")
            self.query_phone_recharge_records(user_token)
        else:
            self.log("权益超市-领奖: ⏭️ 未开启自动领奖")
        self.query_market_raffle_records(user_token)
        self.query_phone_recharge_records(user_token)

    def init_cloud_urls(self):
        if not hasattr(self, 'cloudDiskUrls'):
            self.cloudDiskUrls = {
                'onLine': "https://m.client.10010.com/mobileService/onLine.htm",
                'getTicketByNative': "https://m.client.10010.com/edop_ng/getTicketByNative",
                'userticket': "https://panservice.mail.wo.cn/api-user/api/user/ticket",
                'ltypDispatcher': "https://panservice.mail.wo.cn/wohome/dispatcher",
                'query': "https://m.jf.10010.com/jf-external-application/page/query",
                'taskDetail': "https://m.jf.10010.com/jf-external-application/jftask/taskDetail",
                'taskRecords': "https://m.jf.10010.com/jf-external-application/jftask/taskRecords",
                'dosign': "https://m.jf.10010.com/jf-external-application/jftask/sign",
                'upload2C': "https://tjupload.pan.wo.cn/openapi/client/upload2C",
                'doPopUp': "https://m.jf.10010.com/jf-external-application/jftask/popUp",
                'toFinish': "https://m.jf.10010.com/jf-external-application/jftask/toFinish",
                'lottery': "https://panservice.mail.wo.cn/activity/lottery",
                'lotteryTimestamp': "https://panservice.mail.wo.cn/activity/getTimestamp",
                'openActivity': "https://panservice.mail.wo.cn/activity/openActivity",
                'checkActivityStatus': "https://panservice.mail.wo.cn/activity/checkActivityStatus",
                'userInfo': "https://m.jf.10010.com/jf-external-application/jftask/userInfo",
                'ai_query': "https://panservice.mail.wo.cn/wohome/ai/assistant/query",
                'lottery_times': "https://panservice.mail.wo.cn/activity/lottery/lottery-times",
                'activityList': "https://panservice.mail.wo.cn/activity/lottery/activityList",
                'aiMoveFile': "https://panservice.mail.wo.cn/wohome/open/v1/ai/moveFile2SystemFolder",
                'activityUpload2C': "https://du.smartont.net:8443/openapi/client/upload2C",
                'queryPhoneLocation': "https://panservice.mail.wo.cn/api-user/user/info/query",
                'getScanState': "https://s.pan.wo.cn/wohome/intelligentClean/getScanStateAndResult",
                'getCleanData': "https://s.pan.wo.cn/wohome/intelligentClean/getCleanData",
                'batchClean': "https://s.pan.wo.cn/wohome/intelligentClean/batchClean",
                'vote': "https://panservice.mail.wo.cn/activity/activity-task/vote",
                'secretKey': "https://m.jf.10010.com/jf-external-application/jftask/getSecretKey",
                'taskFinish': "https://panservice.mail.wo.cn/activity/member-point/v1/task/finish",
            }

    def cloudRequest(self, url_name, payload, is_changer=False, method='post', custom_headers=None):
        self.init_cloud_urls()
        url = self.cloudDiskUrls.get(url_name)
        if not url:
            self.log(f"云盘无效的URL名称: {url_name}")
            return {'result': None, 'headers': None}
        headers = {
            'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 unicom{version:iphone_c@12.0301}",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
        }
        if custom_headers:
             headers.update(custom_headers)
        if url_name in ['dosign', 'userInfo', 'doPopUp', 'toFinish', 'taskDetail', 'taskRecords']:
            if not getattr(self.cloudDisk, 'userticket', None):
                self.log(f"云盘 [{{url_name}}] userticket 未获取")
                return {'result': None, 'headers': None}
            headers['ticket'] = self.cloudDisk.userticket
            headers['content-type'] = "application/json;charset=UTF-8"
            headers['partnersid'] = "1649"
            headers['origin'] = "https://m.jf.10010.com"
            if getattr(self.cloudDisk, 'jeaId', None):
                headers['Cookie'] = f"_jea_id={self.cloudDisk.jeaId};"
            if url_name in ['dosign', 'toFinish']:
                sig_headers = self.build_signature_headers_cloud()
                if sig_headers:
                    headers.update(sig_headers)
            if is_changer:
                headers['clienttype'] = "yunpan_unicom_applet"
                headers['x-requested-with'] = "com.sinovatech.unicom.ui"
                if url_name == 'toFinish':
                    headers['User-Agent'] = "Mozilla/5.0 (Linux; Android 12; Redmi K30 Pro Build/SKQ1.220303.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/131.0.6778.39 Mobile Safari/537.36/woapp LianTongYunPan/4.0.4 (Android 12)"
                    headers['clienttype'] = "yunpan_android"
                    headers['x-requested-with'] = "com.chinaunicom.bol.cloudapp"
            else:
                headers['clienttype'] = "yunpan_android"
                headers['x-requested-with'] = "com.sinovatech.unicom.ui"
        elif url_name == 'ai_query':
             model_id = payload.get('modelId', 1)
             headers.update({
                'accept': 'text/event-stream',
                'X-YP-Access-Token': self.cloudDisk.userToken,
                'X-YP-App-Version': '5.0.12',
                'X-YP-Client-Id': '1001000035',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 9; SM-N9810 Build/PQ3A.190705.11211540; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/91.0.4472.114 Mobile Safari/537.36/woapp LianTongYunPan/5.0.12 (Android 9)',
                'Content-Type': 'application/json',
                'Origin': 'https://panservice.mail.wo.cn',
                'X-Requested-With': 'com.chinaunicom.bol.cloudapp',
                'Referer': f"https://panservice.mail.wo.cn/h5/wocloud_ai/?modelType={model_id}&clientId=1001000035&touchpoint=300300010001&token={self.cloudDisk.userToken}",
             })
        elif url_name == 'lottery_times':
             method = 'get'
             headers.update({
                 'X-YP-Access-Token': self.cloudDisk.userToken, 'source-type': 'woapi', 'clientId': '1001000165',
                 'token': self.cloudDisk.userToken, 'X-YP-Client-Id': '1001000165',
             })
        elif url_name == 'aiMoveFile':
             headers.update({
                 'X-YP-Device-Id': 'yOH1Y2/Ck5tBHRRBEAPCoGRGBOHCob7I',
                 'app-type': 'liantongyunpanapp',
                 'Access-Token': self.cloudDisk.userToken,
                 'Client-Id': '1001000035',
                 'App-Version': 'yp-app/5.1.0',
                 'Sys-Version': 'Android/15',
                 'User-Agent': 'LianTongYunPan/5.1.0 (Android 15)',
                 'X-YP-Client-Id': '1001000035',
                 'X-YP-Access-Token': self.cloudDisk.userToken,
                 'oaid': '00000000',
                 'Content-Type': 'application/json;charset=utf-8',
                 'Origin': 'https://panservice.mail.wo.cn',
             })
        elif url_name.startswith('cloud_') or 'shareCard' in url_name:
             current_token = getattr(self.cloudDisk, 'userToken', '')
             headers.update({
                'Host': 'panservice.mail.wo.cn',
                'Accept': 'application/json, text/plain, */*',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 15; PJZ110 Build/AP3A.240617.008; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/144.0.7559.109 Mobile Safari/537.36/woapp LianTongYunPan/5.1.0 (Android 15)',
                'client-Id': '1001000035',
                'X-YP-Client-Id': '1001000035',
                'accessToken': current_token,
                'access-token': current_token,
                'X-YP-Access-Token': current_token,
                'Authorization': f'Bearer {current_token}',
                'X-Requested-With': 'com.chinaunicom.bol.cloudapp',
                'Content-Type': 'application/json',
                'Origin': 'https://panservice.mail.wo.cn',
             })
             touchpoint = '300300010032'
             if 'lightPuzzle' in url_name: touchpoint = '300300010003'
             if 'shareCardReceive' in url_name:
                  headers['User-Agent'] = "Mozilla/5.0 (Linux; Android 15; PJZ110 Build/AP3A.240617.008; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/142.0.7444.173 Mobile Safari/537.36 XWEB/1420229 MMWEBSDK/20250802 MMWEBID/7928 MicroMessenger/8.0.62.2900(0x28003EA0) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64"
                  headers['X-Requested-With'] = "com.tencent.mm"
                  headers['X-YP-GRAY-FLAG'] = "undefined"
                  uniq_key = payload.get('uniqKey', '') if isinstance(payload, dict) else ''
                  card_code = payload.get('_cardCode', 'LT') if isinstance(payload, dict) else 'LT'
                  if isinstance(payload, dict) and '_cardCode' in payload:
                       del payload['_cardCode']
                  headers['Referer'] = f"https://panservice.mail.wo.cn/h5/activitymobile/newYears26?uniqKey={uniq_key}&cardCode={card_code}&activityId=SPRING_FESTIVAL_2026&page=1&touchpoint=undefined"
             else:
                  headers['Referer'] = f"https://panservice.mail.wo.cn/h5/activitymobile/newYears26?activityId=SPRING_FESTIVAL_2026&touchpoint={touchpoint}&token={current_token}"
                  if url_name == 'shareCard':
                       headers['X-YP-GRAY-FLAG'] = "undefined"
        for attempt in range(1, 4):
            try:
                if method == 'get':
                    res = self.session.get(url, params=payload, headers=headers, timeout=15)
                else:
                    res = self.session.post(url, json=payload, headers=headers, timeout=15)
                if url_name == 'ai_query':
                     return {'result': None, 'body': res.text, 'headers': res.headers}
                try:
                    res_json = res.json()
                    return {'result': res_json, 'headers': res.headers, 'status': res.status_code}
                except:
                    return {'result': res.text, 'headers': res.headers, 'status': res.status_code}
            except Exception as e:
                err_msg = str(e)
                if attempt < 3 and os.environ.get("UNICOM_PROXY_API") and ("Max retries exceeded" in err_msg or "timed out" in err_msg.lower() or "connection" in err_msg.lower() or "SOCKS" in err_msg):
                    self.log(f"cloudRequest [{url_name}] 网络异常触发故障转移({err_msg}), 正在更换代理...")
                    self.failover_proxy()
                    continue
                if attempt == 3:
                     self.log(f"cloudRequest Exception [{url_name}]: {e}")
                     return {'result': None, 'headers': None, 'status': 599}
                self.log(f"cloudRequest [{url_name}] 网络异常({e}), 重试第{attempt}次...")
                time.sleep(2)

    def encrypt_data_cloud(self, data, key, iv="wNSOYIB1k1DjY5lA"):
        key_padded = key.ljust(16)[:16]
        cipher = AES.new(key_padded.encode(), AES.MODE_CBC, iv.encode())
        padded = pad(data.encode(), AES.block_size, style="pkcs7")
        return base64.b64encode(cipher.encrypt(padded)).decode()

    def getTicketByNative_cloud(self):
        for attempt in range(1, 4):
            try:
                url = f"{self.cloudDiskUrls['getTicketByNative']}?appId=edop_unicom_d67b3e30&token={self.ecs_token}"
                headers = {
                    'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 unicom{version:iphone_c@12.0301}",
                    'Connection': "Keep-Alive",
                    'Accept-Encoding': "gzip",
                }
                res = self.session.get(url, headers=headers).json()
                if res.get('ticket'):
                    self.cloudDisk.ticket = res['ticket']
                    return res['ticket']
                elif str(res.get('code')) == "9999":
                    self.log(f"getTicketByNative_cloud 票据失效或被拦截: {res}")
            except Exception as e:
                err_msg = str(e)
                if attempt < 3 and os.environ.get("UNICOM_PROXY_API") and ("Max retries exceeded" in err_msg or "timed out" in err_msg.lower() or "connection" in err_msg.lower() or "SOCKS" in err_msg):
                    self.log(f"getTicketByNative_cloud 第{attempt}次异常触发故障转移: {err_msg}")
                    self.failover_proxy()
                    continue
                self.log(f"getTicketByNative_cloud 第{attempt}次重试 - 异常: {e}")
                time.sleep(2)
        return None

    def get_ltypDispatcher_cloud(self, ticket):
        for attempt in range(1, 4):
            try:
                timestamp = str(int(time.time() * 1000))
                result_rnd = str(random.randint(123456, 199999))
                string_to_hash = "HandheldHallAutoLoginV2" + timestamp + result_rnd + "wohome"
                sign = hashlib.md5(string_to_hash.encode()).hexdigest()
                payload = {
                    "header": {
                        "key": "HandheldHallAutoLoginV2",
                        "resTime": timestamp,
                        "reqSeq": result_rnd,
                        "channel": "wohome",
                        "version": "",
                        "sign": sign
                    },
                    "body": {
                        "clientId": "1001000003",
                        "ticket": ticket
                    }
                }
                url = self.cloudDiskUrls['ltypDispatcher']
                headers = {'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 12; leijun Pro Build/SKQ1.22013.001);unicom{version:android@11.0702}"}
                res = self.session.post(url, json=payload, headers=headers).json()
                token = res.get('RSP', {}).get('DATA', {}).get('token')
                if token:
                    self.cloudDisk.userToken = token
                    return token
            except Exception as e:
                 err_msg = str(e)
                 if attempt < 3 and os.environ.get("UNICOM_PROXY_API") and ("Max retries exceeded" in err_msg or "timed out" in err_msg.lower() or "connection" in err_msg.lower() or "SOCKS" in err_msg):
                     self.log(f"get_ltypDispatcher_cloud 第{attempt}次异常触发故障转移: {err_msg}")
                     self.failover_proxy()
                     continue
                 self.log(f"get_ltypDispatcher_cloud 第{attempt}次重试 - 异常: {e}")
                 time.sleep(2)
        return None

    def get_userticket_cloud(self, is_changer=False):
        if not getattr(self.cloudDisk, 'userToken', None):
            self.log("云盘任务: 获取userticket失败, userToken未获取")
            return None
        headers = {}
        if is_changer:
            headers = {
                'User-Agent': "LianTongYunPan/4.0.4 (Android 12)",
                'app-type': "liantongyunpanapp",
                'Client-Id': "1001000035",
                'App-Version': "yp-app/4.0.4",
                'Sys-Version': "Android/12",
                'X-YP-Client-Id': "1001000035",
                'X-YP-Access-Token': self.cloudDisk.userToken,
            }
        else:
             headers = {
                'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 unicom{version:iphone_c@12.0301}",
                'Content-Type': 'application/json',
                'X-YP-Access-Token': self.cloudDisk.userToken,
                'accesstoken': self.cloudDisk.userToken,
                'token': self.cloudDisk.userToken,
                'clientId': "1001000003",
                'X-YP-Client-Id': "1001000003",
                'source-type': "woapi",
                'app-type': "unicom"
             }
        for attempt in range(1, 4):
            try:
                 res = self.session.post(self.cloudDiskUrls['userticket'], json={}, headers=headers, timeout=15).json()
                 if res and isinstance(res, dict) and res.get('result', {}).get('ticket'):
                     self.cloudDisk.userticket = res['result']['ticket']
                     return self.cloudDisk.userticket
                 else:
                     self.log(f"get_userticket_cloud failed: {res}")
                     return None
            except Exception as e:
                 self.log(f"[get_userticket_cloud] 请求异常[{e}]，重试第{attempt}次")
                 time.sleep(2)
        return None

    def get_userInfo_cloud(self):
        if not self.get_userticket_cloud(False): return
        data = self.cloudRequest('userInfo', {}, False, 'post')
        res = data.get('result')
        headers = data.get('headers')
        if headers:
            cookie = headers.get('Set-Cookie', '')
            match = re.search(r'_jea_id=([^;]+)', cookie)
            if match:
                self.cloudDisk.jeaId = match.group(1)
        if res and res.get('data'):
             avail = res['data'].get('availableScore')
             today_earn = res['data'].get('todayEarnScore', 0)
             if not hasattr(self.cloudDisk, 'initial_avail'):
                 self.cloudDisk.initial_avail = avail
                 self.log(f"云盘任务: 运行前 - 今日已赚: {today_earn}, 可用积分: {avail}")
             else:
                 earned = int(avail) - int(self.cloudDisk.initial_avail)
                 self.log(f"云盘任务: 运行后 - 今日已赚: {today_earn}, 可用: {avail}, 本次获得: {earned}", notify=True)

    def do_ai_interaction_cloud(self, taskCode, taskName):
        self.log(f"云盘任务: 执行AI通通查询请求...")
        payload = {
          "input": "你好",
          "platform": 2,
          "modelId": 0,
          "tag": 21,
          "subTag": 210000,
          "conversationId": "",
          "knowledgeId": "",
          "referFileInfo": []
        }
        data = self.cloudRequest('ai_query', payload, False, 'post')
        body = data.get('body', '')
        if body and ('"finish":1' in body or 'success' in body):
             self.log(f"云盘任务: ✅ [{taskName}] 互动成功")
             self.doPopUp_cloud(taskCode, taskName, False)
             return True
        self.log(f"云盘任务: ❌ [{taskName}] 互动失败")
        return False

    def get_cloud_upload_file_path(self):
        custom_path = os.environ.get("UNICOM_CLOUD_UPLOAD_FILE", "").strip()
        if custom_path:
            full_path = os.path.abspath(custom_path)
            if os.path.isfile(full_path):
                return full_path
            self.log(f"云盘任务: 上传文件不存在: {full_path}")
            return None
        seed_path = os.path.join(tempfile.gettempdir(), "unicom_cloud_upload_seed.jpg")
        target_size = max(UNICOM_CLOUD_UPLOAD_PROGRESS_BYTES, 1024)
        if not os.path.exists(seed_path) or os.path.getsize(seed_path) != target_size:
            seed_bytes = base64.b64decode("/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBxAQEBAQEBAPEA8PEA8QDw8PDw8QDw8QFREWFhURFRUYHSggGBolGxUVITEhJSkrLi4uFx8zODMsNygtLisBCgoKDg0OGxAQGy0lICYtLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLf/AABEIAAEAAgMBIgACEQEDEQH/xAAXAAADAQAAAAAAAAAAAAAAAAAAAQID/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQACEAMQAAAB6A//xAAXEAEAAwAAAAAAAAAAAAAAAAABAAIR/9oACAEBAAEFAkqf/8QAFBEBAAAAAAAAAAAAAAAAAAAAEP/aAAgBAwEBPwEf/8QAFBEBAAAAAAAAAAAAAAAAAAAAEP/aAAgBAgEBPwEf/8QAFBABAAAAAAAAAAAAAAAAAAAAEP/aAAgBAQAGPwJf/8QAFBABAAAAAAAAAAAAAAAAAAAAEP/aAAgBAQABPyFf/9k=")
            with open(seed_path, "wb") as f:
                f.write(seed_bytes)
                if target_size > len(seed_bytes):
                    f.seek(target_size - 1)
                    f.write(b"\0")
        return seed_path

    def get_cloud_upload_progress_bytes(self, file_size=0):
        progress_bytes = max(int(UNICOM_CLOUD_UPLOAD_PROGRESS_BYTES or 0), 1)
        if file_size and int(file_size) > 0:
            return min(int(file_size), progress_bytes)
        return progress_bytes

    def parse_cloud_size_to_bytes(self, value):
        match = re.search(r'(\d+(?:\.\d+)?)\s*([KMGT])', str(value).upper())
        if not match:
            return 0
        unit_power = {'K': 1, 'M': 2, 'G': 3, 'T': 4}
        return int(float(match.group(1)) * (1024 ** unit_power[match.group(2)]))

    def get_cloud_upload_times(self, task, file_size):
        progress_list = task.get('taskExtend', {}).get('taskProgressVOList', []) or []
        targets = []
        for item in progress_list:
            size_bytes = self.parse_cloud_size_to_bytes(item.get('progressName'))
            if size_bytes > 0:
                targets.append(size_bytes)
        finished = max(int(task.get('finishCount', 0) or 0), 0)
        stage_goal = finished + 1
        progress_bytes = self.get_cloud_upload_progress_bytes(file_size)
        if targets:
            stage_goal = min(stage_goal, len(targets))
            final_target = targets[stage_goal - 1]
            completed_target = targets[min(finished, len(targets)) - 1] if finished > 0 else 0
            remaining_bytes = max(final_target - completed_target, 0)
            if remaining_bytes <= 0:
                return 0, stage_goal
            return max((remaining_bytes + progress_bytes - 1) // progress_bytes, 1), stage_goal
        required = max(int(task.get('needCount', 0) or 0), 0)
        if required > 0:
            stage_goal = min(stage_goal, required)
        remaining = max(stage_goal - finished, 0)
        return remaining, stage_goal

    def query_cloud_task_list_cloud(self):
        if not self.get_userticket_cloud(False):
            return []
        data = self.cloudRequest('taskDetail', {}, False, 'post')
        if not isinstance(data, dict):
            self.log("云盘任务: taskDetail 返回结构异常，已跳过本轮任务列表")
            return []
        res = data.get('result')
        if not isinstance(res, dict):
            body = str(res).replace('\r', ' ').replace('\n', ' ').strip()[:120]
            self.log(f"云盘任务: taskDetail 返回异常，已跳过本轮任务列表 (status={data.get('status')}, body={body or 'None'})")
            return []
        task_detail = res.get('data', {}).get('taskDetail', {})
        if not isinstance(task_detail, dict):
            self.log("云盘任务: taskDetail 数据结构异常，已跳过本轮任务列表")
            return []
        return task_detail.get('taskList', []) or []

    def query_task_records_cloud(self, cursor=""):
        if not self.get_userticket_cloud(False):
            return []
        data = self.cloudRequest('taskRecords', {"cursor": cursor}, False, 'post')
        if not isinstance(data, dict):
            self.log("云盘任务: taskRecords 返回结构异常，已跳过积分明细查询")
            return []
        res = data.get('result')
        if not isinstance(res, dict):
            body = str(res).replace('\r', ' ').replace('\n', ' ').strip()[:120]
            self.log(f"云盘任务: taskRecords 返回异常，已跳过积分明细查询 (status={data.get('status')}, body={body or 'None'})")
            return []
        return res.get('data', []) or []

    def init_cloud_task_records_state(self):
        records = self.query_task_records_cloud("")
        self.cloudDisk.knownTaskRecordIds = {str(item.get('id')) for item in records if item.get('id')}

    def match_new_cloud_task_record(self, task_name, before_ids=None):
        records = self.query_task_records_cloud("")
        known_ids = set(before_ids if before_ids is not None else getattr(self.cloudDisk, 'knownTaskRecordIds', set()))
        new_record = None
        for item in records:
            record_id = str(item.get('id') or '')
            if not record_id or record_id in known_ids:
                continue
            if item.get('taskName') == task_name and not new_record:
                new_record = item
            known_ids.add(record_id)
        self.cloudDisk.knownTaskRecordIds = known_ids
        return new_record

    def get_cloud_task_by_code_cloud(self, task_code):
        if not task_code:
            return None
        for task in self.query_cloud_task_list_cloud():
            if task.get('taskCode') == task_code:
                return task
        return None

    def finalize_generic_task_cloud(self, task_code, task_name):
        current_task = self.get_cloud_task_by_code_cloud(task_code)
        if not isinstance(current_task, dict):
            return
        finish_text = current_task.get('finishText')
        finished = int(current_task.get('finishCount', 0) or 0)
        required = int(current_task.get('needCount', 0) or 0)
        if finish_text == "待领取":
            self.doPopUp_cloud(task_code, task_name, False)
            return
        if finish_text in ["已完成", "已领取"] or (required > 0 and finished >= required):
            record = self.match_new_cloud_task_record(task_name)
            if record:
                self.log(f"云盘任务: ✅ [{task_name}] 完成, 获得积分: {record.get('earnScoreDesc')}")
            else:
                self.log(f"云盘任务: ✅ [{task_name}] 已完成")

    def get_cloud_upload_name_cloud(self):
        return os.environ.get("UNICOM_CLOUD_UPLOAD_FILENAME", "8648").strip() or "8648"

    def doUpload_cloud(self, taskCode, taskName, prefix="云盘任务", notify=True):
        token = getattr(self.cloudDisk, 'userToken', '')
        upload_path = self.get_cloud_upload_file_path()
        if not token or not upload_path:
            return False
        file_size = os.path.getsize(upload_path)
        progress_file_size = self.get_cloud_upload_progress_bytes(file_size)
        file_name = self.get_cloud_upload_name_cloud()
        headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0",
            'Accept-Encoding': "gzip, deflate, br, zstd",
            'Origin': "https://pan.wo.cn",
            'Referer': "https://pan.wo.cn/",
            'Accept-Language': "zh-CN,zh;q=0.9",
            'Sec-Fetch-Site': "same-site",
            'Sec-Fetch-Mode': "cors",
            'Sec-Fetch-Dest': "empty",
        }
        for attempt in range(1, 3):
            request_time = str(int(time.time() * 1000))
            file_info = self.encrypt_data_cloud(json.dumps({
                "spaceType": "0",
                "directoryId": "0",
                "batchNo": datetime.now().strftime("%Y%m%d"),
                "fileName": file_name,
                "fileSize": progress_file_size,
                "fileType": "1",
            }, ensure_ascii=False, separators=(',', ':')), token)
            try:
                with open(upload_path, 'rb') as file_obj:
                    files = {
                        "uniqueId": (None, f"{request_time}_{''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=6))}"),
                        "accessToken": (None, token),
                        "fileName": (None, file_name),
                        "psToken": (None, "undefined"),
                        "fileSize": (None, str(file_size)),
                        "totalPart": (None, "1"),
                        "partSize": (None, str(file_size)),
                        "partIndex": (None, "1"),
                        "channel": (None, "wocloud"),
                        "directoryId": (None, "0"),
                        "fileInfo": (None, file_info),
                        "file": (file_name, file_obj, "image/jpeg"),
                    }
                    res = self.request_direct("POST", self.cloudDiskUrls['upload2C'], headers=headers, files=files, timeout=UNICOM_CLOUD_UPLOAD_TIMEOUT)
                res_json = {}
                try:
                    res_json = res.json()
                except:
                    pass
                meta_code = str(res_json.get('meta', {}).get('code', ''))
                code = str(res_json.get('code', ''))
                if res.status_code == 200 and (not res_json or meta_code in ('200', '0', '0000') or code in ('200', '0', '0000')):
                    self.cloudDisk.uploadedFileCount = int(getattr(self.cloudDisk, 'uploadedFileCount', 0) or 0) + 1
                    self.log(f"{prefix}: [{taskName}] 上传成功")
                    if taskCode:
                        time.sleep(1)
                        self.doPopUp_cloud(taskCode, taskName, False, notify=notify)
                    return True
                if attempt < 2 and res.status_code >= 500:
                    self.log(f"{prefix}: [{taskName}] 上传返回 {res.status_code}，重建请求重试一次")
                    time.sleep(2)
                    continue
                self.log(f"{prefix}: ❌ [{taskName}] 上传失败: HTTP {res.status_code} {res_json if res_json else res.text[:200]}")
                return False
            except Exception as e:
                if attempt < 2:
                    self.log(f"{prefix}: [{taskName}] 上传异常，重建请求重试一次: {e}")
                    time.sleep(2)
                    continue
                self.log(f"{prefix}: ❌ [{taskName}] 上传异常: {e}")
        return False

    def doPopUp_cloud(self, taskCode, taskName, is_changer, notify=True):
        if not self.get_userticket_cloud(is_changer): return
        known_ids = set(getattr(self.cloudDisk, 'knownTaskRecordIds', set()))
        time.sleep(5)
        data = self.cloudRequest('doPopUp', {}, is_changer, 'post')
        res = data.get('result')
        if not isinstance(res, dict):
             res = {}
        code = res.get('meta', {}).get('code')
        code2 = res.get('code')
        if str(code) == "0000" or str(code) == "0" or str(code2) == "0000" or str(code2) == "0":
             record = self.match_new_cloud_task_record(taskName, known_ids)
             if record:
                 score_desc = record.get('earnScoreDesc') or res.get('data', {}).get('score', 0)
                 self.log(f"云盘任务: ✅ [{taskName}] 完成, 获得积分: {score_desc}", notify=notify)
                 return
             score = res.get('data', {}).get('score', 0)
             if str(score) not in ('', '0', '0积分'):
                 self.log(f"云盘任务: ✅ [{taskName}] 领取到积分: {score}，但未在积分明细匹配到当前任务", notify=notify)
             else:
                 self.log(f"云盘任务: ✅ [{taskName}] 完成", notify=notify)
        else:
             self.log(f"云盘任务: ❌ [{taskName}] 领取奖励失败: {res}")

    def toFinish_cloud(self, taskCode, taskName, is_changer):
        if not self.get_userticket_cloud(is_changer): return False
        data = self.cloudRequest('toFinish', {'taskCode': taskCode}, is_changer, 'post')
        res = data.get('result')
        if not isinstance(res, dict):
             res = {}
        if res.get('code') == "0000": return True
        return False

    def dosign_cloud(self, taskCode, taskName):
        if not self.get_userticket_cloud(False): return
        data = self.cloudRequest('dosign', {'taskCode': taskCode}, False, 'post')
        res = data.get('result')
        if not isinstance(res, dict):
             res = {}
        if "0000" in str(res.get('code')) and res.get('data', {}).get('score'):
             self.log(f"云盘任务: ✅ [{taskName}] 完成, 获得积分: {res['data']['score']}", notify=True)
        else:
             self.log(f"云盘任务: ❌ [{taskName}] 失败: {res}")

    def upload_specific_file_quick_cloud(self):
        token = getattr(self.cloudDisk, 'userToken', '')
        if not token:
            return False, None
        quick_transfer_url = "https://b.smartont.net/openapi/transfer/quickTransfer"
        headers = {
            "access-token": token,
            "User-Agent": "okhttp-okgo/jeasonlzy LianTongYunPan/5.0.7 (Android 15)",
            "client-Id": "1001000035",
            "app-version": "yp-app/5.0.7",
            "Content-Type": "application/json"
        }
        body = {
            "batchNo": ''.join(random.choices(string.hexdigits.upper(), k=32)),
            "directoryId": "0",
            "fileName": "南网在线_4.3.128.apk",
            "fileSize": "223892168",
            "fileType": "5",
            "sha256": "479f9fe75fd218c0c9f9b8038fcfabcc5068094ceaad4bce3443dff304526656",
            "spaceType": "0",
            "autoRename": 1,
        }
        try:
            res = self.session.post(quick_transfer_url, headers=headers, json=body, timeout=15)
            if res.status_code == 200:
                resp_json = res.json()
                if isinstance(resp_json, dict) and str(resp_json.get("meta", {}).get("code")) in ["0000", "0"]:
                    if resp_json.get("result", {}).get("hasFile") in [1, None, "1"]:
                        fid = resp_json.get("result", {}).get("woCloudId")
                        if fid:
                            return True, fid
        except Exception as e:
            self.log(f"云盘任务: 秒传请求异常: {e}")
        return False, None

    def get_taskDetail_cloud(self):
        taskList = self.query_cloud_task_list_cloud()
        if taskList:
            names = [t.get('taskName', '?') for t in taskList]
            self.log(f"云盘任务: 任务列表({len(taskList)}): {', '.join(names)}")
        else:
            self.log("云盘任务: 任务列表为空")
            return
        for task in taskList:
            time.sleep(0.5)
            tName = task.get('taskName', '')
            tCode = task.get('taskCode')
            finishText = task.get('finishText')
            finished = int(task.get('finishCount', 0))
            required = int(task.get('needCount', 0))
            if finishText == "待领取":
                self.log(f"云盘任务: [{tName}] 待领取")
                self.doPopUp_cloud(tCode, tName, False)
                continue
            if finishText in ["已完成", "已领取"] or task.get('finishState', False) == True or (required > 0 and finished >= required):
                self.log(f"云盘任务: ✅ [{tName}] 已完成")
                continue
            self.log(f"云盘任务: 开始执行 [{tName}] 进度: {finished}/{required}")
            if "签到" in tName:
                self.toFinish_cloud(tCode, tName, False)
                self.dosign_cloud(tCode, tName)
            elif "与AI通通互动" in tName:
                self.toFinish_cloud(tCode, tName, False)
                self.do_ai_interaction_cloud(tCode, tName)
            elif "微信备份" in tName or "通讯录备份" in tName:
                self.log(f"云盘任务: [{tName}] 暂未适配，当前缺少该任务专用协议，先跳过")
            elif "当月上传容量满1GB" in tName:
                self.toFinish_cloud(tCode, tName, False)
                self.log(f"云盘任务: 开始执行1GB秒传任务...")
                upload_ok = 0
                for i in range(5):
                    success, fid = self.upload_specific_file_quick_cloud()
                    if success and fid:
                        upload_ok += 1
                        self.log(f"云盘任务: 第{i + 1}/5次秒传成功")
                        time.sleep(random.uniform(1, 2))
                        self.delete_root_files_cloud([{'id': fid, 'type': '1'}])
                    else:
                        self.log(f"云盘任务: 第{i + 1}/5次秒传失败")
                    time.sleep(random.uniform(2, 4))
                current_task = self.get_cloud_task_by_code_cloud(tCode)
                current_finishText = current_task.get('finishText') if current_task else finishText
                if current_finishText in ["已完成", "已领取"]:
                    self.log(f"云盘任务: ✅ [{tName}] 1GB秒传任务已完成", notify=True)
                else:
                    self.log(f"云盘任务: [{tName}] 秒传结束，当前状态: {current_finishText}", notify=True)
            else:
                self.run_generic_cloud_task(tCode, tName)

    def query_all_files_cloud(self, space_type="0", parent_directory_id="0", page_num=0, page_size=500):
        token = getattr(self.cloudDisk, 'userToken', '')
        if not token:
            return {}
        res = self.request_wohome_dispatcher_cloud("QueryAllFiles", {
            "clientId": "1001000035",
            "spaceType": str(space_type),
            "sortRule": "0",
            "parentDirectoryId": str(parent_directory_id),
            "pageNum": str(page_num),
            "pageSize": int(page_size),
        }, timeout=15)
        rsp = res.get('RSP', {})
        if str(rsp.get('RSP_CODE')) != '0000' or not rsp.get('DATA'):
            return {}
        try:
            key_padded = token.ljust(16)[:16]
            cipher = AES.new(key_padded.encode(), AES.MODE_CBC, b"wNSOYIB1k1DjY5lA")
            plain = unpad(cipher.decrypt(base64.b64decode(rsp['DATA'])), AES.block_size, style="pkcs7").decode('utf-8', errors='ignore')
            return json.loads(plain)
        except Exception as e:
            self.log(f"云盘任务: 查询根目录文件失败: {e}")
            return {}

    def request_wohome_dispatcher_cloud(self, key, param, timeout=15, client_id="1001000035"):
        token = getattr(self.cloudDisk, 'userToken', '')
        if not token:
            return {}
        timestamp = str(int(time.time() * 1000))
        req_seq = str(random.randint(10000, 99999))
        payload = {
            "header": {
                "key": key,
                "resTime": timestamp,
                "reqSeq": req_seq,
                "channel": "wohome",
                "version": "",
                "sign": hashlib.md5(f"{key}{timestamp}{req_seq}wohome".encode()).hexdigest().upper(),
            },
            "body": {
                "param": self.encrypt_data_cloud(json.dumps(param, ensure_ascii=False, separators=(',', ':')), token),
                "secret": True,
            },
        }
        headers = {
            'User-Agent': 'LianTongYunPan/5.1.2 (Android 10)',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'Access-Token': token,
            'accesstoken': token,
            'Client-Id': str(client_id),
        }
        try:
            return self.session.post(self.cloudDiskUrls['ltypDispatcher'], json=payload, headers=headers, timeout=timeout).json()
        except Exception as e:
            self.log(f"云盘任务: [{key}] 请求失败: {e}")
            return {}

    def list_upload_named_files_cloud(self, max_pages=4):
        upload_name = self.get_cloud_upload_name_cloud().strip()
        if not upload_name:
            return []
        pattern = re.compile(rf"^{re.escape(upload_name)}(?:\(\d+\))?(?:\.[^.]+)?$")
        matched = []
        seen = set()
        page_num = 0
        while page_num < max_pages:
            data = self.query_all_files_cloud("0", "0", page_num, 500)
            page_files = data.get('files') or []
            if not page_files:
                break
            for item in page_files:
                file_id = item.get('id')
                file_name = str(item.get('name', '')).strip()
                if file_id and file_id not in seen and pattern.match(file_name):
                    seen.add(file_id)
                    matched.append(item)
            if len(page_files) < 500:
                break
            page_num += 1
        return matched

    def delete_root_files_cloud(self, items, space_type="0"):
        targets = []
        for item in items or []:
            item_id = str(item.get('id', '')).strip()
            if not item_id:
                continue
            targets.append((item_id, str(item.get('type', '1')) == '0'))
        deleted = 0
        for offset in range(0, len(targets), 100):
            batch = targets[offset:offset + 100]
            dir_list = [item_id for item_id, is_dir in batch if is_dir]
            file_list = [item_id for item_id, is_dir in batch if not is_dir]
            if not dir_list and not file_list:
                continue
            res = self.request_wohome_dispatcher_cloud("DeleteFile", {
                "spaceType": str(space_type),
                "vipLevel": "0",
                "dirList": dir_list,
                "fileList": file_list,
                "clientId": "1001000035",
            }, timeout=20)
            rsp = res.get('RSP', {})
            batch_idx = offset // 100 + 1
            if str(rsp.get('RSP_CODE')) == '0000':
                deleted += len(batch)
                self.log(f"云盘任务: 第{batch_idx}批根目录删除成功，共{len(batch)}个文件")
            else:
                self.log(f"云盘任务: 第{batch_idx}批根目录删除失败: {rsp.get('RSP_DESC') or res}")
            time.sleep(1)
        return deleted

    def clean_duplicate_files_cloud(self):
        token = getattr(self.cloudDisk, 'userToken', '')
        if not token:
            return
        self.log("云盘任务: 开始清理云盘重复文件")
        cloud_headers = {
            'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) LianTongYunPan/5.1.0 (iPhone; iOS 16.6)",
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'Accept-Encoding': 'br;q=1.0, gzip;q=0.9, deflate;q=0.8',
            'Access-Token': token, 'X-YP-Access-Token': token,
            'Client-Id': '1001000035', 'X-YP-Client-Id': '1001000035',
            'App-Version': 'yp-app/5.1.0', 'app-type': 'liantongyunpanapp',
            'Sys-Version': 'iOS/16.6',
        }
        uploaded_count = int(getattr(self.cloudDisk, 'uploadedFileCount', 0) or 0)
        retry_count = 6 if uploaded_count > 0 else 1
        task_id = ""
        file_ids = []
        for attempt in range(1, retry_count + 1):
            try:
                res = self.session.post(
                    self.cloudDiskUrls['getScanState'], json={
                        "pathLevelList": [{"levelType": "space", "levelName": "个人云", "busId": "0"}]
                    }, headers=cloud_headers, timeout=10,
                ).json()
            except Exception as e:
                self.log(f"云盘任务: 获取扫描状态失败: {e}")
                return
            if res.get('meta', {}).get('code') != '200':
                self.log("云盘任务: 获取扫描状态失败")
                return
            task_id = ""
            for item in res.get('result', {}).get('subTaskList', []):
                if item.get('taskId'):
                    task_id = item['taskId']
                    break
            if task_id:
                file_ids = []
                page = max_page = 1
                while page <= max_page:
                    try:
                        page_res = self.session.post(
                            self.cloudDiskUrls['getCleanData'], json={
                                "pageNum": page, "taskId": task_id, "type": 3, "pageSize": 50,
                            }, headers=cloud_headers, timeout=10,
                        ).json()
                    except Exception as e:
                        self.log(f"云盘任务: 获取第{page}页清理数据失败: {e}")
                        return
                    if page_res.get('meta', {}).get('code') != '200':
                        break
                    max_page = page_res.get('result', {}).get('maxPageNum', 1)
                    for group in page_res.get('result', {}).get('fileGroupList', []):
                        for fi, file_item in enumerate(group.get('fileList', [])):
                            if fi <= 0 or not file_item.get('fileId'):
                                continue
                            file_ids.append({"fileId": file_item['fileId'], "spaceType": file_item.get('spaceType', '0')})
                    page += 1
            if file_ids:
                self.log(f"云盘任务: 第{attempt}次重复扫描完成，共{len(file_ids)}个重复文件")
                break
            if attempt < retry_count:
                wait_seconds = min(5 + (attempt - 1) * 2, 12)
                self.log(f"云盘任务: 第{attempt}次重复扫描未发现可清理文件，{wait_seconds}秒后重试")
                time.sleep(wait_seconds)
        if not file_ids:
            named_files = self.list_upload_named_files_cloud() if uploaded_count > 0 else []
            if named_files:
                preview = "、".join(item.get('name', '') for item in named_files[:6]).strip("、")
                more = "..." if len(named_files) > 6 else ""
                self.log(f"云盘任务: 智能清理未识别到重复项，但根目录检测到{len(named_files)}个[{self.get_cloud_upload_name_cloud()}]系列文件: {preview}{more}")
                deleted = self.delete_root_files_cloud(named_files)
                self.cloudDisk.uploadedFileCount = 0
                if deleted:
                    self.log(f"云盘任务: 已通过官方删除接口清理{deleted}个[{self.get_cloud_upload_name_cloud()}]系列文件")
                else:
                    self.log(f"云盘任务: [{self.get_cloud_upload_name_cloud()}]系列文件删除失败")
            else:
                self.cloudDisk.uploadedFileCount = 0
                self.log("云盘任务: 无重复文件")
            return
        for offset in range(0, len(file_ids), 100):
            batch = file_ids[offset:offset + 100]
            batch_idx = offset // 100 + 1
            try:
                batch_res = self.session.post(
                    self.cloudDiskUrls['batchClean'], json={
                        "fileList": batch, "taskType": 3, "taskId": task_id,
                    }, headers=cloud_headers, timeout=30,
                ).json()
                code = batch_res.get('meta', {}).get('code')
                self.log(f"云盘任务: 第{batch_idx}批清理: {'成功' if code == '200' else '失败'}")
            except Exception as e:
                self.log(f"云盘任务: 第{batch_idx}批清理失败: {e}")
            time.sleep(2)
        named_files = self.list_upload_named_files_cloud() if uploaded_count > 0 else []
        if named_files:
            preview = "、".join(item.get('name', '') for item in named_files[:6]).strip("、")
            more = "..." if len(named_files) > 6 else ""
            self.log(f"云盘任务: 智能清理后根目录仍检测到{len(named_files)}个[{self.get_cloud_upload_name_cloud()}]系列文件: {preview}{more}")
            deleted = self.delete_root_files_cloud(named_files)
            if deleted:
                self.log(f"云盘任务: 已通过官方删除接口补充清理{deleted}个[{self.get_cloud_upload_name_cloud()}]系列文件")
        self.cloudDisk.uploadedFileCount = 0
        self.log("云盘任务: 云盘重复文件清理完成")

    def vote_cloud(self):
        token = getattr(self.cloudDisk, 'userToken', '')
        if not token:
            return
        ypid_list = getattr(self.cloudDisk, 'ypid_list', [])
        if not ypid_list:
            return
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) LianTongYunPan/4.0.2 (iPhone; iOS 16.6)",
            'Sec-Fetch-Mode': 'cors',
            'clientId': '1001000165',
            'Origin': 'https://panservice.mail.wo.cn',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Site': 'same-origin',
            'X-YP-Access-Token': token, 'token': token,
            'X-YP-Client-Id': '1001000165',
            'X-SH-Access-Token': '',
            'source-type': 'woapi',
        }
        for idx in range(3):
            try:
                self.session.post(
                    self.cloudDiskUrls['vote'], json={"activityId": "MjQ=", "id": random.choice(ypid_list)},
                    headers=headers, timeout=10,
                )
                self.log(f"云盘任务: 第{idx + 1}次投票")
            except Exception as e:
                self.log(f"云盘任务: 第{idx + 1}次投票失败: {e}")
            time.sleep(1)

    def build_cloud_lottery_headers(self):
        token = getattr(self.cloudDisk, 'userToken', '')
        if not token:
            return {}
        return {
            'User-Agent': "Mozilla/5.0 (Linux; Android 10; MI 8 Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/143.0.7499.146 Mobile Safari/537.36/woapp LianTongYunPan/5.1.2 (Android 10)",
            'Accept': 'application/json, text/plain, */*',
            'source-type': 'woapi',
            'Sec-Fetch-Site': 'same-origin',
            'clientId': '1001000165',
            'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
            'token': token,
            'X-SH-Access-Token': '',
            'Sec-Fetch-Mode': 'cors',
            'X-YP-Access-Token': token,
            'X-YP-Client-Id': '1001000165',
            'X-Requested-With': 'com.chinaunicom.bol.cloudapp',
            'X-YP-GRAY-FLAG': 'undefined',
            'Sec-Fetch-Dest': 'empty',
        }

    def build_cloud_hometown_headers(self, extra=None):
        token = getattr(self.cloudDisk, 'userToken', '')
        if not token:
            return {}
        headers = {
            'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) LianTongYunPan/5.1.0 (iPhone; iOS 16.6)",
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
            'source-type': 'woapi',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'clientId': '1001000165',
            'X-YP-Client-Id': '1001000165',
            'X-YP-Access-Token': token,
            'token': token,
            'X-SH-Access-Token': '',
            'X-YP-GRAY-FLAG': 'undefined',
            'requestTime': str(int(time.time() * 1000)),
        }
        if extra:
            headers.update(extra)
        return headers

    def build_cloud_activity_headers(self, activity_id=""):
        token = getattr(self.cloudDisk, 'userToken', '')
        if not token:
            return {}
        headers = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 10; MI 8 Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/143.0.7499.146 Mobile Safari/537.36/woapp LianTongYunPan/5.1.2 (Android 10)",
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'source-type': 'woapi',
            'clientId': '1001000165',
            'client-Id': '1001000165',
            'token': token,
            'accessToken': token,
            'access-token': token,
            'X-YP-Access-Token': token,
            'X-YP-Client-Id': '1001000165',
            'X-SH-Access-Token': '',
            'X-Requested-With': 'com.chinaunicom.bol.cloudapp',
            'X-YP-GRAY-FLAG': 'undefined',
            'Origin': 'https://panservice.mail.wo.cn',
        }
        if activity_id:
            point_ticket = getattr(self.cloudDisk, 'ticket', '')
            mobile = getattr(self, 'account_mobile', '') or getattr(self, 'mobile', '')
            if self.is_cloud_upload_activity(activity_id) and point_ticket and mobile:
                headers['Referer'] = (
                    "https://panservice.mail.wo.cn/h5/activitymobile/fileUploadActive"
                    "?touchpoint=300200030001&type=06"
                    f"&ticket={point_ticket}"
                    "&version=iphone_c%4012.0801"
                    f"&timestamp={int(time.time() * 1000)}"
                    f"&desmobile={mobile}"
                    "&num=0&postage=01addda9786dc7eb5ca0eacd9acd664a"
                    f"&activityId={quote(activity_id)}&clientid=1001000003"
                    f"&userNumber={mobile}"
                )
            else:
                headers['Referer'] = f"https://panservice.mail.wo.cn/h5/activitymobile/fileUploadActive?touchpoint=300300010005&activityId={quote(activity_id)}&token={token}"
        return headers

    def get_cloud_lottery_draw_count(self, times_res):
        result = times_res.get('result')
        if isinstance(result, int):
            return result
        if not isinstance(result, dict):
            return 0
        draw_count = result.get('times')
        if draw_count is None:
            for key in ['lotteryTimes', 'freeTimes', 'drawTimes', 'count']:
                if key in result:
                    draw_count = result.get(key)
                    break
        try:
            return int(draw_count or 0)
        except:
            return 0

    def query_cloud_phone_location_cloud(self):
        province_code = str(getattr(self.cloudDisk, 'hometownProvinceCode', '') or '')
        province_name = str(getattr(self.cloudDisk, 'hometownProvinceName', '') or '')
        if province_code and province_name:
            return province_code, province_name
        token = getattr(self.cloudDisk, 'userToken', '')
        mobile = getattr(self, 'account_mobile', '') or getattr(self, 'mobile', '')
        headers = self.build_cloud_hometown_headers({"X-SH-Access-Token": ""})
        if not token or not mobile or not headers:
            return "", ""
        try:
            res = self.session.post(
                self.cloudDiskUrls['queryPhoneLocation'],
                json={"mobile": self.encrypt_data_cloud(mobile, "CBWGjFHjZdhTf7h8")},
                headers=headers,
                timeout=10,
            ).json()
            if str(res.get('meta', {}).get('code')) == '200':
                result = res.get('result') or {}
                province_code = str(result.get('provinceCode') or '')
                province_name = str(result.get('provinceName') or '')
                if province_code and province_name:
                    self.cloudDisk.hometownProvinceCode = province_code
                    self.cloudDisk.hometownProvinceName = province_name
                    self.log(f"家乡打卡 - 归属地: {province_name}({province_code})")
                    return province_code, province_name
            self.log(f"云盘任务: 查询号码归属地失败: {res}")
        except Exception as e:
            self.log(f"云盘任务: 查询号码归属地异常: {e}")
        return "", ""

    def get_cloud_activity_province(self):
        province_code = str(getattr(self.cloudDisk, 'hometownProvinceCode', '') or '')
        province_name = str(getattr(self.cloudDisk, 'hometownProvinceName', '') or '')
        if province_code and province_name:
            return province_code, province_name
        province_code, province_name = self.query_cloud_phone_location_cloud()
        if province_code and province_name:
            return province_code, province_name
        if (not hasattr(self, 'city_info')) or (not self.city_info):
            self.get_city_info()
        if not isinstance(getattr(self, 'city_info', None), list) or not self.city_info:
            return "", ""
        city = self.city_info[0] if isinstance(self.city_info[0], dict) else {}
        province_code = str(city.get('proCode') or city.get('standardProvinceCode') or "").lstrip('0')
        province_name = str(city.get('proName') or city.get('provinceName') or "")
        if province_code and province_name:
            self.cloudDisk.hometownProvinceCode = province_code
            self.cloudDisk.hometownProvinceName = province_name
        return province_code, province_name

    def query_cloud_lottery_times_cloud(self, activity_id, headers=None):
        if not activity_id:
            return None
        use_headers = dict(headers or self.build_cloud_lottery_headers())
        if not use_headers:
            return None
        use_headers['requestTime'] = str(int(time.time() * 1000))
        res = self.session.get(self.cloudDiskUrls['lottery_times'], params={"activityId": activity_id}, headers=use_headers, timeout=10).json()
        self.cloudDisk.lotteryTimesResult = res
        return res

    def ensure_cloud_lottery_activity_open_cloud(self, activity_id):
        headers = self.build_cloud_activity_headers(activity_id)
        if not headers:
            return False
        try:
            check_headers = dict(headers)
            check_headers['requestTime'] = str(int(time.time() * 1000))
            check_res = self.session.get(self.cloudDiskUrls['checkActivityStatus'], params={"activityId": activity_id}, headers=check_headers, timeout=10).json()
            if str(check_res.get('meta', {}).get('code')) == '200' and str(check_res.get('result', {}).get('state')) == '1':
                if self.is_cloud_upload_activity(activity_id):
                    self.log("家乡打卡 - 开启结果：开启成功")
                return True
        except Exception as e:
            self.log(f"云盘任务: 查询抽奖活动开启状态失败: {e}")
        province_code, province_name = self.get_cloud_activity_province()
        if not province_code or not province_name:
            self.log("云盘任务: 开启抽奖活动失败，缺少省份信息")
            return False
        try:
            open_headers = dict(headers)
            open_headers['requestTime'] = str(int(time.time() * 1000))
            res = self.session.post(
                self.cloudDiskUrls['openActivity'],
                json={"activityId": activity_id, "provinceCode": province_code, "provinceName": province_name},
                headers=open_headers,
                timeout=10,
            ).json()
            if str(res.get('meta', {}).get('code')) == '200' and str(res.get('result', {}).get('state')) == '1':
                if self.is_cloud_upload_activity(activity_id):
                    self.log("家乡打卡 - 开启结果：开启成功")
                else:
                    self.log(f"云盘任务: 抽奖活动[{activity_id}] 已开启")
                return True
            if self.is_cloud_upload_activity(activity_id):
                message = res.get('msg') or res.get('meta', {}).get('message') or '开启失败'
                self.log(f"家乡打卡 - 开启结果：{message}")
            else:
                self.log(f"云盘任务: 开启抽奖活动失败: {res}")
        except Exception as e:
            self.log(f"云盘任务: 开启抽奖活动异常: {e}")
        return False

    def query_cloud_lottery_record_cloud(self, activity_id):
        if not activity_id:
            return None
        headers = self.build_cloud_hometown_headers() if self.is_cloud_upload_activity(activity_id) else self.build_cloud_lottery_headers()
        if not headers:
            return None
        try:
            response = self.session.get(
                f"https://panservice.mail.wo.cn/activity/lottery/recordList?activityId={quote(activity_id)}",
                headers=headers,
                timeout=10,
            )
            result = response.json() if response.status_code == 200 else None
            if not isinstance(result, dict):
                return None
            if str(result.get('meta', {}).get('code')) == '200':
                record_list = result.get('result') or []
                prize = record_list[0].get('prizeName', '暂无抽奖记录') if record_list else '暂无抽奖记录'
                if self.is_cloud_upload_activity(activity_id):
                    self.log(f"家乡打卡 - 上次抽奖：{prize}")
                return prize
        except Exception as e:
            self.log(f"云盘任务: 查询抽奖记录异常: {e}")
        return None

    def do_activity_upload_cloud(self, activity_id):
        token = getattr(self.cloudDisk, 'userToken', '')
        upload_path = self.get_cloud_upload_file_path()
        if not token or not upload_path:
            return False
        file_size = os.path.getsize(upload_path)
        file_name = self.get_cloud_upload_name_cloud()
        file_info = self.encrypt_data_cloud(json.dumps({
            "batchNo": datetime.now().strftime("%Y%m%d%H%M%S"),
            "fileName": file_name,
            "fileSize": file_size,
            "fileType": 1,
            "directoryId": "0",
            "spaceType": "0",
        }, ensure_ascii=False, separators=(',', ':')), token)
        headers = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 10; MI 8 Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/143.0.7499.146 Mobile Safari/537.36/woapp LianTongYunPan/5.1.2 (Android 10)",
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Origin': 'https://panservice.mail.wo.cn',
            'Referer': f"https://panservice.mail.wo.cn/h5/activitymobile/fileUploadActive?touchpoint=300300010005&activityId={quote(activity_id)}&token={token}",
            'X-Requested-With': 'com.chinaunicom.bol.cloudapp',
            'accessToken': token,
            'access-token': token,
            'client_id': '1001000165',
            'X-YP-GRAY-FLAG': 'undefined',
            'requestTime': str(int(time.time() * 1000)),
        }
        try:
            if self.is_cloud_upload_activity(activity_id):
                self.log("开始家乡打卡文件上传...")
            with open(upload_path, 'rb') as file_obj:
                files = {
                    "uniqueId": (None, f"{int(time.time() * 1000)}_{random.random()}"),
                    "accessToken": (None, token),
                    "psToken": (None, "undefined"),
                    "totalPart": (None, "1"),
                    "partSize": (None, str(file_size)),
                    "partIndex": (None, "1"),
                    "channel": (None, "wocloud"),
                    "directoryId": (None, "0"),
                    "fileName": (None, file_name),
                    "fileSize": (None, str(file_size)),
                    "fileInfo": (None, file_info),
                    "file": (file_name, file_obj, "image/jpeg"),
                }
                res = self.request_direct("POST", self.cloudDiskUrls['activityUpload2C'], headers=headers, files=files, timeout=UNICOM_CLOUD_UPLOAD_TIMEOUT)
            res_json = {}
            try:
                res_json = res.json()
            except:
                pass
            code = str(res_json.get('code', ''))
            meta_code = str(res_json.get('meta', {}).get('code', ''))
            if res.status_code == 200 and (code in ('200', '0', '0000') or meta_code in ('200', '0', '0000')):
                self.cloudDisk.uploadedFileCount = int(getattr(self.cloudDisk, 'uploadedFileCount', 0) or 0) + 1
                if self.is_cloud_upload_activity(activity_id):
                    self.log("家乡打卡 - 上传成功")
                else:
                    self.log("云盘任务: 活动上传成功，正在刷新抽奖次数...")
                return True
            if self.is_cloud_upload_activity(activity_id):
                self.log(f"家乡打卡 - 上传失败: HTTP {res.status_code}")
            else:
                self.log(f"云盘任务: 活动上传失败: HTTP {res.status_code} {res_json if res_json else res.text[:200]}")
        except Exception as e:
            if self.is_cloud_upload_activity(activity_id):
                self.log(f"家乡打卡 - 上传异常: {e}")
            else:
                self.log(f"云盘任务: 活动上传异常: {e}")
        return False

    def wait_cloud_lottery_times_cloud(self, activity_id, wait_seconds=8):
        headers = self.build_cloud_lottery_headers()
        if not headers:
            return None
        for _ in range(wait_seconds):
            time.sleep(1)
            try:
                res = self.query_cloud_lottery_times_cloud(activity_id, headers)
                if isinstance(res, dict) and str(res.get('meta', {}).get('code')) == '200' and self.get_cloud_lottery_draw_count(res) > 0:
                    return res
            except Exception:
                pass
        return getattr(self.cloudDisk, 'lotteryTimesResult', None)

    CLOUD_UPLOAD_ACTIVITY_KEYWORDS = ("上传", "云端对决")

    def is_cloud_upload_activity(self, activity_id):
        """判断活动是否属于"文件上传/家乡打卡"家族（需走 hometown 头与上传链路）"""
        upload_ids = getattr(self.cloudDisk, 'uploadActivityIds', None)
        if upload_ids is None:
            return activity_id == 'MjU='
        return activity_id in upload_ids

    def fetch_cloud_activity_catalog_cloud(self):
        """拉取云盘活动清单，返回 [{num, code, description, upload}]，按 id 倒序"""
        headers = self.build_cloud_lottery_headers()
        if not headers:
            return []
        try:
            hh = dict(headers)
            hh['requestTime'] = str(int(time.time() * 1000))
            res = self.session.get(self.cloudDiskUrls['activityList'], headers=hh, timeout=15).json()
            items = (res.get('result') or {}).get('activityInfoRspList') or []
        except Exception as e:
            self.log(f"云盘任务: 拉取活动清单失败: {e}")
            return []
        catalog = []
        for item in items:
            try:
                num = int(item.get('id'))
            except (TypeError, ValueError):
                continue
            desc = str(item.get('description') or '')
            catalog.append({
                'num': num,
                'code': base64.b64encode(str(num).encode()).decode(),
                'description': desc,
                'upload': any(k in desc for k in self.CLOUD_UPLOAD_ACTIVITY_KEYWORDS),
            })
        catalog.sort(key=lambda x: x['num'], reverse=True)
        return catalog

    def probe_cloud_activity_live_cloud(self, activity_id, headers):
        """探测活动是否存活，返回 (是否有效, 响应)；90003603=存在但本次无次数"""
        try:
            hh = dict(headers)
            hh['requestTime'] = str(int(time.time() * 1000))
            res = self.session.get(self.cloudDiskUrls['lottery_times'], params={"activityId": activity_id}, headers=hh, timeout=10).json()
        except Exception:
            return False, None
        return str(res.get('meta', {}).get('code')) in ('200', '90003603'), res

    def get_cloud_lottery_activity_id_cloud(self):
        if getattr(self.cloudDisk, 'lotteryActivityId', None):
            return self.cloudDisk.lotteryActivityId
        headers = self.build_cloud_lottery_headers()
        if not headers:
            return None
        custom_id = os.environ.get("UNICOM_CLOUD_LOTTERY_ACTIVITY_ID", "").strip()
        if custom_id:
            ok, res = self.probe_cloud_activity_live_cloud(custom_id, headers)
            if ok:
                self.cloudDisk.lotteryActivityId = custom_id
                self.cloudDisk.lotteryTimesResult = res
                self.log(f"云盘任务: 使用指定抽奖活动[{custom_id}]")
                return custom_id
            self.log(f"云盘任务: 指定抽奖活动[{custom_id}] 无效: {res}")
            return None

        # 自动发现：活动清单 -> 探测存活 -> 优先"上传大比拼"家族
        catalog = self.fetch_cloud_activity_catalog_cloud()
        if not catalog:
            self.log("云盘任务: 活动清单为空，回退默认活动[Mzg=]")
            catalog = [{'num': 38, 'code': 'Mzg=', 'description': '', 'upload': True}]
        self.cloudDisk.uploadActivityIds = {it['code'] for it in catalog if it['upload']}
        live = []
        for item in catalog[:12]:
            ok, res = self.probe_cloud_activity_live_cloud(item['code'], headers)
            if ok:
                item = dict(item)
                item['res'] = res
                live.append(item)
            time.sleep(0.2)
        if not live:
            self.log("云盘任务: 未发现存活的云盘抽奖活动")
            return None
        for item in live:
            self.log(f"云盘任务: 存活活动[{item['num']}] {item['description'] or '未命名'}")
        self.cloudDisk.liveCloudActivities = live
        chosen = next((it for it in live if it['upload']), live[0])
        self.cloudDisk.lotteryActivityId = chosen['code']
        self.cloudDisk.lotteryTimesResult = chosen.get('res')
        self.log(f"云盘任务: 选中抽奖活动[{chosen['num']}] {chosen['description'] or '未命名'}")
        return chosen['code']

    def cloud_lottery_timestamp_cloud(self, key=None):
        """获取 /activity/getTimestamp 的 nonce/timestamp。
        注意: nonce 为一次性凭证, 每次抽奖都必须重新获取, 复用会返回 90000111 验签失败。"""
        self.init_cloud_urls()
        key = key or CLOUD_LOTTERY_TS_KEY
        headers = self.build_cloud_hometown_headers({'Content-Type': 'application/json'})
        if not headers:
            return None
        try:
            res = self.session.post(
                self.cloudDiskUrls['lotteryTimestamp'],
                json={"key": key}, headers=headers, timeout=10,
            ).json()
            info = res.get('result') or {}
            if str((res.get('meta') or {}).get('code')) == '200' and info.get('nonce') and info.get('timestamp'):
                return info
            self.log(f"云盘任务: 获取抽奖时间戳失败: {res}")
        except Exception as e:
            self.log(f"云盘任务: 获取抽奖时间戳异常: {e}")
        return None

    def sign_cloud_lottery_body_cloud(self, payload):
        """云盘 /activity/lottery 验签: 将 body 各字段按 key 升序拼成 k=v&k=v, 末尾追加 &secret=KEY,
        再做 HMAC-SHA256 得到 sign (签名放在 body 里, 不是请求头)。"""
        parts = []
        for k in sorted(payload.keys()):
            if k == 'sign':
                continue
            v = payload.get(k)
            if v is None:
                continue
            text = str(v).strip()
            if not text:
                continue
            parts.append(f"{k}={text}")
        raw = "&".join(parts) + f"&secret={CLOUD_LOTTERY_SECRET}"
        return hmac.new(CLOUD_LOTTERY_SECRET.encode('utf-8'), raw.encode('utf-8'), hashlib.sha256).hexdigest()

    def draw_lottery_cloud(self):
        headers = self.build_cloud_lottery_headers()
        if not headers:
            return
        activity_id = self.get_cloud_lottery_activity_id_cloud()
        if not activity_id:
            self.log("云盘任务: 未找到有效抽奖活动")
            return
        try:
            times_res = getattr(self.cloudDisk, 'lotteryTimesResult', None)
            if not isinstance(times_res, dict):
                times_res = self.query_cloud_lottery_times_cloud(activity_id, headers)
            times_code = str(times_res.get('meta', {}).get('code'))
            draw_count = self.get_cloud_lottery_draw_count(times_res) if times_code == '200' else 0
            # draw_count < 0 = 不限次数(权益活动), 不需要走"上传换次数"链路, 交给权益活动模块处理
            if draw_count >= 0 and (times_code == '90003603' or draw_count == 0):
                if self.ensure_cloud_lottery_activity_open_cloud(activity_id) and self.do_activity_upload_cloud(activity_id):
                    refreshed = self.wait_cloud_lottery_times_cloud(activity_id)
                    if isinstance(refreshed, dict):
                        times_res = refreshed
                        times_code = str(times_res.get('meta', {}).get('code'))
                        draw_count = self.get_cloud_lottery_draw_count(times_res) if times_code == '200' else 0
            if self.is_cloud_upload_activity(activity_id):
                self.query_cloud_lottery_record_cloud(activity_id)
            if times_code == '90003603':
                if self.is_cloud_upload_activity(activity_id):
                    self.log("家乡打卡 - 抽奖失败：没有抽奖机会")
                else:
                    self.log(f"云盘任务: 抽奖活动[{activity_id}] 活动上传后仍未获得抽奖次数")
                return
            if times_code != '200':
                self.log(f"云盘任务: 查询抽奖次数失败: {times_res}")
                return
            if draw_count < 0:
                self.log(f"云盘任务: 抽奖活动[{activity_id}] 为不限次数权益活动，交由权益活动模块抽取")
                return
            if draw_count == 0:
                if self.is_cloud_upload_activity(activity_id):
                    self.log("家乡打卡 - 抽奖失败：没有抽奖机会")
                else:
                    self.log(f"云盘任务: 抽奖活动[{activity_id}] 当前无抽奖次数")
                return
            for idx in range(draw_count):
                # 每次抽奖都要取一份新的 nonce/timestamp 并重新签名 (nonce 一次性)
                ts_info = self.cloud_lottery_timestamp_cloud()
                if not ts_info:
                    self.log("云盘任务: 抽奖中断, 未能获取签名时间戳")
                    return
                draw_headers = dict(headers)
                draw_headers['requestTime'] = str(int(time.time() * 1000))
                draw_headers['Content-Type'] = 'application/json'
                body = {
                    'activityId': activity_id,
                    'nonce': ts_info.get('nonce'),
                    'timestamp': ts_info.get('timestamp'),
                }
                body['sign'] = self.sign_cloud_lottery_body_cloud(body)
                res = self.session.post(self.cloudDiskUrls['lottery'], json=body, headers=draw_headers, timeout=10).json()
                code = str((res.get('meta') or {}).get('code'))
                if code == '92000017':
                    self.log("云盘任务: 转盘已抽奖")
                    return
                if code == '90000111':
                    self.log(f"云盘任务: 第{idx + 1}次抽奖验签失败: {res}")
                    return
                if 'result' in res:
                    if self.is_cloud_upload_activity(activity_id):
                        self.log(f"家乡打卡 - 抽奖结果：{res['result'].get('prizeName', '')}", notify=True)
                    else:
                        self.log(f"云盘任务: 转盘获得: {res['result'].get('prizeName', '')}", notify=True)
                    continue
                self.log(f"云盘任务: 抽奖无结果: {res}")
        except Exception as e:
            self.log(f"云盘任务: 抽奖失败: {e}")

    # ==================== 云盘「不限次数」权益活动 (39/41) ====================
    def collect_cloud_benefit_activities_cloud(self):
        """找出所有"不限次数"的云盘权益活动 (lottery-times 返回负数)。

        判定口径: get_cloud_lottery_draw_count() < 0  →  -1 = 不限次数 (每抽必中)
        数据来源优先级:
          1) 环境变量 UNICOM_CLOUD_BENEFIT_ACTIVITY_IDS (逗号分隔 base64 活动码)
          2) self.cloudDisk.liveCloudActivities (get_cloud_lottery_activity_id_cloud 已探好)
          3) 自己拉活动清单 + 逐个探测
        """
        if CLOUD_BENEFIT_ACTIVITY_IDS:
            return [{'num': None, 'code': c, 'description': '指定权益活动'} for c in CLOUD_BENEFIT_ACTIVITY_IDS]
        live = getattr(self.cloudDisk, 'liveCloudActivities', None) or []
        if not live:
            headers = self.build_cloud_lottery_headers()
            if not headers:
                return []
            catalog = self.fetch_cloud_activity_catalog_cloud()
            live = []
            for item in catalog[:12]:
                ok, res = self.probe_cloud_activity_live_cloud(item['code'], headers)
                if ok:
                    item = dict(item)
                    item['res'] = res
                    live.append(item)
                time.sleep(0.2)
            self.cloudDisk.liveCloudActivities = live
        picked = []
        for item in live:
            if item.get('upload'):
                continue
            item = dict(item)
            item['drawCount'] = self.get_cloud_lottery_draw_count(item.get('res') or {})
            if item['drawCount'] < 0:
                picked.append(item)
        return picked

    def draw_benefit_activities_cloud(self):
        """补充抽取「不限次数」权益活动。

        原 draw_lottery_cloud() 只处理 1 个活动, 且把 times=-1 当成"没次数"跳过,
        导致 39(权益大放送-山东海南) / 41(权益放送-上海重庆) 一直没被抽到。
        """
        if not CLOUD_BENEFIT_ENABLE or CLOUD_BENEFIT_DRAW_TIMES <= 0:
            return
        headers = self.build_cloud_lottery_headers()
        if not headers:
            return
        try:
            activities = self.collect_cloud_benefit_activities_cloud()
        except Exception as e:
            self.log(f"云盘任务: 查找权益活动异常: {e}")
            return
        if not activities:
            self.log("云盘任务: 未发现不限次数的权益活动")
            return
        total = 0
        for item in activities:
            code = item['code']
            name = item.get('description') or code
            label = f"[{item['num']}]{name}" if item.get('num') else name
            got = 0
            for idx in range(CLOUD_BENEFIT_DRAW_TIMES):
                # nonce 一次性, 每次都要重新取
                ts_info = self.cloud_lottery_timestamp_cloud()
                if not ts_info:
                    self.log(f"云盘任务: 权益活动{label} 抽奖中断, 未能获取签名时间戳")
                    break
                draw_headers = dict(headers)
                draw_headers['requestTime'] = str(int(time.time() * 1000))
                draw_headers['Content-Type'] = 'application/json'
                body = {
                    'activityId': code,
                    'nonce': ts_info.get('nonce'),
                    'timestamp': ts_info.get('timestamp'),
                }
                body['sign'] = self.sign_cloud_lottery_body_cloud(body)
                try:
                    res = self.session.post(self.cloudDiskUrls['lottery'], json=body, headers=draw_headers, timeout=10).json()
                except Exception as e:
                    self.log(f"云盘任务: 权益活动{label} 抽奖异常: {e}")
                    break
                mcode = str((res.get('meta') or {}).get('code'))
                if mcode == '200' and 'result' in res:
                    prize = (res.get('result') or {}).get('prizeName', '')
                    got += 1
                    total += 1
                    self.log(f"云盘任务: 权益活动{label} 第{idx + 1}次获得: {prize}", notify=True)
                    path_use_notice = (res.get('result') or {}).get('pathUseNotice')
                    if path_use_notice:
                        self.log(f"   使用路径: {path_use_notice}")
                elif mcode == '92000017':
                    self.log(f"云盘任务: 权益活动{label} 本轮已抽过")
                    break
                elif mcode == '90000111':
                    self.log(f"云盘任务: 权益活动{label} 验签失败: {res}")
                    break
                elif mcode == '90000109':
                    self.log(f"云盘任务: 权益活动{label} 没有抽奖机会")
                    break
                else:
                    self.log(f"云盘任务: 权益活动{label} 抽奖无结果: {res}")
                    break
                if CLOUD_BENEFIT_INTERVAL > 0:
                    time.sleep(CLOUD_BENEFIT_INTERVAL)
            if got == 0:
                self.log(f"云盘任务: 权益活动{label} 本次未获得奖品")
        if total:
            self.log(f"云盘任务: 不限次数权益活动共获得 {total} 份奖品", notify=True)

    def get_secret_key_cloud(self):
        if getattr(self.cloudDisk, 'secretKey', None):
            return self.cloudDisk.secretKey
        if not getattr(self.cloudDisk, 'userticket', None) or not getattr(self.cloudDisk, 'jeaId', None):
            return None
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
            'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) LianTongYunPan/4.0.2 (iPhone; iOS 16.6)",
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Origin': 'https://m.jf.10010.com',
            'Host': 'm.jf.10010.com',
            'clienttype': 'yunpan_iOS',
            'partnersid': '1649',
            'ticket': self.cloudDisk.userticket,
            'Cookie': f"_jea_id={self.cloudDisk.jeaId};",
        }
        try:
            res = self.session.get(self.cloudDiskUrls['secretKey'], headers=headers, timeout=10).json()
            secret = res.get('data', {}).get('secretKey')
            if res.get('code') == '0000' and secret:
                self.cloudDisk.secretKey = secret.encode('utf-8')
                self.log("云盘任务: secretKey 获取成功")
                return self.cloudDisk.secretKey
            self.log(f"云盘任务: getSecretKey 失败: {res}")
        except Exception as e:
            self.log(f"云盘任务: getSecretKey 异常: {e}")
        return None

    def build_signature_headers_cloud(self):
        secret_key = self.get_secret_key_cloud()
        if not secret_key:
            return {}
        request_ts = str(round(time.time() * 1000))
        nonce = ''.join(random.choices('0123456789abcdefghijklmnopqrstuvwxyz', k=8))
        signature = hmac.new(
            secret_key, f"{nonce}{request_ts}".encode('utf-8'), hashlib.sha256,
        ).hexdigest()
        return {
            'x-request-timestamp': request_ts,
            'x-request-nonce': nonce,
            'x-request-signature': signature,
        }

    def run_generic_cloud_task(self, task_code, task_name):
        self.log(f"云盘任务: [{task_name}] 尝试通用完成接口")
        self.toFinish_cloud(task_code, task_name, False)
        time.sleep(2)
        self.handle_unknown_task_cloud(task_code, task_name)
        time.sleep(3)
        self.finalize_generic_task_cloud(task_code, task_name)

    def handle_unknown_task_cloud(self, task_code, task_name=""):
        token = getattr(self.cloudDisk, 'userToken', '')
        if not token:
            return False
        headers = {
            'User-Agent': 'LianTongYunPan/5.0.4 (iOS 16.3)',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'Accept-Encoding': 'br;q=1.0, gzip;q=0.9, deflate;q=0.8',
            'Access-Token': token, 'X-YP-Access-Token': token,
            'Client-Id': '1001000035', 'X-YP-Client-Id': '1001000035',
            'App-Version': 'yp-app/5.0.4', 'app-type': 'liantongyunpanapp',
            'Sys-Version': 'iOS/16.3',
            'Accept-Language': 'zh-Hans-CN;q=1.0',
        }
        prefix = f"云盘任务: [{task_name}]" if task_name else "云盘任务: 未知任务"
        try:
            res = self.session.post(
                self.cloudDiskUrls['taskFinish'],
                json={"taskCode": task_code, "taskStatus": {"isBackUp": "1"}},
                headers=headers,
                timeout=10,
            ).json()
            meta_code = str(res.get('meta', {}).get('code'))
            if meta_code == '90003600':
                self.log(f"{prefix} 处理完成")
                return True
            if meta_code in ('200', '0') or str(res.get('code')) in ('200', '0', '0000'):
                self.log(f"{prefix} 处理完成: {res.get('msg', res.get('meta', {}).get('message', '成功'))}")
                return True
            self.log(f"{prefix} 处理失败: {res}")
        except Exception as e:
            self.log(f"云盘任务: [{task_name or task_code}] 处理失败: {e}")
        return False

    def ltyp_task(self, is_query_only=False):
        self.log("==== 联通云盘任务 ====")
        self.init_cloud_urls()
        class CloudDiskState: pass
        self.cloudDisk = CloudDiskState()
        if not self.ecs_token:
            self.log("云盘任务: 缺少 ecs_token，跳过。")
            return
        ticket = self.getTicketByNative_cloud()
        if not ticket: return
        if not hasattr(self, 'city_info') or not self.city_info:
             self.get_city_info()
        token = self.get_ltypDispatcher_cloud(ticket)
        if not token: return
        time.sleep(0.5)
        self.get_userInfo_cloud()
        self.init_cloud_task_records_state()
        if is_query_only:
            self.log("云盘任务: [查询模式] 跳过任务执行...")
            self.get_userInfo_cloud()
            return
        time.sleep(0.5)
        self.get_secret_key_cloud()
        self.get_taskDetail_cloud()
        time.sleep(0.5)
        self.get_userInfo_cloud()
        time.sleep(2)
        self.draw_lottery_cloud()
        time.sleep(2)
        self.draw_benefit_activities_cloud()
        time.sleep(2)
        self.clean_duplicate_files_cloud()

    # ==================== 披荆斩棘2026 · 海岛逐浪应援 ====================
    def island_waves_post(self, path, payload, headers=None, ts_key=None):
        """海岛逐浪应援: 带 nonce/timestamp/sign 的 /activity/* 请求

        验签口径与云盘抽奖**完全一致** → 直接复用 sign_cloud_lottery_body_cloud():
          sign = HMAC-SHA256( "按key升序拼 k=v&k=v" + "&secret=<CLOUD_LOTTERY_SECRET>", SECRET )
          - 参与签名字段 = body 里除 sign 外的全部非空值 (str().strip())
          - sign 放在 body 里, 不是请求头
        ⚠️ nonce 是一次性的, 每次请求都必须重新取 getTimestamp
        ⚠️ getTimestamp 的 key 必须与目标接口匹配(实测: 签到/关卡用 activity:island:activate,
           抽奖 /activity/lottery 用 activity:lottery), 用错 key 会回 90000111 验签失败
        """
        h = headers or self.build_cloud_activity_headers()
        if not h:
            return None
        try:
            ts_res = self.session.post(
                f"{ISLAND_WAVES_BASE}/activity/getTimestamp",
                json={"key": ts_key or ISLAND_WAVES_TS_KEY}, headers=h, timeout=12).json()
        except Exception as e:
            self.log(f"披荆斩棘2026: 获取签名时间戳异常 {e}")
            return None
        info = ts_res.get("result") or {}
        if not info.get("nonce") or not info.get("timestamp"):
            self.log(f"披荆斩棘2026: 获取签名时间戳失败 {response_summary(ts_res)}")
            return None
        body = dict(payload)
        body["nonce"] = info["nonce"]
        body["timestamp"] = info["timestamp"]
        body["sign"] = self.sign_cloud_lottery_body_cloud(body)
        try:
            return self.session.post(f"{ISLAND_WAVES_BASE}{path}", json=body, headers=h, timeout=15).json()
        except Exception as e:
            self.log(f"披荆斩棘2026: {path} 请求异常 {e}")
            return None

    def island_waves_ensure_login(self):
        """确保有云盘登录态 (userToken); 复用 ltyp_task 建立的, 没有就自己走一遍"""
        if getattr(getattr(self, "cloudDisk", None), "userToken", None):
            return True
        self.init_cloud_urls()
        if not self.ecs_token:
            self.log("披荆斩棘2026: ⏭️ 缺少 ecs_token，跳过")
            return False
        class _CloudDiskState: pass
        self.cloudDisk = _CloudDiskState()
        if not self.getTicketByNative_cloud():
            return False
        if not self.get_ltypDispatcher_cloud(self.cloudDisk.ticket):
            return False
        time.sleep(0.3)
        return True

    def island_waves_stage1(self, headers):
        """第1关: 转存指定哥哥的海报 → 登顶值+20 / 抽奖+1

        ⚠️ 不可逆: 登顶值将作为助力值**永久共享**给该哥哥(官方原文: 不可更改哥哥及取消共享),
           同时在个人云盘写入 1 张 jpg。选谁由 ISLAND_WAVES_TARGET 决定, 不要在代码里随机。
        """
        target = (ISLAND_WAVES_TARGET or "").strip()
        if not target:
            self.log("第1关: ⏭️ 未配置 UNICOM_ISLANDWAVES_TARGET(哥哥名)，跳过第1关")
            return False
        try:
            res = self.session.get(
                f"{ISLAND_WAVES_BASE}/activity/poster/list",
                params={"activityId": ISLAND_WAVES_ACT_ID},
                headers=headers, timeout=12).json()
        except Exception as e:
            self.log(f"第1关-海报列表异常: {e}")
            return False
        posters = res.get("result") or []
        if not posters:
            self.log(f"第1关-海报列表为空: {response_summary(res)}")
            return False
        pick = next((p for p in posters if str(p.get("targetName") or "").strip() == target), None)
        if not pick:
            names = " / ".join(str(p.get("targetName") or "") for p in posters[:10])
            self.log(f"❌ 第1关-未找到哥哥[{target}]；可选前10位: {names}", notify=True)
            return False
        body = {
            "activityId": ISLAND_WAVES_ACT_ID,
            "fids": [pick.get("fid")],
            "taskType": 10,
            "fileType": 2,
            "fileName": pick.get("fileName"),
            "directoryId": 0,
            "additionalParams": {"aiHeaderSubType": 0},
        }
        try:
            r = self.session.post(
                f"{ISLAND_WAVES_BASE}/wohome/open/v1/ai/moveFile2Person",
                json=body, headers=headers, timeout=20).json()
        except Exception as e:
            self.log(f"第1关-转存异常: {e}")
            return False
        if str((r.get("meta") or {}).get("code")) == "200":
            self.log(f"🎬 [披荆斩棘2026] 第1关已转存[{target}]海报，登顶值+20、抽奖+1", notify=True)
            return True
        self.log(f"❌ 第1关-转存[{target}]失败: {response_summary(r)}", notify=True)
        return False

    def island_waves_checkin(self, headers):
        """第2关: 每日签到 (前置: 必须已过第1关, 否则回 92000010)"""
        month = datetime.now().strftime("%Y-%m")
        # ⚠️ panel 必须带 month("2026-09"), 只传 activityId 会回 90003600 参数错误
        panel = self.island_waves_post(
            "/activity/islandWaves/task2/checkin/panel",
            {"activityId": ISLAND_WAVES_ACT_ID, "month": month}, headers)
        if not panel:
            return False
        if str((panel.get("meta") or {}).get("code")) != "200":
            self.log(f"❌ 签到面板查询失败: {response_summary(panel)}")
            return False
        data = panel.get("result") or {}
        today = next((x for x in (data.get("calendarList") or []) if x.get("isToday")), None) or {}
        days = safe_int(data.get("continuousCheckinDays"), 0) or 0
        if today.get("isChecked"):
            self.log(f"✅ [披荆斩棘2026] 今日已签到 (连续 {days} 天)")
            return True
        res = self.island_waves_post(
            "/activity/islandWaves/task2/checkin/submit",
            {"activityId": ISLAND_WAVES_ACT_ID}, headers)
        if not res:
            return False
        r_code = str((res.get("meta") or {}).get("code"))
        if r_code == "200" and res.get("result") is True:
            reward = safe_int(today.get("rewardPoints"), 0) or 0
            self.log(f"🎬 [披荆斩棘2026] 签到成功，登顶值 +{reward}（连续 {days + 1} 天）", notify=True)
            return True
        if r_code == "92000010":
            self.log("❌ [披荆斩棘2026] 签到失败：需先完成第1关（转存哥哥海报）", notify=True)
            return False
        self.log(f"❌ [披荆斩棘2026] 签到失败: {response_summary(res)}", notify=True)
        return False

    def island_waves_lottery(self, headers):
        """转盘抽奖 (与云盘抽奖同一签名口径, 活动码换成 NDA=)"""
        try:
            t_res = self.session.get(
                f"{ISLAND_WAVES_BASE}/activity/lottery/lottery-times",
                params={"activityId": ISLAND_WAVES_ACT_ID},
                headers=headers, timeout=12).json()
        except Exception as e:
            self.log(f"披荆斩棘2026-抽奖: 查询次数异常 {e}")
            return
        if str((t_res.get("meta") or {}).get("code")) != "200":
            self.log(f"披荆斩棘2026-抽奖: 查询次数失败 {response_summary(t_res)}")
            return
        try:
            times = int(str(t_res.get("result")).strip())
        except Exception:
            times = 0
        if times <= 0:
            self.log("披荆斩棘2026-抽奖: 当前无抽奖次数")
            return
        self.log(f"披荆斩棘2026-抽奖: 可抽 {times} 次")
        for i in range(min(times, 10)):
            res = self.island_waves_post(
                "/activity/lottery", {"activityId": ISLAND_WAVES_ACT_ID}, headers,
                ts_key=CLOUD_LOTTERY_TS_KEY)
            if not res:
                return
            code = str((res.get("meta") or {}).get("code"))
            if code == "92000017":
                self.log("披荆斩棘2026-抽奖: 已抽完")
                return
            if code != "200":
                self.log(f"披荆斩棘2026-抽奖: 第{i + 1}次失败 {response_summary(res)}")
                return
            prize = (res.get("result") or {}).get("prizeName") or "未中奖"
            self.log(f"🎬 [披荆斩棘2026] 抽奖: {prize}", notify=True)
            time.sleep(1)

    def island_ai_video(self):
        """海岛逐浪应援 第3步: 芒果「AI 入戏」视频制作 (移植自上游 v1.2.0)

        流程: 云盘 token 换云盘 ticket → mgtv 登录 → popup/check → 提交模板生成视频。
        ⚠️ 模板 ID / 素材 FID 是**海岛逐浪活动专用**，与已下线的乘风不是同一套。
        三类可重试/兜底情况都会自动处理:
          ① 「照片识别失败」= 芒果对同一素材的短时频控(多账号连跑只有第1个通过) → 等待后重试
          ② 响应为空 / 非 JSON (多账号连跑偶发, 状态码正常但 body 为空) → 等待后重试
          ③ 「权益扣减失败」→ 先 offlineSubscribe 领权益再重试一次
        """
        token = getattr(getattr(self, "cloudDisk", None), "userToken", "") or ""
        if not token:
            self.log("海岛逐浪: AI入戏缺少云盘 token，跳过")
            return
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) LianTongYunPan/6.0.0 (iPhone; iOS 16.6)",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "X-YP-GRAY-FLAG": "undefined",
            "requestTime": str(int(time.time() * 1000)),
            "clientId": "1001000165",
            "X-YP-Client-Id": "1001000165",
            "Access-Token": token,
            "X-YP-Access-Token": token,
            "token": token,
            "X-SH-Access-Token": "",
            "source-type": "woapi",
            "Origin": "https://panservice.mail.wo.cn",
            "Referer": (
                f"{ISLAND_WAVES_BASE}/h5/activitymobile/cmf2026/home"
                f"?activityId={quote(ISLAND_WAVES_ACT_ID)}&touchpoint=300300010005&token={token}"
            ),
        }
        try:
            res = self.session.post(
                f"{ISLAND_WAVES_BASE}/api-user/api/user/ticket",
                json={}, headers=headers, timeout=20,
            ).json()
        except Exception as e:
            self.log(f"海岛逐浪: AI入戏获取凭据异常 {e}")
            return
        ticket = (res.get("result") or {}).get("ticket")
        if not ticket:
            self.log(f"海岛逐浪: AI入戏未获取到登录凭据 {response_summary(res)}")
            return

        base = ISLAND_AI_MGTV_BASE
        mgtv_headers = {
            "User-Agent": headers["User-Agent"],
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": "https://pop.mgtv.com",
            "Referer": "https://pop.mgtv.com/",
            "sec-fetch-site": "same-site",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "accept-language": "zh-CN,zh-Hans;q=0.9",
        }
        try:
            login = self.session.get(
                base + "/api/cu/login",
                params={"ticket": ticket, "t": int(time.time() * 1000)},
                headers=mgtv_headers, timeout=30,
            ).json()
        except Exception as e:
            self.log(f"海岛逐浪: AI入戏登录异常 {e}")
            return
        mgtv_ticket = (login.get("data") or {}).get("ticket")
        if not mgtv_ticket:
            self.log(f"海岛逐浪: AI入戏登录失败 {response_summary(login)}")
            return
        try:
            self.session.get(
                base + "/api/cu/popup/check",
                params={"ticket": mgtv_ticket, "t": int(time.time() * 1000)},
                headers=mgtv_headers, timeout=30,
            )
        except Exception:
            pass

        def _submit():
            """提交模板生成。返回 (json, status, detail); 响应非 JSON / 网络异常时 json=None。"""
            try:
                resp = self.session.post(base + "/api/cu/video/template/submit", json={
                    "ticket": mgtv_ticket,
                    "t": int(time.time() * 1000),
                    "templateId": ISLAND_AI_TEMPLATE_ID,
                    "index": 0,
                    "imgUrl": ISLAND_AI_IMG_FID,
                }, headers=mgtv_headers, timeout=30)
            except Exception as e:
                return None, None, "网络异常: %s" % e
            status = getattr(resp, "status_code", "?")
            raw = resp.text or ""
            try:
                return resp.json(), status, raw[:300]
            except Exception:
                return None, status, raw[:300]

        def _need_retry(result):
            """可重试 = 没有 taskId 且 (芒果短时频控 或 响应不可解析/为空)"""
            if not isinstance(result, dict):
                return True
            if (result.get("data") or {}).get("taskId"):
                return False
            return "照片识别失败" in str(result.get("msg", ""))

        try:
            result, status, detail = _submit()
            # 提交重试兜底 (上游原版没有, 2026-10-06 多账号实测补上):
            #   ① 「照片识别失败」= 芒果对同一素材的短时频控(3 账号 16 秒内连提交只有第 1 个通过,
            #      单独隔 30 秒再提交连续 2 次成功) → 等待后重试;
            #   ② 响应为空/非 JSON(实测账号连跑偶发: 状态码正常但 body 为空) → 同样等待重试。
            freq = 0
            while _need_retry(result) and freq < ISLAND_AI_RETRY_TIMES:
                freq += 1
                why = "响应不可解析/为空" if not isinstance(result, dict) else "素材被频控"
                self.log(f"海岛逐浪: AI入戏{why}(状态{status})，{ISLAND_AI_RETRY_WAIT} 秒后重试"
                         f" ({freq}/{ISLAND_AI_RETRY_TIMES})")
                time.sleep(ISLAND_AI_RETRY_WAIT)
                result, status, detail = _submit()
            if not isinstance(result, dict):
                self.log(f"海岛逐浪: AI入戏提交失败 状态{status} {detail}")
                return
            # 权益扣减兜底: 先领权益再重试一次
            if not (result.get("data") or {}).get("taskId") and "权益扣减失败" in str(result.get("msg", "")):
                try:
                    grant = self.session.get(
                        base + "/api/cu/offlineSubscribe",
                        params={"ticket": mgtv_ticket, "t": int(time.time() * 1000)},
                        headers=mgtv_headers, timeout=30,
                    ).json()
                except Exception as e:
                    self.log(f"海岛逐浪: AI入戏领权益异常 {e}")
                    return
                ok = str((grant.get("data") or {}).get("success")) in ("1", "True", "true")
                if ok:
                    time.sleep(10)
                    result, status, detail = _submit()
                    if not isinstance(result, dict):
                        self.log(f"海岛逐浪: AI入戏提交失败 状态{status} {detail}")
                        return
                else:
                    self.log(f"海岛逐浪: AI入戏权益未满足 {response_summary(grant)}")
                    return
            if (result.get("data") or {}).get("taskId"):
                self.log("海岛逐浪: AI入戏制作已提交", notify=True)
            else:
                self.log(f"海岛逐浪: AI入戏未完成 {response_summary(result)}")
        except Exception as e:
            self.log(f"海岛逐浪: AI入戏提交异常 {e}")

    def island_waves_task(self, query_only=False):
        """披荆斩棘2026 · 海岛逐浪应援 (联通云盘活动) 总入口

        关卡: 1=转存哥哥海报  2=每日签到  3=应援打榜  4=聚力/邀请
        本函数只做 1/2 + 转盘抽奖 (3/4 需人工参与, 不自动化)
        """
        self.log("==== 披荆斩棘2026 · 海岛逐浪应援 ====")
        if not self.island_waves_ensure_login():
            return
        headers = self.build_cloud_activity_headers()
        if not headers:
            return

        # 开启活动 (幂等) + 查关卡进度
        self.island_waves_post("/activity/task/activate", {
            "activityId": ISLAND_WAVES_ACT_ID,
            "touchpoint": ISLAND_WAVES_TOUCHPOINT,
            "isMember": "0",
            "signed": "0",
        }, headers)
        max_pass = 0
        prog = self.island_waves_post(
            "/activity/user/levelProgress", {"activityId": ISLAND_WAVES_ACT_ID}, headers)
        if prog and str((prog.get("meta") or {}).get("code")) == "200":
            max_pass = safe_int((prog.get("result") or {}).get("maxPassLevel"), 0) or 0
        self.log(f"当前已通过 {max_pass} 关 (哥哥: {ISLAND_WAVES_TARGET or '未设置'})")

        if query_only:
            panel = self.island_waves_post(
                "/activity/islandWaves/task2/checkin/panel",
                {"activityId": ISLAND_WAVES_ACT_ID, "month": datetime.now().strftime("%Y-%m")}, headers)
            if panel and str((panel.get("meta") or {}).get("code")) == "200":
                d = panel.get("result") or {}
                t = next((x for x in (d.get("calendarList") or []) if x.get("isToday")), None) or {}
                self.log(f"  └─ 今日签到: {'已签' if t.get('isChecked') else '未签'}"
                         f" | 连续 {safe_int(d.get('continuousCheckinDays'), 0)} 天")
            return

        if max_pass < 1:
            self.island_waves_stage1(headers)
            time.sleep(1)
        self.island_waves_checkin(headers)
        time.sleep(1)
        # 第3步: 芒果「AI 入戏」视频 (移植自上游 v1.2.0)
        if ISLAND_AI_ENABLE:
            self.island_ai_video()
        time.sleep(1)
        self.island_waves_lottery(headers)

    def getTicketByNative_sec(self):
        for attempt in range(1, 4):
            try:
                url = f"https://m.client.10010.com/edop_ng/getTicketByNative?token={self.ecs_token}&appId=edop_unicom_3a6cc75a"
                city_code = ""
                cookie_str = f"PvSessionId={datetime.now().strftime('%Y%m%d%H%M%S')}{self.unicomTokenId};c_mobile={self.account_mobile}; c_version=iphone_c@11.0800; city=036|{city_code}|90063345|-99;devicedId={self.unicomTokenId}; ecs_token={self.ecs_token};t3_token="
                headers = {
                    "Cookie": cookie_str,
                    "Accept": "*/*",
                    "Connection": "keep-alive",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "User-Agent": "ChinaUnicom4.x/12.3.1 (com.chinaunicom.mobilebusiness; build:77; iOS 16.6.0) Alamofire/4.7.3 unicom{version:iphone_c@12.0301}",
                    "Accept-Language": "zh-Hans-CN;q=1.0"
                }
                res = self.session.get(url, headers=headers, timeout=10)
                if res.status_code != 200:
                    self.log(f"安全管家: getTicketByNative_sec http请求失败 {res.status_code}")
                    return
                try:
                    result = res.json()
                except:
                    self.log(f"安全管家: getTicketByNative_sec json解析失败: {res.text[:100]}")
                    return
                self.sec_ticket1 = result.get('ticket')
                if self.sec_ticket1:
                    return
                else:
                    self.log(f"安全管家: getTicketByNative_sec 失败 - {result}")
            except Exception as e:
                err_msg = str(e)
                if attempt < 3 and os.environ.get("UNICOM_PROXY_API") and ("Max retries exceeded" in err_msg or "timed out" in err_msg.lower() or "connection" in err_msg.lower() or "SOCKS" in err_msg):
                    self.log(f"安全管家: getTicketByNative_sec 第{attempt}次异常触发故障转移: {err_msg}")
                    self.failover_proxy()
                    continue
                self.log(f"安全管家: getTicketByNative_sec 第{attempt}次重试 - 异常: {e}")
                time.sleep(2)

    def getAuthToken_sec(self):
        if not getattr(self, 'sec_ticket1', None):
            self.log("安全管家 getAuthToken_sec 缺少 ticket1，跳过")
            return
        try:
            url = "https://uca.wo116114.com/api/v1/auth/ticket?product_line=uasp&entry_point=h5&entry_point_id=edop_unicom_3a6cc75a"
            headers = {
                "User-Agent": "ChinaUnicom4.x/12.3.1 (com.chinaunicom.mobilebusiness; build:77; iOS 16.6.0) Alamofire/4.7.3 unicom{version:iphone_c@12.0301}",
                "Content-Type": "application/json",
                "clientType": "uasp_unicom_applet"
            }
            data = { "productId": "", "type": 1, "ticket": self.sec_ticket1 }
            res = self.session.post(url, json=data, headers=headers).json()
            if res.get('data'):
                self.sec_token = res['data'].get('access_token')
            else:
                self.log(f"安全管家: getAuthToken_sec 失败 - {res}")
        except Exception as e:
            self.log(f"安全管家: getAuthToken_sec 异常: {e}")

    def getTicketForJF_sec(self):
        if not getattr(self, 'sec_token', None):
            self.log("安全管家 getTicketForJF_sec 缺少 token，跳过")
            return
        try:
            url1 = "https://uca.wo116114.com/api/v1/auth/getTicket?product_line=uasp&entry_point=h5&entry_point_id=edop_unicom_3a6cc75a"
            headers1 = {
                "User-Agent": "ChinaUnicom4.x/12.3.1 (com.chinaunicom.mobilebusiness; build:77; iOS 16.6.0) Alamofire/4.7.3 unicom{version:iphone_c@12.0301}",
                "Content-Type": "application/json",
                "auth-sa-token": self.sec_token,
                "clientType": "uasp_unicom_applet"
            }
            data1 = { "productId": "91311616", "phone": self.account_mobile }
            res1 = self.session.post(url1, json=data1, headers=headers1).json()
            if res1.get('data'):
                self.sec_ticket = res1['data'].get('ticket')
            else:
                self.log("安全管家获取积分票据失败")
                return
            url2 = "https://m.jf.10010.com/jf-external-application/page/query"
            headers2 = {
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 unicom{version:iphone_c@12.0301};ltst;OSVersion/16.6",
                "partnersid": "1702",
                "ticket": unquote(self.sec_ticket),
                "clienttype": "uasp_unicom_applet",
            }
            if hasattr(self, 'sec_jeaId'):
                headers2["Cookie"] = f"_jea_id={self.sec_jeaId}"
            res2 = self.session.post(url2, json={"activityId": "s747395186896173056", "partnersId": "1702"}, headers=headers2)
            res2 = self.session.post(url2, json={"activityId": "s747395186896173056", "partnersId": "1702"}, headers=headers2)
            for cookie in self.session.cookies:
                if cookie.name == '_jea_id':
                    self.sec_jeaId = cookie.value
            if 'Set-Cookie' in res2.headers:
                match = re.search(r'_jea_id=([^;]+)', res2.headers['Set-Cookie'])
                if match:
                    self.sec_jeaId = match.group(1)
        except Exception as e:
            self.log(f"安全管家: getTicketForJF_sec 异常: {e}")

    def get_secret_key_sec(self, silent=False):
        if getattr(self, 'sec_secretKey', None):
            return self.sec_secretKey
        if not getattr(self, 'sec_ticket', None):
            return None
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 unicom{version:iphone_c@12.0301};ltst;OSVersion/16.6",
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Origin': 'https://m.jf.10010.com',
            'Host': 'm.jf.10010.com',
            'clienttype': 'uasp_unicom_applet',
            'partnersid': '1702',
            'ticket': unquote(self.sec_ticket),
        }
        if hasattr(self, 'sec_jeaId') and self.sec_jeaId:
            headers['Cookie'] = f"_jea_id={self.sec_jeaId};"
        try:
            res = self.session.get("https://m.jf.10010.com/jf-external-application/jftask/getSecretKey", headers=headers, timeout=10).json()
            secret = res.get('data', {}).get('secretKey')
            if res.get('code') == '0000' and secret:
                self.sec_secretKey = secret.encode('utf-8')
                if not silent:
                    self.log("secretKey 获取成功")
                return self.sec_secretKey
            self.log(f"安全管家: getSecretKey 失败: {res}")
        except Exception as e:
            self.log(f"安全管家: getSecretKey 异常: {e}")
        return None

    def build_signature_headers_sec(self):
        secret_key = self.get_secret_key_sec()
        if not secret_key:
            return {}
        request_ts = str(round(time.time() * 1000))
        nonce = ''.join(random.choices('0123456789abcdefghijklmnopqrstuvwxyz', k=8))
        signature = hmac.new(
            secret_key, f"{nonce}{request_ts}".encode('utf-8'), hashlib.sha256,
        ).hexdigest()
        return {
            'x-request-timestamp': request_ts,
            'x-request-nonce': nonce,
            'x-request-signature': signature,
        }

    def sec_uca_post(self, url_path, body):
        try:
            headers = {
                "clientType": "uasp_unicom_applet",
                "auth-sa-token": self.sec_token,
                "Content-Type": "application/json",
                "Accept": "*",
                "User-Agent": "ChinaUnicom4.x/12.3.1 (com.chinaunicom.mobilebusiness; build:77; iOS 16.6.0) Alamofire/4.7.3 unicom{version:iphone_c@12.0301}"
            }
            return self.session.post(url_path, json=body, headers=headers, timeout=10).json()
        except Exception as e:
            self.log(f"安全管家: uca_post 异常: {e}")
            return None

    def addToBlacklist_sec(self):
        url = "https://uca.wo116114.com/sjgj/woAssistant/umm/configs/v1/config?product_line=uasp&entry_point=h5&entry_point_id=wxdefbc1986dc757a6"
        self.sec_uca_post(url, {
            "productId": "91242950", "operationType": 1, "type": 1,
            "contents": [{"checked": True, "configTime": None, "nickname": None, "contentTag": "疑似诈骗", "content": "13800138000"}]
        })
        time.sleep(2)
        self.sec_uca_post(url, {
            "productId": "91242950", "blacklistSource": 0, "type": 1, "operationType": 0,
            "contents": [{"contentTag": "疑似诈骗", "content": "13800138000"}]
        })

    def markPhoneNumber_sec(self):
        url = "https://uca.wo116114.com/sjgj/unicomAssistant/uasp/configs/v1/addressBook/saveTagPhone?product_line=uasp&entry_point=h5&entry_point_id=wxdefbc1986dc757a6"
        self.sec_uca_post(url, {"productId": "91311616", "status": 0, "tagIds": [26], "tagPhoneNo": "13800138000"})

    def syncAddressBook_sec(self):
        url = "https://uca.wo116114.com/sjgj/unicomAssistant/uasp/configs/v1/addressBookBatchConfig?product_line=uasp&entry_point=h5&entry_point_id=edop_unicom_3a6cc75a"
        self.sec_uca_post(url, {
            "opType": "1", "productId": "91311616",
            "addressBookDTOList": [{"addressBookName": "张三", "addressBookPhoneNo": "13800138001"}]
        })

    def setInterceptionRules_sec(self):
        url = "https://uca.wo116114.com/sjgj/woAssistant/umm/configs/v1/config?product_line=uasp&entry_point=h5&entry_point_id=wxdefbc1986dc757a6"
        self.sec_uca_post(url, {
            "productId": "91311616", "type": 3, "operationType": 0,
            "contents": [{"icon": "alerting", "content": "1", "contentName": "响一声", "contentTag": "8", "name": "rings-once"}]
        })
        time.sleep(2)
        self.sec_uca_post(url, {
            "productId": "91311616", "type": 3, "operationType": 0,
            "contents": [{"icon": "alerting", "content": "0", "contentName": "响一声", "contentTag": "8", "name": "rings-once"}]
        })

    def viewWeeklyReport_sec(self):
        base = "https://uca.wo116114.com/sjgj/unicomAssistant/uasp"
        body = {"productId": "91311616"}
        self.sec_uca_post(f"{base}/configs/v1/weeklySwitchStatus?product_line=uasp&entry_point=h5&entry_point_id=wxdefbc1986dc757a6", body)
        self.sec_uca_post(f"{base}/report/v1/queryKeyData?product_line=uasp&entry_point=h5&entry_point_id=wxdefbc1986dc757a6", body)
        self.sec_uca_post(f"{base}/report/v1/weeklySummary?product_line=uasp&entry_point=h5&entry_point_id=wxdefbc1986dc757a6", body)

    def zhushou_sec(self):
        try:
            headers = {
                "auth-sa-token": self.sec_token, "token": self.sec_token,
                "Content-Type": "application/json", "Accept": "*",
                "User-Agent": "ChinaUnicom4.x/12.3.1 (com.chinaunicom.mobilebusiness; build:77; iOS 16.6.0) Alamofire/4.7.3 unicom{version:iphone_c@12.0301}"
            }
            self.session.post("https://ims.wo116114.com/api/AiAssistant/autoReply",
                              json={"history": [], "message": "1", "promptId": 10000}, headers=headers, timeout=10)
        except Exception as e:
            self.log(f"安全管家: 智能助手异常: {e}")

    def daijie_sec(self):
        try:
            headers = {
                "auth-sa-token": self.sec_token, "token": self.sec_token, "Authorization": self.sec_token,
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B)"
            }
            self.session.post("https://ims.wo116114.com/api/Assistant/assis_save", json={
                "page_type": 1, "old_ainumber": "XF0", "level": 3, "dialog": "0",
                "opertype": 1, "videoimage": "", "speechtype": "06", "ainumber": "BD1"
            }, headers=headers, timeout=10)
        except Exception as e:
            self.log(f"安全管家: 代接助理异常: {e}")

    def anquanfen_sec(self):
        url = "https://uca.wo116114.com/sjgj/woAssistant/umm/configs/v1/config?product_line=uasp&entry_point=h5&entry_point_id=wxdefbc1986dc757a6"
        score_url = "https://uca.wo116114.com/sjgj/unicomAssistant/uasp/report/v1/queryScore?product_line=uasp&entry_point=h5&entry_point_id=wxdefbc1986dc757a6"
        off_body = {"productId": "91351080", "type": 3, "operationType": 0,
                    "contents": [{"icon": "phone-fraud", "content": "1", "contentName": "疑似诈骗", "contentTag": "0", "name": "fraud"}]}
        on_body = {"productId": "91351080", "type": 3, "operationType": 0,
                   "contents": [{"contentTag": "0", "content": "0"}]}
        self.sec_uca_post(url, off_body)
        time.sleep(2)
        self.sec_uca_post(score_url, {"productId": "91311616"})
        time.sleep(2)
        self.sec_uca_post(url, on_body)
        time.sleep(2)
        self.sec_uca_post(score_url, {"productId": "91311616"})
        time.sleep(2)
        self.sec_uca_post(url, off_body)

    def haoduan_sec(self):
        url = "https://uca.wo116114.com/sjgj/woAssistant/umm/configs/v1/config?product_line=uasp&entry_point=h5&entry_point_id=wxdefbc1986dc757a6"
        item_off = {"checked": True, "content": "1", "contentName": "拦截400开头的10位特服号码", "contentTag": "1"}
        item_on = {"checked": False, "content": "0", "contentName": "拦截400开头的10位特服号码", "contentTag": "1"}
        base = {"productId": "91351080", "type": 7, "operationType": 0}
        self.sec_uca_post(url, {**base, "contents": [item_off]})
        time.sleep(2)
        self.sec_uca_post(url, {**base, "contents": [item_on]})
        time.sleep(2)
        self.sec_uca_post(url, {**base, "contents": [item_off]})

    def ojbk_sec(self, taskCode):
        try:
            url = "https://m.jf.10010.com/jf-external-application/jftask/taskFinish"
            headers = self._sec_jf_headers()
            self.session.post(url, json={"taskCode": taskCode}, headers=headers, timeout=10)
        except Exception as e:
            self.log(f"安全管家: 活动浏览异常: {e}")

    def sec_wo_ai_headers(self, use_mobile=False, override_token=None):
        ua_pc = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 "
            "MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI "
            "MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) "
            "UnifiedPCWindowsWechat(0xf2541818) XWEB/19201 miniProgram/wx1e83eef922822ee0"
        )
        ua_mobile = (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_3 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 "
            "MicroMessenger/8.0.69(0x1800452f) NetType/WIFI Language/zh_CN "
            "miniProgram/wx1e83eef922822ee0"
        )
        return {
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Origin": "https://ai.wo.cn",
            "Authorization": override_token or self.sec_token,
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "User-Agent": ua_mobile if use_mobile else ua_pc,
        }

    def sec_get_knowledge_id(self):
        try:
            response = self.session.post(
                "https://ai.wo.cn/web-tongtong/knowledge/getKnowledgeList",
                headers=self.sec_wo_ai_headers(),
                data=json.dumps({"appType": 1}),
                timeout=10,
            )
            res = response.json()
            if res.get("code") == 0 and res.get("data"):
                return res["data"][0].get("id")
            self.log(f"获取知识库ID失败：{res.get('msg') or res}")
        except Exception as e:
            self.log(f"获取知识库ID异常：{e}")
        return ""

    def upload_knowledge_file_sec(self):
        try:
            kid = self.sec_get_knowledge_id()
            if not kid:
                return False
            upload_headers = {
                k: v for k, v in self.sec_wo_ai_headers().items()
                if k.lower() != "content-type"
            }
            files = {"file": ("task_upload.txt", b" ", "text/plain")}
            data = {
                "knowledgeId": kid,
                "fileName": "task_upload.txt",
                "fileType": "text/plain",
                "fileSize": "1",
                "currentPartSize": "1",
                "currentIndex": "1",
                "totalPart": "1",
                "spaceType": "0",
            }
            response = self.session.post(
                "https://ai.wo.cn/web-tongtong/knowledge/uploadLocalFileToKnowledge",
                headers=upload_headers,
                files=files,
                data=data,
                timeout=15,
            )
            res = response.json()
            if res.get("code") == 0:
                self.log("上传知识库文件成功")
                return True
            self.log(f"上传知识库文件失败：{res.get('msg') or res}")
            return False
        except Exception as e:
            self.log(f"安全管家: 上传知识库文件异常: {e}")
            return False

    def sec_get_chat_list(self):
        try:
            headers = self.sec_wo_ai_headers()
            headers["Referer"] = "https://ai.wo.cn/wxMini"
            response = self.session.get(
                "https://ai.wo.cn/web-tongtong/historyChat/list",
                headers=headers,
                timeout=10,
            )
            res = response.json()
            if res.get("code") == 0:
                return ((res.get("data") or {}).get("content") or [])
            if res.get("msg"):
                self.log(f"获取AI对话历史失败：{res.get('msg')}")
        except Exception as e:
            self.log(f"获取AI对话历史异常：{e}")
        return []

    def sec_send_ai_chat(self):
        try:
            session_id = f"mmru{''.join(str(random.randint(0, 9)) for _ in range(10))}"
            request_id = f"rqid_mmru{''.join(str(random.randint(0, 9)) for _ in range(10))}"
            headers = self.sec_wo_ai_headers(use_mobile=True)
            headers["Accept"] = "text/event-stream"
            headers["Referer"] = "https://ai.wo.cn/wxMini/psychologicalApp/chat?id=1&type=ruole"
            payload = {
                "modelKey": "87e622d9e488",
                "message": "帮我推荐1个必吃饭店",
                "deepThink": False,
                "webSearch": False,
                "attachments": [],
                "imgSize": 0,
                "sessionId": session_id,
                "requestId": request_id,
                "promptKey": "",
                "knowledgeId": "",
                "ragSearch": False,
                "moduleType": 12,
            }
            response = self.session.post(
                "https://ai.wo.cn/web-tongtong/chat/chatReplyV2",
                headers=headers,
                data=json.dumps(payload),
                timeout=60,
                stream=True,
            )
            for _ in response.iter_lines():
                pass
            if response.ok:
                self.log("已发送AI对话")
                return True
            self.log(f"发送AI对话失败：HTTP {response.status_code}")
        except Exception as e:
            self.log(f"发送AI对话异常：{e}")
        return False

    def sec_get_share_key(self, session_id):
        try:
            headers = self.sec_wo_ai_headers()
            headers["Referer"] = "https://ai.wo.cn/wxMini"
            response = self.session.post(
                "https://ai.wo.cn/web-tongtong/historyChat/shareDetail",
                headers=headers,
                data=json.dumps({"sessionId": session_id}),
                timeout=10,
            )
            res = response.json()
            if res.get("code") == 0 and res.get("data"):
                return str(res["data"])
            self.log(f"获取分享key失败：{res.get('msg') or res}")
        except Exception as e:
            self.log(f"获取分享key异常：{e}")
        return ""

    def sec_view_share_detail(self, key, view_token):
        try:
            response = self.session.post(
                "https://ai.wo.cn/web-tongtong/historyChat/getShareDetail",
                headers=self.sec_wo_ai_headers(use_mobile=True, override_token=view_token),
                data=json.dumps({"key": key, "pageSize": 10, "pageNum": 1}),
                timeout=10,
            )
            res = response.json()
            if res.get("code") == 0:
                self.log("查看分享对话成功")
                return True
            self.log(f"查看分享对话失败：{res.get('msg') or res}")
        except Exception as e:
            self.log(f"查看分享对话异常：{e}")
        return False

    def share_ai_chat_sec(self, taskCode=""):
        try:
            content = self.sec_get_chat_list()
            if not content:
                self.log("暂无AI对话历史，先发送一条对话...")
                if not self.sec_send_ai_chat():
                    return False
                time.sleep(2)
                content = self.sec_get_chat_list()
            if not content:
                self.log("仍无AI对话历史，跳过分享任务")
                return False
            session_id = content[0].get("chatSessionId", "")
            if not session_id:
                self.log("获取分享key失败：缺少sessionId")
                return False
            share_key = self.sec_get_share_key(session_id)
            if not share_key:
                return False
            self.sec_ai_share_key = share_key
            if taskCode:
                self.sec_share_task_code = taskCode
            short_key = share_key[:8] + "..." if len(share_key) > 8 else share_key
            self.log(f"AI对话分享key获取成功: {short_key}")
            return True
        except Exception as e:
            self.log(f"安全管家: 分享AI对话异常: {e}")
            return False

    def role_chat_sec(self):
        try:
            session_id = f"mmrp{''.join(str(random.randint(0, 9)) for _ in range(10))}"
            request_id = f"rqid_mmrp{''.join(str(random.randint(0, 9)) for _ in range(10))}"
            headers = self.sec_wo_ai_headers()
            headers["Accept"] = "text/event-stream"
            headers["Referer"] = "https://ai.wo.cn/wxMini/psychologicalApp/chat?id=1&type=ruole"
            response = self.session.post(
                "https://ai.wo.cn/web-tongtong/lxzn/chat",
                headers=headers,
                data=json.dumps({
                    "sessionId": session_id,
                    "requestId": request_id,
                    "roleId": 1,
                    "message": "我有拖延症，好多事情不想做。",
                }),
                timeout=60,
                stream=True,
            )
            for _ in response.iter_lines():
                pass
            if not response.ok:
                self.log(f"角色助手对话失败：HTTP {response.status_code}")
                return False
            self.log("角色助手对话完成")
            return True
        except Exception as e:
            self.log(f"安全管家: 角色助手对话异常: {e}")
            return False

    def sec_finalize_share_ai_task(self):
        if not self.sec_share_task_code:
            return False
        self.sec_track_pending_claim(self.sec_share_task_code, self.sec_share_task_name)
        latest_task = self.sec_refresh_task_snapshot(
            self.sec_share_task_code,
            self.sec_share_task_name,
            retries=5,
            delay=2,
        )
        if not latest_task:
            self.sec_refresh_security_context(refresh_secret=True)
            latest_task = self.sec_refresh_task_snapshot(
                self.sec_share_task_code,
                self.sec_share_task_name,
                retries=5,
                delay=2,
            )
        if not latest_task:
            self.log("联通助理-分享AI助手对话：互看后未查询到任务状态")
            return False
        finish_count, need_count, finish_text = self.sec_parse_task(latest_task)
        if finish_text == "待领取" or (need_count > 0 and finish_count >= need_count):
            self.log("联通助理-分享AI助手对话：互看完成，尝试领取奖励")
            receive_state = self.receivePoints_sec(self.sec_share_task_code, self.sec_share_task_name)
            if receive_state in ("received", "auto"):
                self.getUserInfo_sec()
                return True
            if receive_state == "pending":
                self.sec_recover_pending_claims(rounds=2, delay=6, refresh_context=True)
                if self.sec_share_task_code not in self.sec_pending_claim_tasks:
                    return True
        self.log(f"联通助理-分享AI助手对话：互看后状态 {finish_count}/{need_count} - {finish_text}")
        return False

    def _sec_jf_headers(self, with_signature=False):
        headers = {
            "ticket": unquote(self.sec_ticket),
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 unicom{version:iphone_c@12.0301};ltst;OSVersion/16.6",
            "partnersid": "1702",
            "clienttype": "uasp_unicom_applet",
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://m.jf.10010.com",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
        }
        if hasattr(self, 'sec_jeaId') and self.sec_jeaId:
            headers["Cookie"] = f"_jea_id={self.sec_jeaId};"
        if with_signature:
            headers.update(self.build_signature_headers_sec())
        return headers

    def update_sec_jea_id(self, response=None):
        jea_id = ""
        if response is not None:
            cookie = response.headers.get("Set-Cookie", "")
            match = re.search(r"_jea_id=([^;]+)", cookie)
            if match:
                jea_id = match.group(1)
        if not jea_id:
            for cookie_item in self.session.cookies:
                if cookie_item.name == "_jea_id":
                    jea_id = cookie_item.value
                    break
        if jea_id:
            self.sec_jeaId = jea_id
        return jea_id

    def sec_query_task_list(self):
        url = "https://m.jf.10010.com/jf-external-application/jftask/taskDetail"
        last_error = ""
        for attempt in range(1, 4):
            response = None
            try:
                response = self.session.post(url, json={}, headers=self._sec_jf_headers(), timeout=15)
                self.update_sec_jea_id(response)
                res = response.json()
                task_detail = ((res or {}).get("data") or {}).get("taskDetail") or {}
                return task_detail.get("taskList", [])
            except ValueError:
                preview = ((response.text if response is not None else "") or "").strip().replace("\n", " ")
                last_error = f"非JSON响应[{attempt}/3]: {preview[:60] or 'empty'}"
            except Exception as e:
                last_error = str(e)
            if attempt < 3:
                time.sleep(2)
        self.log(f"联通助理任务列表查询异常: {last_error}")
        return []

    def sec_parse_task(self, task):
        finish_count = safe_int(task.get("finishCount", 0))
        need_count = safe_int(task.get("needCount", 0))
        finish_text = task.get("finishText") or task.get("taskStatusName") or task.get("taskStatusDesc") or "未知状态"
        return finish_count, need_count, finish_text

    def sec_supports_delayed_claim(self, task_name):
        delayed_keywords = (
            "上传知识库文件",
            "分享AI助手对话",
            "角色助手对话",
        )
        return any(keyword in task_name for keyword in delayed_keywords)

    def sec_track_pending_claim(self, task_code, task_name):
        if task_code and task_name and self.sec_supports_delayed_claim(task_name):
            self.sec_pending_claim_tasks[task_code] = task_name

    def sec_untrack_pending_claim(self, task_code):
        if task_code:
            self.sec_pending_claim_tasks.pop(task_code, None)

    def sec_refresh_security_context(self, refresh_secret=False):
        try:
            self.sec_ticket1 = ""
            self.sec_token = ""
            self.sec_ticket = ""
            self.getTicketByNative_sec()
            if not getattr(self, 'sec_ticket1', None):
                return False
            self.getAuthToken_sec()
            if not getattr(self, 'sec_token', None):
                return False
            self.getTicketForJF_sec()
            if not getattr(self, 'sec_ticket', None):
                return False
            if refresh_secret:
                self.sec_secretKey = None
                if not self.get_secret_key_sec(silent=True):
                    return False
            return True
        except Exception as e:
            self.log(f"联通助理上下文刷新异常: {e}")
            return False

    def sec_get_task_snapshot(self, task_code="", task_name=""):
        for task in self.sec_query_task_list():
            if task_code and task.get("taskCode") == task_code:
                return task
            if task_name and task.get("taskName") == task_name:
                return task
        return None

    def sec_refresh_task_snapshot(self, task_code, task_name, retries=3, delay=2):
        latest_task = None
        for attempt in range(retries):
            if attempt:
                time.sleep(delay)
            latest_task = self.sec_get_task_snapshot(task_code, task_name)
            if not latest_task:
                continue
            finish_count, need_count, finish_text = self.sec_parse_task(latest_task)
            if finish_text == "待领取" or (need_count > 0 and finish_count >= need_count):
                return latest_task
        return latest_task

    def sec_should_manual_finish(self, task_name):
        manual_keywords = (
            "新增亲情守护成员",
            "新增宽带绑定",
            "语音提醒",
            "反诈险领取",
            "设置日程提醒",
        )
        return any(keyword in task_name for keyword in manual_keywords)

    def sec_wait_seconds(self, task_name):
        if any(keyword in task_name for keyword in ("上传知识库文件", "分享AI助手对话", "角色助手对话")):
            return 5
        if any(keyword in task_name for keyword in ("添加黑名单", "骚扰拦截设置", "安全分提升", "号段拦截")):
            return 8
        return 4

    def receivePoints_sec(self, taskCode, taskName=""):
        url = "https://m.jf.10010.com/jf-external-application/jftask/receive"
        last_error = ""
        for attempt in range(1, 3):
            response = None
            try:
                headers = self._sec_jf_headers(with_signature=True)
                response = self.session.post(url, json={"taskCode": taskCode}, headers=headers, timeout=10)
                self.update_sec_jea_id(response)
                res = response.json()
                score = str((res.get("data") or {}).get("score") or "").strip()
                msg = str(res.get("msg") or "").strip()
                if score:
                    self.sec_untrack_pending_claim(taskCode)
                    self.log(f"领取{score}成功", notify=True)
                    return "received"
                if "任务未完成" in msg or "不可领取" in msg:
                    self.log("领取任务未完成")
                    return "pending"
                if "自动发放" in msg or "已领取" in msg:
                    self.sec_untrack_pending_claim(taskCode)
                    self.log("任务已完成且奖励已领取")
                    return "auto"
                if msg:
                    self.log(f"领取失败：{msg}")
                    return "failed"
                self.log(f"领取失败：{res}")
                return "failed"
            except ValueError:
                preview = ((response.text if response is not None else "") or "").strip().replace("\n", " ")
                last_error = f"非JSON响应[{attempt}/2]: {preview[:60] or 'empty'}"
            except Exception as e:
                last_error = str(e)
            if attempt < 2:
                time.sleep(2)
        self.log(f"安全管家: 领取积分异常: {last_error}")
        return "error"

    def finishTask_sec(self, taskCode, taskName):
        try:
            url = "https://m.jf.10010.com/jf-external-application/jftask/toFinish"
            headers = self._sec_jf_headers(with_signature=True)
            response = self.session.post(url, json={"taskCode": taskCode}, headers=headers, timeout=10)
            self.update_sec_jea_id(response)
            action_map = {
                "添加黑名单": self.addToBlacklist_sec,
                "号码标记": self.markPhoneNumber_sec,
                "同步通讯录": self.syncAddressBook_sec,
                "骚扰拦截设置": self.setInterceptionRules_sec,
                "智能助手": self.zhushou_sec,
                "代接助理": self.daijie_sec,
                "安全分": self.anquanfen_sec,
                "号段拦截": self.haoduan_sec,
                "查看周报": self.viewWeeklyReport_sec,
                "活动浏览": lambda: self.ojbk_sec(taskCode),
                "上传知识库文件": self.upload_knowledge_file_sec,
                "分享AI助手对话": lambda: self.share_ai_chat_sec(taskCode),
                "角色助手对话": self.role_chat_sec,
            }
            for key, action in action_map.items():
                if key in taskName:
                    result = action()
                    return False if result is False else True
            self.log(f"任务 {taskName} 需要手动完成")
            return False
        except Exception as e:
            self.log(f"安全管家: finishTask异常: {e}")
            return False

    def signIn_sec(self, taskCode):
        try:
            url = "https://m.jf.10010.com/jf-external-application/jftask/sign"
            headers = self._sec_jf_headers(with_signature=True)
            response = self.session.post(url, json={"taskCode": taskCode}, headers=headers, timeout=10)
            self.update_sec_jea_id(response)
            res = response.json()
            if res.get("code") == "0000":
                return True
            self.log(f"签到失败：{res.get('msg') if res else '状态未知'}")
            return False
        except Exception as e:
            self.log(f"安全管家: 签到异常: {e}")
            return False

    def executeAllTasks_sec(self):
        try:
            task_list = self.sec_query_task_list()
            if not task_list:
                self.log("联通助理任务列表查询失败")
                return
            for task in task_list:
                task_name = task.get("taskName", "")
                task_code = task.get("taskCode", "")
                finish_count, need_count, finish_text = self.sec_parse_task(task)
                self.log(f"{task_name}：{finish_count}/{need_count} - {finish_text}")
                if not task_code or need_count <= 0:
                    self.log("---------------------")
                    continue
                if finish_count >= need_count:
                    if finish_text == "待领取":
                        time.sleep(2)
                        receive_state = self.receivePoints_sec(task_code, task_name)
                        if receive_state == "pending":
                            self.sec_track_pending_claim(task_code, task_name)
                    else:
                        self.log("任务已完成且奖励已领取")
                    self.log("---------------------")
                    continue
                remaining = max(need_count - finish_count, 1)
                self.log(f"任务未完成，需要再执行 {remaining} 次")
                if self.sec_should_manual_finish(task_name):
                    self.log(f"任务 {task_name} 需要手动完成")
                    self.log("---------------------")
                    continue
                for i in range(remaining):
                    try:
                        if i:
                            time.sleep(2)
                        handled = self.signIn_sec(task_code) if "签到" in task_name else self.finishTask_sec(task_code, task_name)
                        if not handled:
                            break
                        wait_seconds = self.sec_wait_seconds(task_name)
                        if wait_seconds > 0:
                            time.sleep(wait_seconds)
                        latest_task = self.sec_refresh_task_snapshot(task_code, task_name, retries=3, delay=2)
                        if latest_task:
                            finish_count, need_count, finish_text = self.sec_parse_task(latest_task)
                        self.log(f"第 {i + 1} 次执行{task_name}任务完成")
                        receive_state = self.receivePoints_sec(task_code, task_name)
                        if receive_state == "pending":
                            self.sec_track_pending_claim(task_code, task_name)
                        if receive_state in ("received", "auto"):
                            break
                        if need_count > 0 and finish_count >= need_count:
                            self.log("任务已完成且奖励已领取")
                            break
                    except Exception as e:
                        self.log(f"执行 {task_name} 失败：{e}")
                        break
                self.log("---------------------")
        except Exception as e:
            self.log(f"联通助理任务执行异常: {e}")

    def getUserInfo_sec(self):
        url = "https://m.jf.10010.com/jf-external-application/jftask/userInfo"
        last_error = ""
        for attempt in range(1, 3):
            response = None
            try:
                headers = self._sec_jf_headers()
                response = self.session.post(url, json={}, headers=headers, timeout=10)
                self.update_sec_jea_id(response)
                res = response.json()
                if not res or res.get('code') != '0000' or not res.get('data'):
                    self.log(f"安全管家: 查询积分失败: {res.get('msg') if res else '无响应'}")
                    return
                current = int(res['data'].get('availableScore', 0))
                today = res['data'].get('todayEarnScore', 0)
                if not hasattr(self, 'sec_oldJFPoints') or self.sec_oldJFPoints is None:
                    self.sec_oldJFPoints = current
                    self.log(f"当前积分：{current}，今日已赚 {today}")
                else:
                    gained = current - self.sec_oldJFPoints
                    user_label = mask_str(self.mobile) if self.mobile else f"账号[{self.index}]"
                    self.log(f"用户{user_label}积分变动：{self.sec_oldJFPoints} → {current} | 新增: {gained}", notify=True)
                return
            except ValueError:
                preview = ((response.text if response is not None else "") or "").strip().replace("\n", " ")
                last_error = f"非JSON响应[{attempt}/2]: {preview[:60] or 'empty'}"
            except Exception as e:
                last_error = str(e)
            if attempt < 2:
                time.sleep(2)
        self.log(f"安全管家: 查询积分异常: {last_error}")

    def sec_recover_pending_claims(self, rounds=2, delay=12, refresh_context=False):
        if not self.sec_pending_claim_tasks:
            return False
        recovered = False
        last_status_map = {}
        self.log(f"联通助理：待补领任务 {len(self.sec_pending_claim_tasks)} 个，开始补查")
        for attempt in range(rounds):
            if attempt:
                time.sleep(delay)
            if not self.sec_pending_claim_tasks:
                break
            if refresh_context and not self.sec_refresh_security_context(refresh_secret=True):
                continue
            for task_code, task_name in list(self.sec_pending_claim_tasks.items()):
                latest_task = self.sec_refresh_task_snapshot(task_code, task_name, retries=3, delay=2)
                if not latest_task:
                    status_key = "missing"
                    if last_status_map.get(task_code) != status_key:
                        self.log(f"{task_name}：补查未取到任务状态")
                        last_status_map[task_code] = status_key
                    continue
                finish_count, need_count, finish_text = self.sec_parse_task(latest_task)
                if finish_text == "待领取" or (need_count > 0 and finish_count >= need_count):
                    self.log(f"{task_name}：补查后尝试领取")
                    receive_state = self.receivePoints_sec(task_code, task_name)
                    if receive_state in ("received", "auto"):
                        recovered = True
                        last_status_map.pop(task_code, None)
                        continue
                else:
                    status_key = f"{finish_count}/{need_count}-{finish_text}"
                    if last_status_map.get(task_code) != status_key:
                        self.log(f"{task_name}：补查状态 {finish_count}/{need_count} - {finish_text}")
                        last_status_map[task_code] = status_key
        if recovered:
            self.getUserInfo_sec()
        if self.sec_pending_claim_tasks:
            names = "、".join(self.sec_pending_claim_tasks.values())
            self.log(f"联通助理：仍待补领 {names}")
        return recovered

    def securityButlerTask(self, is_query_only=False):
        self.log("==== 联通安全管家 ====")
        if not self.ecs_token:
            self.log("安全管家: 缺少 ecs_token，跳过")
            return
        try:
            self.getTicketByNative_sec()
            if not getattr(self, 'sec_ticket1', None): return
            self.getAuthToken_sec()
            if not getattr(self, 'sec_token', None): return
            self.getTicketForJF_sec()
            if not getattr(self, 'sec_ticket', None): return
            self.sec_oldJFPoints = None
            self.getUserInfo_sec()
            if is_query_only:
                self.log("联通助理积分：[查询模式] 跳过任务执行")
                return
            self.get_secret_key_sec()
            self.executeAllTasks_sec()
            self.log("等待积分到账，等待一会...")
            self.sec_recover_pending_claims(rounds=2, delay=12, refresh_context=True)
            time.sleep(3)
            self.getUserInfo_sec()
        except Exception as e:
            self.log(f"安全管家: 异常: {e}")

    def aiting_query_integral(self):
        url = "https://m.jf.10010.com/jf-external-application/jftask/userInfo"
        response = self.session.post(url, json={}, headers=self.aiting_jf_headers())
        self.update_aiting_jea_id(response)
        res = response.json()
        if res.get('code') == '0000':
            data = res.get('data', {})
            self.log(f"积分概览: 今日已赚 {data.get('todayEarnScore')}, 当前余额 {data.get('availableScore')}", notify=True)

    def aiting_jf_headers(self, with_signature=False):
        headers = {
            'ticket': unquote(self.aiting_biz_ticket),
            'pageid': 's789081246969976832',
            'clienttype': 'aiting_android',
            'partnersid': '1706',
            'content-type': 'application/json;charset=UTF-8',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 12; Redmi K30 Pro Build/SKQ1.220303.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.159 Mobile Safari/537.36 WoReaderApp/Android',
            'Origin': 'https://m.jf.10010.com',
            'Host': 'm.jf.10010.com',
        }
        jea_id = getattr(self, 'aiting_jeaId', '')
        if jea_id:
            headers['Cookie'] = f"_jea_id={jea_id};"
        if with_signature:
            headers.update(self.build_signature_headers_aiting())
        return headers

    def update_aiting_jea_id(self, response=None):
        jea_id = ''
        if response is not None:
            cookie = response.headers.get('Set-Cookie', '')
            match = re.search(r'_jea_id=([^;]+)', cookie)
            if match:
                jea_id = match.group(1)
        if not jea_id:
            for cookie_item in self.session.cookies:
                if cookie_item.name == '_jea_id':
                    jea_id = cookie_item.value
                    break
        if jea_id:
            self.aiting_jeaId = jea_id
        return jea_id

    def get_secret_key_aiting(self):
        if getattr(self, 'aiting_secretKey', None):
            return self.aiting_secretKey
        try:
            self.update_aiting_jea_id()
            res = self.session.get(
                "https://m.jf.10010.com/jf-external-application/jftask/getSecretKey",
                headers=self.aiting_jf_headers(),
                timeout=10,
            )
            self.update_aiting_jea_id(res)
            data = res.json()
            secret = data.get('data', {}).get('secretKey')
            if data.get('code') == '0000' and secret:
                self.aiting_secretKey = secret.encode('utf-8')
                return self.aiting_secretKey
            self.log(f"爱听任务: getSecretKey 失败: {data}")
        except Exception as e:
            self.log(f"爱听任务: getSecretKey 异常: {e}")
        return None

    def build_signature_headers_aiting(self):
        secret_key = self.get_secret_key_aiting()
        if not secret_key:
            return {}
        request_ts = str(round(time.time() * 1000))
        nonce = ''.join(random.choices('0123456789abcdefghijklmnopqrstuvwxyz', k=8))
        signature = hmac.new(
            secret_key, f"{nonce}{request_ts}".encode('utf-8'), hashlib.sha256,
        ).hexdigest()
        return {
            'x-request-timestamp': request_ts,
            'x-request-nonce': nonce,
            'x-request-signature': signature,
        }

    def ltzf_task(self):
        self.log("==== 联通祝福 ====")
        base_url = "https://wocare.unisk.cn/mbh/getToken"
        params = {
            "channelType": WOCARE_CONSTANTS["serviceLife"],
            "homePage": "home",
            "duanlianjieabc": "qAz2m"
        }
        targetUrl = f"{base_url}?{urlencode(params)}"
        res = self.openPlatLineNew(targetUrl)
        if not res or 'ticket' not in res:
            self.log("联通祝福: 获取Ticket失败")
            return
        ticket = res['ticket']
        if not self.wocare_getToken(ticket):
            self.log("联通祝福: 获取Wocare Token失败")
            return
        self.wocare_getSpecificityBanner()
        wocare_activities = [
            {"name": "星座配对", "id": 2},
            {"name": "大转盘", "id": 3},
            {"name": "盲盒抽奖", "id": 4}
        ]
        for activity in wocare_activities:
            self.wocare_getDrawTask(activity)
            self.wocare_loadInit(activity)

    def openPlatLineNew(self, to_url):
        try:
            base_url = "https://m.client.10010.com/mobileService/openPlatform/openPlatLineNew.htm"
            params = {"to_url": to_url}
            for attempt in range(1, 4):
                try:
                    res = self.session.get(base_url, params=params, allow_redirects=False, timeout=15)
                    break
                except Exception as e:
                    err_msg = str(e)
                    if attempt < 3 and os.environ.get("UNICOM_PROXY_API") and ("Max retries exceeded" in err_msg or "timed out" in err_msg.lower() or "connection" in err_msg.lower() or "SOCKS" in err_msg):
                        self.log(f"openPlatLineNew 第{attempt}次异常触发故障转移: {err_msg}")
                        self.failover_proxy()
                        continue
                    self.log(f"openPlatLineNew 第{attempt}次重试 - 异常: {e}")
                    if attempt == 3:
                         return None
                    time.sleep(2)
            if res.status_code == 302 and 'Location' in res.headers:
                loc = res.headers['Location']
                parsed = urlparse(loc)
                qs = parse_qs(parsed.query)
                ticket = qs.get('ticket', [''])[0]
                type_val = qs.get('type', [''])[0]
                if ticket:
                    return {'ticket': ticket, 'type': type_val, 'loc': loc}
                else:
                    self.log("openPlatLineNew: 重定向URL中无ticket")
            else:
                self.log(f"openPlatLineNew: 状态码{res.status_code} (期望302)")
        except Exception as e:
            self.log(f"openPlatLineNew 异常: {str(e)}")
        return None

    def random_string(self, length, chars=string.ascii_letters + string.digits):
        return ''.join(random.choice(chars) for _ in range(length))

    def get_bizchannelinfo(self):
        info = {
            "bizChannelCode": "225",
            "disriBiz": "party",
            "unionSessionId": "",
            "stType": "",
            "stDesmobile": "",
            "source": "",
            "rptId": self.rptId,
            "ticket": "",
            "tongdunTokenId": self.tokenId_cookie,
            "xindunTokenId": self.unicomTokenId
        }
        return json.dumps(info)

    def get_epay_authinfo(self):
        info = {
            "mobile": "",
            "sessionId": getattr(self, 'sessionId', ''),
            "tokenId": getattr(self, 'tokenId', ''),
            "userId": ""
        }
        return json.dumps(info)

    def ttlxj_task(self, is_query_only=False):
        self.log("==== 天天领现金 ====")
        for attempt in range(1, 31):
            try:
                ticket_res = self.openPlatLineNew("https://epay.10010.com/ci-mps-st-web/ttlxj/")
                if not ticket_res or not ticket_res.get('ticket'):
                    if attempt < 30:
                        self.log(f"天天领现金: 获取Ticket失败，正在重试 ({attempt}/30)...")
                        time.sleep(2)
                        continue
                    else:
                        self.log("天天领现金: 获取Ticket失败，已达最大重试次数，跳过任务")
                        return
                ticket = ticket_res['ticket']
                type_val = ticket_res['type']
                if self.ttlxj_authorize(ticket, type_val, ticket_res['loc']):
                    if self.ttlxj_auth_check():
                         if is_query_only:
                            self.ttlxj_query_available()
                            return
                         self.ttlxj_do_tasks()
                         self.ttlxj_query_available()
                         break
                else:
                     if attempt < 30:
                        self.log(f"天天领现金: 授权失败，正在重试 ({attempt}/30)...")
                        time.sleep(2)
                     else:
                        self.log("天天领现金: 授权失败，已达最大重试次数")
            except Exception as e:
                if attempt < 30:
                    self.log(f"天天领现金: 任务异常 ({e})，正在重试 ({attempt}/30)...")
                    time.sleep(2)
                else:
                    self.log(f"天天领现金: 任务异常: {e}")

    def ttlxj_authorize(self, ticket, type_val, referer_url):
        try:
            url = "https://epay.10010.com/woauth2/v2/authorize"
            headers = {
                "Origin": "https://epay.10010.com",
                "Referer": referer_url
            }
            payload = {
                "response_type": "rptid",
                "client_id": "73b138fd-250c-4126-94e2-48cbcc8b9cbe",
                "redirect_uri": "https://epay.10010.com/ci-mps-st-web/",
                "login_hint": {
                    "credential_type": "st_ticket",
                    "credential": ticket,
                    "st_type": type_val,
                    "force_logout": True,
                    "source": "app_sjyyt"
                },
                "device_info": {
                    "token_id": f"chinaunicom-pro-{int(time.time()*1000)}-{self.random_string(13)}",
                    "trace_id": self.random_string(32)
                }
            }
            res = self.session.post(url, json=payload, headers=headers, timeout=10)
            if res.status_code == 200:
                return True
            else:
                self.log(f"天天领现金: Authorize失败[{res.status_code}]: {res.text}")
                return False
        except Exception as e:
             self.log(f"ttlxj_authorize error: {e}")
             return False

    def ttlxj_auth_check(self):
        try:
            url = "https://epay.10010.com/ps-pafs-auth-front/v1/auth/check"
            headers = {
                "bizchannelinfo": self.get_bizchannelinfo()
            }
            res = self.session.post(url, headers=headers, json={}, timeout=10)
            data = res.json()
            code = data.get("code")
            if code == "0000":
                auth_info = data.get("data", {}).get("authInfo", {})
                self.sessionId = auth_info.get("sessionId", "")
                self.tokenId = auth_info.get("tokenId", "")
                self.epay_userId = auth_info.get("userId", "")
                return True
            elif code == "2101000100":
                login_url = data.get("data", {}).get("woauth_login_url")
                if login_url:
                    return self.ttlxj_login(login_url)
            else:
                self.log(f"天天领现金: AuthCheck失败[{code}]: {data.get('msg')}")
                return False
        except Exception as e:
            self.log(f"ttlxj_auth_check error: {e}")
            return False

    def ttlxj_login(self, login_url):
        try:
            full_url = f"{login_url}https://epay.10010.com/ci-mcss-party-web/clockIn/?bizFrom=225&bizChannelCode=225"
            res = self.session.get(full_url, allow_redirects=False, timeout=10)
            if res.status_code == 302 and 'Location' in res.headers:
                loc = res.headers['Location']
                parsed = urlparse(loc)
                qs = parse_qs(parsed.query)
                rptid = qs.get('rptid', [''])[0]
                if rptid:
                    self.rptId = rptid
                    return self.ttlxj_auth_check()
                else:
                    self.log("天天领现金: Login跳转后无rptid")
            else:
                self.log(f"天天领现金: Login失败[{res.status_code}]")
            return False
        except Exception as e:
            self.log(f"ttlxj_login error: {e}")
            return False

    def ttlxj_do_tasks(self):
        info_url = "https://epay.10010.com/ci-mcss-party-front/v1/ttlxj/userDrawInfo"
        headers = {
            "bizchannelinfo": self.get_bizchannelinfo(),
            "authinfo": self.get_epay_authinfo()
        }
        res = self.request("post", info_url, json={}, headers=headers)
        if not res: return
        data = res.json()
        if data.get('code') == '0000':
            day_of_week = data.get("data", {}).get("dayOfWeek", "")
            draw_key = f"day{day_of_week}"
            has_not_clocked_in = data.get("data", {}).get(draw_key) == "1"
            if has_not_clocked_in:
                self.log(f"天天领现金: 今天未打卡", notify=True)
                today_js = (datetime.now().weekday() + 1) % 7
                draw_type = "C" if today_js == 0 else "B"
                self.ttlxj_unifyDrawNew(draw_type)
            else:
                 self.log(f"天天领现金: 今天已打卡", notify=True)
        else:
            self.log(f"天天领现金: 查询失败: {data.get('msg')}")

    def ttlxj_unifyDrawNew(self, draw_type):
        draw_url = "https://epay.10010.com/ci-mcss-party-front/v1/ttlxj/unifyDrawNew"
        headers = {
            "bizchannelinfo": self.get_bizchannelinfo(),
            "authinfo": self.get_epay_authinfo()
        }
        req_data = {
            "drawType": draw_type,
            "bizFrom": "225",
            "activityId": "TTLXJ20210330"
        }
        res = self.request("post", draw_url, data=req_data, headers=headers)
        if not res: return
        data = res.json()
        if data.get('code') == '0000':
            prize = data.get('data', {}).get('prizeName', '未知奖品')
            self.log(f"天天领现金: 抽奖成功: {prize}", notify=True)
        else:
            self.log(f"天天领现金: 抽奖失败: {data.get('msg')}")

    def ttlxj_query_available(self):
        avail_url = "https://epay.10010.com/ci-mcss-party-front/v1/ttlxj/queryAvailable"
        headers = {
            "bizchannelinfo": self.get_bizchannelinfo(),
            "authinfo": self.get_epay_authinfo()
        }
        res = self.request("post", avail_url, json={}, headers=headers)
        if not res: return
        data = res.json()
        if data.get('code') == '0000':
            d = data.get('data', {})
            amount_raw = int(d.get('availableAmount', '0'))
            amount_yuan = f"{amount_raw / 100:.2f}"
            msg = f"天天领现金: 可用立减金: {amount_yuan}元"
            seven_day = int(d.get('sevenDayExpireAmount', 0))
            if seven_day > 0:
                msg += f", 7天内过期立减金: {seven_day / 100:.2f}元"
            min_exp_amt = int(d.get('minExpireAmount', 0))
            min_exp_date = d.get('minExpireDate')
            if min_exp_amt > 0 and min_exp_date:
                msg += f", 最早过期立减金: {min_exp_amt / 100:.2f}元 -- {min_exp_date}过期"
            self.log(msg, notify=True)
        else:
            self.log(f"天天领现金: 查询余额失败: {data.get('msg')}")

    def aiting_get_aes(self, data, key):
        iv_str = "16-Bytes--String"
        key_bytes = key[:16].encode('utf-8')
        iv_bytes = iv_str[:16].encode('utf-8')
        text = json.dumps(data, separators=(',', ':')) if isinstance(data, (dict, list)) else str(data)
        padded_data = pad(text.encode('utf-8'), 16)
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
        ciphertext = cipher.encrypt(padded_data)
        hex_str = ciphertext.hex()
        return base64.b64encode(hex_str.encode('utf-8')).decode('utf-8')

    def aiting_aes_encrypt(self, data, key, iv):
        key_bytes = key.encode('utf-8')
        iv_bytes = iv.encode('utf-8')
        text = json.dumps(data, separators=(',', ':')) if isinstance(data, (dict, list)) else str(data)
        padded_data = pad(text.encode('utf-8'), 16)
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
        ciphertext = cipher.encrypt(padded_data)
        hex_str = ciphertext.hex().upper()
        return base64.b64encode(hex_str.encode('utf-8')).decode('utf-8')

    def aiting_md5(self, text):
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def aiting_generate_sign(self, params, key):
        sorted_keys = sorted(params.keys())
        sign_str = '&'.join([f"{k}={params[k]}" for k in sorted_keys])
        final_str = f"{sign_str}&key={key}"
        return self.aiting_md5(final_str)

    def aiting_timestamp(self):
        return str(int(time.time() * 1000))

    def aiting_nonce(self):
        return str(random.randint(100000, 999999))

    def aiting_generate_woid(self, imei):
        random6 = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        imei8 = imei[:8] if len(imei) >= 8 else imei.ljust(8, '0')
        random4 = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
        random2 = ''.join(random.choices(string.ascii_letters + string.digits, k=2))
        return f"WOA{random6}{imei8}LOT{random4}LV{random2}"

    def aiting_calculate_clientconfirm(self, userid, imei):
        plaintext = f"android{userid}{imei}"
        return self.aiting_aes_encrypt(plaintext, AITING_AES_KEY, AITING_AES_IV)

    def aiting_calculate_passcode(self, timestamp, phone):
        return self.aiting_md5(timestamp + phone + AITING_CLIENT_KEY)

    def aiting_build_statisticsinfo(self, userid, useraccount, imei, clientconfirm):
        params = {
            'channelid': '28015001',
            'sid': ''.join(random.choices(string.ascii_letters + string.digits + "_-", k=20)),
            'eid': ''.join(random.choices(string.ascii_letters + string.digits + "_", k=20)),
            'osversion': 'Android12',
            'clientallid': '000000100000000000058.0.2.1225',
            'display': '2400_1080',
            'ip': '192.168.3.24',
            'nettypename': 'wifi',
            'version': '802',
            'versionname': '8.0.2',
            'terminalName': 'Redmi',
            'terminalType': 'Redmi_K30_Pro',
            'udid': 'null',
            'woid': self.aiting_generate_woid(imei),
            'useraccount': useraccount,
            'userid': userid,
            'clientconfirm': clientconfirm
        }
        return '&'.join([f"{k}={params[k]}" for k in params])

    def generate_random_imei(self):
        tac = ''.join([str(random.randint(0, 9)) for _ in range(8)])
        snr = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        imei_raw = tac + snr
        digits = [int(d) for d in imei_raw]
        for i in range(len(digits) - 1, -1, -2):
            digits[i] *= 2
            if digits[i] > 9: digits[i] -= 9
        total = sum(digits)
        check_digit = (10 - (total % 10)) % 10
        return imei_raw + str(check_digit)

    def aiting_woread_login(self, phone):
        access_token = "ODZERTZCMjA1NTg1MTFFNDNFMThDRDYw"
        token_enc = ""
        if self.token_online:
             token_enc = self.aiting_get_aes(self.token_online, WOREAD_KEY)
        else:
             self.log("阅读专区: 未找到 token_online，尝试仅使用手机号登录")
        phone_enc = self.aiting_get_aes(phone, WOREAD_KEY)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        if token_enc:
            inner_data = {
                "tokenOnline": token_enc,
                "phone": phone_enc,
                "timestamp": timestamp
            }
        else:
            inner_data = {
                "phone": phone_enc,
                "timestamp": timestamp
            }
        sign_result = self.aiting_get_aes(inner_data, WOREAD_KEY)
        url = "https://10010.woread.com.cn/ng_woread_service/rest/account/login"
        body = {"sign": sign_result}
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 11; Redmi Note 10 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.159 Mobile Safari/537.36",
            "accesstoken": access_token,
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "https://10010.woread.com.cn"
        }
        res = self.session.post(url, json=body, headers=headers).json()
        if res.get("code") == "0000":
            return res.get("data", {}).get("token")
        self.log(f"爱听登录: 沃阅读登录失败: {res}")
        return None

    def aiting_get_jwt_token(self, statisticsinfo):
        timestamp = self.aiting_timestamp()
        sign_params = {
            'clientSource': '3',
            'clientId': 'android',
            'source': '3',
            'timestamp': timestamp
        }
        sign_val = self.aiting_generate_sign(sign_params, AITING_SIGN_KEY_APPKEY)
        client_id_const = "395DEDE9C1D6FE11B7C9C0D82B353E74"
        client_id_b64 = base64.b64encode(client_id_const.encode('utf-8')).decode('utf-8')
        body = {
            'clientSource': '3',
            'clientId': client_id_b64,
            'source': '3',
            'timestamp': timestamp,
            'sign': sign_val
        }
        url = f"{AITING_BASE_URL}/oauth/client/appkey"
        headers = {
            'Skip-Authorization-Check': 'true',
            'statisticsinfo': statisticsinfo,
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; Redmi K30 Pro Build/SKQ1.220303.001)"
        }
        try:
            res = self.session.post(url, json=body, headers=headers).json()
            if res.get("code") == "0000" and res.get("key"):
                return res.get("key")
            self.log(f"爱听登录: 获取JWT失败: {res}")
        except Exception as e:
            self.log(f"爱听登录: 获取JWT异常: {e}")
        return None

    def aiting_api_login(self, phone, useraccount, jwt_token, statisticsinfo):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        passcode = self.aiting_calculate_passcode(timestamp, phone)
        query_params_list = [
            'networktype=3', 'ua=Redmi+K30+Pro', 'isencode=false',
            'clientversion=8.0.2', 'versionname=Android_1_1080x2356',
            'channelid=28015001', 'userlabelisencode=0', 'validatecode=', 'sid=',
            f"timestamp={timestamp}", f"passcode={passcode}"
        ]
        query_str = '&'.join(query_params_list)
        final_account = useraccount
        url = f"{AITING_BASE_URL}/mainrest/rest/read/user/ulogin/3/{final_account}/1/1/0?{query_str}"
        req_time = self.aiting_timestamp()
        nonce = self.aiting_nonce()
        sign_params = {
            'jwt': jwt_token,
            'nonestr': nonce,
            'osversion': 'Android12',
            'terminalName': 'Redmi',
            'timestamp': req_time
        }
        sorted_keys = sorted(sign_params.keys())
        sign_str = '&'.join([f"{k}={sign_params[k]}" for k in sorted_keys])
        requertid = self.aiting_md5(f"{sign_str}&key={AITING_SIGN_KEY_REQUERTID}")
        headers = {
            'statisticsinfo': statisticsinfo,
            'requerttime': req_time,
            'nonestr': nonce,
            'requertid': requertid,
            'AuthorizationClient': f"Bearer {jwt_token}",
            'User-Agent': 'okhttp/4.9.0'
        }
        try:
            res = self.session.get(url, headers=headers).json()
            if res.get("code") == "0000" and res.get("message"):
                msg = res.get("message")
                token = msg.get("token")
                userid = msg.get("userid")
                if msg.get("accountinfo"):
                    token = msg.get("accountinfo", {}).get("token") or token
                    userid = msg.get("accountinfo", {}).get("userid") or userid
                return {"token": token, "userid": userid}
            self.log(f"爱听登录: 业务API登录失败: {res}")
        except Exception as e:
            self.log(f"爱听登录: 业务API异常: {e}")
        return None

    def aiting_login_flow(self):
        self.log("正在执行爱听登录流程...")
        woread_token = self.aiting_woread_login(self.mobile)
        if not woread_token: return False
        self.aiting_woread_token = woread_token
        imei = self.generate_random_imei()
        userid = self.mobile
        useraccount = self.mobile
        clientconfirm = self.aiting_calculate_clientconfirm(userid, imei)
        statisticsinfo = self.aiting_build_statisticsinfo(userid, useraccount, imei, clientconfirm)
        self.aiting_statisticsinfo = statisticsinfo
        jwt = self.aiting_get_jwt_token(statisticsinfo)
        if not jwt: return False
        self.aiting_jwt = jwt
        login_data = self.aiting_api_login(self.mobile, useraccount, jwt, statisticsinfo)
        if not login_data: return False
        self.aiting_biz_token = login_data.get('token')
        self.aiting_base_userid = login_data.get('userid') or self.mobile
        self.log(f"✅ 爱听业务登录成功! Token已获取")
        biz_ticket = self.aiting_get_ticket()
        if biz_ticket:
            self.aiting_biz_ticket = biz_ticket
            return True
        return False

    def aiting_get_ticket(self):
        url = f"{AITING_BASE_URL}/activity/rest/unicom/points/getInfoTicket"
        timestamp = self.aiting_timestamp()
        sign_params = {
            "token": self.aiting_biz_token,
            "timestamp": timestamp,
            "userid": self.aiting_base_userid
        }
        sign_val = self.aiting_generate_sign(sign_params, AITING_SIGN_KEY_API)
        body = {
            "sign": sign_val,
            "timestamp": timestamp,
            "token": self.aiting_biz_token,
            "userid": self.aiting_base_userid
        }
        nonce = self.aiting_nonce()
        head_sign_params = {
            'jwt': self.aiting_jwt,
            'nonestr': nonce,
            'osversion': 'Android12',
            'terminalName': 'Redmi',
            'timestamp': timestamp
        }
        sorted_keys = sorted(head_sign_params.keys())
        sign_str = '&'.join([f"{k}={head_sign_params[k]}" for k in sorted_keys])
        final_sign_str = f"{sign_str}&key={AITING_SIGN_KEY_REQUERTID}"
        requertid = self.aiting_md5(final_sign_str)
        headers = {
            "AuthorizationClient": f"Bearer {self.aiting_jwt}",
            "statisticsinfo": self.aiting_statisticsinfo,
            "requerttime": timestamp,
            "nonestr": nonce,
            "requertid": requertid
        }
        try:
            res = self.session.post(url, json=body, headers=headers).json()
            if res.get("code") == "0000":
                msg = res.get("message", "")
                if "ticket=" in msg:
                    match = re.search(r'ticket=([^&]+)', msg)
                    if match:
                        return match.group(1)
                return msg # Fallback if message is ticket itself? No, standard is URL.
            self.log(f"爱听登录: 获取Ticket失败: {res}")
        except Exception as e:
            self.log(f"爱听登录: 获取Ticket异常: {e}")
        return None

    def jf_get_task_detail(self, ticket):
        url = "https://m.jf.10010.com/jf-external-application/jftask/taskDetail"
        headers = self.aiting_jf_headers()
        headers['Referer'] = f"https://m.jf.10010.com/jf-external-application/index.html?ticket={ticket}&pageID=s789081246969976832"
        response = self.session.post(url, json={}, headers=headers)
        self.update_aiting_jea_id(response)
        res = response.json()
        return res.get("data", {}).get("taskDetail", {}).get("taskList", [])

    def jf_to_finish(self, ticket, task_code):
        url = "https://m.jf.10010.com/jf-external-application/jftask/toFinish"
        response = self.session.post(
            url,
            json={'taskCode': task_code},
            headers=self.aiting_jf_headers(with_signature=True),
        )
        self.update_aiting_jea_id(response)

    def jf_pop_up(self, ticket):
        url = "https://m.jf.10010.com/jf-external-application/jftask/popUp"
        response = self.session.post(url, json={}, headers=self.aiting_jf_headers())
        self.update_aiting_jea_id(response)
        try:
            res = response.json()
        except Exception:
            self.log(f"  └─ ⚠️ 积分弹窗响应非JSON (状态码{response.status_code})")
            return {}
        if isinstance(res, dict):
            if res.get('code') == "0000" and res.get('data', {}).get('score'):
                self.log(f"  └─ 🎉 获得 {res['data']['score']} 积分", notify=True)
            elif res.get('code') != "0000":
                self.log(f"  └─ 📝 积分弹窗返回: {res.get('desc', res)}")
        return res

    def aiting_complete_task_api(self, type_val):
        timestamp = self.aiting_timestamp()
        nonce = self.aiting_nonce()
        sign_params = {'jwt': self.aiting_jwt, 'nonestr': nonce, 'osversion': 'Android12', 'terminalName': 'Redmi', 'timestamp': timestamp}
        sign_str = '&'.join([f"{k}={sign_params[k]}" for k in sorted(sign_params.keys())])
        requertid = self.aiting_md5(f"{sign_str}&key={AITING_SIGN_KEY_REQUERTID}")
        body_params = {'source': '3', 'timestamp': timestamp, 'token': self.aiting_woread_token, 'type': str(type_val), 'userid': self.aiting_base_userid}
        body_str = '&'.join([f"{k}={body_params[k]}" for k in sorted(body_params.keys())])
        sign = self.aiting_md5(f"{body_str}&key={AITING_SIGN_KEY_API}")
        url = f"{AITING_BASE_URL}/activity/rest/unicom/points/completiontask"
        payload = {**body_params, 'sign': sign}
        headers = {
            'AuthorizationClient': f"Bearer {self.aiting_jwt}",
            'requerttime': timestamp,
            'nonestr': nonce,
            'requertid': requertid,
            'statisticsinfo': self.aiting_statisticsinfo
        }
        self.session.post(url, json=payload, headers=headers)

    def aiting_get_secretkey(self):
        timestamp = self.aiting_timestamp()
        nonce = self.aiting_nonce()
        sign_params = {'jwt': self.aiting_jwt, 'nonestr': nonce, 'osversion': 'Android12', 'terminalName': 'Redmi', 'timestamp': timestamp}
        sign_str = '&'.join([f"{k}={sign_params[k]}" for k in sorted(sign_params.keys())])
        requertid = self.aiting_md5(f"{sign_str}&key={AITING_SIGN_KEY_REQUERTID}")
        url = f"https://woread.com.cn/rest/read/statistics/getsecretkey/3/{self.aiting_base_userid}"
        headers = {
            'AuthorizationClient': f"Bearer {self.aiting_jwt}",
            'requerttime': timestamp, 'nonestr': nonce, 'requertid': requertid,
            'statisticsinfo': self.aiting_statisticsinfo, 'User-Agent': 'okhttp/4.9.0'
        }
        params = {'token': self.aiting_woread_token}
        res = self.session.get(url, params=params, headers=headers).json()
        if res.get("code") == "0000":
            return res.get("message")
        return None

    def aiting_add_read_time(self, read_time_seconds):
        secretkey = self.aiting_get_secretkey()
        if not secretkey: return
        timestamp = self.aiting_timestamp()
        count_time_str = str(read_time_seconds * 1000)
        book_id = "4524960"
        data_obj = {
            "userid": self.aiting_base_userid,
            "counttime": count_time_str,
            "timestamp": timestamp,
            "secretkey": secretkey,
            "cntindex": book_id,
            "cnttype": 1,
            "readtype": 1
        }
        encrypted = self.aiting_aes_encrypt(data_obj, ADDREADTIME_AES_KEY, AITING_AES_IV)
        nonce = self.aiting_nonce()
        sign_params = {'jwt': self.aiting_jwt, 'nonestr': nonce, 'osversion': 'Android12', 'terminalName': 'Redmi', 'timestamp': timestamp}
        sign_str = '&'.join([f"{k}={sign_params[k]}" for k in sorted(sign_params.keys())])
        requertid = self.aiting_md5(f"{sign_str}&key={AITING_SIGN_KEY_REQUERTID}")
        url = f"https://woread.com.cn/rest/read/statistics/addreadtime/3/{encrypted}"
        random_uuid = str(uuid.uuid4()).replace('-', '')
        body = {
            "channelid": "28015001", "creadertime": datetime.now().strftime("%y%m%d%H%M%S"),
            "imei": self.generate_random_imei(),
            "list": { "cntindex": book_id, "cnttype": 1, "readtime": count_time_str, "readtype": 1 },
            "list1": [{ "cntindex": book_id, "cnttype": 1, "readtime": count_time_str, "readtype": 1 }],
            "listentimes": count_time_str, "uuid": random_uuid
        }
        headers = {
            'AuthorizationClient': f"Bearer {self.aiting_jwt}",
            'requerttime': timestamp, 'nonestr': nonce, 'requertid': requertid,
            'statisticsinfo': self.aiting_statisticsinfo, 'User-Agent': 'okhttp/4.9.0'
        }
        res = self.session.post(url, json=body, headers=headers)
        if res.status_code == 200:
             self.last_read_submission_time = time.time()
             self.log(f"✅ 阅读时长上报成功 ({read_time_seconds}s)")

    def aiting_new_read_add(self):
        timestamp = self.aiting_timestamp()
        nonce = self.aiting_nonce()
        sign_params = {'jwt': self.aiting_jwt, 'nonestr': nonce, 'osversion': 'Android12', 'terminalName': 'Redmi', 'timestamp': timestamp}
        sign_str = '&'.join([f"{k}={sign_params[k]}" for k in sorted(sign_params.keys())])
        requertid = self.aiting_md5(f"{sign_str}&key={AITING_SIGN_KEY_REQUERTID}")
        url = f"https://woread.com.cn/rest/read/new/newreadadd/3/{self.aiting_base_userid}/{self.aiting_woread_token}"
        params = {'isfreeLimt': '0', 'isgray': 'true'}
        body = {"source": 3, "cntindex": "4524960", "chapterallindex": "100136247350", "readtype": 3}
        headers = {
             'AuthorizationClient': f"Bearer {self.aiting_jwt}", 'requerttime': timestamp, 'nonestr': nonce, 'requertid': requertid, 'statisticsinfo': self.aiting_statisticsinfo, 'User-Agent': 'Redmi K30 Pro'
        }
        self.session.post(url, params=params, json=body, headers=headers)

    def jf_sign(self, ticket, task_code):
        """爱听「签到」类任务 (taskType=4 / 任务名含「签到」) —— 移植自上游 v1.2.0

        ⚠️ 与 jf_to_finish 是**两个不同接口**:
           签到类 → POST jf-external-application/uasptask/sign  {taskCode, remindEnabled}
           其余   → POST jf-external-application/jftask/toFinish {taskCode}
        原脚本把签到任务从待办里过滤掉却没有对应分支 → 爱听签到任务从不执行。
        """
        url = "https://m.jf.10010.com/jf-external-application/uasptask/sign"
        referer = (
            f"https://m.jf.10010.com/ts-mobile/well/{getattr(self, 'aiting_pageid', 's789081246969976832')}"
            f"?distributeId={getattr(self, 'aiting_distribute_id', '')}&partnersId=1706"
            f"&clientType=aiting_ios&ticket={ticket}"
        )
        headers = self.aiting_jf_headers(with_signature=True)
        headers.update({"referer": referer, "origin": "https://m.jf.10010.com"})
        response = None
        try:
            response = self.session.post(
                url, json={'taskCode': task_code, 'remindEnabled': '1'}, headers=headers)
            self.update_aiting_jea_id(response)
        except Exception as e:
            self.log(f"爱听任务: 积分签到异常: {e}")
            return False
        if response is None:
            self.log("爱听任务: 积分签到无响应")
            return False
        try:
            res = response.json()
        except Exception:
            self.log(f"爱听任务: 积分签到响应非JSON (状态码{getattr(response, 'status_code', '未知')})")
            return False
        if isinstance(res, dict) and res.get('code') == "0000":
            self.log(f"爱听任务: 积分签到 - {res.get('msg') or '成功'}", notify=True)
            return True
        if isinstance(res, dict):
            self.log(f"爱听任务: 积分签到返回 - {res.get('desc') or res.get('msg') or response_summary(res)}")
        return False

    def aiting_task(self, is_query_only=False):
        self.log("==== 联通爱听任务 ====")
        if not self.aiting_login_flow():
            self.log("爱听任务: 登录失败，跳过")
            return
        self.log("爱听任务: 登录成功，正在获取任务列表...")
        try:
            self.aiting_query_integral()
        except: pass
        task_list = self.jf_get_task_detail(self.aiting_biz_ticket)
        done_list = [t for t in task_list if t.get('finish') == 1]
        printed_names = set()
        for t in done_list:
             name = t.get('taskName')
             if name not in printed_names:
                 self.log(f"  ✅ {name} ({t.get('finishCount')}/{t.get('needCount')})")
                 printed_names.add(name)
        todo_list = [t for t in task_list if t.get('finish') == 0 and "邀请" not in t.get('taskName', '')]
        if not todo_list:
            self.log("爱听任务: ✅ 所有任务已完成")
            if is_query_only:
                self.log("爱听任务: [查询模式] 跳过任务执行...")
            return
        self.log(f"爱听任务: 发现 {len(todo_list)} 个待办任务")
        if is_query_only:
            self.log("爱听任务: [查询模式] 跳过任务执行...")
            return
        read_tasks = [t for t in todo_list if ("阅读" in t.get('taskName','') or "听读" in t.get('taskName','')) and "邀请" not in t.get('taskName','')]
        for task in read_tasks:
            remaining = int(task.get('needCount', 1)) - int(task.get('finishCount', 0))
            if remaining <= 0: continue
            self.log(f"执行阅读任务: {task.get('taskName')} (剩余 {remaining} 次)")
            for i in range(remaining):
                self.jf_to_finish(self.aiting_biz_ticket, task.get('taskCode'))
                self.log(f"  └─ 第 {i + 1}/{remaining} 次: 极速提交中...")
                self.aiting_new_read_add()
                time.sleep(5)
                self.aiting_add_read_time(120)
                time.sleep(2)
                self.jf_pop_up(self.aiting_biz_ticket)
        # 签到类任务 (taskType=4 或任务名含「签到」) —— 移植自上游 v1.2.0
        # ⚠️ 原先这些任务被下面的 other_tasks 过滤条件排除、且没有任何处理分支, 等于从不执行
        sign_tasks = [t for t in todo_list
                      if "签到" in t.get('taskName', '') or str(t.get('taskType', '')) == '4']
        for task in sign_tasks:
            self.log(f"执行签到任务: {task.get('taskName')}")
            self.jf_sign(self.aiting_biz_ticket, task.get('taskCode'))
            time.sleep(1.5)
            self.jf_pop_up(self.aiting_biz_ticket)
        other_tasks = [t for t in todo_list if not any(x in t.get('taskName','') for x in ["通知", "阅读", "听读", "邀请", "签到"])
                       and str(t.get('taskType', '')) != '4']
        notify_task = next((t for t in todo_list if "通知" in t.get('taskName','')), None)
        if notify_task:
            self.log(f"执行通知任务: {notify_task.get('taskName')}")
            self.jf_to_finish(self.aiting_biz_ticket, notify_task.get('taskCode'))
            time.sleep(1)
            self.aiting_complete_task_api(2)
            time.sleep(2)
            self.jf_pop_up(self.aiting_biz_ticket)
        for task in other_tasks:
            remaining = int(task.get('needCount', 1)) - int(task.get('finishCount', 0))
            if remaining <= 0: continue
            self.log(f"执行通用任务: {task.get('taskName')} (剩余 {remaining} 次)")
            for i in range(remaining):
                 self.jf_to_finish(self.aiting_biz_ticket, task.get('taskCode'))
                 time.sleep(1.5)
                 self.aiting_complete_task_api(4) # Type 4
                 time.sleep(2)
                 self.jf_pop_up(self.aiting_biz_ticket)
        try:
            self.aiting_query_integral()
        except: pass

    # ============ 沃云手机 (uphone.wostore.cn / h5forphone.wostore.cn) ============
    # 活动分两族, 登录方式不同 —— 这是上游脚本最容易踩错的地方:
    #   task    族 (Points_Obtain_25xx / Points_Sign_25xx / Points_Exchange_25xx) → user/login 不带 activityId
    #   lottery 族 (HD2026xxxxxxxxx / Lottery_25xx)                                → user/login 必须带 activityId=活动码
    # activityCode 按月轮换, 用 wostore_discover_live_codes() 自动发现存活码。

    def wostore_cloud_get_ticket(self):
        if not getattr(self, 'ecs_token', ''):
            self.log("沃云手机: 缺少 ecs_token，无法获取入口 Ticket")
            return ""
        city_code = ""
        if self.city_info and isinstance(self.city_info, list):
            city_code = str((self.city_info[0] or {}).get("cityCode") or "")
        headers = {
            "User-Agent": "ChinaUnicom4.x/12.11 (com.chinaunicom.mobilebusiness; build:36; iOS 16.6.0) Alamofire/4.7.3 unicom{version:iphone_c@12.1100}",
            "Accept": "*/*",
            "Accept-Encoding": "gzip;q=1.0, compress;q=0.5",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Language": "zh-Hans-CN;q=1.0, en-CN;q=0.9",
            "Cookie": (
                f"ecs_token={self.ecs_token};t3_token={getattr(self, 't3_token', '')};"
                f"PvSessionId={datetime.now().strftime('%Y%m%d%H%M%S')}{self.uuid};devicedId={self.uuid};"
                f"c_mobile={self.account_mobile or self.mobile};c_version=iphone_c@12.1100;city=036|{city_code}|90063345|-99;"
            ),
        }
        try:
            res = self.session.get(
                "https://m.client.10010.com/edop_ng/getTicketByNative",
                params={"token": self.ecs_token, "appId": "edop_unicom_68e8fa69"},
                headers=headers,
                timeout=20,
            ).json()
            if res.get("rsp_code") == "0000" and res.get("ticket"):
                return res.get("ticket")
            self.log(f"沃云手机: 获取入口 Ticket 失败 - {res.get('rsp_desc') or res.get('msg') or pretty_json(res)}")
        except Exception as e:
            self.log(f"沃云手机: 获取入口 Ticket 异常 {e}")
        return ""

    def wostore_cloud_login(self, ticket):
        """ticket → cloud_token (云手机侧令牌)"""
        try:
            res = self.session.post(
                "https://uphone.wostore.cn/h5api/token-service/getTokenByTicket",
                data=json.dumps({"ticket": ticket, "channel": "ST-Kuaidai001"}),
                headers={
                    "User-Agent": "ChinaUnicom4.x/12.11 (com.chinaunicom.mobilebusiness; build:36; iOS 16.6.0) Alamofire/4.7.3 unicom{version:iphone_c@12.1100}",
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip;q=1.0, compress;q=0.5",
                    "Content-Type": "application/json",
                    "channel": "ST-Kuaidai001",
                    "X-Tingyun": "c=A|uBuVhVARE0A",
                    "source": "4",
                    "os": "H5",
                    "Accept-Language": "zh-Hans-CN;q=1.0, en-CN;q=0.9",
                    "channelCode": "ST-Kuaidai001",
                },
                timeout=20,
            ).json()
            if str(res.get("code")) == "200" and res.get("data"):
                return {"cloud_token": res.get("data")}
            self.log(f"沃云手机: 获取 Token 失败 - {res.get('msg') or pretty_json(res)}")
        except Exception as e:
            self.log(f"沃云手机: 登录异常 {e}")
        return None

    def wostore_cloud_h5_headers(self, cloud_token=None):
        return {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.57(0x18003930) NetType/WIFI Language/zh_CN",
            "Host": "h5forphone.wostore.cn",
            "X-Requested-With": "XMLHttpRequest",
            **({"Authorization": cloud_token} if cloud_token else {}),
        }

    def wostore_cloud_activity_headers(self, user_token=""):
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.57(0x18003930) NetType/WIFI Language/zh_CN",
            "Host": "uphone.wostore.cn",
            "Origin": "https://uphone.wostore.cn",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }
        if user_token:
            headers["X-USR-TOKEN"] = user_token
        return headers

    def wostore_cloud_headers(self, user_token):
        return {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 unicom{version:iphone_c@12.0601};ltst;OSVersion/16.6",
            "Authorization": user_token,
        }

    def wostore_cloud_bucp_get(self, path, user_token):
        try:
            return self.session.get(f"https://uphone.wo-adv.cn/bucp{path}",
                                    headers=self.wostore_cloud_headers(user_token),
                                    timeout=WOSTORE_CLOUD_TIMEOUT).json()
        except Exception:
            return {}

    def wostore_cloud_bucp_post(self, path, user_token, payload=None):
        try:
            return self.session.post(f"https://uphone.wo-adv.cn/bucp{path}", json=payload or {},
                                     headers=self.wostore_cloud_headers(user_token),
                                     timeout=WOSTORE_CLOUD_TIMEOUT).json()
        except Exception:
            return {}

    def wostore_cloud_activity_post(self, path, payload, user_token="", label="云手机请求", quiet=False):
        """uphone.wostore.cn/h5api/activity-service/* 统一 POST"""
        try:
            return self.session.post(
                f"https://uphone.wostore.cn{path}",
                data=json.dumps(payload, ensure_ascii=False),
                headers=self.wostore_cloud_activity_headers(user_token),
                timeout=WOSTORE_CLOUD_TIMEOUT,
            ).json()
        except Exception as e:
            if not quiet:
                self.log(f"沃云手机: {label}异常 {e}")
            return {}

    def wostore_cloud_point_info(self, cloud_token, notify=True):
        """返回当前积分(int)"""
        res = self.wostore_cloud_bucp_get("/servers/order/user-point/point-info", cloud_token)
        if str(res.get("code")) == "200":
            data = res.get("data") or {}
            point = data.get("balanceScoreNum")
            if point is None:
                point = data.get("totalPoint") or data.get("point") or data.get("availablePoint")
            if point is not None:
                self.log(f"沃云手机: 当前积分 {point}", notify=notify)
                return safe_int(point, 0)
        else:
            self.log(f"沃云手机: 积分查询失败 - {res.get('msg') or pretty_json(res)}")
        return None

    def wostore_cloud_sign(self, cloud_token):
        try:
            res = self.session.post(
                "https://h5forphone.wostore.cn/h5forphone/activity/signIn",
                data=json.dumps({"accesstoken": cloud_token}),
                headers=self.wostore_cloud_h5_headers(cloud_token),
                timeout=WOSTORE_CLOUD_TIMEOUT,
            ).json()
            msg = res.get('msg', '未知')
            self.log(f"沃云手机: 签到：{msg}", notify=("成功" in msg))
            return res
        except Exception as e:
            self.log(f"沃云手机: 签到异常 {e}")
            return {}

    def wostore_cloud_sign_rewards(self, cloud_token, auto_receive=True):
        try:
            res = self.session.post(
                "https://h5forphone.wostore.cn/h5forphone/activity/signInRightList",
                data=json.dumps({"accesstoken": cloud_token}),
                headers=self.wostore_cloud_h5_headers(cloud_token),
                timeout=WOSTORE_CLOUD_TIMEOUT,
            ).json()
        except Exception as e:
            self.log(f"沃云手机: 签到奖励列表异常 {e}")
            return {}
        goods = (res.get("data") or {}).get("goodsList") or []
        pending = [g for g in goods if g.get("state") in ("", None, 0, "0")]
        if auto_receive:
            for item in pending:
                self.wostore_cloud_receive_sign_reward(cloud_token, item.get("name", ""), item.get("activityOrderId", ""))
        return pending

    def wostore_cloud_receive_sign_reward(self, cloud_token, name, order_id):
        try:
            res = self.session.post(
                "https://h5forphone.wostore.cn/h5forphone/activity/raffleSignIn",
                data=json.dumps({"accesstoken": cloud_token, "activityOrderid": order_id,
                                 "account": "", "accountType": ""}),
                headers=self.wostore_cloud_h5_headers(cloud_token),
                timeout=WOSTORE_CLOUD_TIMEOUT,
            ).json()
            msg = res.get('msg', '未知')
            self.log(f"沃云手机: 领取签到奖励[{name}]：{msg}", notify=("成功" in msg))
            return res
        except Exception as e:
            self.log(f"沃云手机: 领取签到奖励异常 {e}")
            return {}

    def wostore_cloud_activity_login(self, cloud_token, activity_code, login_activity_id=None, quiet=False):
        """登录活动域, 返回 X-USR-TOKEN。task 族不传 login_activity_id; lottery 族必须传。"""
        payload = {"identityType": "cloudPhoneLogin", "code": cloud_token, "device": "device"}
        if login_activity_id:
            payload["activityId"] = login_activity_id
        res = self.wostore_cloud_activity_post("/h5api/activity-service/user/login", payload,
                                               "", "获取活动Token", quiet=quiet)
        token = (res.get("data") or {}).get("user_token") or ""
        if not token and not quiet:
            self.log(f"沃云手机: 活动[{activity_code}]Token 获取失败 - {res.get('msg') or response_summary(res)}")
        return token

    def wostore_cloud_points_sign(self, user_token, sign_code):
        if not sign_code:
            return {}
        res = self.wostore_cloud_activity_post("/h5api/activity-service/points/v1/sign",
                                               {"activityCode": sign_code}, user_token, "积分签到")
        msg = res.get('msg', '未知')
        self.log(f"沃云手机: 积分签到：{msg}", notify=("成功" in msg))
        return res

    @staticmethod
    def wostore_is_transient(res):
        """服务端限流/更新中的软错误, 可重试"""
        msg = str((res or {}).get("msg") or "")
        return any(k in msg for k in ("更新中", "太火爆", "稍后重试", "系统繁忙", "请稍后再试"))

    def wostore_cloud_task_list(self, user_token, activity_code, auto_execute=True, retry=1):
        """查询并按需执行任务; 返回统计字典"""
        stat = {"total": 0, "done": 0, "pending": 0, "claimed": 0, "raffles": 0, "ok": False}
        res = self.wostore_cloud_activity_post("/h5api/activity-service/user/task/list",
                                               {"activityCode": activity_code}, user_token, "查询任务列表")
        while str(res.get("code")) != "200" and retry > 0 and self.wostore_is_transient(res):
            retry -= 1
            time.sleep(4)
            res = self.wostore_cloud_activity_post("/h5api/activity-service/user/task/list",
                                                   {"activityCode": activity_code}, user_token, "查询任务列表")
        if str(res.get("code")) != "200":
            self.log(f"沃云手机: 活动[{activity_code}]不可用 - {response_summary(res)}")
            return stat
        stat["ok"] = True
        stat["raffles"] = safe_int(res.get("rafflesLeftCount"), 0)
        task_list = res.get("taskList") or (res.get("data") or {}).get("taskList") or []
        stat["total"] = len(task_list)
        if not task_list:
            self.log(f"沃云手机: 活动[{activity_code}]无任务 (可抽奖 {stat['raffles']} 次)")
            return stat
        pending_names = []
        claim_stopped = False
        for task in task_list:
            name = task.get("taskName") or task.get("taskDesc") or task.get("taskCode", "未知任务")
            code = task.get("taskCode", "")
            status = str(task.get("status") or task.get("taskStatus") or task.get("state") or "").upper()
            if status in {"OBTAINED", "RECEIVED", "FINISHED", "DONE"}:
                stat["done"] += 1
                continue
            if not auto_execute or claim_stopped:
                stat["pending"] += 1
                pending_names.append(name)
                continue
            if status in {"UNCLAIMED", "CLAIMABLE", "COMPLETED", "FINISH"}:
                res = self.wostore_cloud_receive_task(user_token, activity_code, code, name)
            else:
                self.wostore_cloud_finish_task(user_token, activity_code, task)
                res = self.wostore_cloud_receive_task(user_token, activity_code, code, name)
            if str(res.get("code")) == "200":
                stat["claimed"] += 1
            else:
                stat["pending"] += 1
                pending_names.append(name)
                # 命中每日领取上限后立即收手, 避免刷一屏无效请求
                if "每日限" in str(res.get("msg") or ""):
                    claim_stopped = True
        self.log(f"沃云手机: 活动[{activity_code}]已完成 {stat['done']}/{stat['total']} 个任务，"
                 f"{stat['total'] - stat['done']} 个未完成" + (f"，本次新领 {stat['claimed']} 个" if stat['claimed'] else ""))
        if pending_names:
            preview = "、".join(pending_names[:6]) + ("…" if len(pending_names) > 6 else "")
            self.log(f"沃云手机: 活动[{activity_code}]未完成明细 - {preview}")
        return stat

    def wostore_cloud_finish_task(self, user_token, activity_code, task):
        """上报任务日志 (仅服务端认可的任务才真正完成, 其余会被拒)"""
        task_code = task.get("taskCode", "")
        task_name = task.get("taskName") or task.get("taskDesc") or task_code
        res = self.wostore_cloud_activity_post(
            "/h5api/activity-service/user/task/logs",
            {"logType": "01", "logCode": task_code, "logSource": "01", "logDetail": task_name},
            user_token, "上报任务日志",
        )
        ok = str(res.get("code")) == "200"
        if not ok:
            self.log(f"沃云手机: 上报任务日志[{task_name}]：{res.get('msg') or '失败'}")
        time.sleep(1)
        return res

    def wostore_cloud_receive_task(self, user_token, activity_code, task_code, task_name=""):
        res = self.wostore_cloud_activity_post("/h5api/activity-service/user/task/raffle/get",
                                               {"activityCode": activity_code, "taskCode": task_code},
                                               user_token, "领取任务奖励")
        msg = res.get('msg', '未知')
        if str(res.get("code")) == "200":
            self.log(f"沃云手机: 领取[{task_name or task_code}]：{msg}", notify=("积分" in str(msg) or "成功" in msg))
        else:
            self.log(f"沃云手机: 领取[{task_name or task_code}]：{msg}")
        return res

    def wostore_cloud_lottery_count(self, user_token, activity_code):
        res = self.wostore_cloud_activity_post("/h5api/activity-service/user/task/list",
                                               {"activityCode": activity_code}, user_token, "查询抽奖次数", quiet=True)
        data = res.get("data") or {}
        count = safe_int(data.get("rafflesLeftCount") or data.get("raffleLeftCount")
                         or res.get("rafflesLeftCount") or res.get("raffleLeftCount"), 0)
        return count

    def wostore_cloud_draw(self, user_token, activity_code):
        """抽一次; 返回 (是否成功, 奖品名)"""
        res = self.wostore_cloud_activity_post("/h5api/activity-service/lottery",
                                               {"activityCode": activity_code}, user_token, "抽奖")
        if str(res.get("code")) == "200":
            data = res.get("data") or {}
            prize = data.get("prizeName") or data.get("name") or res.get("msg") or "未知奖励"
            self.log(f"沃云手机: 抽奖获得 - {prize}", notify=True)
            return True, prize
        msg = res.get("msg") or response_summary(res)
        self.log(f"沃云手机: 抽奖失败 - {msg}")
        return False, msg

    # ---- 积分兑换 (当前轮次无积分抽奖, 只有直接兑换) ----
    def wostore_points_goods_list(self, user_token, quiet=False):
        try:
            res = self.session.get(
                f"https://uphone.wostore.cn/h5api/activity-service/points/v1/exchange/list"
                f"?activityCode={WOSTORE_POINTS_ACT_CODE}",
                headers=self.wostore_cloud_activity_headers(user_token),
                timeout=WOSTORE_CLOUD_TIMEOUT,
            ).json()
        except Exception as e:
            if not quiet:
                self.log(f"沃云手机: 积分商品列表异常 {e}")
            return []
        if str(res.get("code")) != "200":
            if not quiet:
                self.log(f"沃云手机: 积分商品列表失败 - {response_summary(res)}")
            return []
        return res.get("data") or []

    def wostore_points_exchange(self, user_token, goods_id, goods_name=""):
        res = self.wostore_cloud_activity_post("/h5api/activity-service/points/v1/exchange",
                                               {"activityCode": WOSTORE_POINTS_ACT_CODE, "goodsId": str(goods_id)},
                                               user_token, "积分兑换")
        ok = str(res.get("code")) == "200"
        label = goods_name or f"goodsId={goods_id}"
        self.log(f"沃云手机: 积分兑换[{label}]：{res.get('msg') or ('成功' if ok else '失败')}", notify=ok)
        return ok

    def wostore_points_auto_exchange(self, user_token, balance):
        """按 WOSTORE_EXCHANGE_GOODS 配置兑换; 留空则只打印可选菜单"""
        goods = self.wostore_points_goods_list(user_token)
        if not goods:
            return 0
        by_id = {str(g.get("goodsId")): g for g in goods}
        targets = [str(x) for x in WOSTORE_EXCHANGE_GOODS if str(x) in by_id]
        if not targets:
            if balance is not None:
                affordable = [g for g in goods if safe_int(g.get("points"), 0) <= balance]
                self.log(f"沃云手机: 积分 {balance} 可兑换 " +
                         "、".join(f"{g.get('goodsName')}/{g.get('goodsSubtitle')}({g.get('points')}分)" for g in affordable))
                self.log("沃云手机: 设置 UNICOM_WOSTORE_EXCHANGE_GOODS=goodsId,goodsId 可自动兑换")
            return 0
        done = 0
        for gid in targets:
            g = by_id[gid]
            cost = safe_int(g.get("points"), 0)
            if balance is not None and balance - cost < WOSTORE_EXCHANGE_KEEP_POINTS:
                self.log(f"沃云手机: 跳过兑换[{g.get('goodsName')}/{g.get('goodsSubtitle')}] - 积分不足"
                         f"({balance}<{cost + WOSTORE_EXCHANGE_KEEP_POINTS})")
                continue
            name = f"{g.get('goodsName')}/{g.get('goodsSubtitle')}"
            if self.wostore_points_exchange(user_token, gid, name):
                done += 1
                if balance is not None:
                    balance -= cost
        return done

    # ---- 活动码自动发现 (activityCode 按月轮换) ----
    def wostore_probe_activity(self, cloud_token, code, is_lottery=False, retry=1):
        token = self.wostore_cloud_activity_login(cloud_token, code,
                                                  login_activity_id=(code if is_lottery else None), quiet=True)
        if not token:
            return None
        res = self.wostore_cloud_activity_post("/h5api/activity-service/user/task/list",
                                               {"activityCode": code}, token, "", quiet=True)
        while str(res.get("code")) != "200" and retry > 0 and self.wostore_is_transient(res):
            retry -= 1
            time.sleep(3)
            res = self.wostore_cloud_activity_post("/h5api/activity-service/user/task/list",
                                                   {"activityCode": code}, token, "", quiet=True)
        if str(res.get("code")) != "200":
            return None
        return {"code": code, "token": token,
                "raffles": safe_int(res.get("rafflesLeftCount"), 0),
                "tasks": res.get("taskList") or []}

    def wostore_discover_live_codes(self, cloud_token, span=1):
        """探测相邻月份的候选活动码, 返回 {task:[], sign:[], exchange:[], lottery:[]}"""
        found = {"task": [], "sign": [], "exchange": [], "lottery": []}
        cands = []
        for cfg, prefix in (
            (WOSTORE_CLOUD_SIGN_CODE, "Points_Sign_"),
            (WOSTORE_CLOUD_ACTIVITY_CODES[0] if WOSTORE_CLOUD_ACTIVITY_CODES else "Points_Obtain_2507",
             "Points_Obtain_"),
            (WOSTORE_POINTS_ACT_CODE, "Points_Exchange_"),
        ):
            cands.extend((c, prefix) for c in wostore_month_variants(cfg, prefix, span))
        for code, prefix in dict.fromkeys(cands):
            hit = self.wostore_probe_activity(cloud_token, code, is_lottery=False)
            if hit:
                kind = "sign" if "Sign" in prefix else ("exchange" if "Exchange" in prefix else "task")
                found[kind].append(hit)
            time.sleep(0.8)
        # 抽奖族活动码无法按月份推导, 只验证配置项
        for code in WOSTORE_LOTTERY_ACTIVITY_CODES:
            hit = self.wostore_probe_activity(cloud_token, code, is_lottery=True)
            if hit:
                found["lottery"].append(hit)
            time.sleep(0.8)
        return found

    def wostore_cloud_device_status(self, cloud_token):
        res = self.wostore_cloud_bucp_get("/servers/resource/instance/list?pageNum=1&pageSize=200", cloud_token)
        rows = res.get("rows") or (res.get("data") or {}).get("rows") or []
        if not rows:
            return res
        for device in rows:
            device_id = device.get("id") or device.get("deviceId") or ""
            status = device.get("status", "?")
            if status == "running":
                self.log("沃云手机: 云手机设备运行正常")
            elif status == "pre_create":
                self.wostore_cloud_device_action(cloud_token, "/servers/resource/instance/cpInstanceAction",
                                                 {"action": "allot", "cpInstanceId": device_id}, "激活设备")
            else:
                self.wostore_cloud_device_action(cloud_token, "/servers/resource/backup/recover",
                                                 {"cpInstanceId": device_id}, "恢复设备")
        return res

    def wostore_cloud_device_action(self, cloud_token, path, payload, label):
        res = self.wostore_cloud_bucp_post(path, cloud_token, payload)
        self.log(f"沃云手机: {label}结果：{res.get('msg', '未知')}")
        return res

    def wostore_cloud_task(self, is_query_only=False):
        self.log("==== 沃云手机 ====")
        ticket = self.wostore_cloud_get_ticket()
        if not ticket:
            self.log("沃云手机: 获取入口 Ticket 失败 (为空)")
            return
        tokens = self.wostore_cloud_login(ticket)
        if not tokens:
            self.log("沃云手机: 登录失败，跳过后续任务")
            return
        cloud_token = tokens["cloud_token"]

        if is_query_only:
            balance = self.wostore_cloud_point_info(cloud_token)
            self.wostore_cloud_sign_rewards(cloud_token, auto_receive=False)
            found = self.wostore_discover_live_codes(cloud_token)
            for hit in found["task"] + found["sign"] + found["exchange"] + found["lottery"]:
                self.wostore_cloud_task_list(hit["token"], hit["code"], auto_execute=False)
            pt = self.wostore_cloud_activity_login(cloud_token, WOSTORE_CLOUD_SIGN_CODE) \
                or (found["sign"][0]["token"] if found["sign"] else "")
            if pt:
                self.wostore_points_auto_exchange(pt, balance)
            return

        point_before = self.wostore_cloud_point_info(cloud_token, notify=False)
        self.wostore_cloud_sign(cloud_token)
        time.sleep(2)
        self.wostore_cloud_sign_rewards(cloud_token)
        time.sleep(1)

        # 1) 自动发现存活活动码 (activityCode 按月轮换)
        found = self.wostore_discover_live_codes(cloud_token)
        if not (found["task"] or found["sign"] or found["exchange"] or found["lottery"]):
            self.log("沃云手机: 未发现存活活动，请用 UNICOM_WOSTORE_*_CODES 指定新活动码")
            return
        # 2) 积分签到
        for hit in found["sign"]:
            self.wostore_cloud_points_sign(hit["token"], hit["code"])
            time.sleep(1)
        # 3) 积分任务
        points_token = (found["sign"][0]["token"] if found["sign"] else "")
        for hit in found["task"]:
            if not points_token:
                points_token = hit["token"]
            self.wostore_cloud_task_list(hit["token"], hit["code"])
            time.sleep(1)

        # 4) 抽奖: 先领机会再抽 (该活动每日限领一次)
        drew = []
        for hit in found["lottery"]:
            stat = self.wostore_cloud_task_list(hit["token"], hit["code"])
            time.sleep(1)
            count = max(stat.get("raffles", 0), self.wostore_cloud_lottery_count(hit["token"], hit["code"]))
            for _ in range(count):
                ok, prize = self.wostore_cloud_draw(hit["token"], hit["code"])
                if ok:
                    drew.append(prize)
                time.sleep(2)
        if not drew:
            self.log("沃云手机: 本日无可用抽奖机会 (抽奖每日限一次, 明日再来)")

        # 5) 积分兑换 (UNICOM_WOSTORE_EXCHANGE_GOODS 留空则只打印菜单)
        if not points_token:
            points_token = self.wostore_cloud_activity_login(cloud_token, WOSTORE_CLOUD_SIGN_CODE)
        if points_token and WOSTORE_EXCHANGE_ENABLE:
            balance = self.wostore_cloud_point_info(cloud_token, notify=False)
            if balance is None:
                balance = point_before
            self.wostore_points_auto_exchange(points_token, balance)

        self.wostore_cloud_point_info(cloud_token)
        self.wostore_cloud_device_status(cloud_token)

    # ============ 通通乡村 ============
    def ttxc_headers(self, auth=True, ecs=False):
        headers = {
            "user-agent": COMMON_CONSTANTS["MARKET_H5_UA"],
            "content-type": "application/json",
            "accept": "*/*",
            "origin": "https://epay.10010.com",
            "referer": TTXC_REFERER,
            "x-requested-with": "com.sinovatech.unicom.ui",
        }
        if auth and getattr(self, "ttxc_token", ""):
            headers["authorization"] = self.ttxc_token
        if ecs and self.ecs_token:
            headers["Cookie"] = f"ecs_token={self.ecs_token}"
        return headers

    def ttxc_post(self, path, payload=None, auth=True, with_user=True, ecs=False):
        data = dict(payload or {})
        if with_user:
            data.setdefault("userId", getattr(self, "ttxc_user_id", ""))
        data.setdefault("channel", TTXC_CHANNEL)
        res = self.request("post", f"{TTXC_BASE_URL}{path}", json=data, headers=self.ttxc_headers(auth=auth, ecs=ecs), timeout=10)
        if not res:
            return {}
        try:
            return res.json()
        except Exception:
            return {}

    def ttxc_init_ttgame(self):
        self.session.cookies.set("ecs_token", self.ecs_token)
        url = f"{TTXC_APP_BASE_URL}/v1/login/ttGame?channel={TTXC_CHANNEL}&rptId="
        data = {}
        for attempt in range(1, 4):
            data = self.ttxc_json(self.request("post", url, json={"unicomTokenId": self.unicomTokenId}, headers=self.ttxc_headers(auth=False, ecs=True), timeout=10))
            if data.get("code") == "0000":
                return True
            if data.get("code") == "4003" and data.get("data") and self.ttxc_finish_woauth(data.get("data")):
                data = self.ttxc_json(self.request("post", url, json={"unicomTokenId": self.unicomTokenId}, headers=self.ttxc_headers(auth=False, ecs=True), timeout=10))
                if data.get("code") == "0000":
                    return True
            if attempt < 3:
                time.sleep(2)
        self.log(f"通通乡村: 初始化失败[{data.get('code')}]: {data.get('msg', '')}")
        return False

    def ttxc_json(self, res):
        if not res:
            return {}
        try:
            return res.json()
        except Exception:
            return {}

    def ttxc_finish_woauth(self, login_url):
        headers = {
            "Referer": "https://epay.10010.com/",
            "User-Agent": COMMON_CONSTANTS["MARKET_H5_UA"],
        }
        res = self.request("get", login_url, headers=headers, timeout=10)
        if not res:
            return False
        match = re.search(r'var token = "([^"]+)"', res.text or "")
        if not match:
            return False
        next_url = (
            "https://epay.10010.com/woauth2/after-collected-device-digest"
            f"?deviceDigestTraceId=&deviceDigestTokenId=&token={quote(match.group(1))}&source=app_sjyyt"
        )
        referer = login_url
        for _ in range(6):
            res = self.request("get", next_url, headers={"Referer": referer, "User-Agent": COMMON_CONSTANTS["MARKET_H5_UA"]}, allow_redirects=False, timeout=10)
            if not res:
                return False
            location = res.headers.get("Location", "")
            if not location:
                return res.status_code == 200
            referer = next_url
            next_url = location
        return False

    def ttxc_login(self, update_nick=True):
        if not self.ecs_token:
            self.onLine()
            if not self.ecs_token:
                self.log("通通乡村: 缺少 ecs_token，跳过")
                return False
        if not self.ttxc_init_ttgame():
            return False
        data = self.ttxc_post("/user/v1/login", auth=False, with_user=False, ecs=True)
        if data.get("code") != 0:
            self.log(f"通通乡村: 登录失败[{data.get('code')}]: {data.get('msg', '')}")
            return False
        user = data.get("data") or {}
        self.ttxc_user_id = user.get("userId", "")
        self.ttxc_token = data.get("token", "")
        self.ttxc_charge_level = user.get("chargeLevel") or {}
        self.ttxc_newbie_list = user.get("newbieList")
        self.ttxc_nick_name = user.get("nickName") or ""
        if not self.ttxc_user_id or not self.ttxc_token:
            self.log("通通乡村: 登录响应缺少 userId/token")
            return False
        carbon = self.ttxc_charge_level.get("carbonNum", 0)
        eco = self.ttxc_charge_level.get("ecologyAmount", 0)
        self.log(f"通通乡村: 登录成功，碳能量{carbon}g，生态值{eco}", notify=True)
        if update_nick and not self.ttxc_nick_name and self.ttxc_newbie_done():
            self.ttxc_update_nick()
        return True

    def ttxc_update_nick(self):
        nick = (self.account_mobile or self.mobile or "")[-4:] or str(random.randint(1000, 9999))
        data = self.ttxc_post("/user/v1/updateNick", {"nickName": nick})
        if data.get("code") == 0:
            self.ttxc_nick_name = nick
            self.log(f"通通乡村: 已设置昵称 {nick}")
            return True
        self.log(f"通通乡村: 设置昵称失败[{data.get('code')}]: {data.get('msg', '')}")
        return False

    def ttxc_newbie_done(self):
        steps = getattr(self, "ttxc_newbie_list", None)
        return not isinstance(steps, list) or all(step in steps for step in TTXC_NEWBIE_STEPS)

    def ttxc_newbie_mark(self, step):
        target = []
        for item in TTXC_NEWBIE_STEPS:
            target.append(item)
            if item == step:
                break
        data = self.ttxc_post("/user/v1/newbie", {"newbieList": target, "type": 1})
        if data.get("code") == 0:
            self.ttxc_newbie_list = data.get("data") or target
            return True
        self.log(f"通通乡村: 新手步骤{step}失败[{data.get('code')}]: {data.get('msg', '')}")
        return False

    def ttxc_newbie_need(self, step):
        steps = getattr(self, "ttxc_newbie_list", None)
        return isinstance(steps, list) and step not in steps

    def ttxc_first_newbie_land(self, lands=None):
        lands = lands if lands is not None else self.ttxc_get_lands()
        active = next((land for land in lands if land.get("status") in [2, 3] and (land.get("plant") or {}).get("plantId")), None)
        if active:
            return active
        return next((land for land in lands if land.get("status") == 1), None)

    def ttxc_newbie_charge_land(self):
        lands = self.ttxc_get_lands()
        active = [land for land in lands if land.get("status") == 3 and (land.get("plant") or {}).get("plantId")]
        return next((land for land in active if str((land.get("plant") or {}).get("curLevel")) in ["0", "1"]), None) or (active[0] if active else None)

    def ttxc_harvest_land(self, land, newbie=False):
        if not land:
            return None
        plant = land.get("plant") or {}
        plant_id = plant.get("plantId")
        land_index = land.get("landIndex")
        if not plant_id or not land_index:
            return None
        if land.get("status") == 2 and TTXC_HARVEST_WAIT_SECONDS > 0:
            time.sleep(TTXC_HARVEST_WAIT_SECONDS)
        path = "/plant/v1/newHarvest" if newbie else "/plant/v1/harvest"
        data = self.ttxc_post(path, {"landIndex": land_index, "plantId": plant_id})
        if data.get("code") == 0:
            self.log(f"通通乡村: 地块{land_index}收获成功")
            return data.get("data") or {"landIndex": land_index, "status": 1, "plant": None}
        self.log(f"通通乡村: 地块{land_index}收获失败[{data.get('code')}]: {data.get('msg', '')}")
        return None

    def ttxc_newbie_task(self):
        if self.ttxc_newbie_done():
            return False
        need_farm = any(self.ttxc_newbie_need(step) for step in ["G03", "G03_2", "G04", "G05", "G09", "G10"])
        lands = self.ttxc_get_lands() if need_farm else []
        plant_id = ""
        current = self.ttxc_first_newbie_land(lands) if need_farm else None
        if need_farm:
            self.ttxc_post("/client/v1/plant/type", {})
            plant_id = self.ttxc_get_plant_id()
            if not plant_id:
                self.log("通通乡村: 新手任务缺少作物ID")
                return False
        if self.ttxc_newbie_need("G03") and not self.ttxc_newbie_mark("G03"):
            return False
        if self.ttxc_newbie_need("G03_2"):
            has_crop = current and current.get("status") in [2, 3] and (current.get("plant") or {}).get("plantId")
            if not has_crop:
                data = self.ttxc_post("/client/v1/plant/buy", {"plantId": plant_id, "gameCfgId": ""})
                if data.get("code") != 0:
                    self.log(f"通通乡村: 新手购买作物失败[{data.get('code')}]: {data.get('msg', '')}")
                    return False
            if not self.ttxc_newbie_mark("G03_2"):
                return False
        if self.ttxc_newbie_need("G04"):
            if not current or not current.get("landIndex"):
                self.log("通通乡村: 新手任务缺少可种植地块")
                return False
            if not (current.get("status") in [2, 3] and (current.get("plant") or {}).get("plantId")):
                data = self.ttxc_post("/plant/v1/planting", {"landIndex": current.get("landIndex"), "plantId": plant_id})
                if data.get("code") != 0:
                    self.log(f"通通乡村: 新手种植失败[{data.get('code')}]: {data.get('msg', '')}")
                    return False
                current = data.get("data") or {"landIndex": current.get("landIndex"), "status": 3, "plant": {"plantId": plant_id}}
            if not self.ttxc_newbie_mark("G04"):
                return False
        if self.ttxc_newbie_need("G05"):
            current = current if current and current.get("plant") else self.ttxc_first_newbie_land()
            current = self.ttxc_charge_land(current)
            if not current or not self.ttxc_newbie_mark("G05"):
                return False
        if self.ttxc_newbie_need("G09"):
            plant = (current or {}).get("plant") or {}
            level = str(plant.get("curLevel") or "")
            if not (current and current.get("status") == 3 and plant.get("plantId") and level in ["", "0", "1"]):
                current = self.ttxc_newbie_charge_land()
            current = self.ttxc_charge_land(current, mock=1)
            if not current or not self.ttxc_newbie_mark("G09"):
                return False
        if self.ttxc_newbie_need("G10"):
            current = current if current and current.get("plant") else self.ttxc_first_newbie_land()
            if not self.ttxc_harvest_land(current, newbie=True) or not self.ttxc_newbie_mark("G10"):
                return False
        if self.ttxc_newbie_need("G11") and not self.ttxc_newbie_mark("G11"):
            return False
        if self.ttxc_newbie_need("G12"):
            if not self.ttxc_nick_name and not self.ttxc_update_nick():
                return False
            if not self.ttxc_newbie_mark("G12"):
                return False
        self.log("通通乡村: 新手任务已完成")
        return True

    def ttxc_sign(self, is_query_only=False):
        info = self.ttxc_post("/client/v1/sign/info", {})
        code = (info.get("data") or {}).get("signinCode")
        if not code:
            self.log("通通乡村: 获取签到码失败")
            return
        user = self.ttxc_post("/client/v1/sign/user", {"code": code})
        last_time = str((user.get("data") or {}).get("lastSigninTime") or "")
        signed = last_time[:10] == datetime.now().strftime("%Y-%m-%d")
        if signed:
            self.log("通通乡村: 今日已签到", notify=True)
            return
        if is_query_only:
            self.log("通通乡村: 今日未签到", notify=True)
            return
        data = self.ttxc_post("/client/v1/sign/signIn", {"code": code})
        if data.get("code") == 0:
            sign_data = data.get("data") or {}
            keep_value = safe_int(sign_data.get("keepSigninValue") or sign_data.get("lastKeepSigninValue") or sign_data.get("totalSigninValue"))
            award_items = (info.get("data") or {}).get("awards") or []
            energy = 0
            for item in award_items:
                if item.get("awardType") == "KEEP" and safe_int(item.get("signinValue")) == keep_value:
                    energy = safe_int(item.get("carbonEnergyAmount"))
                    break
            if not energy:
                charge_level = data.get("chargeLevel") or {}
                before = safe_int(getattr(self, "ttxc_charge_level", {}).get("carbonNum"))
                after = safe_int(charge_level.get("carbonNum"))
                energy = max(after - before, 0)
            if data.get("chargeLevel"):
                self.ttxc_charge_level = data.get("chargeLevel") or self.ttxc_charge_level
            msg = f"通通乡村: 签到成功 +{energy}g" if energy else "通通乡村: 签到成功"
            self.log(msg, notify=True)
        else:
            self.log(f"通通乡村: 签到失败[{data.get('code')}]: {data.get('msg', '')}")

    def ttxc_get_tasks(self):
        data = self.ttxc_post("/client/v1/task/list", {})
        if data.get("code") != 0:
            self.log(f"通通乡村: 获取任务列表失败[{data.get('code')}]: {data.get('msg', '')}")
            return []
        tasks = []
        for group in data.get("data") or []:
            for task in group.get("taskList") or []:
                task["taskGroupName"] = group.get("taskGroupName", "")
                tasks.append(task)
        return tasks

    def ttxc_finish_task(self, task):
        task_id = task.get("taskCode")
        if not task_id:
            return False
        data = self.ttxc_post("/client/v1/task/finish", {"taskId": task_id})
        name = task.get("taskTitle", task_id)
        if data.get("code") == 0:
            reward = task.get("carbonEnergyAmount") or 0
            self.log(f"通通乡村: 领取[{name}]成功 +{reward}g")
            return True
        self.log(f"通通乡村: 领取[{name}]失败[{data.get('code')}]: {data.get('msg', '')}")
        return False

    def ttxc_do_task(self, task):
        data = self.ttxc_post("/client/v1/task/do", {"taskId": task.get("taskCode")})
        name = task.get("taskTitle", task.get("taskCode", ""))
        if data.get("code") == 0:
            self.log(f"通通乡村: 已执行[{name}]")
            return True
        self.log(f"通通乡村: 执行[{name}]失败[{data.get('code')}]: {data.get('msg', '')}")
        return False

    def ttxc_claim_ready_tasks(self, tasks, claimed=None):
        if claimed is None:
            claimed = set()
        count = 0
        for task in tasks:
            task_id = task.get("taskCode")
            if task.get("taskStatus") == "UNCLA" and task_id not in claimed:
                if self.ttxc_finish_task(task):
                    claimed.add(task_id)
                    count += 1
        return count

    def ttxc_do_jump_tasks(self, tasks):
        count = 0
        for task in tasks:
            if task.get("taskType") == "GAME" and task.get("taskStatus") == "UNDO" and task.get("jumpUrl"):
                if self.ttxc_do_task(task):
                    count += 1
                time.sleep(1)
        return count

    def ttxc_do_garbage_task(self, tasks):
        task = next((t for t in tasks if t.get("taskType") == "GAME" and t.get("taskStatus") == "UNDO" and "垃圾分类" in t.get("taskTitle", "")), None)
        if not task:
            return False
        start = self.ttxc_post("/user/v1/start", {})
        answer_no = (start.get("data") or {}).get("answerNo")
        if not answer_no:
            self.log("通通乡村: 垃圾分类开始失败")
            return False
        time.sleep(TTXC_GARBAGE_WAIT_SECONDS)
        data = self.ttxc_post("/user/v1/finish", {"answerNo": answer_no})
        if data.get("code") == 0:
            self.log("通通乡村: 垃圾分类已通关")
            return True
        self.log(f"通通乡村: 垃圾分类通关失败[{data.get('code')}]: {data.get('msg', '')}")
        return False

    def ttxc_prepare_newbie_energy(self, claimed=None):
        if claimed is None:
            claimed = set()
        self.ttxc_sign()
        tasks = self.ttxc_get_tasks()
        self.ttxc_claim_ready_tasks(tasks, claimed)
        self.ttxc_do_jump_tasks(tasks)
        self.ttxc_do_garbage_task(tasks)
        tasks = self.ttxc_get_tasks()
        self.ttxc_claim_ready_tasks(tasks, claimed)

    def ttxc_get_lands(self):
        land = safe_int(getattr(self, "ttxc_charge_level", {}).get("land"), 4)
        data = self.ttxc_post("/plant/v1/user", {"land": land})
        if data.get("code") != 0:
            self.log(f"通通乡村: 获取土地失败[{data.get('code')}]: {data.get('msg', '')}")
            return []
        return data.get("data") or []

    def ttxc_get_plant_id(self):
        data = self.ttxc_post("/client/v1/plant/page", {"itemType": "SPE", "pageNum": 1, "pageSize": 20})
        items = (data.get("data") or {}).get("list") or []
        return items[0].get("itemNo", "") if items else ""

    def ttxc_plant_land(self, land_index, plant_id=None):
        plant_id = plant_id or self.ttxc_get_plant_id()
        if not plant_id or not land_index:
            return None
        self.ttxc_post("/client/v1/plant/buy", {"plantId": plant_id, "gameCfgId": ""})
        data = self.ttxc_post("/plant/v1/planting", {"landIndex": land_index, "plantId": plant_id})
        if data.get("code") == 0:
            self.log(f"通通乡村: 已在地块{land_index}种植作物")
            return {"landIndex": land_index, "status": 3, "plant": {"plantId": plant_id}}
        self.log(f"通通乡村: 地块{land_index}种植失败[{data.get('code')}]: {data.get('msg', '')}")
        return None

    def ttxc_ensure_planted_lands(self, lands, needed=None):
        active = [l for l in lands if l.get("status") in [2, 3] and (l.get("plant") or {}).get("plantId")]
        empty = [l for l in lands if l.get("status") == 1]
        if not empty:
            return active
        plant_id = self.ttxc_get_plant_id()
        if not plant_id:
            return active
        for land in empty:
            planted = self.ttxc_plant_land(land.get("landIndex"), plant_id)
            if planted:
                active.append(planted)
        return active

    def ttxc_charge_land(self, land, mock=None):
        if not land:
            return False
        plant = land.get("plant") or {}
        plant_id = plant.get("plantId")
        land_index = land.get("landIndex")
        if not plant_id or not land_index:
            return False
        data = self.ttxc_post("/plant/v1/charge", {"landIndex": land_index, "plantId": plant_id, "mock": mock})
        if data.get("code") == 0:
            self.log(f"通通乡村: 地块{land_index}充能成功")
            result = data.get("data") or {}
            if result and not result.get("plant"):
                result["plant"] = plant
            return result or land
        self.log(f"通通乡村: 地块{land_index}充能失败[{data.get('code')}]: {data.get('msg', '')}")
        return None

    def ttxc_harvest_and_replant(self, land):
        harvested = self.ttxc_harvest_land(land)
        return self.ttxc_plant_land(land.get("landIndex")) if harvested and land else None

    def ttxc_grow_land_to_harvest(self, land):
        current = land
        if current.get("status") == 2:
            self.ttxc_harvest_and_replant(current)
            return
        charged = 0
        while current.get("status") == 3 and charged < TTXC_GROW_MAX_CHARGE_PER_LAND:
            current = self.ttxc_charge_land(current)
            if not current:
                return
            charged += 1
            if current.get("status") == 2:
                self.ttxc_harvest_and_replant(current)
                return
            if charged < TTXC_GROW_MAX_CHARGE_PER_LAND:
                time.sleep(1)
        if current.get("status") == 3:
            self.log(f"通通乡村: 地块{current.get('landIndex')}催熟达到上限，跳过")

    def ttxc_replace_land(self, lands, updated):
        land_index = updated.get("landIndex")
        for i, land in enumerate(lands):
            if land.get("landIndex") == land_index:
                lands[i] = updated
                return
        lands.append(updated)

    def ttxc_complete_charge_task(self, active, remaining):
        while remaining > 0:
            immature = [land for land in active if land.get("status") == 3 and (land.get("plant") or {}).get("plantId")]
            if not immature:
                self.log("通通乡村: 未成熟作物不足，提前结束10次充能补足")
                return
            progressed = False
            for land in immature:
                if remaining <= 0:
                    return
                result = self.ttxc_charge_land(land)
                if result:
                    self.ttxc_replace_land(active, result)
                    remaining -= 1
                    progressed = True
                time.sleep(1)
            if not progressed:
                self.log("通通乡村: 充能未成功，提前结束10次充能补足")
                return

    def ttxc_farm_tasks(self, tasks):
        charge_task = next((t for t in tasks if "10次作物充能" in t.get("taskTitle", "")), None)
        land_task = next((t for t in tasks if "三块不同" in t.get("taskTitle", "")), None)
        harvest_task = next((t for t in tasks if "收获一次作物" in t.get("taskTitle", "")), None)
        if not charge_task and not land_task and not harvest_task:
            return
        charge_pending = charge_task if (charge_task or {}).get("taskStatus") == "UNDO" else None
        land_pending = land_task if (land_task or {}).get("taskStatus") == "UNDO" else None
        harvest_pending = harvest_task if (harvest_task or {}).get("taskStatus") == "UNDO" else None
        if not charge_pending and not land_pending and not harvest_pending:
            return
        lands = self.ttxc_get_lands()
        active = self.ttxc_ensure_planted_lands(lands)
        need_land = max(safe_int((land_pending or {}).get("finishValue")) - safe_int((land_pending or {}).get("doneValue")), 0)
        if harvest_pending and not charge_pending and not land_pending:
            for land in active:
                if land.get("status") == 2:
                    self.ttxc_harvest_and_replant(land)
        if not active:
            self.log("通通乡村: 没有可充能作物")
            return
        if not safe_int(getattr(self, "ttxc_charge_level", {}).get("carbonNum"), 0):
            self.log("通通乡村: 碳能量为0g，跳过充能/催熟 (需先做任务攒能量)")
            return
        charged = 0
        for i, land in enumerate(active[:need_land]):
            result = self.ttxc_charge_land(land)
            if result:
                active[i] = result
                charged += 1
                time.sleep(1)
        need_charge = max(safe_int((charge_pending or {}).get("finishValue")) - safe_int((charge_pending or {}).get("doneValue")) - charged, 0)
        self.ttxc_complete_charge_task(active, need_charge)
        for land in active:
            self.ttxc_grow_land_to_harvest(land)

    def ttxc_task(self, is_query_only=False):
        self.log("==== 通通乡村 ====")
        try:
            if not self.ttxc_login(update_nick=not is_query_only):
                return
            claimed = set()
            if not is_query_only:
                if not self.ttxc_newbie_done():
                    self.ttxc_prepare_newbie_energy(claimed)
                if not self.ttxc_newbie_done() and not self.ttxc_newbie_task():
                    return
            self.ttxc_sign(is_query_only=is_query_only)
            tasks = self.ttxc_get_tasks()
            if is_query_only:
                todo = sum(1 for t in tasks if t.get("taskStatus") == "UNDO")
                claim = sum(1 for t in tasks if t.get("taskStatus") == "UNCLA")
                self.log(f"通通乡村: 待做{todo}个，可领取{claim}个", notify=True)
                return
            self.ttxc_claim_ready_tasks(tasks, claimed)
            self.ttxc_do_jump_tasks(tasks)
            self.ttxc_do_garbage_task(tasks)
            self.ttxc_farm_tasks(tasks)
            tasks = self.ttxc_get_tasks()
            self.ttxc_claim_ready_tasks(tasks, claimed)
        except Exception as e:
            self.log(f"通通乡村异常: {e}")

    def regional_task(self, is_query_only=False):
        """区域专区任务入口"""
        is_xinjiang = False
        is_henan = False
        is_yunnan = False
        is_liaoning = False
        is_anhui = False
        if hasattr(self, 'city_info') and self.city_info and isinstance(self.city_info, list):
            try:
                for city in self.city_info:
                    pro_name = city.get('proName', '')
                    if "新疆" in pro_name: is_xinjiang = True
                    if "河南" in pro_name: is_henan = True
                    if "云南" in pro_name: is_yunnan = True
                    if "辽宁" in pro_name: is_liaoning = True
                    if "安徽" in pro_name: is_anhui = True
            except: pass
        rc = globalConfig.get("regional_config", {})
        if is_query_only:
            self.log("==== 区域专区 (查询模式) ====")
            if is_xinjiang:
                self.log("新疆专区: [查询模式] 跳过每日打卡，尝试查询每月抽奖记录")
                try:
                    ticket_res = self.openPlatLineNew("https://zy100.xj169.com/touchpoint/openapi/jumpHandRoom1G?source=155&type=02")
                    if ticket_res and ticket_res.get("ticket"):
                        token = self.xj_get_token(ticket_res.get("ticket"))
                        if token:
                            self.xj_query_monthly_draw_records(token)
                except Exception as e:
                    self.log(f"新疆专区: [查询模式] 查询每月抽奖记录异常 {e}")
            if is_henan:
                is_signed = self.shangdu_get_sign_status()
                if is_signed is True:
                    self.log("河南商都: [状态查询] 今日已签到")
                elif is_signed is False:
                    self.log("河南商都: [状态查询] 今日未签到")
                else:
                    self.log("河南商都: [状态查询] 查询失败")
            if is_yunnan:
                self.yunnan_life_task(is_query_only=True)
            if is_liaoning:
                self.ln_flmf_task(is_query_only=True)
            if is_anhui and AH_FRIDAY_AMOUNT:
                self.log(f"安徽超级星期五: [查询模式] 目标面额{AH_FRIDAY_AMOUNT}元 (仅周五10点执行)")
            return
        if is_xinjiang:
            self.log("==== 新疆专区 ====")
            self.xj_task_main()
        if is_henan:
            self.log("==== 河南商都 ====")
            self.shangdu_task_main()
        if is_yunnan:
            self.log("==== 云南生活 ====")
            self.yunnan_life_task()
        if is_liaoning:
            self.log("==== 辽宁福利魔方 ====")
            self.ln_flmf_task()
        if is_anhui and AH_FRIDAY_AMOUNT and rc.get("run_ah_friday", True):
            self.log("==== 安徽超级星期五 ====")
            self.ah_friday_task()

    def yunnan_life_base_headers(self, token=None, extra=None):
        headers = {
            "Referer": "https://wsm.wx.yn10010.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Content-Type": "application/json;charset=UTF-8",
            "Accept-Language": "zh-CN,en-US;q=0.8",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 unicom{version:iphone_c@12.1001};ltst;OSVersion/16.6",
        }
        if token:
            headers["token"] = token
        if extra:
            headers.update(extra)
        return headers

    def yunnan_life_calc_sign(self, payload):
        parts = []
        for key in sorted(payload.keys()):
            value = payload[key]
            if isinstance(value, dict):
                encoded = quote(json.dumps(value, ensure_ascii=False, separators=(',', ':')), safe="")
            else:
                encoded = quote(str(value), safe="")
            parts.append(f"{key}={encoded}")
        raw = "&".join(parts).lower() + YUNNAN_LIFE_SIGN_SALT
        return hashlib.md5(hashlib.md5(raw.encode('utf-8')).hexdigest().encode('utf-8')).hexdigest()

    def yunnan_life_signed_headers(self, token, payload):
        return self.yunnan_life_base_headers(token, {
            "Origin": YUNNAN_LIFE_BASE_URL,
            "accessKeyId": YUNNAN_LIFE_ACCESS_KEY,
            "time": str(round(time.time() * 1000)),
            "sign": self.yunnan_life_calc_sign(payload),
        })

    def yunnan_life_get_ticket(self):
        if not self.ecs_token:
            return None
        try:
            res = self.session.get(
                "https://m.client.10010.com/mobileService/openPlatform/openPlatLineNew.htm",
                params={
                    "to_url": YUNNAN_LIFE_TO_URL,
                    "amp;s": "100000425",
                    "amp;boothCode": "YN-QCQYCS245",
                    "amp;boothAccessMode": "24",
                },
                headers={
                    "Cookie": f"ecs_token={self.ecs_token}",
                    "Referer": "https://wsm.wx.yn10010.com/",
                    "Accept-Language": "zh-CN,zh-Hans;q=0.9",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Site": "cross-site",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "User-Agent": self.yunnan_life_base_headers().get("User-Agent"),
                },
                allow_redirects=False,
                timeout=15,
            )
            location = res.headers.get("Location", "")
            match = re.search(r'ticket=([^&]+)', location)
            return match.group(1) if match else None
        except Exception as e:
            self.log(f"云南生活: 获取 ticket 异常: {e}")
            return None

    def yunnan_life_get_token(self, ticket):
        if not ticket:
            return None
        try:
            resp = self.session.get(
                f"{YUNNAN_LIFE_BASE_URL}/2b2c-mobile/getPhoneNumber",
                params={"ticket": ticket},
                headers=self.yunnan_life_base_headers(extra={"Content-Type": "application/json;charset=gb2312"}),
                timeout=15,
            )
            token = resp.headers.get("token") or resp.headers.get("Token")
            if not token:
                try:
                    data = resp.json()
                except Exception:
                    data = {}
                token = data.get("token") or data.get("data", {}).get("token")
            if not token:
                self.log(f"云南生活: 未找到 token，响应: {resp.text[:160]}")
                return None
            return token if str(token).startswith("Bearer ") else f"Bearer {token}"
        except Exception as e:
            self.log(f"云南生活: 获取 token 异常: {e}")
            return None

    def yunnan_life_login(self):
        ticket = self.yunnan_life_get_ticket()
        if not ticket:
            self.log("云南生活: 获取 ticket 失败")
            return None
        token = self.yunnan_life_get_token(ticket)
        if not token:
            self.log("云南生活: 获取 token 失败")
            return None
        return token

    def yunnan_life_do_task(self, token, payload):
        task_name = payload.get("taskName", payload.get("taskCode", "未知任务"))
        try:
            res = self.session.post(
                f"{YUNNAN_LIFE_BASE_URL}/2b2c-mobile/activity/task/addTaskUser",
                data=json.dumps(payload, ensure_ascii=False, separators=(',', ':')),
                headers=self.yunnan_life_signed_headers(token, payload),
                timeout=15,
            ).json()
            if res.get("resultCode") == "0000":
                self.log(f"云南生活: ✅ {task_name}")
            else:
                self.log(f"云南生活: ❌ {task_name}: {res.get('resultMsg', '')}")
        except Exception as e:
            self.log(f"云南生活: [{task_name}] 异常: {e}")

    def yunnan_life_do_lottery(self, token, times=2):
        payload = {"actId": YUNNAN_LIFE_ACT_ID, "boothCode": ""}
        headers = self.yunnan_life_base_headers(token, {"Origin": YUNNAN_LIFE_BASE_URL})
        for i in range(times):
            try:
                res = self.session.post(
                    f"{YUNNAN_LIFE_BASE_URL}/2b2c-mobile/acttmpl/lottery/actLuckyDrawy",
                    data=json.dumps(payload, ensure_ascii=False, separators=(',', ':')),
                    headers=headers,
                    timeout=15,
                ).json()
                if res.get("resultCode") == "0000":
                    self.log(f"云南生活: ✅ 第{i + 1}次抽奖请求成功")
                else:
                    self.log(f"云南生活: ❌ 第{i + 1}次抽奖失败: {res.get('resultMsg', '')}")
            except Exception as e:
                self.log(f"云南生活: 第{i + 1}次抽奖异常: {e}")
            if i < times - 1:
                time.sleep(2)

    def yunnan_life_get_lottery_results(self, token):
        try:
            resp = self.session.get(
                f"{YUNNAN_LIFE_BASE_URL}/2b2c-mobile/acttmpl/lottery/getUserRecordListActInfo",
                params={"actId": YUNNAN_LIFE_ACT_ID, "periodId": YUNNAN_LIFE_ACT_ID},
                headers=self.yunnan_life_base_headers(token, {"Content-Type": "application/json;charset=gb2312"}),
                timeout=15,
            )
            data = resp.json()
            today = datetime.now().strftime("%Y-%m-%d")
            awards = []
            for item in data.get("data", {}).get("recordList", []):
                if str(item.get("createTime", "")).startswith(today):
                    awards.append(item.get("awardName", "未知"))
            if awards:
                for award in awards:
                    self.log(f"云南生活: 🎁 抽奖结果 - {award}", notify=True)
            else:
                self.log("云南生活: 今日暂无抽奖记录")
        except Exception as e:
            self.log(f"云南生活: 查询抽奖结果异常: {e}")

    def yunnan_life_get_bean_balance(self, token):
        try:
            payload = {}
            res = self.session.post(
                f"{YUNNAN_LIFE_BASE_URL}/user/beans/api/getTotalAvailableBeansByPhone",
                data=json.dumps(payload, ensure_ascii=False, separators=(',', ':')),
                headers=self.yunnan_life_signed_headers(token, payload),
                timeout=15,
            ).json()
            if res.get("resultCode") == "0000":
                self.log(f"云南生活: 💰 当前云豆余额: {res.get('data', 0)}", notify=True)
            else:
                self.log(f"云南生活: 获取云豆失败: {res.get('resultMsg', '')}")
        except Exception as e:
            self.log(f"云南生活: 查询云豆异常: {e}")

    def yunnan_life_task(self, is_query_only=False):
        token = self.yunnan_life_login()
        if not token:
            return
        if is_query_only:
            self.log("云南生活: [查询模式] 查询云豆余额")
            self.yunnan_life_get_bean_balance(token)
            return
        for task in YUNNAN_LIFE_TASKS:
            self.yunnan_life_do_task(token, task)
            time.sleep(2)
        self.yunnan_life_do_lottery(token, times=2)
        self.yunnan_life_get_lottery_results(token)
        self.yunnan_life_get_bean_balance(token)

    def xj_task_main(self):
        ticket_res = self.openPlatLineNew("https://zy100.xj169.com/touchpoint/openapi/jumpHandRoom1G?source=155&type=02")
        if not ticket_res or not ticket_res.get("ticket"):
            self.log("新疆专区: 获取入口 ticket 失败")
            return
        token = self.xj_get_token(ticket_res.get("ticket"))
        if token:
            self.xj_do_draw(token, "Jan2026Act")
            day = datetime.now().day
            if 19 <= day <= 25:
                self.xj_usersday_task(token)
            self.xj_monthly_draw_task(token)

    def xj_get_token(self, ticket):
        try:
            url = "https://zy100.xj169.com/touchpoint/openapi/getTokenAndCity"
            if isinstance(ticket, dict):
                ticket = ticket.get("ticket")
            data = {"ticket": ticket}
            headers = {
                "Referer": f"https://zy100.xj169.com/touchpoint/openapi/jumpHandRoom1G?source=155&type=02&ticket={ticket}",
                "User-Agent": XJ_USER_AGENT,
            }
            res = self.session.post(url, data=data, headers=headers).json()
            result = res.get('result', {})
            if result.get('code') == 0 and result.get('data', {}).get('token'):
                return result.get('data', {}).get('token')
            token = res.get("data", {}).get("token")
            if token:
                return token
            return None
        except Exception as e:
            self.log(f"新疆专区: 获取 token 异常 {e}")
            return None

    def xj_do_draw(self, token, act_id):
        try:
            url = f"https://zy100.xj169.com/touchpoint/openapi/marchAct/draw_{act_id}"
            data = {"activityId": f"daka{act_id}", "prizeId": ""}
            headers = {"userToken": token, "User-Agent": XJ_USER_AGENT}
            res = self.session.post(url, data=data, headers=headers).json()
            msg = res.get('result', {}).get('msg') or res.get('result', {}).get('data') or "失败"
            self.log(f"新疆专区: 每日打卡 - {msg}", notify=True)
        except Exception as e:
            self.log(f"新疆专区: 打卡异常 {e}")

    def xj_usersday_task(self, token):
        try:
            url = "https://zy100.xj169.com/touchpoint/openapi/marchAct/draw_UsersDay2025Act"
            data = {"activityId": "usersDay2025Act", "prizeId": "hfq_twenty"}
            headers = {"userToken": token, "User-Agent": XJ_USER_AGENT}
            res = self.session.post(url, data=data, headers=headers).json()
            msg = res.get('result', {}).get('msg') or res.get('result', {}).get('data') or "失败"
            self.log(f"新疆客户日: 秒杀结果 - {msg}", notify=True)
        except Exception as e:
            self.log(f"新疆客户日: 秒杀异常 {e}")

    def xj_monthly_draw_once(self, token):
        headers = {
            "User-Agent": XJ_USER_AGENT,
            "userToken": token,
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        }
        payload = {"activityId": XJ_ACTIVITY_ID, "prizeId": "", "commHighFlag": "false"}
        try:
            res = self.session.post(
                f"https://zy100.xj169.com/touchpoint/openapi/themeAct/draw_{XJ_ACTIVITY_ID}",
                data=payload,
                headers=headers,
                timeout=10,
            ).json()
            code = res.get("code")
            msg = str(res.get("msg", ""))
            msg_type = str(res.get("msgType", ""))
            data = res.get("data", "")
            if code == "ERROR":
                data_str = str(data)
                if "已用完" in data_str or "已抽完" in data_str or msg_type == "101":
                    return "done", f"今日机会已用尽 ({data_str or msg or '无可用次数'})"
                if "频率过高" in msg:
                    return "done", "接口频率限制"
                if "缺少参数" in msg:
                    return "invalid", "token 已失效"
                return "done", f"抽奖失败: {data_str or msg or '未知错误'}"
            if code == "SUCCESS":
                if msg == "thanks1":
                    return "continue", f"未中奖 ({data or msg})"
                return "won", f"中奖: {data or '未知奖品'}"
            if str(code) == "401":
                return "invalid", "token 已失效"
            return "continue", f"未中奖 ({msg or data or code})"
        except Exception as e:
            return "error", f"请求异常: {e}"

    def xj_query_monthly_draw_records(self, token):
        headers = {
            "User-Agent": XJ_USER_AGENT,
            "userToken": token,
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        }
        try:
            res = self.session.post(
                "https://zy100.xj169.com/touchpoint/openapi/drawAct/getPrizesScroll",
                data={"activityId": XJ_ACTIVITY_ID},
                headers=headers,
                timeout=10,
            ).json()
            data = res.get("data", [])
            if not data:
                self.log("新疆专区: 每月抽奖暂无中奖记录")
                return
            if isinstance(data, dict):
                data = [data]
            if isinstance(data, list) and data and isinstance(data[0], str):
                for item in data[:5]:
                    self.log(f"新疆专区: 每月抽奖记录 - {item}", notify=True)
                return
            displayed = 0
            for item in data:
                if not isinstance(item, dict):
                    continue
                prize_name = item.get("prizeName") or item.get("prizeId") or "未知奖品"
                draw_ts = safe_int(item.get("drawDate"), 0)
                draw_date = datetime.fromtimestamp(draw_ts / 1000).strftime("%m-%d") if draw_ts else "未知时间"
                self.log(f"新疆专区: 每月抽奖记录 - {prize_name} ({draw_date})", notify=True)
                displayed += 1
                if displayed >= 5:
                    break
            if displayed == 0:
                self.log("新疆专区: 每月抽奖暂无可展示记录")
        except Exception as e:
            self.log(f"新疆专区: 查询每月抽奖记录异常 {e}")

    def xj_monthly_draw_task(self, token):
        self.log(f"新疆专区: 每月抽奖活动 {XJ_ACTIVITY_ID}")
        for i in range(XJ_MONTHLY_DRAW_ATTEMPT_COUNT):
            status, msg = self.xj_monthly_draw_once(token)
            self.log(
                f"新疆专区: 每月抽奖第{i + 1}次 - {msg}",
                notify=status == "won",
            )
            if status in {"done", "won", "invalid"}:
                break
            time.sleep(random.uniform(1, 2))
        self.xj_query_monthly_draw_records(token)

    def shangdu_get_sign_status(self):
        try:
            url = "https://app.shangdu.com/monthlyBenefit/v1/signIn/queryCumulativeSignAxis"
            headers = {
                "Origin": "https://app.shangdu.com",
                "Referer": "https://app.shangdu.com/monthlyBenefit/index.html",
                "edop_flag": "0", "Content-Type": "application/json"
            }
            res = self.session.post(url, json={}, headers=headers).json()
            if res.get('result', {}).get('code') == "0000":
                return res.get('result', {}).get('data', {}).get('todaySignFlag') == "1"
            return None
        except: return None

    def shangdu_sign_retry(self):
        try:
            url = "https://app.shangdu.com/monthlyBenefit/v1/signIn/userSignIn"
            headers = {
                "Origin": "https://app.shangdu.com",
                "Referer": "https://app.shangdu.com/monthlyBenefit/index.html",
                "edop_flag": "0", "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/json"
            }
            res = self.session.post(url, json={}, headers=headers).json()
            code = res.get('result', {}).get('code')
            data = res.get('result', {}).get('data', {})
            if code == "0000":
                prize = data.get('prizeResp', {}).get('prizeName')
                if prize: self.log(f"河南商都: 签到成功(重试) - 获得 {prize}", notify=True)
                else: self.log("河南商都: 签到成功(重试)")
            elif code == "0019":
                self.log("河南商都: 重试仍返回重复签到")
            else:
                self.log(f"河南商都: A签到重试失败 - {res.get('result', {}).get('msg')}")
        except Exception as e:
            self.log(f"河南商都: 签到重试异常 {e}")

    def shangdu_task_main(self):
        if not self.ecs_token: return
        url = f"https://m.client.10010.com/edop_ng/getTicketByNative?appId=edop_unicom_4b80047a&token={self.ecs_token}"
        res = self.session.get(url).json()
        ticket = res.get('result', {}).get('ticket')
        if not ticket:
            self.log("河南商都: 获取Ticket失败")
            return
        login_url = f"https://app.shangdu.com/monthlyBenefit/v1/common/config?ticket={ticket}"
        headers_login = {
             "Origin": "https://app.shangdu.com",
             "Referer": "https://app.shangdu.com/monthlyBenefit/index.html",
             "edop_flag": "0", "Accept": "application/json, text/plain, */*"
        }
        self.session.get(login_url, headers=headers_login)
        time.sleep(1.5)
        sign_url = "https://app.shangdu.com/monthlyBenefit/v1/signIn/userSignIn"
        headers_sign = {
             "Origin": "https://app.shangdu.com",
             "Referer": "https://app.shangdu.com/monthlyBenefit/index.html",
             "edop_flag": "0", "X-Requested-With": "XMLHttpRequest",
             "Content-Type": "application/json"
        }
        res_sign = self.session.post(sign_url, json={}, headers=headers_sign).json()
        code = res_sign.get('result', {}).get('code')
        data = res_sign.get('result', {}).get('data', {})
        if code == "0000":
             if data.get('value') == "0001":
                 self.log("河南商都: 签到失败 - Cookie无效")
             else:
                 prize = data.get('prizeResp', {}).get('prizeName', '已签到')
                 self.log(f"河南商都: 签到结果 - {prize}", notify=True)
        elif code == "0019":
             time.sleep(1)
             is_signed = self.shangdu_get_sign_status()
             if is_signed is True:
                 self.log("河南商都: 今日已签到")
             elif is_signed is False:
                 self.log("河南商都: 状态未签到但返回重复，尝试重试...")
                 time.sleep(2)
                 self.shangdu_sign_retry()
             else:
                 self.log("河南商都: 今日已签到 (状态未知)")
        else:
             self.log(f"河南商都: 签到失败 - {code} : {res_sign.get('result', {}).get('msg')}")

    def ln_flmf_get_sid(self):
        """辽宁福利魔方: 通过 openPlatLineNew → autoLogin 获取 sid"""
        try:
            ticket_res = self.openPlatLineNew("https://weixin.linktech.hk/lv-web/handHall/autoLogin?actcode=sign")
            if not ticket_res or not ticket_res.get('ticket'):
                self.log("辽宁福利魔方: 获取ticket失败")
                return None
            ticket = ticket_res['ticket']
            type_val = ticket_res.get('type', '06')
            mobile = getattr(self, 'account_mobile', getattr(self, 'mobile', ''))
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            postage = hashlib.md5(f"{mobile}{timestamp}".encode()).hexdigest()
            login_url = "https://weixin.linktech.hk/lv-web/handHall/autoLogin"
            params = {
                "actcode": "sign",
                "type": type_val,
                "ticket": ticket,
                "version": COMMON_CONSTANTS["APP_VERSION"],
                "timestamp": timestamp,
                "desmobile": mobile,
                "num": "0",
                "postage": postage,
                "userNumber": mobile
            }
            res = self.session.get(login_url, params=params, allow_redirects=False, timeout=15)
            if res.status_code != 302 or 'Location' not in res.headers:
                self.log(f"辽宁福利魔方: autoLogin期望302, 实际{res.status_code}")
                return None
            loc = res.headers['Location']
            sid_match = re.search(r'sid[=%]3[Dd]?([a-f0-9]{32})', loc)
            if not sid_match:
                parsed = urlparse(unquote(loc))
                qs = parse_qs(parsed.query)
                params_val = qs.get('params', [''])[0]
                if 'sid=' in params_val:
                    inner_qs = parse_qs(params_val)
                    sid = inner_qs.get('sid', [''])[0]
                else:
                    sid = qs.get('sid', [''])[0]
            else:
                sid = sid_match.group(1)
            if sid and len(sid) == 32:
                self.log(f"辽宁福利魔方: 获取sid成功 ({sid[:8]}...)")
                return sid
            self.log(f"辽宁福利魔方: 重定向中未找到sid")
        except Exception as e:
            self.log(f"辽宁福利魔方: 获取sid异常 - {e}")
        return None

    def ln_flmf_api(self, sid, endpoint, extra_data=None):
        """辽宁福利魔方: 通用API调用"""
        url = f"https://weixin.linktech.hk/lv-apiaccess/welfareCenter/{endpoint}"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://weixin.linktech.hk",
            "Referer": f"https://weixin.linktech.hk/app/flmf/LV-202111-04/moreShatter?sid={sid}&actcode=welfareCenter",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; MI 8) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/143.0.7499.146 Mobile Safari/537.36; unicom{version:android@11.0802}"
        }
        data = f"sid={sid}&actcode=welfareCenter"
        if extra_data:
            data += f"&{extra_data}"
        try:
            res = self.session.post(url, headers=headers, data=data, timeout=15).json()
            return res
        except Exception as e:
            self.log(f"辽宁福利魔方: {endpoint} 请求异常 - {e}")
            return None

    def ln_flmf_task(self, is_query_only=False):
        """辽宁福利魔方: 主入口"""
        sid = self.ln_flmf_get_sid()
        if not sid:
            return
        res = self.ln_flmf_api(sid, "addUser")
        if not res or res.get('resultCode') != '0000':
            self.log(f"辽宁福利魔方: 用户初始化失败 - {(res or {}).get('resultMsg', '无响应')}")
            return
        time.sleep(1)
        init_res = self.ln_flmf_api(sid, "signInInit")
        if init_res and init_res.get('resultCode') == '0000':
            init_data = init_res.get('data', {})
            is_signed = init_data.get('isSigned', 0)
            consecutive = init_data.get('consecutiveDays', 0)
            if is_signed:
                self.log(f"辽宁福利魔方: 今日已签到 (连续{consecutive}天)")
            elif is_query_only:
                self.log(f"辽宁福利魔方: 今日未签到 (连续{consecutive}天)")
            else:
                time.sleep(1)
                sign_res = self.ln_flmf_api(sid, "signIn")
                if sign_res and sign_res.get('resultCode') == '0000':
                    self.log(f"辽宁福利魔方: ✅ 签到成功 (连续{consecutive + 1}天)", notify=True)
                else:
                    self.log(f"辽宁福利魔方: 签到失败 - {(sign_res or {}).get('resultMsg', '无响应')}")
        else:
            self.log(f"辽宁福利魔方: 查询签到状态失败 - {(init_res or {}).get('resultMsg', '无响应')}")
        time.sleep(1)
        info_res = self.ln_flmf_api(sid, "getUserInfo")
        if info_res and info_res.get('resultCode') == '0000':
            info = info_res.get('data', {})
            wobi = info.get('woBi', 0)
            sign_times = info.get('signTimes', 0)
            member_wobi = info.get('memberwobi', 0)
            member_trun = info.get('membertrun', 0)
            rights_num = info.get('rightsNum', '0')
            self.log(f"辽宁福利魔方: 沃币{wobi} | 累计签到{sign_times}天 | 会员碎片{member_wobi} | 等级{member_trun} | 权益{rights_num}次", notify=True)
        if is_query_only:
            return
        time.sleep(1)
        task_res = self.ln_flmf_api(sid, "taskList", "refresh=0&nowTask=")
        if task_res and task_res.get('resultCode') == '0000':
            groups = task_res.get('data', {}).get('taskInfoList', [])
            for group in groups:
                tasks = group.get('taskInfoList', [])
                for t in tasks:
                    status = "✅" if t.get('done', 0) > 0 else "⏳"
                    self.log(f"辽宁福利魔方: {status} {t.get('taskName')} ({t.get('done', 0)}/{t.get('count', 0)})")

    def ah_friday_get_entry(self):
        """安徽超级星期五: 获取活动入口ticket"""
        try:
            entry_url = f"{AH_FRIDAY_BASE_URL}/wxopen/hh/activity/superFriday/index?chnlId=app-ty&type=02"
            ticket_res = self.openPlatLineNew(entry_url)
            if not ticket_res or not ticket_res.get('ticket'):
                self.log("安徽超级星期五: 获取入口ticket失败")
                return None
            ticket = ticket_res['ticket']
            mobile = getattr(self, 'account_mobile', getattr(self, 'mobile', ''))
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            postage = hashlib.md5(f"{mobile}{timestamp}".encode()).hexdigest()
            page_url = f"{AH_FRIDAY_BASE_URL}/wxopen/hh/activity/superFriday/index"
            params = {
                "chnlId": "app-ty",
                "type": "02",
                "ticket": ticket,
                "version": COMMON_CONSTANTS["APP_VERSION"],
                "timestamp": timestamp,
                "desmobile": mobile,
                "num": "0",
                "postage": postage,
                "userNumber": mobile
            }
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "User-Agent": COMMON_CONSTANTS["UA"],
            }
            res = self.session.get(page_url, params=params, headers=headers, timeout=15)
            cookies = res.cookies.get_dict()
            act_ticket = cookies.get('ticket', '')
            if not act_ticket:
                cookie_header = res.headers.get('Set-Cookie', '')
                m = re.search(r'ticket=([^;]+)', cookie_header)
                if m:
                    act_ticket = m.group(1)
            if not act_ticket:
                m = re.search(r'ticket=([a-f0-9]+)', res.text)
                if m:
                    act_ticket = m.group(1)
            if not act_ticket:
                self.log("安徽超级星期五: 未获取到活动ticket")
                return None
            self.log(f"安徽超级星期五: 获取活动ticket成功 ({act_ticket[:12]}...)")
            return {
                "ticket": act_ticket,
                "mobile": mobile,
                "timestamp": timestamp,
                "postage": postage,
                "app_ticket": ticket,
            }
        except Exception as e:
            self.log(f"安徽超级星期五: 获取入口异常 - {e}")
            return None

    def ah_friday_get_items(self, entry_info):
        """安徽超级星期五: 获取奖品列表并匹配目标面额"""
        try:
            url = f"{AH_FRIDAY_BASE_URL}/wxopen/app-activity/AHSecKill/querySecKillInfo"
            headers = {
                "Accept": "application/json, text/plain, */*",
                "Content-Type": "application/json",
                "Origin": AH_FRIDAY_BASE_URL,
                "Cookie": f"ticket={entry_info['ticket']}",
                "User-Agent": COMMON_CONSTANTS["UA"],
            }
            res = self.session.post(url, json={}, headers=headers, timeout=10)
            result = res.json()
            if not result.get('success') and not result.get('data'):
                self.log(f"安徽超级星期五: 查询奖品列表失败 - {result.get('alertMsg', '未知')}")
                return None
            items = result.get('data', {}).get('itemList', [])
            if not items:
                items = result.get('data', []) if isinstance(result.get('data'), list) else []
            target_amount = str(AH_FRIDAY_AMOUNT)
            for item in items:
                item_code = item.get('itemCode', '')
                item_name = item.get('itemName', '')
                if target_amount in item_name or f"hb{target_amount}" in item_code:
                    key_val = item.get('key', '')
                    self.log(f"安徽超级星期五: 匹配到目标 [{item_name}] (code: {item_code})")
                    return {
                        "itemCode": item_code,
                        "itemName": item_name,
                        "key": key_val,
                    }
            item_code = f"AWARD_AHFridaySecKill_10_hb{target_amount}"
            self.log(f"安徽超级星期五: 未从列表匹配到{target_amount}元, 使用默认itemCode: {item_code}")
            return {"itemCode": item_code, "itemName": f"{target_amount}元红包", "key": ""}
        except Exception as e:
            self.log(f"安徽超级星期五: 查询奖品异常 - {e}")
            item_code = f"AWARD_AHFridaySecKill_10_hb{AH_FRIDAY_AMOUNT}"
            return {"itemCode": item_code, "itemName": f"{AH_FRIDAY_AMOUNT}元红包", "key": ""}

    def ah_friday_seckill(self, entry_info, item_info):
        """安徽超级星期五: 批量抢购"""
        ticket = entry_info['ticket']
        item_code = item_info['itemCode']
        key_val = item_info.get('key', '')
        mobile = entry_info['mobile']
        timestamp_str = entry_info['timestamp']
        postage = entry_info['postage']
        referer = (
            f"{AH_FRIDAY_BASE_URL}/wxopen/hh/activity/superFriday/index"
            f"?chnlId=app-ty&type=02&ticket={entry_info['app_ticket']}"
            f"&version={COMMON_CONSTANTS['APP_VERSION']}&timestamp={timestamp_str}"
            f"&desmobile={mobile}&num=0&postage={postage}&userNumber={mobile}"
        )
        success_count = 0
        fail_count = 0
        self.log(f"安徽超级星期五: 开始批量抢购 [{item_info['itemName']}]，共{AH_FRIDAY_SECKILL_TIMES}次")
        for i in range(1, AH_FRIDAY_SECKILL_TIMES + 1):
            try:
                ts = str(int(time.time() * 1000))
                params = {
                    "ticket": ticket,
                    "itemCode": item_code,
                    "time": ts,
                }
                if key_val:
                    params["key"] = key_val
                url = f"{AH_FRIDAY_BASE_URL}/wxopen/app-activity/AHSecKill/lotteryAction"
                headers = {
                    "Accept": "application/json, text/plain, */*",
                    "Content-Type": "application/json",
                    "Origin": AH_FRIDAY_BASE_URL,
                    "Referer": referer,
                    "Cookie": f"ticket={ticket}",
                    "User-Agent": COMMON_CONSTANTS["UA"],
                    "Connection": "keep-alive",
                }
                res = self.session.post(url, params=params, json={}, headers=headers, timeout=5)
                data = res.json()
                if data.get('success'):
                    success_count += 1
                    self.log(f"安徽超级星期五: 🎉 第{i}次抢购成功！{json.dumps(data, ensure_ascii=False)}", notify=True)
                    return True
                else:
                    fail_count += 1
                    alert = data.get('alertMsg', '')
                    if i <= 3 or i % 20 == 0:
                        self.log(f"安徽超级星期五: 第{i}次 - {alert or data.get('statusCode', '未知')}")
                    if "已抢完" in alert or "已结束" in alert or "已领取" in alert:
                        self.log(f"安徽超级星期五: ⚠️ {alert}，停止抢购")
                        break
            except Exception as e:
                fail_count += 1
                if i <= 3:
                    self.log(f"安徽超级星期五: 第{i}次异常 - {e}")
            if i < AH_FRIDAY_SECKILL_TIMES:
                time.sleep(AH_FRIDAY_INTERVAL)
        self.log(f"安徽超级星期五: 抢购完成 (共{AH_FRIDAY_SECKILL_TIMES}次, 失败{fail_count}次)", notify=True)
        return False

    def ah_friday_task(self):
        """安徽超级星期五: 主入口"""
        if not AH_FRIDAY_AMOUNT:
            return
        rc = globalConfig.get("regional_config", {})
        if not rc.get("run_ah_friday", True):
            self.log("安徽超级星期五: ⏭️ 已被子开关关闭，跳过")
            return
        weekday = datetime.now().weekday()
        if weekday != 4:
            self.log(f"安徽超级星期五: 今天不是周五 (当前周{weekday + 1})，跳过")
            return
        self.log(f"安徽超级星期五: 🎯 目标面额 {AH_FRIDAY_AMOUNT}元")
        entry_info = self.ah_friday_get_entry()
        if not entry_info:
            return
        item_info = self.ah_friday_get_items(entry_info)
        if not item_info:
            return
        now = datetime.now()
        target = now.replace(hour=10, minute=0, second=0, microsecond=0)
        wait_seconds = (target - now).total_seconds()
        if wait_seconds > 300:
            self.log(f"安徽超级星期五: ⏳ 距10:00还有 {wait_seconds:.0f}秒，大于5分钟，建议临近时启动")
            return
        if wait_seconds > 0:
            self.log(f"安徽超级星期五: ⏳ 等待开抢 (剩余 {wait_seconds:.1f}秒)...")
            while (datetime.now().replace(hour=10, minute=0, second=0, microsecond=0) - datetime.now()).total_seconds() > 0.3:
                time.sleep(0.1)
            self.log("安徽超级星期五: ⚡ 时间到！开始抢购！")
        else:
            self.log(f"安徽超级星期五: ⚡ 已过10点 {abs(wait_seconds):.1f}秒，直接抢购！")
        self.ah_friday_seckill(entry_info, item_info)

    def woread_encrypt(self, data):
        try:
            key = b'woreadst^&*12345'
            iv = b'16-Bytes--String'
            cipher = AES.new(key, AES.MODE_CBC, iv)
            if isinstance(data, dict):
                data_str = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
            else:
                data_str = str(data)
            pad_len = 16 - (len(data_str.encode('utf-8')) % 16)
            data_str = data_str + chr(pad_len) * pad_len
            ciphertext = cipher.encrypt(data_str.encode('utf-8'))
            hex_str = ciphertext.hex()
            return base64.b64encode(hex_str.encode('utf-8')).decode('utf-8')
        except Exception as e:
            self.log(f"woread_encrypt error: {e}")
            return ""

    def woread_auth(self):
        try:
            product_id = "10000002"
            secret_key = "7k1HcDL8RKvc"
            timestamp = str(round(time.time() * 1000))
            sign_str = f"{product_id}{secret_key}{timestamp}"
            md5_hash = hashlib.md5(sign_str.encode('utf-8')).hexdigest()
            date_str = datetime.now().strftime('%Y%m%d%H%M%S')
            crypt_text_obj = {"timestamp": date_str}
            encoded_sign = self.woread_encrypt(crypt_text_obj)
            url = f"https://10010.woread.com.cn/ng_woread_service/rest/app/auth/{product_id}/{timestamp}/{md5_hash}"
            headers = {
                "Content-Type": "application/json",
                "User-Agent": COMMON_CONSTANTS['UA'],
            }
            res = self.session.post(url, json={"sign": encoded_sign}, headers=headers).json()
            if res.get('code') == "0000":
                self.woread_accesstoken = res.get('data', {}).get('accesstoken')
                return True
            else:
                self.log(f"阅读专区认证失败: {res.get('message')}")
                return False
        except Exception as e:
            self.log(f"woread_auth error: {e}")
            return False

    def woread_login(self):
        try:
            if not hasattr(self, 'woread_accesstoken') or not self.woread_accesstoken:
                if not self.woread_auth():
                    return False
            if not self.token_online:
                self.log("阅读专区: 缺少 token_online，无法登录")
                return False
            token_enc = self.woread_encrypt(self.token_online)
            phone_str = self.account_mobile if self.account_mobile else "13800000000"
            phone_enc = self.woread_encrypt(phone_str)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            inner_json = json.dumps({
                "tokenOnline": token_enc,
                "phone": phone_enc,
                "timestamp": timestamp
            }, separators=(',', ':'), ensure_ascii=False)
            encoded_sign = self.woread_encrypt(inner_json)
            url = "https://10010.woread.com.cn/ng_woread_service/rest/account/login"
            headers = {
                "Content-Type": "application/json",
                "User-Agent": COMMON_CONSTANTS['UA'],
            }
            if hasattr(self, 'woread_accesstoken') and self.woread_accesstoken:
                headers["accesstoken"] = self.woread_accesstoken
            res = self.session.post(url, json={"sign": encoded_sign}, headers=headers, timeout=15).json()
            if res.get('code') == "0000":
                data = res.get('data', {})
                self.woread_token = data.get('token')
                self.woread_userid = data.get('userid')
                self.woread_userindex = data.get('userindex')
                self.woread_verifycode = data.get('verifycode')
                if data.get('phone'):
                    self.mobile = data['phone']
                self.log("阅读专区: 登录成功")
                return True
            else:
                self.log(f"阅读专区登录失败: {res.get('message')}")
                return False
        except Exception as e:
            self.log(f"woread_login error: {e}")
            return False

    def woread_queryTicketAccount(self):
        try:
            if not hasattr(self, 'woread_token') or not self.woread_token:
                if not self.woread_login():
                     return
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            params = {
                "timestamp": timestamp,
                "phone": self.mobile if self.mobile else "",
                "token": self.woread_token
            }
            sign = self.woread_encrypt(params)
            url = "https://10010.woread.com.cn/ng_woread_service/rest/phone/vouchers/queryTicketAccount"
            headers = {
                "Content-Type": "application/json",
                "User-Agent": COMMON_CONSTANTS['UA'],
            }
            if hasattr(self, 'woread_accesstoken') and self.woread_accesstoken:
                headers["accesstoken"] = self.woread_accesstoken
            res = self.session.post(url, json={"sign": sign}, headers=headers).json()
            if res.get('code') == "0000":
                data = res.get('data', {})
                usable_num = int(data.get('usableNum', 0))
                balance_yuan = "{:.2f}".format(usable_num / 100)
                self.log(f"💰 [资产-阅读红包] 余额: {balance_yuan}元", notify=True)
            else:
                self.log(f"阅读红包查询失败: {res.get('message')}")
        except Exception as e:
            self.log(f"woread_queryTicketAccount error: {e}")

    def woread_get_book_info(self):
        try:
            url1 = "https://10010.woread.com.cn/ng_woread_service/rest/basics/recommposdetail/14856"
            headers = {
                "User-Agent": COMMON_CONSTANTS['UA'],
                "accesstoken": self.woread_accesstoken
            }
            res1 = self.session.get(url1, headers=headers)
            try:
                res1 = res1.json()
            except:
                self.log(f"阅读专区: 获取书架响应非JSON: {res1.text[:100]}")
                return False
            if res1.get('code') == '0000':
                msg_list = res1.get('data', {}).get('booklist', {}).get('message', [])
                if msg_list:
                    self.wr_catid = msg_list[0].get('catindex')
                    self.wr_cntindex = msg_list[0].get('cntindex')
                bind_info = res1.get('data', {}).get('bindinfo', [])
                if bind_info:
                    self.wr_cardid = bind_info[0].get('recommposiindex')
            else:
                self.log("阅读专区: 获取书架失败")
                return False
            if not getattr(self, 'wr_cntindex', None): return False
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            param = {
                "curPage": 1, "limit": 30, "index": self.wr_cntindex, "sort": 0, "finishFlag": 1,
                "timestamp": timestamp,
                "phone": self.mobile if self.mobile else "",
                "token": getattr(self, 'woread_token', ''),
                "userid": getattr(self, 'woread_userid', ''),
                "userId": getattr(self, 'woread_userid', ''),
                "userIndex": getattr(self, 'woread_userindex', ''),
                "verifyCode": getattr(self, 'woread_verifycode', '')
            }
            sign = self.woread_encrypt(param)
            url2 = "https://10010.woread.com.cn/ng_woread_service/rest/cnt/chalist"
            res2_raw = self.session.post(url2, json={"sign": sign}, headers=headers)
            try:
                res2 = res2_raw.json()
            except:
                self.log(f"阅读专区: 获取章节响应非JSON: {res2_raw.text[:100]}")
                return False
            lst = res2.get('list', []) or res2.get('data', {}).get('list', [])
            if lst:
                content = lst[0].get('charptercontent', [])
                if content:
                    self.wr_chapterallindex = content[0].get('chapterallindex')
                    self.wr_chapterid = content[0].get('chapterid')
                    return True
            return False
        except Exception as e:
            self.log(f"阅读专区: 获取书籍信息异常: {e}")
            return False

    def woread_read_process(self):
        if not self.woread_get_book_info():
            self.log("阅读专区: 无法获取书籍信息，跳过阅读")
            return
        headers = {
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 unicom{version:iphone_c@12.0301}",
                "accesstoken": self.woread_accesstoken
        }
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        phone = self.mobile if self.mobile else ""
        token = getattr(self, 'woread_token', '')
        userid = getattr(self, 'woread_userid', '')
        userindex = getattr(self, 'woread_userindex', '')
        verifycode = getattr(self, 'woread_verifycode', '')
        common_params = {
            "timestamp": timestamp,
            "phone": phone,
            "token": token,
            "userid": userid,
            "userId": userid,
            "userIndex": userindex,
            "userAccount": phone,
            "verifyCode": verifycode
        }
        param = {
          "chapterAllIndex": self.wr_chapterallindex,
          "cntIndex": self.wr_cntindex,
          "cntTypeFlag": "1",
          **common_params
        }
        sign = self.woread_encrypt(param)
        hb_url = f"https://10010.woread.com.cn/ng_woread_service/rest/cnt/wordsDetail?catid={self.wr_catid}&cardid={self.wr_cardid}&cntindex={self.wr_cntindex}&chapterallindex={self.wr_chapterallindex}&chapterseno=1"
        self.session.post(hb_url, json={"sign": sign}, headers=headers)
        add_param = {
          "readTime": "2",
          "cntIndex": self.wr_cntindex,
          "cntType": "1",
          "catid": "0",
          "pageIndex": "",
          "cardid": self.wr_cardid,
          "cntindex": self.wr_cntindex,
          "cnttype": "1",
          "chapterallindex": self.wr_chapterallindex,
          "chapterseno": "1",
          "channelid": "",
          "chapterid": self.wr_chapterid,
          "readtype": 1,
          "isend": "0",
          **common_params
        }
        add_sign = self.woread_encrypt(add_param)
        add_url = "https://10010.woread.com.cn/ng_woread_service/rest/history/addReadTime"
        res = self.session.post(add_url, json={"sign": add_sign}, headers=headers).json()
        res_code = str(res.get('code', ''))
        res_msg = str(res.get('message', ''))
        if res_code == '0000':
            self.log("阅读专区: 模拟阅读成功")
        elif res_code == '9999' or '9999' in res_msg or '不存在阅读记录' in res_msg:
            # addReadTime 返回9999不影响实际阅读结果
            self.log("阅读专区: 模拟阅读成功（阅读记录已提交）")
        else:
             self.log(f"阅读专区: 模拟阅读失败: {res_msg or res}")



    def woread_draw_new(self):
        try:
             headers = {
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 unicom{version:iphone_c@12.0301}",
                "accesstoken": self.woread_accesstoken
             }
             timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
             param = {
                "activeindex": "8051",
                "timestamp": timestamp, "phone": self.mobile if self.mobile else "", "token": self.woread_token
             }
             sign = self.woread_encrypt(param)
             url = "https://10010.woread.com.cn/ng_woread_service/rest/basics/doDraw"
             res = self.session.post(url, json={"sign": sign}, headers=headers).json()
             if res.get('code') == '0000':
                 prize = res.get('data', {}).get('prizedesc')
                 if prize:
                     self.log(f"阅读专区: 抽奖成功: {prize}", notify=True)
                 else:
                     self.log("阅读专区: 抽奖完成 (未中奖)")
             else:
                 self.log(f"阅读专区: 抽奖失败: {res.get('message')}")
        except Exception as e:
            self.log(f"woread_draw_new error: {e}")

    def woread_task(self):
        self.log("==== 联通阅读 ====")
        if not self.woread_login():
             self.log("阅读专区: 登录失败，跳过任务")
             return
        self.woread_queryTicketAccount()
        self.woread_read_process()
        time.sleep(3)
        self.woread_draw_new()

    def query_market_raffle_records(self, user_token):
        self.log("权益超市: 正在查询抽奖记录...")
        try:
            url = "https://backward.bol.wo.cn/prod-api/market/contactReceive/queryReceiveRecord"
            headers = {
                "Authorization": f"Bearer {user_token}",
                "User-Agent": COMMON_CONSTANTS["MARKET_UA"],
                "Origin": "https://contact.bol.wo.cn",
                "Referer": "https://contact.bol.wo.cn/"
            }
            mobile = getattr(self, "account_mobile", getattr(self, "mobile", ""))
            payload = {
                "isReceive": None,
                "receiveStatus": None,
                "limit": 20,
                "page": 1,
                "mobile": mobile,
                "businessSources": ["3", "4", "5", "6", "99"],
                "isPromotion": 1,
                "returnFormatType": 1
            }
            res = self.session.post(url, json=payload, headers=headers).json()
            if res.get('code') == 200:
                records = res.get('data', {}).get('recordObjs', [])
                if records:
                    now = datetime.now()
                    current_month = now.strftime('%Y-%m')
                    # 显示口径: 本月全部 + 近 60 天内(含上月早些时候)的, 其余一律不推送 (2026-10-07 由 5 天放宽至 60 天)
                    #   放宽目的: 让更早的历史非垃圾奖品也能在日报显示;
                    #   命中 blocked_keywords 的奖品(含哈啰)仍一律不展示不推送
                    recent_cutoff = (now - timedelta(days=60)).strftime('%Y-%m-%d')
                    # 推送屏蔽: 命中关键词的奖品不展示不推送 (2026-09-06 新增; 哈啰 2026-10-07 追加)
                    # 屏蔽策略: 出行类(一嗨/哈啰) + 电商生活券(名创/京东) 全屏蔽, 视频会员类(5G宽视界/WPS) 全显示 (2026-10-07 确认)
                    blocked_keywords = ["名创优品", "京东权益", "京东支付", "一嗨租车", "哈啰"]
                    display_records = []
                    for item in records:
                        record_name = item.get('recordName') or ''
                        if any(k in record_name for k in blocked_keywords):
                            continue
                        create_time = item.get('receiveTime') or ''
                        if len(create_time) < 10:
                            continue
                        if create_time[:7] == current_month:
                            display_records.append(item)                    # 本月: 全收
                        elif create_time[:10] >= recent_cutoff:
                            display_records.append(item)                    # 上月: 仅距今 5 天内
                    if display_records:
                        head = f"权益超市: 抽奖记录 (本月 {current_month} 全部 + 近 60 天):"
                        self.log(head, notify_html=f'<font color="#ff0000">{head}</font>')
                        for item in display_records:
                            line = f"    - [{item.get('receiveTime') or ''}] {item.get('recordName')}"
                            if str(item.get('receiveTime') or '')[:7] == current_month:
                                # 本月所得 → 推送红色
                                self.log(line, notify_html=f'<font color="#ff0000">{line}</font>')
                            else:
                                # 近 60 天 → 普通色
                                self.log(line, notify=True)
                    else:
                        self.log("权益超市: 无近期抽奖记录。")
                else:
                    self.log("权益超市: 无近期抽奖记录。")
            else:
                self.log(f"权益超市: 查询抽奖记录失败: {res.get('msg')}")
        except Exception as e:
            self.log(f"query_market_raffle_records error: {e}")

    def query_phone_recharge_records(self, user_token):
        self.log("权益超市: 正在查询本月话费抢购记录...")
        try:
            url = "https://backward.bol.wo.cn/prod-api/market/contactReceive/queryReceiveRecord"
            headers = {
                "Authorization": f"Bearer {user_token}",
                "User-Agent": COMMON_CONSTANTS["MARKET_UA"],
                "Origin": "https://contact.bol.wo.cn",
                "Referer": "https://contact.bol.wo.cn/"
            }
            mobile = getattr(self, "account_mobile", getattr(self, "mobile", ""))
            payload = {
                "isReceive": None,
                "receiveStatus": None,
                "limit": 50,
                "page": 1,
                "mobile": mobile,
                "businessSources": ["3", "4", "5", "6", "99"],
                "isPromotion": 1,
                "returnFormatType": 1
            }
            res = self.session.post(url, json=payload, headers=headers).json()
            if res.get('code') == 200:
                records = res.get('data', {}).get('recordObjs', [])
                total_amount = 0.0
                current_month = datetime.now().strftime('%Y-%m')
                count = 0
                for item in records:
                    create_time = item.get('receiveTime') or ''
                    name = item.get('recordName', '')
                    if not create_time or current_month not in create_time:
                        continue
                    if any(k in name for k in ['话费', '充值', '红包']):
                        match = re.search(r'(\d+(\.\d+)?)元', name)
                        if match:
                            amount = float(match.group(1))
                            total_amount += amount
                            count += 1
                if count > 0:
                     line = f"💰 [资产-抢购] 本月权益超市话费累计: {total_amount:.2f}元"
                     self.log(line, notify_html=f'<font color="#ff0000">{line}</font>')
                else:
                     self.log("权益超市: 本月暂无话费抢购记录")
            else:
                self.log(f"权益超市: 查询话费记录失败: {res.get('msg')}")
        except Exception as e:
            self.log(f"query_phone_recharge_records error: {e}")

    def sign_month_sign_gift(self, is_query_only=False):
        """签到区-月签有礼: 六宫格转盘月度签到奖励 (移植自上游 v1.1.2)"""
        try:
            url = "https://activity.10010.com/sixPalaceGridTurntableLottery/floor/getMonthSign"
            headers = {"Referer": "https://img.client.10010.com/"}
            res = self.request("get", url, headers=headers, timeout=10)
            if not res: return
            result = res.json()
            code = result.get('code')
            if code != "0000":
                self.log(f"签到区-月签有礼: 查询失败[{code}]: {result.get('desc', '')}")
                return
            task_list = result.get('data', {}).get('taskList', []) or []
            if not task_list:
                self.log("签到区-月签有礼: 暂无月签任务")
                return
            claim_tasks = [
                t for t in task_list
                if str(t.get('taskStatus')) == "1" and t.get('taskId') and t.get('id')
            ]
            claimed_count = sum(1 for t in task_list if str(t.get('taskStatus')) == "2")
            if is_query_only:
                self.log(f"签到区-月签有礼: 可领取 {len(claim_tasks)} 个，已领取 {claimed_count} 个")
                return
            if not claim_tasks:
                self.log(f"签到区-月签有礼: 暂无可领取奖励，已领取 {claimed_count}/{len(task_list)}")
                return
            for task in claim_tasks:
                self.sign_get_month_sign_reward(task)
                time.sleep(1)
        except Exception as e:
            self.log(f"sign_month_sign_gift 异常: {str(e)}")

    def sign_get_month_sign_reward(self, task):
        """领取单个月签奖励 (移植自上游 v1.1.2)"""
        task_name = task.get('taskName') or "月签奖励"
        try:
            url = "https://activity.10010.com/sixPalaceGridTurntableLottery/task/getTaskReward"
            params = {
                "taskId": task.get('taskId'),
                "taskType": "30",
                "id": task.get('id')
            }
            headers = {"Referer": "https://img.client.10010.com/"}
            res = self.request("get", url, params=params, headers=headers, timeout=10)
            if not res: return
            result = res.json()
            code = result.get('code')
            data = result.get('data', {}) or {}
            if code == "0000" and data.get('code') == "0000":
                prize_name = data.get('prizeName', '')
                prize_red = data.get('prizeNameRed', '')
                reward = f"[{prize_name}] {prize_red}".strip() if prize_name or prize_red else data.get('statusDesc', '领取成功')
                self.log(f"签到区-月签有礼: [{task_name}] {reward}", notify=True)
                return
            msg = data.get('desc') or result.get('desc') or result.get('msg') or "未知错误"
            self.log(f"签到区-月签有礼: [{task_name}] 领取失败[{data.get('code') or code}]: {msg}")
        except Exception as e:
            self.log(f"sign_get_month_sign_reward 异常: {str(e)}")

    def sign_query_my_prizes(self):
        """账户明细: 只打印/推送【本月】的兑换记录 (往月记录不再占用推送, 2026-10-06 改)"""
        self.log("正在查询账户明细 (抢兑)...")
        try:
            url = "https://act.10010.com/SigninApp/convert/phoneDetails"
            form = {
                "log_type": "1",
                "number": "1",
                "list_num": ""
            }
            headers = {"Origin": "https://img.client.10010.com"}
            res = self.request("post", url, data=form, headers=headers)
            if not res: return
            result = res.json()
            if result.get('status') != '0000':
                self.log(f"[账户明细] 查询异常: {result.get('msg', 'Result Error')}")
                return
            data = result.get('data', {}).get('detailedBO', [])
            if not (data and isinstance(data, list)):
                self.log("[账户明细] 暂无兑换记录")
                return
            current_month = datetime.now().strftime('%Y-%m')
            logged_count = 0
            for item in data:
                if logged_count >= 5: break
                remark = item.get('remark', '')
                buss_name = item.get('from_bussname', '')
                if "兑换" not in remark and "兑换" not in buss_name:
                    continue
                # 只保留【本月】记录: 9 月及更早的不再打印/推送 (2026-10-06 改)
                order_time = str(item.get('order_time') or '')
                norm = order_time.replace('/', '-')
                if not norm:
                    for k in ("createTime", "receiveTime", "time"):
                        if item.get(k):
                            norm = str(item.get(k)).replace('/', '-')
                            break
                if not norm.startswith(current_month):
                    continue
                if logged_count == 0:
                    self.log(f"📋 [账户明细] 本月({current_month})兑换记录 (最多 5 条):", notify=True)
                amount = item.get('booksNumber') or item.get('books_number') or "0"
                self.log(f"   🎁 [抢兑] {order_time} | {remark} (变动:{amount})", notify=True)
                logged_count += 1
            if logged_count == 0:
                self.log(f"[账户明细] 本月({current_month})暂无兑换记录")
        except Exception as e:
            self.log(f"sign_query_my_prizes error: {e}")

    def sign_task_main(self):
        self.log("==== 签到区 ====")
        # 1) 话费资产优先: 话费红包余额 + 临期提醒 (🔺话费优先)
        self.sign_huafei_summary()
        # 2) 抢兑话费券优先: 整点场次稍纵即逝, 必须排在耗时的任务中心之前
        sc = globalConfig.get("sign_config", {})
        if sc.get("run_grab_coupon", False):
            self.sign_grabCoupon()
        else:
            self.log("签到区-抢话费券: ⏭️ 已被子开关关闭，跳过")
        # 3) 签到 + 任务中心 (浏览类任务每个返 0.01元话费红包)
        self.sign_getContinuous(is_query_only=False)
        self.sign_month_sign_gift()   # 月签有礼 (移植自 v1.1.2)
        self.sign_getTaskList()
        # 4) 收尾: 话费红包增量 + 兑换明细
        self.sign_getTelephone()
        self.sign_query_my_prizes()
        self.sign_task_v2()

    # ========================================
    # 签到区 v2 (2026-09-17 用真实CK复测)
    # 存活: 1G流量日包(act.10010.com/SigninApp/doTask/getTaskInfo + finishVideo + getPrize, 带登录态可读写)
    # 已下线(302 -> /error/busy1.html): m.client.10010.com/growth/sign/doSign (沃之树浇水)
    #                                  m.client.10010.com/dailylottery/static/* (金币抽奖登录/双色球抽奖)
    # 真下线(404): SigninApp/signin 积分签到翻倍, mySignin/addFlow 领流量
    # 注意: 给 m.client.10010.com 的 onLine.htm 带 img.client.10010.com 的 Referer/Origin 会触发
    #       安全校验返回 code=1「绑定关系失效」, 保持不传 Referer 即可.
    # ========================================
    def sign_v2_headers(self):
        return {
            "User-Agent": COMMON_CONSTANTS["UA"],
            "Referer": "https://img.client.10010.com/",
            "Origin": "https://img.client.10010.com"
        }

    def sign_v2_is_wait_page(self, text):
        """联通统一兜底页: 无登录态/无权限时返回'沃妹陪着您'等待页, 非JSON"""
        return isinstance(text, str) and "沃妹" in text

    def sign_v2_flow_task(self):
        """1G流量日包: 读 doTask/getTaskInfo 判断状态, 完成看视频任务后领奖(050拥堵自动重试)"""
        try:
            headers = self.sign_v2_headers()
            res = self.request("post", "https://act.10010.com/SigninApp/doTask/getTaskInfo", headers=headers)
            if res:
                try:
                    info = res.json()
                except Exception:
                    info = None
                if isinstance(info, dict) and info.get('status') == '0000':
                    task_list = (info.get('data') or {}).get('taskList') or []
                    watch = next((t for t in task_list
                                  if str(t.get('action')) == 'LOCAL_DOTASK_WATCH_VIDEO'), None)
                    if watch and str(watch.get('status')) == '0':
                        self.log("签到区-1G流量日包: 看视频任务今日已完成, 无需重做")
                        return
            self.request("post", "https://act.10010.com/SigninApp/doTask/finishVideo", headers=headers)
            time.sleep(2)
            for i in range(3):
                res = self.request("post", "https://act.10010.com/SigninApp/doTask/getPrize", headers=headers)
                if not res:
                    return
                try:
                    r = res.json()
                except Exception:
                    self.log("签到区-1G流量日包: 响应异常(可能活动下线)")
                    return
                data = r.get('data') or {}
                state = str(data.get('state') or '')
                desc = str(data.get('statusDesc') or '')
                ret_str = str(data.get('returnStr') or '')
                if state == '0' and '失败' not in desc:
                    self.log(f"签到区-1G流量日包: 领取成功 {ret_str}".strip(), notify=True)
                    return
                if '拥堵' in ret_str or '050' in ret_str:
                    if i < 2:
                        time.sleep(4 + i * 3)
                        continue
                    self.log(f"签到区-1G流量日包: 服务器繁忙, 本次未领到({ret_str})")
                    return
                self.log(f"签到区-1G流量日包: {ret_str or desc or r.get('msg', '今日已领取')}")
                return
        except Exception as e:
            self.log(f"sign_v2_flow_task 异常: {e}")

    def sign_v2_growth_request(self, url, label):
        """growth 系接口统一请求: 自动识别下线(302→error/busy1)与JSON响应"""
        res = self.request("post", url, data={})
        if not res:
            self.log(f"{label}: 无响应")
            return None
        if self.sign_v2_is_wait_page(res.text):
            self.log(f"{label}: 接口已下线或需App内登录态(返回沃妹页), 跳过")
            return None
        try:
            return res.json()
        except Exception:
            self.log(f"{label}: 响应非JSON(可能活动已下线)")
            return None

    def sign_v2_arbor_day(self):
        """沃之树每日浇水 (growth新版接口, 旧版arbordayJson已下线)"""
        r = self.sign_v2_growth_request(
            "https://m.client.10010.com/growth/sign/doSign", "沃之树-每日浇水")
        if r is None:
            return
        try:
            msg = r.get('msg') or r.get('respDesc') or r.get('message') or "已完成"
            self.log(f"沃之树-每日浇水: {msg}", notify="成功" in str(msg))
        except Exception as e:
            self.log(f"沃之树-每日浇水: 解析异常 {e}")

    def sign_v2_gold_lottery(self):
        """金币抽奖(双色球) 免费3次 (新版登录态接口, 取代旧encryptmobile页面抓取)"""
        # 第一步: 登录换取抽奖会话
        r = self.sign_v2_growth_request(
            "https://m.client.10010.com/dailylottery/static/textdl/userLogin", "金币抽奖-登录")
        if r is None:
            return
        encrypt_mobile = ""
        try:
            encrypt_mobile = (r.get('data') or {}).get('encryptmobile') or r.get('encryptmobile') or ""
        except Exception:
            pass
        if not encrypt_mobile:
            # 兼容旧版: 从页面JS变量中提取
            res = self.request("post", "https://m.client.10010.com/dailylottery/static/textdl/userLogin")
            if res and not self.sign_v2_is_wait_page(res.text):
                m = re.search(r"encryptmobile=(.+?)';", res.text)
                if m:
                    encrypt_mobile = m.group(1)
        if not encrypt_mobile:
            self.log("金币抽奖: 未获取到抽奖凭证, 跳过")
            return
        data = {"usernumberofjsp": encrypt_mobile, "flag": "convert"}
        for i in range(3):
            res = self.request("post", "https://m.client.10010.com/dailylottery/static/doubleball/choujiang",
                               data=data, headers=self.sign_v2_headers())
            if not res: break
            if self.sign_v2_is_wait_page(res.text):
                self.log("金币抽奖: 需要App内登录态, 跳过")
                return
            try:
                rr = res.json()
                msg = rr.get('RspMsg') or rr.get('msg') or '未知'
            except Exception:
                msg = "响应异常"
            # 推送精简: 仅中奖才推送
            self.log(f"金币抽奖({i+1}/3): {msg}", notify=("中奖" in msg or "获得" in msg))
            time.sleep(3)

    def sign_task_v2(self):
        """签到区 v2 模块入口: 1G流量日包/沃之树/金币抽奖"""
        sc = globalConfig.get("sign_config", {})
        v2 = sc.get("run_task_v2", True)
        if not v2:
            self.log("签到区-v2活动: ⏭️ 已被子开关关闭，跳过")
            return
        self.log("==== 签到区-v2(流量日包/沃之树/金币抽奖) ====")
        try:
            self.sign_v2_flow_task()
        except Exception as e:
            self.log(f"签到区-v2流量任务异常: {e}")
        try:
            self.sign_v2_arbor_day()
        except Exception as e:
            self.log(f"签到区-v2沃之树异常: {e}")
        try:
            self.sign_v2_gold_lottery()
        except Exception as e:
            self.log(f"签到区-v2金币抽奖异常: {e}")

    def execute_daily_tasks(self, query_only=False):
        if query_only:
            self.log("📋 [查询模式] 仅查询资产，跳过任务执行", notify=True)
            try:
                self.queryRemain()
                if globalConfig.get("enable_sign", True):
                    try:
                        self.sign_getContinuous(is_query_only=True)
                        self.sign_month_sign_gift(is_query_only=True)
                        self.sign_getTelephone()
                    except Exception as e:
                        self.log(f"首页签到查询异常: {e}")
                    try:
                        self.sign_query_my_prizes()
                    except Exception as e:
                        self.log(f"抢兑记录查询异常: {e}")
                if globalConfig.get("enable_ttlxj", True):
                    try:
                        self.ttlxj_task(is_query_only=True)
                    except Exception as e:
                        self.log(f"天天领现金查询异常: {e}")
                if globalConfig.get("enable_ttxc", True):
                    try:
                        self.ttxc_task(is_query_only=True)
                    except Exception as e:
                        self.log(f"通通乡村查询异常: {e}")
                if globalConfig.get("enable_market", True):
                    try:
                        self.market_task(is_query_only=True)
                    except Exception as e:
                        self.log(f"权益超市查询异常: {e}")
                if globalConfig.get("enable_woread", True):
                    try:
                        self.woread_queryTicketAccount()
                    except Exception as e:
                        self.log(f"联通阅读查询异常: {e}")
                if globalConfig.get("enable_aiting", True):
                    try:
                        self.aiting_task(is_query_only=True)
                    except Exception as e:
                        self.log(f"联通爱听查询异常: {e}")
                if globalConfig.get("enable_security", True):
                    try:
                        self.securityButlerTask(is_query_only=True)
                    except Exception as e:
                        self.log(f"安全管家查询异常: {e}")
                if globalConfig.get("enable_ltyp", True):
                    try:
                        self.ltyp_task(is_query_only=True)
                    except Exception as e:
                        self.log(f"联通云盘查询异常: {e}")
                if globalConfig.get("enable_islandwaves", True):
                    try:
                        self.island_waves_task(query_only=True)
                    except Exception as e:
                        self.log(f"披荆斩棘2026查询异常: {e}")
                if globalConfig.get("enable_wostore", True):
                    try:
                        self.wostore_cloud_task(is_query_only=True)
                    except Exception as e:
                        self.log(f"沃云手机查询异常: {e}")
                if globalConfig.get("enable_regional", True):
                    try:
                        self.regional_task(is_query_only=True)
                    except Exception as e:
                        pass
            except Exception as e:
                self.log(f"查询异常: {e}")
            return
        self.log("==== 今日话费余额 ====")
        try:
            self.queryRemain()
        except Exception as e:
            self.log(f"话费余额查询异常: {e}")
        if globalConfig.get("enable_sign", True):
            self.sign_task_main()
        else:
            self.log("==== 签到区 ====")
            self.log("⏭️ 已被总开关关闭，跳过")
        if globalConfig.get("enable_ltzf", True):
            self.ltzf_task()
        else:
            self.log("==== 联通祝福 ====")
            self.log("⏭️ 已被总开关关闭，跳过")
        if globalConfig.get("enable_ttlxj", True):
            self.ttlxj_task()
        else:
            self.log("==== 天天领现金 ====")
            self.log("⏭️ 已被总开关关闭，跳过")
        if globalConfig.get("enable_ttxc", True):
            self.ttxc_task()
        else:
            self.log("==== 通通乡村 ====")
            self.log("⏭️ 已被总开关关闭，跳过")
        if globalConfig.get("enable_market", True):
            self.market_task()
        else:
            self.log("==== 权益超市 ====")
            self.log("⏭️ 已被总开关关闭，跳过")
        if globalConfig.get("enable_woread", True):
            self.woread_task()
        else:
            self.log("==== 联通阅读 ====")
            self.log("⏭️ 已被总开关关闭，跳过")
        need_cooldown = globalConfig.get("enable_woread", True) and globalConfig.get("enable_aiting", True)
        if need_cooldown:
            self.log("⏳ 等待120秒（阅读冷却：联通限制两次阅读间隔2分钟）...")
            time.sleep(120)
        if globalConfig.get("enable_aiting", True):
            self.aiting_task()
        else:
            self.log("==== 联通爱听 ====")
            self.log("⏭️ 已被总开关关闭，跳过")
        if globalConfig.get("enable_security", True):
            self.securityButlerTask()
        else:
            self.log("==== 安全管家 ====")
            self.log("⏭️ 已被总开关关闭，跳过")
        if globalConfig.get("enable_ltyp", True):
            self.ltyp_task()
        else:
            self.log("==== 联通云盘 ====")
            self.log("⏭️ 已被总开关关闭，跳过")
        if globalConfig.get("enable_islandwaves", True):
            try:
                self.island_waves_task()
            except Exception as e:
                self.log(f"披荆斩棘2026异常: {e}")
        else:
            self.log("==== 披荆斩棘2026 · 海岛逐浪应援 ====")
            self.log("⏭️ 已被总开关关闭，跳过")
        if globalConfig.get("enable_wostore", True):
            self.wostore_cloud_task()
        else:
            self.log("==== 沃云手机 ====")
            self.log("⏭️ 已被总开关关闭，跳过")
        if globalConfig.get("enable_regional", True):
            self.regional_task()
        else:
            self.log("==== 区域专区 ====")
            self.log("⏭️ 已被总开关关闭，跳过")

def cross_view_security_share_keys(users):
    participants = [
        u for u in users
        if getattr(u, "sec_ai_share_key", "") and getattr(u, "sec_token", "") and getattr(u, "sec_share_task_code", "")
    ]
    if not participants:
        return
    if len(participants) < 2:
        participants[0].log("联通助理-分享AI助手对话：仅 1 个账号拿到分享key，跳过跨账号互看")
        return
    print("")
    print("========= 联通助理-开始跨账号查看AI分享对话 =========")
    n = len(participants)
    for i, viewer in enumerate(participants):
        target = participants[(i + 1) % n]
        viewer.log(f"联通助理-分享AI助手对话：查看账号[{target.index}]分享")
        try:
            viewer.sec_view_share_detail(target.sec_ai_share_key, viewer.sec_token)
        except Exception as e:
            viewer.log(f"联通助理-分享AI助手对话：互看异常 {e}")
        time.sleep(2)
    for u in participants:
        try:
            u.sec_refresh_security_context(refresh_secret=True)
            u.sec_finalize_share_ai_task()
            u.sec_recover_pending_claims(rounds=2, delay=6, refresh_context=True)
        except Exception as e:
            u.log(f"联通助理-分享AI助手对话：互看后领奖异常 {e}")

def do_notify(users):
    notify_content = []
    # 🔺 推送顺序: 主卡账号整段提前, 副卡/亲情卡依次跟在后面
    #    is_main_card 由 queryFlowUsage() 判定 (None=未判定, 当普通账号处理);
    #    sorted 是稳定排序, 所以非主卡之间保持原有账号顺序, 【账号X】序号也不变
    ordered = sorted(users, key=lambda u: 0 if getattr(u, "is_main_card", None) is True else 1)
    mains = [u.index for u in ordered if getattr(u, "is_main_card", None) is True]
    if mains:
        print(f"推送排序: 主卡账号[{mains[0]}]排最前, 其余按原顺序")
    for u in ordered:
        if u.notify_logs:
            phone = u.mobile or u.account_mobile
            phone_str = mask_str(phone) if phone else ""
            notify_content.append(f"【账号{u.index}】{phone_str}")
            notify_content.extend(u.notify_logs)
            notify_content.append("")
    if notify_content:
        content = "\n".join(notify_content)
        try:
            sendkey = os.environ.get("SERVERCHAN_SENDKEY", "").strip()
            if sendkey:
                response = requests.post(
                    f"https://sctapi.ftqq.com/{quote(sendkey, safe='')}.send",
                    data={"title": "中国联通", "desp": content},
                    timeout=15,
                )
                response.raise_for_status()
                if response.json().get("code") != 0:
                    raise RuntimeError("Server酱未接受推送，请检查 SendKey")
            else:
                from notify import send
                send("中国联通", content)
            print(f"推送成功 (内容长度: {len(content)})")
        except Exception as e:
            print(f"推送失败，可能未配置 notify.py: {str(e)}")
    else:
        print("无推送内容")

def main():
    global GRAB_AMOUNT
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [Script Start] chinaUnicom Python v1.0.8")
    cookies = os.environ.get("chinaUnicomCookie", "")
    if not cookies:
        # 无环境变量时，自动读取同目录下的 config.json
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
        if not os.path.exists(config_path):
            print("[-] 未找到环境变量 chinaUnicomCookie，也未找到同目录下的 config.json")
            print("    请先运行 联通Token助手-Windows.bat 或 联通Token助手-飞牛NAS.sh 获取Token")
            sys.exit(1)
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            token = cfg.get("token_online", "").strip()
            appid = cfg.get("appid", "").strip()
            phone = cfg.get("phone", "").strip()
            if not token:
                print("[-] config.json 中未找到有效的 token_online")
                sys.exit(1)
            # 原始脚本格式：Token#AppId（多账号用 & 或换行分隔）
            if appid:
                cookies = f"{token}#{appid}"
            else:
                cookies = token
            print(f"✅ 已从 config.json 加载账号 {mask_str(phone)} 的Token")
        except Exception as e:
            print(f"[-] 读取 config.json 失败: {e}")
            sys.exit(1)
    accounts = [c for c in re.split(r'[&\n]', cookies) if c.strip()]
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 发现 {len(accounts)} 个账号")
    print("")
    users = []
    for idx, config in enumerate(accounts):
        u = UserService(idx + 1, config.strip())
        users.append(u)
        if u.appId:
             print(f"账号[{idx+1}] 识别到 Token#AppId 模式，使用自定义AppId: {u.appId}")
        elif u.account_mobile:
             print(f"账号[{idx+1}] 识别到账号密码模式: {mask_str(u.account_mobile)}")
        try:
            if u.token_online:
                u.get_city_info()
        except: pass
    print(f"共找到{len(accounts)}个账号")
    print("")
    env_amount = os.environ.get("UNICOM_GRAB_AMOUNT", "")
    if env_amount and env_amount.isdigit():
        GRAB_AMOUNT = int(env_amount)
    global GRAB_AMOUNTS
    if not os.environ.get("UNICOM_GRAB_AMOUNTS", "").strip():
        GRAB_AMOUNTS = parse_grab_amounts("", (str(GRAB_AMOUNT),))
    query_only = os.environ.get("UNICOM_TEST_MODE", "").strip().lower() == "query"
    if query_only:
        print("[Test Mode] 仅查询模式，跳过任务执行")
    sc = globalConfig.get("sign_config", {})
    mc = globalConfig.get("market_config", {})
    rc = globalConfig.get("regional_config", {})
    grab_mode = False
    ah_friday_grab = False
    hour = datetime.now().hour
    current_min = datetime.now().minute
    is_friday = datetime.now().weekday() == 4
    if not query_only:
        if sc.get("run_grab_coupon", False) and globalConfig.get("enable_sign", True):
            if hour in [9, 17] and (58 <= current_min <= 59):
                grab_mode = True
        if (AH_FRIDAY_AMOUNT and is_friday and rc.get("run_ah_friday", True)
                and globalConfig.get("enable_regional", True)
                and hour == 9 and (58 <= current_min <= 59)):
            ah_friday_grab = True
            grab_mode = True
    print("-" * 36)
    switch_map = [
        ("enable_sign",     "首页签到"),
        ("enable_ltzf",     "联通祝福"),
        ("enable_ttlxj",    "天天领现金"),
        ("enable_ttxc",    "通通乡村"),
        ("enable_market",   "权益超市"),
        ("enable_woread",   "联通阅读"),
        ("enable_aiting",   "联通爱听"),
        ("enable_security", "安全管家"),
        ("enable_ltyp",     "联通云盘"),
        ("enable_wostore",  "沃云手机"),
        ("enable_regional", "区域专区"),
        ("enable_flow",     "流量查询"),
        ("enable_islandwaves", "披荆斩棘2026"),
        ("enable_cloud_benefit", "云盘权益活动"),
    ]
    for key, label in switch_map:
        enabled = globalConfig.get(key, True)
        if grab_mode:
            if key == "enable_sign" and sc.get("run_grab_coupon", False):
                status = "运行(仅抢兑)"
            elif key == "enable_regional" and ah_friday_grab:
                status = "运行(安徽抢红包)"
            else:
                status = "跳过(抢兑模式)"
        elif query_only:
            status = "仅查询" if enabled else "关闭"
        else:
            status = "运行" if enabled else "关闭"
        print(f"{label}设置为: {status}")
        if key == "enable_sign" and enabled and not query_only:
            grab_amt = "/".join(str(a) for a in GRAB_AMOUNTS) if GRAB_AMOUNTS else str(GRAB_AMOUNT)
            print(f"  └─ 抢话费券: {'开启' if sc.get('run_grab_coupon', False) else '关闭'}"
                  + (f" (面额 {grab_amt}元, 场次 10:00 / 18:00)" if sc.get('run_grab_coupon', False) else ""))
        if key == "enable_regional" and enabled and not query_only:
            ah_status = "开启" if rc.get("run_ah_friday", True) and AH_FRIDAY_AMOUNT else "关闭"
            print(f"  └─ 安徽超级星期五: {ah_status}" + (f" (面额{AH_FRIDAY_AMOUNT}元)" if AH_FRIDAY_AMOUNT else ""))
        if key == "enable_islandwaves" and enabled and not query_only:
            print(f"  └─ 助力哥哥: {ISLAND_WAVES_TARGET or '未设置(跳过第1关)'}"
                  f"  ⚠️ 第1关转存后不可更改、不可取消")
        if key == "enable_cloud_benefit" and enabled and not query_only:
            targets = "/".join(CLOUD_BENEFIT_ACTIVITY_IDS) if CLOUD_BENEFIT_ACTIVITY_IDS else "自动发现(不限次数活动)"
            print(f"  └─ 不限次数权益活动: 每个抽 {CLOUD_BENEFIT_DRAW_TIMES} 次  目标: {targets}")
        if key == "enable_market" and enabled and not query_only and not grab_mode:
            print(f"  └─ 浇水: {'开启' if mc.get('run_water', True) else '关闭'}")
            print(f"  └─ 做任务: {'开启' if mc.get('run_task', True) else '关闭'}")
            print(f"  └─ 会员中心: {'开启' if mc.get('run_member_center', True) else '关闭'}")
            print(f"  └─ 抽奖: {'开启' if mc.get('run_draw', True) else '关闭'}")
            print(f"  └─ 自动领奖: {'开启' if mc.get('run_claim', False) else '关闭'}")
    print(f"设备ID刷新: {'强制刷新' if globalConfig.get('refresh_device_id', False) else '使用缓存'}")
    print("-" * 36)
    print("")
    if grab_mode:
        print(f"⏰ [自动触发] 检测到抢兑时间点 ({hour}:{current_min:02d})，进入并发抢兑模式")
        tasks_desc = []
        if sc.get("run_grab_coupon", False) and globalConfig.get("enable_sign", True):
            tasks_desc.append(f"{'/'.join(str(a) for a in GRAB_AMOUNTS)}元话费券")
        if ah_friday_grab:
            tasks_desc.append(f"安徽{AH_FRIDAY_AMOUNT}元红包")
        print(f"🚨🚨🚨 [抢兑模式已启动] 目标: {' + '.join(tasks_desc)} 🚨🚨🚨")
        print("")
        from concurrent.futures import ThreadPoolExecutor

        def run_grab_task(u):
            u.configure_proxy()
            if not u.token_online and u.account_mobile:
                u.load_token_from_cache()
            is_valid = u.onLine()
            if not is_valid and u.account_mobile and u.account_password:
                u.unicom_login()
                is_valid = u.onLine()
            if is_valid:
                u.save_token_to_cache()
                sub_futures = []
                with ThreadPoolExecutor(max_workers=2) as sub_executor:
                    if sc.get("run_grab_coupon", False) and globalConfig.get("enable_sign", True):
                        sub_futures.append(sub_executor.submit(u.sign_grabCoupon))
                    if ah_friday_grab:
                        sub_futures.append(sub_executor.submit(u.ah_friday_task))
                    for f in sub_futures:
                        try:
                            f.result()
                        except Exception as e:
                            u.log(f"抢兑子任务异常: {e}")
            else:
                u.log("登录流程失败，跳过该账号")

        print(f"🚀 [并发模式] 启动 {len(accounts)} 个账号同时抢兑...")
        with ThreadPoolExecutor(max_workers=len(accounts)) as executor:
            futures = [executor.submit(run_grab_task, u) for u in users]
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    print(f"[-] Thread Error: {e}")
        do_notify(users)
        return
    print("🚀 开始串行执行日常任务...")
    print("")
    for u in users:
        print("")
        print(f"🔄 正在初始化账号[{u.index}]...")
        u.configure_proxy()
        if not u.token_online and u.account_mobile:
            u.load_token_from_cache()
        if not u.token_online and u.account_mobile and u.account_password:
             u.unicom_login()
        if u.onLine():
             u.save_token_to_cache()
             print("")
             print(f"------------------ 账号[{u.index}][{mask_str(u.account_mobile)}] ------------------")
             print("")
             u.execute_daily_tasks(query_only=query_only)
             print("⏳ 账号处理完毕，等待 2 秒...")
             time.sleep(2)
        else:
             u.log("登录流程失败，跳过该账号")
    cross_view_security_share_keys(users)
    do_notify(users)
if __name__ == "__main__":
    main()
