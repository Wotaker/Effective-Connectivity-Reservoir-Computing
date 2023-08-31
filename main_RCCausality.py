## Relative imports
from execution.utils import run_RCC

import time
if __name__ == '__main__':
    start = time.time()
    run_RCC()
    end = time.time()
    print(f"[Python] Execution time: {end - start:.4f}")