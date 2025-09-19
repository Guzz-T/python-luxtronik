from threading import RLock

# Share the same lock-objects over all used instances
management_lock = RLock()
hosts_locks = {}

def get_host_lock(host):
    """
    Create a new lock object for a host string if one does not already exist.
    Then return the unique lock object associated with that host.
    """
    # Ensure a dedicated lock is created for each IP.
    with management_lock:
        if not host in hosts_locks:
            hosts_locks[host] = RLock()
        return hosts_locks[host]
