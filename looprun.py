import os
import subprocess
import time
import csv
import sys
from find_order import generate_all_combinations

def compile_c_file(c_file, exe_file):
    """Compile a C file with clang -O3, return True if success."""
    try:
        compile_cmd = ["clang", c_file, "-O3", "-march=native", "-funroll-loops", "-o", exe_file]
        subprocess.run(compile_cmd, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Compilation failed for {c_file}:\n{e.stderr}")
        return False

def run_with_timing(exe_file):
    """Run an executable and measure real/user/sys times. Returns tuple."""
    start = time.time()
    process = subprocess.Popen([exe_file],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
    try:
        pid, status, usage = os.wait4(process.pid, 0)
        end = time.time()
    except ChildProcessError:
        return None, None, None, False

    real_time = end - start
    user_time = usage.ru_utime
    sys_time = usage.ru_stime

    return user_time, sys_time, real_time, True


if __name__ == "__main__":
    output_folder = "tiled_c_outputs"
    if not os.path.exists(output_folder):
        print(f"Error: Output folder '{output_folder}' not found.")
        sys.exit(1)

    # --- Step 1: baseline test.c ---
    print("🏁 Running baseline test.c...")
    test_c = "test.c"   # in same folder
    test_exe = "./test"
    if not compile_c_file(test_c, test_exe):
        print("❌ Baseline test.c failed. Exiting.")
        sys.exit(1)

    base_user, base_sys, base_real, ok = run_with_timing(test_exe)
    if not ok or base_real is None:
        print("❌ Baseline test.c execution failed. Exiting.")
        sys.exit(1)

    baseline_time = base_real
    print(f"📊 Baseline real time: {baseline_time:.4f}s")

    # --- Step 2: prepare CSV file ---
    csv_file = os.path.join(output_folder, "timing_results_detailed.csv")
    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["Index", "Tile Size", "Loop Order", "User Time (s)", "System Time (s)", "Real Time (s)"]
        )
        writer.writeheader()

    # --- Step 3: run tiled codes and write incrementally ---
    combinations = generate_all_combinations()

    for idx, combo in enumerate(combinations, 1):
        c_file = os.path.join(output_folder, f"tiled_output_{idx}.c")
        exe_file = os.path.join(output_folder, f"tiled_output_{idx}")

        if not os.path.exists(c_file):
            print(f"⚠️ Skipping missing file {c_file}")
            continue

        print(f"\n⚙️ Compiling {c_file} ...")
        if not compile_c_file(c_file, exe_file):
            row = {
                "Index": idx,
                "Tile Size": combo['tiles']['i'],
                "Loop Order": "".join(combo['order']),
                "User Time (s)": "Compile Error",
                "System Time (s)": "Compile Error",
                "Real Time (s)": "Compile Error"
            }
        else:
            print(f"🚀 Running {exe_file} (timeout = {baseline_time:.2f}s)...")
            start = time.time()
            process = subprocess.Popen([exe_file],
                                       stdout=subprocess.DEVNULL,
                                       stderr=subprocess.DEVNULL)

            try:
                pid, status, usage = os.wait4(process.pid, 0)
                end = time.time()
                real_time = end - start

                if real_time > baseline_time:
                    print(f"⏱️ Exceeded baseline ({real_time:.4f}s > {baseline_time:.4f}s), marking No Runtime")
                    row = {
                        "Index": idx,
                        "Tile Size": combo['tiles']['i'],
                        "Loop Order": "".join(combo['order']),
                        "User Time (s)": "No Runtime",
                        "System Time (s)": "No Runtime",
                        "Real Time (s)": "No Runtime"
                    }
                else:
                    row = {
                        "Index": idx,
                        "Tile Size": combo['tiles']['i'],
                        "Loop Order": "".join(combo['order']),
                        "User Time (s)": usage.ru_utime,
                        "System Time (s)": usage.ru_stime,
                        "Real Time (s)": real_time
                    }

            except ChildProcessError:
                process.kill()
                row = {
                    "Index": idx,
                    "Tile Size": combo['tiles']['i'],
                    "Loop Order": "".join(combo['order']),
                    "User Time (s)": "No Runtime",
                    "System Time (s)": "No Runtime",
                    "Real Time (s)": "No Runtime"
                }

        # Append row immediately
        with open(csv_file, "a", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["Index", "Tile Size", "Loop Order", "User Time (s)", "System Time (s)", "Real Time (s)"]
            )
            writer.writerow(row)

        print(f"✅ Recorded result for program {idx}")

    print(f"\n📁 Final timing results saved to {csv_file}")
