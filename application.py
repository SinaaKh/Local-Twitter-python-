from exception import Exception
from database import Database
from datetime import datetime


class App:
    requests_list = [('database_migration', []),
                     ('login', ['username', 'password']),
                     ('register',
                      ['name', 'username', 'password', 'confirm_password']),
                     ('view', []), ('likes', ['tweet_id'])]

    def show_requests(self):
        i = 1
        print('------------------------------------------')
        for request in self.requests_list:
            print('→', i, request[0].replace('_', ' ').title())
            i += 1
        inp = input('🤔 Which one? ')
        if not inp.isnumeric():
            Exception.print(list(range(1, i)))
            self.show_requests()
        inp = int(inp)
        if inp not in range(1, i):
            Exception.print(list(range(1, i)))
            self.show_requests()
        dict = {}
        for q in self.requests_list[inp - 1][1]:
            dict[q] = input('{}: '.format(q.replace('_', ' ').title()))
        getattr(Request, self.requests_list[inp - 1][0])(dict)


class Request:
    @staticmethod
    def database_migration(dict):
        with open('Schema.txt', 'r') as f:
            lines = f.readlines()
            lines.append('\n')
        last = 0
        for i in range(len(lines)):
            if lines[i] == '\n':
                Request.database_migration_table(lines[last:i])
                last = i + 1
        app.show_requests()

    @staticmethod
    def database_migration_table(lines):
        table = lines[0].replace('\n', '')
        with open(table + '.txt', 'w') as f:
            for l in lines[1:]:
                f.write(l.split(' ')[0] + ' ')
            f.write('\n')

    @staticmethod
    def login(dict):
        global auth
        auth.login(dict['username'], dict['password'])

    @staticmethod
    def register(dict):
        global auth
        if (dict['password'] != dict['confirm_password']):
            Exception.print('Password not match!!!')
            global app
            app.show_requests()
        auth.register(dict['name'], dict['username'], dict['password'])

    @staticmethod
    def tweet(dict, par='0'):
        global auth
        if (not auth.check()):
            Exception.print('You must be login first!!!')
            app.show_requests()
        Database.query('INSERT INTO tweets VALUES (' + ','.join(
            [auth.user['id'], par, dict['message'],
             str(datetime.now())]) + ')')
        app.show_requests()

    @staticmethod
    def view(dict):
        tweets = Database.query('SELECT FROM tweets')
        for tweet in tweets:
            print('------------------------------------------')
            print('🦄 {} 🤠 {} ❤  {} 📅 {}'.format(
                tweet['id'],
                Database.query('SELECT FROM users WHERE id=="' +
                               tweet['user_id'] + '"')[0]['username'],
                len(
                    Database.query(
                        'SELECT FROM likes WHERE tweet_id=="{}"'.format(
                            tweet['id']))), tweet['created_at']) +
                  (' 🔁' if tweet['par_tweet_id'] != '0' else ''))
            print('')
            Request.print_tweet_message(tweet)
            print('')
        app.show_requests()

    @staticmethod
    def print_tweet_message(tweet):
        if tweet['message'] != '':
            print('{}'.format(tweet['message']))
        if tweet['par_tweet_id'] != '0':
            par_tweet = Database.query(
                'SELECT FROM tweets WHERE id=="{}"'.format(
                    tweet['par_tweet_id']))[0]
            if par_tweet['message'] != '':
                print('👀 {} → '.format(
                    Database.query('SELECT FROM users WHERE id=="' +
                                   par_tweet['user_id'] + '"')[0]['username']),
                      end='')
            Request.print_tweet_message(par_tweet)

    @staticmethod
    def like(dict):
        global auth
        if (not auth.check()):
            Exception.print('You must be login first!!!')
            app.show_requests()
        like_cnt = len(
            Database.query(
                'SELECT FROM likes WHERE tweet_id=="{}" AND user_id=="{}"'.
                format(dict['tweet_id'], auth.user['id'])))
        tweet_cnt = len(
            Database.query('SELECT FROM tweets WHERE id=="{}"'.format(
                dict['tweet_id'])))
        if like_cnt == 0 and tweet_cnt == 1:
            Database.query('INSERT INTO likes VALUES (' +
                           ','.join([dict['tweet_id'], auth.user['id']]) + ')')
        elif like_cnt == 0:
            Exception.print('Invalid Tweet Id!!!')
        else:
            Exception.print('You Liked it before!!!')
        app.show_requests()

    @staticmethod
    def likes(dict):
        tweet_cnt = len(
            Database.query('SELECT FROM tweets WHERE id=="{}"'.format(
                dict['tweet_id'])))
        if tweet_cnt == 0:
            Exception.print('Invalid Tweet Id!!!')
            app.show_requests()
        likes = Database.query('SELECT FROM likes WHERE tweet_id=="{}"'.format(
            dict['tweet_id']))
        for like in likes:
            print('🤠 {}'.format(
                Database.query('SELECT FROM users WHERE id=="{}"'.format(
                    like['user_id']))[0]['username']))
        app.show_requests()

    @staticmethod
    def retweet(dict):
        tweet_cnt = len(
            Database.query('SELECT FROM tweets WHERE id=="{}"'.format(
                dict['tweet_id'])))
        if tweet_cnt == 1:
            Request.tweet(dict, dict['tweet_id'])
        else:
            Exception.print('Invalid Tweet Id!!!')
            app.show_requests()

    @staticmethod
    def logout(dict):
        global auth
        auth.user = {}
        app.requests_list = [
            ('database_migration', []),
            ('login', ['username', 'password']),
            ('register', ['name', 'username', 'password', 'confirm_password']),
            ('view', []),
            ('likes', ['tweet_id'])
        ]
        app.show_requests()


class Auth:
    user = {}

    def login(self, username, password):
        global app
        self.user = Database.query('SELECT FROM users WHERE username=="' +
                                   username + '" AND password=="' + password +
                                   '"')
        if (not auth.check()):
            Exception.print('Login failed!!!')
            app.show_requests()
        else:
            self.user = self.user[0]
            app.requests_list = [('tweet', ['message']), ('view', []),
                                 ('like', ['tweet_id']),
                                 ('likes', ['tweet_id']),
                                 ('retweet', ['tweet_id', 'message']),
                                 ('logout', [])]
            app.show_requests()

    def register(self, name, username, password):
        Database.query(
            'INSERT INTO users VALUES (' +
            ','.join([name, username, password,
                      str(datetime.now())]) + ')')
        self.login(username, password)

    def check(self):
        return len(self.user) > 0


# database = Database()
# print(database.query('UPDATE hey WHERE abi=="slm" AND li=="1" VALUES (a,b,c)'))

app = App()
auth = Auth()
app.show_requests()
