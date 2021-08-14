class Exception:
    @staticmethod
    def print(x):
        print('------------------------------------------')
        print('|🤪🤪🤪 Invalid!!! 🤪🤪🤪')
        if type(x) == type([]):
            print('|🤨 Input must be one of', ', '.join(str(i) for i in x))
        else:
            print('|🤨', x)
