from dataclasses import dataclass
from typing import List, Optional
import matplotlib.pyplot as plt
import pandas as pd

# -------------------- Data Classes --------------------

@dataclass
class Job:
    id: int
    time: int
    size: int
    start_time: Optional[int] = None
    end_time: Optional[int] = None
    waiting_time: Optional[int] = None

@dataclass
class MemoryBlock:
    id: int
    size: int
    allocated: bool = False
    job_id: Optional[int] = None

# -------------------- Allocation Strategies --------------------

def first_fit_allocate(job: Job, memory: List[MemoryBlock]) -> Optional[int]:
    for block in memory:
        if not block.allocated and block.size >= job.size:
            block.allocated = True
            block.job_id = job.id
            return block.id
    return None

def best_fit_allocate(job: Job, memory: List[MemoryBlock]) -> Optional[int]:
    best_block = None
    for block in memory:
        if not block.allocated and block.size >= job.size:
            if best_block is None or block.size < best_block.size:
                best_block = block
    if best_block:
        best_block.allocated = True
        best_block.job_id = job.id
        return best_block.id
    return None

def worst_fit_allocate(job: Job, memory: List[MemoryBlock]) -> Optional[int]:
    worst_block = None
    for block in memory:
        if not block.allocated and block.size >= job.size:
            if worst_block is None or block.size > worst_block.size:
                worst_block = block
    if worst_block:
        worst_block.allocated = True
        worst_block.job_id = job.id
        return worst_block.id
    return None

# -------------------- Simulation with Safety --------------------

def simulate_allocation_with_safety(strategy_func, jobs: List[Job], memory_template: List[MemoryBlock]):
    time = 0
    queue = jobs.copy()
    memory = [MemoryBlock(b.id, b.size) for b in memory_template]
    running_jobs = []
    finished_jobs = []

    # 🔄 snapshot of memory after last successful allocation
    memory_snapshot = []

    while queue or running_jobs:
        for j in running_jobs[:]:
            if j.end_time == time:
                for block in memory:
                    if block.job_id == j.id:
                        block.allocated = False
                        block.job_id = None
                running_jobs.remove(j)
                finished_jobs.append(j)

        progress_made = False

        for job in queue[:]:
            block_id = strategy_func(job, memory)
            if block_id is not None:
                job.start_time = time
                job.end_time = time + job.time
                job.waiting_time = time
                running_jobs.append(job)
                queue.remove(job)
                progress_made = True

        # Save memory state after any allocation
        if progress_made:
            memory_snapshot = [MemoryBlock(b.id, b.size, b.allocated, b.job_id) for b in memory]

        if time % 100 == 0:
            print(f"Time: {time}, Jobs waiting: {len(queue)}, Running: {len(running_jobs)}, Finished: {len(finished_jobs)}")

        if not running_jobs and not progress_made and queue:
            print(f"\nSimulation stopped early at time {time}. Remaining job(s) cannot be allocated due to memory limits.")
            break

        time += 1

    return finished_jobs, time, queue, memory_snapshot

# -------------------- Fragmentation Calculation --------------------

def compute_fragmentation(memory: List[MemoryBlock], jobs: List[Job]) -> int:
    return sum(
        block.size - next((job.size for job in jobs if job.id == block.job_id), 0)
        for block in memory if block.allocated
    )

# -------------------- Strategy Runner --------------------

def run_strategy(name: str, strategy_func, jobs: List[Job], memory_template: List[MemoryBlock]):
    print(f"\n🔧 Running {name} Allocation Simulation...")
    result, total_time, remaining, memory_state = simulate_allocation_with_safety(strategy_func, jobs, memory_template)
    job_count = len(result)
    avg_wait = sum(job.waiting_time for job in result) / job_count if job_count > 0 else 0
    frag = compute_fragmentation(memory_state, result)
    return {
        "Strategy": name,
        "Jobs Completed": job_count,
        "Total Time": total_time,
        "Avg Waiting Time": round(avg_wait, 2),
        "Unallocated Jobs": [job.id for job in remaining],
        "Internal Fragmentation": frag
    }

# -------------------- Input Data --------------------

jobs = [
    Job(1, 5, 5760), Job(2, 4, 4190), Job(3, 8, 3290), Job(4, 2, 2030),
    Job(5, 2, 2550), Job(6, 6, 6990), Job(7, 8, 8940), Job(8, 10, 740),
    Job(9, 7, 3930), Job(10, 6, 6890), Job(11, 5, 6580), Job(12, 8, 3820),
    Job(13, 9, 9140), Job(14, 10, 420), Job(15, 10, 220), Job(16, 7, 7540),
    Job(17, 3, 3210), Job(18, 1, 1380), Job(19, 9, 9850), Job(20, 3, 3610),
    Job(21, 7, 7540), Job(22, 2, 2710), Job(23, 8, 8390), Job(24, 5, 5950),
    Job(25, 10, 760)
]

memory_template = [
    MemoryBlock(1, 9500), MemoryBlock(2, 7000), MemoryBlock(3, 4500),
    MemoryBlock(4, 8500), MemoryBlock(5, 3000), MemoryBlock(6, 9000),
    MemoryBlock(7, 1000), MemoryBlock(8, 5500), MemoryBlock(9, 1500),
    MemoryBlock(10, 500)
]

# -------------------- Main Execution --------------------

if __name__ == "__main__":
    results = [
        run_strategy("First-Fit", first_fit_allocate, jobs, memory_template),
        run_strategy("Best-Fit", best_fit_allocate, jobs, memory_template),
        run_strategy("Worst-Fit", worst_fit_allocate, jobs, memory_template)
    ]

    df = pd.DataFrame(results)
    print("\n Strategy Comparison Table:\n")
    print(df.to_string(index=False))

    # -------------------- Comparison Graph --------------------
    strategies = [res["Strategy"] for res in results]
    jobs_completed = [res["Jobs Completed"] for res in results]
    avg_waiting_times = [res["Avg Waiting Time"] for res in results]
    fragmentations = [res["Internal Fragmentation"] for res in results]
    simulation_times = [res["Total Time"] for res in results]

    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Comparison of Memory Allocation Strategies', fontsize=16)

    axs[0, 0].bar(strategies, jobs_completed, color='skyblue')
    axs[0, 0].set_title("Jobs Completed")
    axs[0, 0].set_ylabel("Count")
    axs[0, 0].grid(True)

    axs[0, 1].bar(strategies, avg_waiting_times, color='lightcoral')
    axs[0, 1].set_title("Average Waiting Time")
    axs[0, 1].set_ylabel("Time Units")
    axs[0, 1].grid(True)

    bars = axs[1, 0].bar(strategies, fragmentations, color='mediumseagreen')
    axs[1, 0].set_title("Internal Fragmentation")
    axs[1, 0].set_ylabel("Unused Units")
    axs[1, 0].grid(True)
    axs[1, 0].bar_label(bars)


    axs[1, 1].bar(strategies, simulation_times, color='gold')
    axs[1, 1].set_title("Total Simulation Time")
    axs[1, 1].set_ylabel("Time Units")
    axs[1, 1].grid(True)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()
