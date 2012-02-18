import datetime

def str2date(date_str):
    return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()

def classlist2int(class_list):
    def add(x, y): return x + (1 << (y - 1))
    return reduce(add, class_list, 0)
