import os
from exception import Exception
os.chdir(os.path.dirname(__file__))

class Database:
    @staticmethod
    def query(q):
        if q[-1] == ';':
            q = q[0:-1]
        return getattr(Database, q.split(' ', 1)[0].lower())(q)

    @staticmethod
    def insert(q):
        q = q.split(' ', 4)
        table = q[2]
        values = q[4][1:-1].split(',')
        values = Database.encode(values)
        Database.check_type(table, values)
        with open(table + '.txt', 'r') as f:
            lines = f.readlines()
        with open(table + '.txt', 'a') as f:
            if len(lines) == 1:
                last_id = 1
            else:
                last_line = lines[-1]
                last_id = int(last_line.split()[0]) + 1
            values.insert(0, last_id)
            f.write(' '.join(str(i) for i in values) + '\n')

    @staticmethod
    def select(q):
        q = q.split(' ', 4)
        table = q[2]
        if len(q) > 3:
            condition = q[4]
        else:
            condition = ''
        with open(table + '.txt', 'r') as f:
            lines = f.readlines()
        head, lines = lines[0].split(' '), lines[1:]
        res = []
        for l in lines:
            l = l.replace('\n', '').split(' ')
            l = Database.decode(l)
            if Database.check_condition(dict(zip(head, l)), condition):
                res.append(dict(zip(head, l)))
        return res

    @staticmethod
    def delete(q):
        q = q.split(' ', 4)
        table = q[2]
        condition = q[4]
        with open(table + '.txt', 'r') as f:
            lines = f.readlines()
        head, lines = lines[0].split(' '), lines[1:]
        res = []
        for l in lines:
            l = l.split(' ')
            l = Database.decode(l)
            if not Database.check_condition(dict(zip(head, l)), condition):
                res.append(l)
        with open(table + '.txt', 'w') as f:
            f.write(' '.join(head))
            for l in res:
                f.write(' '.join(Database.encode(l)))

    @staticmethod
    def update(q):
        q = q.split(' ', 3)
        table = q[1]
        condition, values = q[3].split(' VALUES ')
        values = values[1:-1].split(',')
        with open(table + '.txt', 'r') as f:
            lines = f.readlines()
        head, lines = lines[0].split(' '), lines[1:]
        res = []
        for l in lines:
            l = l.split(' ')
            l = Database.decode(l)
            if not Database.check_condition(dict(zip(head, l)), condition):
                res.append(l)
            else:
                values.insert(0, l[0])
                values.append('\n')
                res.append(values)
        with open(table + '.txt', 'w') as f:
            f.write(' '.join(head))
            for l in res:
                f.write(' '.join(Database.encode(l)))

    @staticmethod
    def check_condition(dict, condition):
        if ('AND' in condition):
            a, b = condition.split(' AND ')
            return Database.check_condition(
                dict, a) and Database.check_condition(dict, b)
        if ('OR' in condition):
            a, b = condition.split(' OR ')
            return Database.check_condition(
                dict, a) or Database.check_condition(dict, b)
        if ('==' in condition):
            a, b = condition.split('==')
            b = b[1:-1]
            return dict[a] == b
        if ('!=' in condition):
            a, b = condition.split('!=')
            b = b[1:-1]
            return dict[a] != b
        return True

    @staticmethod
    def encode(val):
        new_val = []
        for v in val:
            new_val.append(v.replace(' ', '`'))
        return new_val

    @staticmethod
    def decode(val):
        new_val = []
        for v in val:
            new_val.append(v.replace('`', ' '))
        return new_val

    @staticmethod
    def check_type(table, values):
        with open(table + '.txt', 'r') as f:
            head = f.readlines()[0].split(' ')[1:-1]
        d = dict(zip(head, values))
        for i in d:
            with open('Schema.txt', 'r') as f:
                check = False
                for l in f.readlines():
                    if l == table + '\n':
                        check = True
                    elif check == True:
                        l = l.split(' ')
                        if len(l) >= 2 and l[0] == i:
                            if l[1] == 'UNIQUE':
                                cnt = len(
                                    Database.query(
                                        'SELECT FROM {} WHERE {}=="{}"'.format(
                                            table, i, d[i])))
                                if cnt > 0:
                                    Exception.print(
                                        '{} is already taken!!!'.format(d[i]))
                                    app.show_requests()
                            if l[1][0:4] == 'CHAR' or (l[1] == 'UNIQUE' and
                                                       l[2][0:4] == 'CHAR'):
                                if l[1][0:4] == 'CHAR':
                                    max_len = int(l[1][5:-2])
                                else:
                                    max_len = int(l[2][5:-2])
                                if max_len < len(d[i]):
                                    Exception.print(
                                        '{} is tooooooo 🤯 long!!!'.format(
                                            d[i]))
                                    app.show_requests()
                            break
