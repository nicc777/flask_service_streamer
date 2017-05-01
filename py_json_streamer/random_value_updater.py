"""
This is a simple app to generate random numbers for keys stored in memcached.

The keys are upper case letters starting from 'A' through to 'Z' (inclusive).

The key value will only be updated if a random number is less than 10 or greater than 100.
"""
from memcache import Client
import string, random, time

servers = ["127.0.0.1:11211"]
mc = Client(servers, debug=1)

if __name__ == '__main__':
    for c in string.ascii_uppercase:
        mc.set(c, 0, noreply=False)
    while True:
        for c in string.ascii_uppercase:
            r = random.randint(0, 100)
            if r < 10 or r > 90:
                print('Setting value for {}'.format(c), end='')
                v = random.randint(0, 100)
                mc.set(c, v, noreply=False)
                print('  -> test: v={}'.format(mc.get(c)))
        print('*')
        time.sleep(1)

# EOF