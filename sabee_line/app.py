import os
import json
import time
from core.helpers import qname, CommandParser
from mirai import At, Plain, Mirai, Group, Member


def t2(i):
    return i[1]

def getpath(name=""):
    return os.path.join("sabee_line/storage", (str(name) or time.strftime("%y%m%d"))+".json")


def sabee_add(d, group_id, member_id):
    if group_id not in d:
        print(group_id, "added")
        d[group_id] = {}
    if member_id not in d[group_id]:
        print(member_id, "added")
        d[group_id][member_id] = 0
    d[group_id][member_id] += 1

def sabee_gets(d, group_id, count=3):
    members = d.get(group_id)
    if not members:
        return None
    result = []
    for m, c in members.items():
        result.append((m, c))
    result.sort(key=t2, reverse=True)  # 少的到后面去
    return result[:count]

if os.path.isfile(getpath()):
    sabee = json.load(open(getpath(), "r"))
else:
    sabee = {}

def save():
    global sabee
    if os.path.isfile(getpath()):
        json.dump(sabee, open(getpath(), "w"), indent=2)
    else:
        sabee = {}
        json.dump({}, open(getpath(), "w"), indent=2)
    print("saved")

async def lm_create(app: Mirai, count_data: dict, gid: int, mid: int):
    raw = sabee_gets(count_data, str(gid), count=8)
    if not raw:
        return [At(mid), Plain("暂时还没有数据..")]
    result = [At(mid), Plain("发言数统计：\n")]
    result.append(Plain("+==================+\n"))
    for p, (m, c) in enumerate(raw):
        if p == 0:
            p = "🔥"
        else:
            p = f" {p+1} "
        result.extend([Plain(f"L[{p}] {(await app.memberInfo(gid, int(m))).name or await qname.query(m)}:  {c}\n")])
    result.append(Plain(f"共{len(count_data[str(gid)])}人水群"))
    return result

async def lm(app: Mirai, group: Group, member: Member, cp: CommandParser):
    arg = cp.parse_with_valid(["Int"])
    if not arg:
        await app.sendGroupMessage(group, await lm_create(app, sabee, group.id, member.id))
    elif isinstance(arg, str):
        await app.sendGroupMessage(group, Plain(arg))
    else:
        if os.path.isfile(getpath(arg[0][1])):
            await app.sendGroupMessage(group, await lm_create(app,
                                                              json.load(open(getpath(arg[0][1]), "r")),
                                                              group.id, member.id))
        else:
            await app.sendGroupMessage(group, [At(member.id), Plain(f"没有找到日期为{arg[0][1]}的记录")])
    return True

async def sabee_plus(group: Group, member: Member):
    sabee_add(sabee, str(group.id), str(member.id))


export = {
    "command": {"rank": lm},
    "active": [sabee_plus]
}
