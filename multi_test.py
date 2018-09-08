from multiprocessing import Process

def func1(argm, dummy):
    print("test" + argm)

arrayResIds = ['aaaaaaa', 'bbbbbbb','ccccccc','dddddd']
p = None

for aId in arrayResIds:
    p = Process(target=func1, args=(aId, "dummy") )
    p.start()

print("before")
if p:
    p.join()

print("finish")