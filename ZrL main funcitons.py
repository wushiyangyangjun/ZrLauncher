#all started in 7 17 2026 by @wushiyangyangjun & @YaatoX & deepseek &ChatGPT
#文件框架############################################################################################
from pathlib import Path                      #引入路径库
import csv                                    #存东西用
import pickle                                 #同上
import time                                   
import requests                               #for 多线程下载
import json              #引入了json
import urllib.request    #方便获取版本ls


CONFIG_PATH = Path("config.csv")              #创建conf文件
print ("启动器所在目录：",Path.cwd())
项目文件夹 = Path.cwd() /".minecraft"          #定义、创建根目录
项目文件夹.mkdir(exist_ok=True)                
print ("项目文件夹在:",Path.cwd())             #创建.minecraft foder 
minecraft目录 = 项目文件夹       #定义MC根目录
#mkdir子文件夹
子文件夹们 = [
    minecraft目录 / "versions",         # 放游戏版本
    minecraft目录 / "libraries",        # 放依赖库
    minecraft目录 / "assets",           # 放资源文件
    minecraft目录 / "assets" / "indexes",  # 资源索引
    minecraft目录 / "assets" / "objects",  # 资源实体
]
for 文件夹 in 子文件夹们:
    文件夹.mkdir(parents=True, exist_ok=True)
    print(f"✓成功！ {文件夹}")
##下载版本！！#######################################################################################

def mutithread(url):
    '''多线程下载'''
    response = requests.get(url, steam=True)
    ...




verls = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"     #######源
print("正在从 Mojang 服务器获取版本列表...")
try:
    with urllib.request.urlopen(verls) as 响应:
        版本清单 = json.load(响应)

    print(f"✓ 获取成功！最新稳定版：{版本清单['latest']['release']}")
    print(f"  总共有 {len(版本清单['versions'])} 个版本可选\n")
    本地保存路径 = minecraft目录 / "version_manifest.json"
    with open(本地保存路径, "w", encoding="utf-8") as f:
        json.dump(版本清单, f, indent=2, ensure_ascii=False)
    print(f"✓ 已保存到：{本地保存路径}")

except Exception as e:
    print(f"✗ 下载失败：{e}")
###读取清单&下载版本################################################################################
minecraft目录 = Path.cwd() / ".minecraft"
清单路径 = minecraft目录 / "version_manifest.json"

with open(清单路径, "r") as f:
    清单 = json.load(f)
tgver = input ("请输入您想要的MC版本")   #向用户请求他想要的版本 #tagret verson
目标版本 = str (tgver)                  #zhuan zi fu cuan 
print (tgver)

版本URL = None
for 版本 in 清单["versions"]:
    if 版本["id"] == 目标版本:
        版本URL = 版本["url"]
        break

if 版本URL is None:
    print(f"✗ 找不到版本 {目标版本}")
else:
    print(f"✓ 找到 {目标版本}")
    print(f"  下载地址：{版本URL}")
#
import urllib.request

#创建版本文件夹
版本文件夹 = minecraft目录 / "versions" / 目标版本
版本文件夹.mkdir(parents=True, exist_ok=True)

#下载版本 JSON（如果本地没有）
JSON路径 = 版本文件夹 / f"{目标版本}.json"
if not JSON路径.exists():
    print("正在下载版本信息...")
    urllib.request.urlretrieve(版本URL, JSON路径)
    print("✓ 版本信息下载完成")
else:
    print("✓ 版本信息已存在，跳过下载")

#读取版本 JSON
with open(JSON路径, "r") as f:
    版本信息 = json.load(f)

print(f"\n{目标版本} 需要的东西：")
print(f"  - 主类：{版本信息['mainClass']}")
print(f"  - 依赖库数量：{len(版本信息['libraries'])}")
print(f"  - 资源版本：{版本信息['assetIndex']['id']}")

#下载客户端 jar
客户端URL = 版本信息["downloads"]["client"]["url"]
客户端路径 = 版本文件夹 / f"{目标版本}.jar"

if not 客户端路径.exists():
    大小MB = 版本信息["downloads"]["client"]["size"] / 1024 / 1024
    print(f"\n正在下载客户端 jar（{大小MB:.1f} MB）...")
    urllib.request.urlretrieve(客户端URL, 客户端路径)
    print("✓ 客户端 jar 下载完成")
else:
    print("✓ 客户端 jar 已存在，跳过下载")

#下载依赖库
依赖库列表 = 版本信息["libraries"]
成功 = 0
跳过 = 0
失败列表 = []

print(f"\n开始下载依赖库（共 {len(依赖库列表)} 个）...")

for 序号, 库 in enumerate(依赖库列表, start=1):
    # 跳过没有下载链接的库
    if "downloads" not in 库 or "artifact" not in 库["downloads"]:
        跳过 += 1
        continue

    下载信息 = 库["downloads"]["artifact"]
    下载地址 = 下载信息["url"]
    本地相对路径 = 下载信息["path"]
    本地完整路径 = minecraft目录 / "libraries" / 本地相对路径

    # 已存在就跳过
    if 本地完整路径.exists():
        成功 += 1
        continue

    # 创建父文件夹并下载
    本地完整路径.parent.mkdir(parents=True, exist_ok=True)
    try:
        urllib.request.urlretrieve(下载地址, 本地完整路径)
        成功 += 1
    except Exception as e:
        失败列表.append(库["name"])
    
    # 每 10 个打印一次进度
    if 序号 % 10 == 0:
        print(f"  进度：{序号}/{len(依赖库列表)}")

print(f"依赖库下载完成！成功：{成功}，跳过：{跳过}，失败：{len(失败列表)}")
if 失败列表:
    print("以下库下载失败：")
    for 名称 in 失败列表[:5]:  # 最多显示5个
        print(f"  - {名称}")

#下载资源索引
资源索引 = 版本信息["assetIndex"]
索引URL = 资源索引["url"]
索引ID = 资源索引["id"]
索引路径 = minecraft目录 / "assets" / "indexes" / f"{索引ID}.json"

if not 索引路径.exists():
    print("\n正在下载资源索引...")
    索引路径.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(索引URL, 索引路径)
    print("✓ 资源索引下载完成")
else:
    print("\n✓ 资源索引已存在，跳过下载")
#Downlod真资源
def 下载资源文件(资源索引ID, minecraft目录):
    """根据资源索引下载所有缺失的资源对象"""
    索引路径 = minecraft目录 / "assets" / "indexes" / f"{资源索引ID}.json"
    if not 索引路径.exists():
        print("❌ 资源索引不存在，请先下载")
        return

    with open(索引路径, "r", encoding="utf-8") as f:
        索引数据 = json.load(f)

    所有对象 = 索引数据.get("objects", {})
    总数 = len(所有对象)
    print(f"需要检查的资源文件数：{总数}")

    基础URL = "https://resources.download.minecraft.net/"

    成功 = 0
    跳过 = 0
    失败列表 = []

    for 文件名, 信息 in 所有对象.items():
        哈希 = 信息["hash"]
        子目录 = 哈希[:2]
        保存路径 = minecraft目录 / "assets" / "objects" / 子目录 / 哈希

        if 保存路径.exists():
            跳过 += 1
            continue

        保存路径.parent.mkdir(parents=True, exist_ok=True)
        下载URL = 基础URL + 子目录 + "/" + 哈希

        try:
            urllib.request.urlretrieve(下载URL, 保存路径)
            成功 += 1
        except Exception as e:
            失败列表.append(哈希)

        # 每 100 个文件输出一次进度
        已完成 = 成功 + 跳过
        if 已完成 % 100 == 0:
            print(f"  资源下载进度：{已完成}/{总数}")

    print(f"资源下载完成！成功：{成功}，跳过（已存在）：{跳过}，失败：{len(失败列表)}")
    if 失败列表:
        print("以下文件下载失败（可重试）：")
        for h in 失败列表[:5]:
            print(f"  - {h}")

print("\n" + "=" * 50)
print(f"！！！ 版本 {目标版本} 全部下载完成！")
print(f"现在可以启动 {目标版本} 了！")
##lunch！###################################################################################################################
import subprocess
import platform
import hashlib
#离线部分
def 离线UUID(玩家名):
    """根据玩家名生成稳定的离线 UUID（和官方启动器一致）"""
    原始字符串 = f"OfflinePlayer:{玩家名}"
    md5哈希 = hashlib.md5(原始字符串.encode("utf-8")).digest()
    # 把 16 字节的哈希转成 UUID 格式
    uuid_str = (
        md5哈希.hex()[:8] + "-" +
        md5哈希.hex()[8:12] + "-" +
        md5哈希.hex()[12:16] + "-" +
        md5哈希.hex()[16:20] + "-" +
        md5哈希.hex()[20:]
    )
    return uuid_str
#生成随机tok
import random
import string
def 随机Token(长度=32):
    """生成随机十六进制 token"""
    return ''.join(random.choices(string.hexdigits.lower(), k=长度))
#CLIENT_ID = "2c6bfa41-3087-484f-8902-04d9aeeffed2"

def 正版登录():
    """
    授权代码流登录（随机端口本地服务器接收回调）
    返回 (玩家名, uuid, access_token) 或 None
    """
    import http.server, threading, urllib.parse, webbrowser, time, requests, socket

    # ===== 改成你自己的 Azure 客户端 ID =====
    CLIENT_ID = "2c6bfa41-3087-484f-8902-04d9aeeffed2"
    # =======================================

    SCOPE = "XboxLive.signin offline_access"
    AUTHORIZE_URL = "https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize"
    TOKEN_URL   = "https://login.microsoftonline.com/consumers/oauth2/v2.0/token"
    XBL_URL     = "https://user.auth.xboxlive.com/user/authenticate"
    XSTS_URL    = "https://xsts.auth.xboxlive.com/xsts/authorize"
    MC_TOKEN    = "https://api.minecraftservices.com/authentication/login_with_xbox"
    MC_PROFILE  = "https://api.minecraftservices.com/minecraft/profile"

    # ---- 1. 随机端口 + 本地服务器 ----
    def 取空闲端口():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            return s.getsockname()[1]

    端口 = 取空闲端口()
    REDIRECT_URI = f"http://localhost:{端口}"
    code_box = [None]

    class 处理器(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.urlparse(self.path).query
            p = urllib.parse.parse_qs(q)
            if "code" in p:
                code_box[0] = p["code"][0]
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"OK! You can close this window.")
            else:
                self.send_response(400); self.end_headers()
        def log_message(self, *args): pass

    try:
        srv = http.server.HTTPServer(("localhost", 端口), 处理器)
    except Exception as e:
        print(f"本地服务器启动失败：{e}"); return None
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    # ---- 2. 打开浏览器 ----
    params = {"client_id": CLIENT_ID, "response_type": "code",
              "redirect_uri": REDIRECT_URI, "scope": SCOPE, "response_mode": "query"}
    url = AUTHORIZE_URL + "?" + urllib.parse.urlencode(params)
    print(f"打开浏览器登录微软账号..."); webbrowser.open(url)

    # ---- 3. 等待回调 ----
    for _ in range(600):        # 最多等 5 分钟
        if code_box[0]: break
        time.sleep(0.5)
    srv.shutdown(); srv.server_close()
    if not code_box[0]: print("超时未登录"); return None
    code = code_box[0]; print("已获得授权码")

    # ---- 4. code -> Microsoft token ----
    try:
        r = requests.post(TOKEN_URL, data={
            "client_id": CLIENT_ID, "code": code,
            "redirect_uri": REDIRECT_URI, "grant_type": "authorization_code"
        }, headers={"Content-Type": "application/x-www-form-urlencoded"})
        r.raise_for_status(); ms_token = r.json()["access_token"]
    except Exception as e: print(f"换取 Microsoft token 失败：{e}"); return None

    # ---- 5. Xbox Live ----
    try:
        r = requests.post(XBL_URL, json={
            "Properties": {"AuthMethod": "RPS", "SiteName": "user.auth.xboxlive.com",
                           "RpsTicket": f"d={ms_token}"},
            "RelyingParty": "http://auth.xboxlive.com", "TokenType": "JWT"
        }); r.raise_for_status(); xbl = r.json()["Token"]
    except Exception as e: print(f"XBL 失败：{e}"); return None

    # ---- 6. XSTS ----
    try:
        r = requests.post(XSTS_URL, json={
            "Properties": {"SandboxId": "RETAIL", "UserTokens": [xbl]},
            "RelyingParty": "rp://api.minecraftservices.com/", "TokenType": "JWT"
        }); r.raise_for_status()
        xsts = r.json()["Token"]; uhs = r.json()["DisplayClaims"]["xui"][0]["uhs"]
    except Exception as e: print(f"XSTS 失败：{e}"); return None

    # ---- 7. Minecraft token ----
    try:
        r = requests.post(MC_TOKEN, json={"identityToken": f"XBL3.0 x={uhs};{xsts}"})
        r.raise_for_status(); mc_tok = r.json()["access_token"]
    except Exception as e: print(f"Minecraft token 失败：{e}"); return None

    # ---- 8. 玩家信息 ----
    try:
        r = requests.get(MC_PROFILE, headers={"Authorization": f"Bearer {mc_tok}"})
        r.raise_for_status(); p = r.json()
        name = p["name"]; uid = p["id"]
        uuid = uid[:8]+"-"+uid[8:12]+"-"+uid[12:16]+"-"+uid[16:20]+"-"+uid[20:]
        print(f"✅ 正版登录成功：{name} ({uuid})")
        return name, uuid, mc_tok
    except Exception as e: print(f"获取信息失败：{e}"); return None

##配置启动#
def readconfig() :                                                     #读 an offline player need: pname , token ,uuid   ！！in aiidtion RAM！！
    if not CONFIG_PATH.exists():
        return None 
    config = open("config.csv",encoding='UTF-8')
    reader = csv.reader(config)
    rows = list(reader)

    if len(rows) < 1:
        return None
    数据行 = rows[0]
    if len(数据行) < 2:
        return None

    
    
    return (数据行[0], 数据行[1])
#旧名字, 旧内存 = readconfig()  # 直接解包返回值

...
登录方式 = input("请选择登录方式（1=离线登录，2=正版登录）：")

if 登录方式 == "2":
    print("正在启动微软登录...")
    结果 = 正版登录()   
    if 结果:
        pmane, uuid, token = 结果
        user_type = "mojang"
    else:
        print("正版登录失败，改为离线登录")
        pmane = input("请输入离线用户名：")
        uuid = 离线UUID(pmane)
        token = 随机Token(32)
        user_type = "legacy"
    配置 = readconfig()
    if 配置:
        # 有配置，用配置里的内存
        _, ram = 配置  # 只取内存
        print(f"使用配置的内存：{ram}")
    else:
        # 没有配置，让用户输入
        ram = input("最大内存（如 2G）：")
        if not (ram.endswith("G") or ram.endswith("M")):
            ram += "G"
        # 保存默认配置（只存内存）
        write_config("default", ram)
else:
    user_type = "legacy"
    if readconfig() == None:
        pmane = input("请输入离线用户名：")
        uuid = 离线UUID(pmane)
        token = 随机Token(32)
        #user_type = "legacy"
    # 2. 分配内存
        ram = input("最大内存（如 2G）：")
        if not (ram.endswith("G") or ram.endswith("M")):
               ram += "G"
        write_config(pmane, ram)
    else:

        旧名字, 旧内存 = readconfig()  # 直接解包返回值
        print ("上次配置：", 旧名字, 旧内存)
        应用配置 = input("您有上次配置，是否应用?是请按0，不是按1")
        if 应用配置 == "0":
           pmane = 旧名字
           ram = 旧内存
           uuid = 离线UUID(pmane)
           token = 随机Token(32)
        else:
            pmane = input("请输入离线用户名：")
            uuid = 离线UUID(pmane)
            token = 随机Token(32)
         #   user_type = "legacy"
    # 2. 分配内存
            ram = input("最大内存（如 2G）：")
            if not (ram.endswith("G") or ram.endswith("M")):
              ram += "G"
            write_config(pmane, ram)
tgver = 目标版本

#存储配置
#config   an offline player need: pname , token ,uuid   ！！in aiidtion RAM！！

def write_config():                                                      #存用户配置
    file = open ('config.csv', 'w', encoding="UTF-8")
    
    writer = csv.writer(file)
    
    #head = ['name', 'token', 'uuid'] 
    line_1 = [pmane, ram]

    #writer.writerow(head)
    writer.writerow(line_1)
    file.close()
... #if 

#write_config ()                             #存


#
JSON路径 = minecraft目录 / "versions" / 目标版本 / f"{目标版本}.json"
with open(JSON路径, "r") as f:
    版本信息 = json.load(f)
#下载缺失的资源文件
print("正在检查资源文件，首次可能需要下载几百MB，请耐心等待...")
下载资源文件(版本信息["assetIndex"]["id"], minecraft目录)
print("资源检查完毕！\n")
#找.jar 's Path
所有jar = []

# 主 jar
主jar = minecraft目录 / "versions" / 目标版本 / f"{目标版本}.jar"
所有jar.append(主jar)

# 依赖库
for 库 in 版本信息["libraries"]:
    if "downloads" in 库 and "artifact" in 库["downloads"]:
        相对路径 = 库["downloads"]["artifact"]["path"]
        所有jar.append(minecraft目录 / "libraries" / 相对路径)

# 拼成 classpath（Windows 用分号，其他用冒号）
分隔符 = ";" if platform.system() == "Windows" else ":"
classpath = 分隔符.join(str(j) for j in 所有jar)
##natives
natives目录 = minecraft目录 / "versions" / 目标版本 / "natives"
natives目录.mkdir(exist_ok=True)
###爆改启动json
替换字典 = {
    "auth_player_name": pmane,
    "version_name": tgver,
    "game_directory": str(minecraft目录),
    "assets_root": str(minecraft目录 / "assets"),
    "assets_index_name": 版本信息["assetIndex"]["id"],
    "auth_uuid": uuid,
    "auth_access_token": token,
    "user_type": user_type,
    "version_type": 版本信息.get("type", "release"),
    "natives_directory": str(natives目录),
    "launcher_name": "PythonLauncher",
    "launcher_version": "1.0",
    "classpath": classpath
}

import platform

def 匹配规则(参数, 系统名称):
    """
    检查参数是否有 rules，有则判断当前系统是否被允许。
    返回 True 表示该参数应该被使用，False 表示跳过。
    """
    规则列表 = 参数.get("rules")
    if not 规则列表:
        return True  # 没有规则，默认全平台通用

    # 默认不允许
    允许 = False
    for 规则 in 规则列表:
        操作 = 规则["action"]   # "allow" 或 "disallow"
        os_info = 规则.get("os", {})
        os_name = os_info.get("name", "")

        # 检查系统是否匹配
        if os_name:
            # 匹配：当前系统等于规则里指定的系统
            系统匹配 = (os_name == 系统名称)
            # macOS 在规则里可能写 "osx"，Linux 写 "linux"，Windows 写 "windows"
            if 系统匹配:
                if 操作 == "allow":
                    允许 = True
                elif 操作 == "disallow":
                    允许 = False
        else:
            # 没有 os 限制，只按 action 处理
            if 操作 == "allow":
                允许 = True
            elif 操作 == "disallow":
                允许 = False
    return 允许


def 替换变量(参数列表, 字典):
    结果 = []
    # 获取当前系统名称（统一为小写，和 Mojang 规则里的匹配）
    系统 = platform.system().lower()  # 返回 "windows", "linux", "darwin"
    # Mojang 用 "osx" 表示 macOS
    if 系统 == "darwin":
        系统 = "osx"

    for 参数 in 参数列表:
        if isinstance(参数, str):
            # 纯字符串参数，直接替换变量
            for 占位符, 值 in 字典.items():
                参数 = 参数.replace("${" + 占位符 + "}", 值)
            结果.append(参数)
        elif isinstance(参数, dict):
            # 字典参数，先检查规则
            if not 匹配规则(参数, 系统):
                continue  # 不匹配当前系统，跳过

            # 规则通过，处理 value
            if "value" in 参数:
                val = 参数["value"]
                if isinstance(val, str):
                    for 占位符, 值 in 字典.items():
                        val = val.replace("${" + 占位符 + "}", 值)
                    结果.append(val)
                elif isinstance(val, list):
                    for v in val:
                        if isinstance(v, str):
                            for 占位符, 值 in 字典.items():
                                v = v.replace("${" + 占位符 + "}", 值)
                            结果.append(v)
    return 结果
###
if "arguments" in 版本信息:
    jvm原始 = 版本信息["arguments"]["jvm"]
    游戏原始 = 版本信息["arguments"]["game"]
else:
    jvm原始 = []
    游戏原始 = 版本信息["minecraftArguments"].split()

jvm参数 = 替换变量(jvm原始, 替换字典)
游戏参数 = 替换变量(游戏原始, 替换字典)
### 超级拼装！ && lunch！
命令 = ["java", f"-Xmx{ram}"] + jvm参数 + [版本信息["mainClass"]] + 游戏参数

# ========== 绝对可靠的参数清洗 ==========
def 清洗命令(原始命令):
    """只保留第一个 --quick，删除多余的，同时删除 --demo"""
    新命令 = []
    已见quick = False
    i = 0
    while i < len(原始命令):
        arg = 原始命令[i]
        
        # 处理 --demo（跳过它和下一个参数）
        if arg == '--demo':
            i += 2  # 跳过 --demo 和它后面的值
            continue
        
        # 处理 --quick 系列
        if arg.startswith('--quick'):
            if not 已见quick:
                新命令.append(arg)
                已见quick = True
            i += 1
            continue
        
        # 其他参数原样保留
        新命令.append(arg)
        i += 1
    
    return 新命令

命令 = 清洗命令(命令)

# 调试输出：看清洗后的参数
print("\n===== 清洗后的前20个参数 =====")
for a in 命令[:20]:
    print(a)
print("...\n")

subprocess.run(命令, cwd=minecraft目录)
#以上是内核。