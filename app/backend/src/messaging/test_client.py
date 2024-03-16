
from RpcClient import RpcClient


rpc = RpcClient()

print(" [x] Requesting fib(30)")
r = rpc.call(10)
print(f" [.] Got {r}")