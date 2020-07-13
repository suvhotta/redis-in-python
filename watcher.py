import ipaddress, redis, time

blacklist = set()
maxvisits = 15

ipwatcher = redis.Redis(db=5)

while True:
    _, addr = ipwatcher.blpop("ips")
    addr = ipaddress.ip_address(addr.decode('utf-8'))
    addr_key = f"{addr}:"
    seconds = time.time()
    ipwatcher.zadd(addr_key, {seconds:seconds})
    ipwatcher.expire(addr_key, 60)
    ipwatcher.zremrangebyscore(addr_key, "-inf", seconds-60)
    num = len(ipwatcher.zrange(addr_key, 0, -1))
    if num >= maxvisits:
        print(f"Bot detected{addr}")
        blacklist.add(addr)
    else:
        now = datetime.datetime.utcnow()
        print(f"{now} saw : {addr}")


# while True:
#     _, addr = ipwatcher.blpop("ips")
#     addr = ipaddress.ip_address(addr.decode("utf-8"))
#     now = datetime.datetime.utcnow()
#     addrts = f"{addr}:{now.minute}"
#     n = ipwatcher.incrby(addrts, 1)
#     if n>= maxvisits:
#         print(f"Bot detected{addr}")
#         blacklist.add(addr)
#     else:
#         now = datetime.datetime.utcnow()
#         print(f"{now} saw : {addr}")
#     _ = ipwatcher.expire(addrts, 60)

# for _ in range(20):
#     r.lpush("ips", "104.174.118.18")
