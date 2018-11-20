import sys
if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('''Specify argument. 
Possible commands:
convert users
For launching flask server see README.md''')
    elif sys.argv[1] == 'convert':
        if len(sys.argv) > 2 and sys.argv[2] == 'users':
            import converters.users
        else:
            print('Specify model to convert')
