import os
import datetime

def get_system_info():
    info = {
        "hostname": os.uname().nodename,
        "os": os.uname().sysname,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": os.environ.get("USER", "unknown")
    }
    return info

def check_disk_usage(path="/"):
    statvfs = os.statvfs(path)
    total = statvfs.f_frsize * statvfs.f_blocks
    free = statvfs.f_frsize * statvfs.f_bavail
    used = total - free
    percent = (used / total) * 100
    return {
        "total_gb": round(total / (1024**3), 2),
        "used_gb": round(used / (1024**3), 2),
        "free_gb": round(free / (1024**3), 2),
        "percent_used": round(percent, 1)
    }

if __name__ == "__main__":
    print("=== System Info ===")
    for key, value in get_system_info().items():
        print(f"  {key}: {value}")

    print("\n=== Disk Usage ===")
    disk = check_disk_usage()
    print(f"  Total:  {disk['total_gb']} GB")
    print(f"  Used:   {disk['used_gb']} GB ({disk['percent_used']}%)")
    print(f"  Free:   {disk['free_gb']} GB")