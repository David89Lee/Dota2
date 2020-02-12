# -*- coding: utf-8 -*-
import itertools
import time
from functools import wraps
import signal

class Hero:
    def __init__(self, id, name, race_id, profession_id, star):
        self.id = id
        self.name = name
        self.race_id = race_id
        self.profession_id = profession_id
        self.star = star

class Race:
    def __init__(self, id, name, link):
        self.id = id
        self.name = name
        self.link = link

class Profession:
    def __init__(self, id, name, link):
        self.id = id
        self.name = name
        self.link = link
class CommonObj:
    def __init__(self):
        self.hero_ids = []
        self.score = 0
    def cal_score(self, link):# link 羁绊
        for x in sorted(link, reverse=True):
            if len(self.hero_ids)>=x:
                self.score = len(self.hero_ids)*(1+x/6)
                break
class Group:
    def __init__(self, hero_ids):
        self.hero_ids = hero_ids
        self.race_dic = {} # {1: common_obj}
        self.profession_dic = {} # {1: common_obj}
        self.star_dic = {} # {1: common_obj}
        self.score = 0
        self.star_rate = 0.5
        self.analysis(self.star_rate)
    def __str__(self):
        race_dic_show = {}
        for k,common_obj in self.race_dic.items():
            if len(common_obj.hero_ids):
                race_dic_show[k] = common_obj
        profession_dic_show = {}
        for k,common_obj in self.profession_dic.items():
            if len(common_obj.hero_ids):
                profession_dic_show[k] = common_obj
        star_dic_show = {}
        for k,common_obj in self.star_dic.items():
            if len(common_obj.hero_ids):
                star_dic_show[k] = common_obj

        heros_str = "分数: {}\n".format(self.score)
        heros_str += "英雄: "
        for id in self.hero_ids:
            heros_str += heros[id].name+" "
        heros_str += "\n种族:\n"
        for race_id, common_obj in race_dic_show.items():
            if common_obj.score!=0:
                race = races[race_id]
                heros_str += "  "+race.name+":"
                for hero_id in common_obj.hero_ids:
                    heros_str += " "+heros[hero_id].name
                heros_str += "\n"
        heros_str += "职业:\n"
        for profession_id, common_obj in profession_dic_show.items():
            if common_obj.score != 0:
                profession = professions[profession_id]
                heros_str += "  " + profession.name + ":"
                for hero_id in common_obj.hero_ids:
                    heros_str += " "+heros[hero_id].name
                heros_str += "\n"
        heros_str += "星级:\n"
        for star, common_obj in star_dic_show.items():
            if common_obj.score != 0:
                heros_str += "  {}:".format(star)
                for hero_id in common_obj.hero_ids:
                    heros_str += " " + heros[hero_id].name
                heros_str += "\n"
        heros_str += "\n"
        return heros_str
    def analysis(self, star_rate):
        for hero_id in self.hero_ids:
            hero = heros[hero_id]
            # 可能属于多个种族
            if isinstance(hero.race_id, list):
                for race_id in hero.race_id:
                    if self.race_dic.has_key(race_id):
                        race_obj = self.race_dic[race_id]
                    else:
                        race_obj = CommonObj()
                        self.race_dic[race_id] = race_obj
            else:
                if self.race_dic.has_key(hero.race_id):
                    race_obj = self.race_dic[hero.race_id]
                else:
                    race_obj = CommonObj()
                    self.race_dic[hero.race_id] = race_obj
            race_obj.hero_ids.append(hero.id)
            if self.profession_dic.has_key(hero.profession_id):
                profession_obj = self.profession_dic[hero.profession_id]
            else:
                profession_obj = CommonObj()
                self.profession_dic[hero.profession_id] = profession_obj
            profession_obj.hero_ids.append(hero.id)
            if self.star_dic.has_key(hero.star):
                star_obj = self.star_dic[hero.star]
            else:
                star_obj = CommonObj()
                self.star_dic[hero.star] = star_obj
            star_obj.hero_ids.append(hero.id)
        for race_id, common_obj in self.race_dic.items():
            common_obj.cal_score(races[race_id].link)
            self.score += common_obj.score
        for profession_id, common_obj in self.profession_dic.items():
            common_obj.cal_score(professions[profession_id].link)
            self.score += common_obj.score
        for star, common_obj in self.star_dic.items():
            common_obj.score = star * len(common_obj.hero_ids) * star_rate
            self.score += common_obj.score

def fn_timer(function):
    @wraps(function)
    def function_timer(*args, **kwargs):
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        print ("Total time running %s: %f seconds" %
               (function.func_name, t1-t0)
               )
        return result
    return function_timer

# @fn_timer
# def hero_group_factory(heros, num_in_group=6):
#     groups = []
#     for hero_ids in itertools.combinations(heros.keys(), num_in_group):
#         group = Group(hero_ids)
#         groups.append(group)
#     print "all groups number:{}".format(len(groups))
#     return groups

class FindBest:
    def __init__(self):
        self.exit = False
        self.count = 0

    def signal_fun(self, signum, frame):
        print "exit"
        self.exit = True
    @fn_timer
    def find_best(self, heros, num_in_group=6, best_num=5):
        groups = []
        it = itertools.combinations(heros.keys(), num_in_group)
        while True:
            try:
                if not self.exit:
                    # 获得下一个值:
                    hero_ids = next(it)
                    self.count += 1
                    print "now process {}, count: {}".format(str(hero_ids), self.count)
                    group = Group(hero_ids)
                    if len(groups) == 0:
                        groups.append(group)
                    else:
                        inserted = False
                        for i,g in enumerate(groups):
                            if group.score > g.score:
                                inserted = True
                                groups.insert(i, group)
                                break
                        if not inserted and len(groups)<best_num:
                            groups.append(group)
                        if len(groups)>best_num:
                            del groups[best_num]
                else:
                    for g in groups:
                        print g
                    break
            except StopIteration:
                # 遇到StopIteration就退出循环
                break
        if not self.exit:
            for g in groups:
                print g



heros_bak = {
    1: Hero(1,"斧王"	,1,1,1),
    2: Hero(2,"魅惑魔女",2,2,1),
    3: Hero(3,"食人魔魔法师",3,3,1),
    4: Hero(4,"巨牙海明",2,1,1),
    5: Hero(5,"卓尔游侠",4,4,1),
    6: Hero(6,"赏金猎人",5,5,1),
    7: Hero(7,"发条技师",5,6,1),
    8: Hero(8,"暗影萨满",6,7,1),
    9: Hero(9,"蝙蝠骑士",6,8,1),
    10: Hero(10,"修补匠",5,6,1),
    11: Hero(11,"敌法师",7,9,1),
    12: Hero(12,"水晶室女",8,3,2),
    13: Hero(13,"兽王",1,4,2),
    14: Hero(14,"剑圣",1,1,2),
    15: Hero(15,"伐木机",5,6,2),
    16: Hero(16,"痛苦女王",9,5,2),
    17: Hero(17,"精灵龙",[7,10],3,2),
    18: Hero(18,"巫医",6,10,2),
    19: Hero(19,"鱼人守卫",11,1,2),
    20: Hero(20,"混沌骑士",9,8,2),
    21: Hero(21,"树精卫士",7,2,2),
    22: Hero(22,"月之骑士",7,8,2),
    23: Hero(23,"先知",7,2,2),
    24: Hero(24,"狼人",[8,2],1,3),
    25: Hero(25,"剧毒术士",2,10,3),
    26: Hero(26,"全能骑士",8,8,3),
    27: Hero(27,"闪电幽魂",12,3,3),
    28: Hero(27,"闪电幽魂",12,3,3),
    29: Hero(29,"幻影刺客",7,5,3),
    30: Hero(30,"死亡骑士",4,8,3),
    31: Hero(31,"沙王",2,5,3),
    32: Hero(32,"鱼人夜行者",11,5,3),
    33: Hero(33,"狙击手",13,4,3),
    34: Hero(34,"冥界亚龙",10,5,3),
    35: Hero(35,"影魔",9,10,3),
    36: Hero(36,"秀逗魔导师",8,3,3),
    37: Hero(37,"末日使者",9,1,4),
    38: Hero(38,"海军上将",8,1,4),
    39: Hero(39,"巨魔战将",6,1,4),
    40: Hero(40,"光之守卫",8,3,4),
    41: Hero(41,"死灵法师",4,10,4),
    42: Hero(42,"圣堂刺客",7,5,4),
    43: Hero(43,"炼金术士",5,10,4),
    44: Hero(44,"干扰者",2,7,4),
    45: Hero(45,"蛇发女妖",11,4,4),
    46: Hero(46,"龙骑士",[8,10],8,4),
    47: Hero(47,"利爪德鲁伊",2,2,4),
    48: Hero(48,"矮人直升机",13,6,5),
    49: Hero(49,"巫妖",4,3,5),
    50: Hero(50,"潮汐猎人",11,4,5),
    51: Hero(51,"谜团",12,10,5),
    52: Hero(52,"地精工程师",5,6,5),
}
heros = {
    5: Hero(5,"狼人",[8,2],1,3),
    1: Hero(1,"剑圣",1,1,2),
    2: Hero(2,"潮汐猎人",11,4,5),
    4: Hero(4,"末日使者",9,1,4),
    3: Hero(3,"矮人直升机",13,6,5),

    14: Hero(14,"斧王"	,1,1,1),
    50: Hero(50,"魅惑魔女",2,2,1),
    48: Hero(48,"食人魔魔法师",3,3,1),
    6: Hero(6,"巨牙海明",2,1,1),
    7: Hero(7,"卓尔游侠",4,4,1),
    37: Hero(37,"赏金猎人",5,5,1),
    24: Hero(24,"发条技师",5,6,1),
    8: Hero(8,"暗影萨满",6,7,1),
    9: Hero(9,"蝙蝠骑士",6,8,1),
    10: Hero(10,"修补匠",5,6,1),
    11: Hero(11,"敌法师",7,9,1),
    12: Hero(12,"水晶室女",8,3,2),
    13: Hero(13,"兽王",1,4,2),

    15: Hero(15,"伐木机",5,6,2),
    16: Hero(16,"痛苦女王",9,5,2),
    17: Hero(17,"精灵龙",[7,10],3,2),
    18: Hero(18,"巫医",6,10,2),
    19: Hero(19,"鱼人守卫",11,1,2),
    20: Hero(20,"混沌骑士",9,8,2),
    21: Hero(21,"树精卫士",7,2,2),
    22: Hero(22,"月之骑士",7,8,2),
    23: Hero(23,"先知",7,2,2),

    25: Hero(25,"剧毒术士",2,10,3),
    26: Hero(26,"全能骑士",8,8,3),
    27: Hero(27,"闪电幽魂",12,3,3),
    28: Hero(27,"闪电幽魂",12,3,3),
    29: Hero(29,"幻影刺客",7,5,3),
    30: Hero(30,"死亡骑士",4,8,3),
    31: Hero(31,"沙王",2,5,3),
    32: Hero(32,"鱼人夜行者",11,5,3),
    33: Hero(33,"狙击手",13,4,3),
    34: Hero(34,"冥界亚龙",10,5,3),
    35: Hero(35,"影魔",9,10,3),
    36: Hero(36,"秀逗魔导师",8,3,3),

    38: Hero(38,"海军上将",8,1,4),
    39: Hero(39,"巨魔战将",6,1,4),
    40: Hero(40,"光之守卫",8,3,4),
    41: Hero(41,"死灵法师",4,10,4),
    42: Hero(42,"圣堂刺客",7,5,4),
    43: Hero(43,"炼金术士",5,10,4),
    44: Hero(44,"干扰者",2,7,4),
    45: Hero(45,"蛇发女妖",11,4,4),
    46: Hero(46,"龙骑士",[8,10],8,4),
    47: Hero(47,"利爪德鲁伊",2,2,4),

    49: Hero(49,"巫妖",4,3,5),

    51: Hero(51,"谜团",12,10,5),
    52: Hero(52,"地精工程师",5,6,5),
}

races = {
    1: Race(1,"兽人",[2,4]),
    2: Race(2,"野兽",[2, 4, 6]),
    3: Race(3,"食人魔",[1]),
    4: Race(4,"亡灵",[2, 4]),
    5: Race(5,"地精",[3, 6]),
    6: Race(6,"巨魔",[2, 4]),
    7: Race(7,"精灵",[2, 4, 6]),
    8: Race(8,"人类",[2, 4, 6]),
    9: Race(9,"恶魔",[1]),
    10: Race(10,"龙",[3]),
    11: Race(11,"娜迦",[2, 4]),
    12: Race(12,"元素",[2]),
    13: Race(13,"矮人",[1]),
}

professions = {
    1: Profession(1,"战士",[3 ,6]),
    2: Profession(2,"德鲁伊",[2 ,4]),
    3: Profession(3,"法师",[3 ,6]),
    4: Profession(4,"猎人",[3 ,6]),
    5: Profession(5,"刺客",[3 ,6]),
    6: Profession(6,"工匠",[2 ,4]),
    7: Profession(7,"萨满祭司",[2]),
    8: Profession(8,"骑士",[2 ,4 ,6]),
    9: Profession(9,"恶魔猎手",[1]),
    10: Profession(10,"术士",[3 ,6]),
}

if __name__ == '__main__':
    fb = FindBest()
    signal.signal(signal.SIGINT, fb.signal_fun)
    fb.find_best(heros, num_in_group=9, best_num=6)