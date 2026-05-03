import psutil
import subprocess
from typing import Dict, Optional

def get_cpu_percent() -> float:
    """Загрузка CPU в % (среднее за 0.5с)"""
    return psutil.cpu_percent(interval=0.5)

def get_ram_info() -> Dict[str, float]:
    """Инфо по оперативке: проценты, использовано/всего в ГБ"""
    mem = psutil.virtual_memory()
    return {
        'percent': mem.percent,
        'used_gb': round(mem.used / 1024**3, 2),
        'total_gb': round(mem.total / 1024**3, 2)
    }

def get_gpu_info() -> Dict[str, Optional[float]]:
    """
    Инфо по NVIDIA GPU через nvidia-smi.
    Возвращает util%, VRAM used/total (MB), temp (°C).
    Если GPU недоступен — поле error.
    """
    result = {
        'util': 0.0, 'mem_used': 0.0, 'mem_total': 0.0,
        'temp': 0.0, 'error': None
    }
    try:
        cmd = [
            'nvidia-smi',
            '--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu',
            '--format=csv,noheader,nounits'
        ]
        res = subprocess.run(
            cmd, capture_output=True, text=True, check=True, timeout=3
        )
        vals = [float(x.strip()) for x in res.stdout.split(',')]
        result.update({
            'util': vals[0],
            'mem_used': vals[1],
            'mem_total': vals[2],
            'temp': vals[3]
        })
    except Exception as e:
        result['error'] = f'GPU недоступен: {type(e).__name__}'
    return result

def get_system_metrics() -> Dict:
    """Собирает все метрики в один словарь для API"""
    return {
        'cpu': get_cpu_percent(),
        'ram': get_ram_info(),
        'gpu': get_gpu_info()
    }

