from threading import RLock

# Share the same lock-objects over all used instances
management_lock = RLock()
hosts_locks = {}

def add_host_to_locks(host):
    # Ensure a dedicated lock is created for each IP.
    with management_lock:
        if not host in hosts_locks:
            hosts_locks[host] = RLock()
