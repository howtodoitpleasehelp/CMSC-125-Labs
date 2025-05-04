import pandas as pd
import matplotlib.pyplot as plt
from collections import deque

# ------------------ File Reading ------------------
def read_batch_file(filename):
    df = pd.read_csv(filename, sep='\t+', engine='python')
    df.columns = [col.strip() for col in df.columns]
    return df.to_dict('records')

# ------------------ FCFS Scheduling ------------------
def fcfs(processes):
    processes.sort(key=lambda x: x['Arrival'])
    time = 0
    gantt, waiting_times, turnaround_times = [], [], []

    print("\nFCFS Scheduling:")
    for p in processes:
        if time < p['Arrival']:
            time = p['Arrival']
        start_time = time
        waiting = time - p['Arrival']
        time += p['CPU Burst Time']
        turnaround = time - p['Arrival']
        gantt.append((p['Process'], start_time, time))
        waiting_times.append(waiting)
        turnaround_times.append(turnaround)
        print(f"P{p['Process']} | Waiting: {waiting} | Turnaround: {turnaround}")

    print_avg(waiting_times, turnaround_times, gantt)

# ------------------ SJF Scheduling ------------------
def sjf(processes):
    time, gantt, waiting_times, turnaround_times = 0, [], [], []
    ready = []
    processes.sort(key=lambda x: (x['Arrival'], x['CPU Burst Time']))

    print("\nSJF Scheduling:")
    while processes or ready:
        while processes and processes[0]['Arrival'] <= time:
            ready.append(processes.pop(0))
        if ready:
            ready.sort(key=lambda x: x['CPU Burst Time'])
            p = ready.pop(0)
            start_time = time
            waiting = time - p['Arrival']
            time += p['CPU Burst Time']
            turnaround = time - p['Arrival']
            gantt.append((p['Process'], start_time, time))
            waiting_times.append(waiting)
            turnaround_times.append(turnaround)
            print(f"P{p['Process']} | Waiting: {waiting} | Turnaround: {turnaround}")
        else:
            time += 1

    print_avg(waiting_times, turnaround_times, gantt)

# ------------------ SRPT Scheduling ------------------
def srpt(processes):
    time = 0
    gantt = []
    remaining = {p['Process']: p['CPU Burst Time'] for p in processes}
    arrival_dict = {p['Process']: p['Arrival'] for p in processes}
    info = {p['Process']: p for p in processes}
    ready, finished = [], set()
    processes.sort(key=lambda x: x['Arrival'])
    current, last_time = None, 0

    print("\nSRPT Scheduling:")
    while len(finished) < len(remaining):
        for p in processes:
            if p['Arrival'] == time:
                ready.append(p['Process'])

        if current and remaining[current] == 0:
            finished.add(current)
            gantt.append((current, last_time, time))
            current = None

        valid_ready = [pid for pid in ready if pid not in finished and remaining[pid] > 0]

        if valid_ready:
            if not current or current not in valid_ready or remaining[current] > min(remaining[pid] for pid in valid_ready):
                if current and remaining[current] > 0:
                    gantt.append((current, last_time, time))
                current = min(valid_ready, key=lambda pid: remaining[pid])
                last_time = time

        if current:
            remaining[current] -= 1

        time += 1

    waiting_times, turnaround_times = [], []
    for pid in arrival_dict:
        turnaround = time - arrival_dict[pid]
        waiting = turnaround - info[pid]['CPU Burst Time']
        print(f"P{pid} | Waiting: {waiting} | Turnaround: {turnaround}")
        waiting_times.append(waiting)
        turnaround_times.append(turnaround)

    print_avg(waiting_times, turnaround_times, gantt)

# ------------------ Priority Scheduling ------------------
def priority_scheduling(processes):
    time, gantt, waiting_times, turnaround_times = 0, [], [], []
    ready = []
    processes.sort(key=lambda x: (x['Arrival'], x['Priority']))

    print("\nPriority Scheduling:")
    while processes or ready:
        while processes and processes[0]['Arrival'] <= time:
            ready.append(processes.pop(0))
        if ready:
            ready.sort(key=lambda x: x['Priority'])
            p = ready.pop(0)
            start_time = time
            waiting = time - p['Arrival']
            time += p['CPU Burst Time']
            turnaround = time - p['Arrival']
            gantt.append((p['Process'], start_time, time))
            waiting_times.append(waiting)
            turnaround_times.append(turnaround)
            print(f"P{p['Process']} | Waiting: {waiting} | Turnaround: {turnaround}")
        else:
            time += 1

    print_avg(waiting_times, turnaround_times, gantt)

# ------------------ Round Robin Scheduling ------------------
def round_robin(processes, quantum=4):
    queue = deque()
    time = 0
    gantt = []
    remaining = {p['Process']: p['CPU Burst Time'] for p in processes}
    arrival_dict = {p['Process']: p['Arrival'] for p in processes}
    info = {p['Process']: p for p in processes}
    end_time = {}
    completed = set()
    i = 0
    processes.sort(key=lambda x: x['Arrival'])

    print("\nRound Robin Scheduling (Quantum=4):")
    while len(completed) < len(processes):
        while i < len(processes) and processes[i]['Arrival'] <= time:
            queue.append(processes[i]['Process'])
            i += 1

        if not queue:
            time += 1
            continue

        pid = queue.popleft()
        burst = min(quantum, remaining[pid])
        gantt.append((pid, time, time + burst))
        remaining[pid] -= burst
        time += burst

        while i < len(processes) and processes[i]['Arrival'] <= time:
            queue.append(processes[i]['Process'])
            i += 1

        if remaining[pid] > 0:
            queue.append(pid)
        else:
            completed.add(pid)
            end_time[pid] = time

    waiting_times, turnaround_times = [], []
    for pid in arrival_dict:
        turnaround = end_time[pid] - arrival_dict[pid]
        waiting = turnaround - info[pid]['CPU Burst Time']
        print(f"P{pid} | Waiting: {waiting} | Turnaround: {turnaround}")
        waiting_times.append(waiting)
        turnaround_times.append(turnaround)

    print_avg(waiting_times, turnaround_times, gantt)

# ------------------ Helper: Print Averages and Gantt Chart ------------------
def print_avg(waiting_times, turnaround_times, gantt):
    print(f"\nAverage Waiting Time: {sum(waiting_times)/len(waiting_times):.2f}")
    print(f"Average Turnaround Time: {sum(turnaround_times)/len(turnaround_times):.2f}")
    print("\nGantt Chart (Text):")
    for pid, start, end in gantt:
        print(f"| P{pid} ({start}-{end}) ", end="")
    print("|")
    draw_gantt_chart(gantt)

# ------------------ Visual Gantt Chart ------------------
def draw_gantt_chart(gantt, title="Gantt Chart"):
    fig, ax = plt.subplots(figsize=(10, 2))
    y = 1
    cmap = plt.colormaps.get_cmap('tab20')

    for i, (pid, start, end) in enumerate(gantt):
        ax.barh(y, end - start, left=start, height=0.5, align='center',
                color=cmap(i % cmap.N), edgecolor='black')
        ax.text((start + end) / 2, y, f"P{pid}", ha='center', va='center', color='white', fontsize=9)

    ax.set_xlim(0, max(end for _, _, end in gantt) + 1)
    ax.set_ylim(0, 2)
    ax.set_xlabel("Time")
    ax.set_yticks([])
    ax.set_title(title)
    ax.grid(True, axis='x', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()

# ------------------ Main ------------------
def main():
    print("CPU Scheduling Simulator")
    filename = input("Enter batch file name (e.g., batch1.txt): ").strip()
    processes = read_batch_file(filename)

    print("\nChoose Scheduling Algorithm:")
    print("1. FCFS")
    print("2. SJF")
    print("3. SRPT")
    print("4. Priority")
    print("5. Round-robin")
    choice = input("Enter your choice (1–5): ").strip()

    if choice == '1':
        fcfs(processes)
    elif choice == '2':
        sjf(processes)
    elif choice == '3':
        srpt(processes)
    elif choice == '4':
        priority_scheduling(processes)
    elif choice == '5':
        round_robin(processes)
    else:
        print("Invalid choice.")

if __name__ == '__main__':
    main()
