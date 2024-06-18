
import os
import json
import subprocess
import time
import pymysql

if os.getenv("CHAIN_TYPE") == "raft":
    print("raft chain don't need to execute exporter latency test")
    exit(0)

# send tx and get tx hash
cmd = "cldi -c default send 0xffffffffffffffffffffffffffffffffff010000 0xabcd"
tx_hash = subprocess.getoutput(cmd).strip()
print(tx_hash)
time1 = time.time()
print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time1)))

# get receipt
while True:
    time.sleep(1)
    cmd = "cldi -c default get receipt {}".format(tx_hash)
    result = subprocess.getoutput(cmd)
    if not result.__contains__("Error"):
        receipt = json.loads(result)
        print(receipt)
        time2 = time.time()
        print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time2)))
        break

# query from doris
# 打开数据库连接
doris_host="doriscluster-sample-storageclass1-fe-internal.{}.svc.cluster.local".format(os.getenv("NAMESPACE"))
db = pymysql.connect(host=doris_host,
                     port=9030,
                     user='root',
                     password='',
                     database='citacloud')
 
# 使用 cursor() 方法创建一个游标对象 cursor
cursor = db.cursor()

# 使用 execute()  方法执行 SQL 查询 
hash = "\"{}\"".format(tx_hash[2:])

while True:
    time.sleep(1)
    cursor.execute("SELECT * from receipts where tx_hash={}".format(hash))
    results = cursor.fetchall()
    if results:
        print(results)
        time3 = time.time()
        print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time3)))
        break

db.close()

print("Done")
print("finalize latency: ", time2 - time1)
print("export latency: ", time3 - time2)
