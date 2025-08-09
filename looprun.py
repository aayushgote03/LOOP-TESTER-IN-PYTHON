import os
import subprocess
import time
import csv
from find_order import generate_all_combinations

def run_executable_and_time(exe_path):
    """
    Runs an executable and measures its user, system, and real (wall-clock) time.
    Returns (user_time, system_time, real_time).
    """
    try:
        start = time.time()
        process = subprocess.Popen(
            [exe_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        pid, status, resource_usage = os.wait4(process.pid, 0)
        end = time.time()

        user_time = resource_usage.ru_utime
        system_time = resource_usage.ru_stime
        real_time = end - start

        if os.WIFEXITED(status) and os.WEXITSTATUS(status) != 0:
            print(f"Warning: {exe_path} exited with non-zero status {os.WEXITSTATUS(status)}")
        return user_time, system_time, real_time

    except FileNotFoundError:
        print(f"Error: Executable not found at {exe_path}")
        return None, None, None
    except Exception as e:
        print(f"An unexpected error occurred while running {exe_path}: {e}")
        return None, None, None

if __name__ == "__main__":
    output_folder = "tiled_c_outputs"
    if not os.path.exists(output_folder):
        print(f"Error: Output folder '{output_folder}' not found. Please generate the C files first.")
        exit(1)
        
    combinations = generate_all_combinations()
    results = []

    print(f"Found {len(combinations)} combinations to compile and run...")

    for idx, combo in enumerate(combinations, 1):
        c_file = os.path.join(output_folder, f"tiled_output_{idx}.c")
        exe_file = os.path.join(output_folder, f"tiled_output_{idx}")
        
        # --- Compile the C file using clang ---
        compile_cmd = ["clang", c_file, "-o", exe_file]
        try:
            subprocess.run(compile_cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"--- Compilation failed for {c_file} ---")
            print(e.stderr)
            results.append({
                "index": idx,
                "tile_size": combo['tiles']['i'],
                "loop_order": "".join(combo['order']),
                "user_time": "Compilation Failed",
                "sys_time": "Compilation Failed",
                "real_time": "Compilation Failed"
            })
            continue

        # --- Run and time the executable ---
        user_time, sys_time, real_time = run_executable_and_time(exe_file)
        
        print(f"Finished run {idx}: {combo['order']} (Tile: {combo['tiles']['i']}) -> User: {user_time:.4f}s, Sys: {sys_time:.4f}s, Real: {real_time:.4f}s")

        results.append({
            "index": idx,
            "tile_size": combo['tiles']['i'],
            "loop_order": "".join(combo['order']),
            "user_time": user_time,
            "sys_time": sys_time,
            "real_time": real_time
        })

    # --- Write results to CSV ---
    csv_file = os.path.join(output_folder, "timing_results_detailed.csv")
    try:
        with open(csv_file, "w", newline="") as f:
            fieldnames = ["Index", "Tile Size", "Loop Order", "User Time (s)", "System Time (s)", "Real Time (s)"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in results:
                writer.writerow({
                    "Index": row["index"],
                    "Tile Size": row["tile_size"],
                    "Loop Order": row["loop_order"],
                    "User Time (s)": row["user_time"],
                    "System Time (s)": row["sys_time"],
                    "Real Time (s)": row["real_time"]
                })
        print(f"\nTiming results written to {csv_file}")
    except IOError as e:
        print(f"Error writing to CSV file: {e}")

