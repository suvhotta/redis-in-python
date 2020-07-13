import redis, random, pprint, logging, json

random.seed(11)
hats = {
    f"hat:{random.getrandbits(32)}": i for i in (
    {    
        "color": "black",
        "price": 49.99,
        "style": "fitted",
        "quantity": 1000,
        "npurchased": 0,
    },
    {
        "color": "maroon",
        "price": 59.99,
        "style": "hipster",
        "quantity": 500,
        "npurchased": 0,
    },
    {
        "color": "green",
        "price": 99.99,
        "style": "baseball",
        "quantity": 200,
        "npurchased": 0,
    })
}
for key, value in hats.items():
    print(key, value)

#using db=1, default is db 0. 1 Redis server can have 16 dbs.
r = redis.Redis(db=1)

"""
With pipeline, all the requests are sent at once, and thus num of round trips is reduced.
Using pipeline, all the commands are buffered at the client side and sent at once.
Instead if this would have been done by r.hmset(), it would have taken 3 round trips.
"""

with r.pipeline() as pipe:
    for h_key, hat in hats.items():
        pipe.hmset(h_key, hat)
    pipe.execute()
r.bgsave()

logging.basicConfig()

class OutOfStockError(Exception):
    """Raised when out of stock for some specific hat"""

def buyitem(r:redis.Redis, itemid:int) -> None:
    """
    The buying is achieved by performing a couple of steps in a transaction format.
    The quantity is increased and the npurchased is decreased in one go. If either of them fails,
    then the transaction is aborted and any steps taken is rolled back.
    The item is being watched by the watch command, which gives a check and set behaviour.
    If any value of the item changes in the mid of performing the buy operation, a watcherror is thrown
    This process is called optimistic locking.
    """
    with r.pipeline() as pipe:
        err_count = 0
        while True:
            try:
                # Get the item, watch for changes before committing any transaction
                pipe.watch(itemid)
                nleft:bytes = r.hget(itemid, "quantity")
                if nleft > b"0":
                    pipe.multi()
                    pipe.hincrby(itemid, "quantity", -1)
                    pipe.hincrby(itemid, "npurchased", 1)
                    pipe.execute()
                    break
                else:
                    #stop watching the itemid and raise eror to break out
                    pipe.unwatch()
                    raise OutOfStockError(
                        f"Sorry, {itemid} is out of stock!"
                    )
            except redis.WatchError:
                err_count += 1
                logging.warning(f"Watcherror #{err_count}: {itemid}; retrying!")

    return None

for _ in range(205):
    buyitem(r, 'hat:2404204071')

print(r.hmget('hat:2404204071', "quantity", "npurchased"))
