import psutil
import game

def get_usage(bars=50):
    cpu_percent = psutil.cpu_percent()
    if cpu_percent == 0:
        cpu_percent = game.CPU_USAGE

    cpu_bar = "█" * int((cpu_percent/100) * bars) + "-" * (bars - int((cpu_percent/100) * bars)) # Turns percent into bar visual
    mem_percent = psutil.virtual_memory().percent

    mem_bar = "█" * int((mem_percent/100) * bars) + "-" * (bars - int((mem_percent/100) * bars))
    return cpu_percent, mem_percent, cpu_bar, mem_bar