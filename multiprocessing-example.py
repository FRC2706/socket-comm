import multiprocessing
import time

def worker(num):
    """thread worker function"""
    print 'Start Worker:', num
    time.sleep(5)
    print 'end Worker:', num
    return

if __name__ == '__main__':
    jobs = []
    for i in range(5):
        p = multiprocessing.Process(target=worker, args=(i,))
        jobs.append(p)
        p.start()
