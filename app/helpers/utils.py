import datetime

def str2date(date_str):
    return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()

def classlist2int(class_list):
    def add(x, y): return x + (1 << (y - 1))
    return reduce(add, class_list, 0)

def merge_time(time_list, assembling):
    ret_list = []
    time_set = set(time_list)
    for i in assembling:
        s = set(range(i.start_no, i.end_no + 1))
        if s <= time_set:
            ret_list.append(i.display)
        elif not time_set.isdisjoint(s):
            ret_list.extend(list(time_set & s))
    return ret_list
