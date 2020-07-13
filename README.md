# redis-in-python
Redis operations like pipeline, watch, transactions etc. implemented using python

Redis is a data-structure storage, usually stored in memory. <br/>
It can be used as for caching, message broker, maintaining leaderboards, storing sessions etc. <br/>

Here I've demonstrated a few used cases of redis. <br/>

## hats.py
### Summary:
There are 3 different kinds of hats up for sale. Information about the hats like the quantities, price, color, style etc is stored in a redis server DB.<br/>

Brief explanation of concepts that have been touched in this script: <br/>
- <strong>Pipeline</strong> <br/>
With pipeline, all the requests are queued at the client side in the form of a buffer and sent at once, thereby reducing the RRC(Request response cycle). Once all the requests have been sent, the server will be queuing up the responses. Using a pipeline not only enhances by altering the RRC but also improves the overall interaction time of the redis server because the redis server has now less I/O related operations to deal with.
```
with r.pipeline() as pipe:
    for h_key, hat in hats.items():
        pipe.hmset(h_key, hat)
    pipe.execute()
 ```
 - <strong>Watch</strong> <br/>
The watch command helps in preserving the atomicity of a transaction. When the key being watched undergoes a change by one user, while it is in the middle of a transaction by another user, an error is sent, so that the atomicity of the transaction isn't disturbed. Once watching is completed, it should be followed by unwatch. However, if exec or discard are being used, they flush the keys to be watched hence no need of calling unwatch again.
```
pipe.watch(itemid)
```
- <strong>multi and execute</strong>
When there are certain dependency in the db values, the best way to change them is to do so by using transactions. They follow a make or break principle i.e. either all of the operations listed in a transaction occur or none of them do. Thus nullifying any chance of partial data updation. The multi function in redis signifies the start of a transaction, and following which all the operations are queued until the exec keyword is reached. Once exec is encountered, all the operations are executed serially.

