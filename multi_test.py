from multiprocessing import Process

def func1(argm, dummy):
    print("test" + argm)

a = 'aaaaaaa'
p = Process(target=func1, args=(a, "dummy") )
p.start()

if p:
    p.join()
