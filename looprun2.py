import os
import subprocess
import time
import csv
import sys
import re
from find_order import generate_all_combinations

# Helper function to write code lines to a file
def write_c_code_from_lines(code_lines, output_file):
    """Write the stored code lines to a new C file."""
    with open(output_file, 'w') as f:
        for line in code_lines:
            f.write(line + '\n')

# Helper function to find a loop nest (re-used from previous script)
def find_3d_loop_nest(code_lines, nest_number=1):
    """
    Finds the start and end line index of the N-th 3-level nested for-loop.
    Returns (start_idx, end_idx) or (None, None).
    """
    in_main = False
    loop_stack = []
    found_nests = 0
    start_idx = -1

    for idx, line in enumerate(code_lines):
        if "int main" in line:
            in_main = True
        if not in_main:
            continue

        stripped = line.strip()
        if stripped.startswith("for ("):
            if not loop_stack:
                start_idx = idx
            loop_stack.append(idx)

            if len(loop_stack) == 3:
                found_nests += 1
                if found_nests == nest_number:
                    # Find the end of the entire loop block
                    brace_level = 0
                    in_block = False
                    for j in range(start_idx, len(code_lines)):
                        if "{" in code_lines[j]:
                            in_block = True
                            brace_level += code_lines[j].count("{")
                        if "}" in code_lines[j]:
                            brace_level -= code_lines[j].count("}")
                        if in_block and brace_level == 0:
                            return start_idx, j # Return start and end indices
                # Reset for next search
                loop_stack = []
                start_idx = -1

    return None, None

def add_timing_wrapper_to_loop(code_lines, nest_number=2):
    """
    Finds the Nth 3D loop nest and wraps it with timing calls.
    Does NOT replace the loop, only wraps it. Used for the baseline test.c.
    """
    start_idx, end_idx = find_3d_loop_nest(code_lines, nest_number=nest_number)
    if start_idx is None:
        print("Warning: Could not find loop to wrap in baseline code.")
        return code_lines

    new_lines = []
    new_lines.extend(code_lines[:start_idx])
    # Add start timer
    new_lines.append("    // --- Start cycle measurement ---")
    new_lines.append("    start_cycles = rdtsc_serialized();")
    # Add the original loop block
    new_lines.extend(code_lines[start_idx : end_idx + 1])
    # Add end timer and printf
    new_lines.append("    // --- End cycle measurement ---")
    new_lines.append("    end_cycles = rdtsc_serialized();")
    new_lines.append('    printf("Execution cycles for tiled loop: %llu\\n", end_cycles - start_cycles);')
    # Add the rest of the code
    new_lines.extend(code_lines[end_idx + 1:])
    return new_lines


def compile_c_file(c_file, exe_file):
    """Compile a C file with clang -O3, return True if success."""
    try:
        compile_cmd = ["clang", c_file, "-O3", "-march=native", "-funroll-loops", "-o", exe_file]
        subprocess.run(compile_cmd, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Compilation failed for {c_file}:\n{e.stderr}")
        return False

def run_and_get_stats(exe_file):
    """
    Run an executable, measure time, and capture the cycle count from stdout.
    Returns a dictionary with all statistics.
    """
    stats = {
        "user_time": None, "sys_time": None, "real_time": None,
        "cycles": None, "ok": False
    }
    try:
        start_time = time.time()
        process = subprocess.Popen([exe_file],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True)
        pid, status, usage = os.wait4(process.pid, 0)
        end_time = time.time()
        stdout, stderr = process.communicate()

        stats["real_time"] = end_time - start_time
        stats["user_time"] = usage.ru_utime
        stats["sys_time"] = usage.ru_stime
        stats["ok"] = True
        
        match = re.search(r'Execution cycles for tiled loop:\s*(\d+)', stdout)
        if match:
            stats["cycles"] = int(match.group(1))
        else:
            stats["cycles"] = "Parse Error"
            if stderr:
                print(f"⚠️  Runtime stderr for {exe_file}:\n{stderr}")
    except (ChildProcessError, FileNotFoundError):
        return stats
    return stats

if __name__ == "__main__":
    # This requires the other python script you provided that creates the C files.
    # We assume it has a function add_cycle_counter_logic(code_lines).
    try:
        from tile_generator import add_cycle_counter_logic, store_c_code_lines
    except ImportError:
        print("❌ Error: Make sure the script that generates C files is named 'tile_generator.py'")
        print("and contains the 'add_cycle_counter_logic' and 'store_c_code_lines' functions.")
        sys.exit(1)

    output_folder = "tiled_c_outputs"
    if not os.path.exists(output_folder):
        print(f"Error: Output folder '{output_folder}' not found. Please run the generator script first.")
        sys.exit(1)

    # --- Step 1: Instrument and run baseline test.c ---
    print("🏁 Instrumenting and running baseline test.c...")
    
    # Read the original test.c
    original_test_c_path = "test.c"
    base_code_lines = store_c_code_lines(original_test_c_path)
    if not base_code_lines:
        print(f"❌ Could not read {original_test_c_path}. Exiting.")
        sys.exit(1)

    # 1a. Add the rdtsc function and variables
    instrumented_code = add_cycle_counter_logic(base_code_lines)
    # 1b. Wrap the main processing loop with timing calls
    timed_code = add_timing_wrapper_to_loop(instrumented_code, nest_number=2)

    # 1c. Write to a temporary file, compile, and run
    timed_test_c_path = "test_timed.c"
    test_exe = "./test_base"
    write_c_code_from_lines(timed_code, timed_test_c_path)

    if not compile_c_file(timed_test_c_path, test_exe):
        print("❌ Baseline test.c failed to compile. Exiting.")
        sys.exit(1)

    base_stats = run_and_get_stats(test_exe)
    os.remove(timed_test_c_path) # Clean up temporary file

    if not base_stats["ok"] or base_stats["real_time"] is None:
        print("❌ Baseline test.c execution failed. Exiting.")
        sys.exit(1)

    baseline_time = base_stats["real_time"]
    print(f"📊 Baseline Real Time: {baseline_time:.4f}s")
    print(f"📊 Baseline Cycles: {base_stats.get('cycles', 'N/A')}")

    # --- Step 2: Prepare CSV file ---
    csv_file = os.path.join(output_folder, "timing_results_detailed.csv")
    csv_fieldnames = ["Index", "Tile Size", "Loop Order", "User Time (s)", "System Time (s)", "Real Time (s)", "Execution Cycles"]
    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fieldnames)
        writer.writeheader()

    # --- Step 3: Run tiled codes ---
    combinations = generate_all_combinations()
    for idx, combo in enumerate(combinations, 1):
        c_file = os.path.join(output_folder, f"tiled_output_{idx}.c")
        exe_file = os.path.join(output_folder, f"tiled_output_{idx}")
        if not os.path.exists(c_file): continue

        print(f"\n⚙️  Processing Program {idx} (Order: {''.join(combo['order'])}, Tile: {combo['tiles']['i']})...")
        row = {"Index": idx, "Tile Size": combo['tiles']['i'], "Loop Order": "".join(combo['order'])}

        if not compile_c_file(c_file, exe_file):
            row.update({k: "Compile Error" for k in csv_fieldnames if k not in row})
        else:
            stats = run_and_get_stats(exe_file)
            if not stats["ok"]:
                row.update({k: "Runtime Error" for k in csv_fieldnames if k not in row})
            elif stats["real_time"] > baseline_time:
                print(f"⏱️  Exceeded baseline ({stats['real_time']:.4f}s > {baseline_time:.4f}s), marking as such.")
                row.update({"User Time (s)": "Exceeded Baseline", "System Time (s)": "Exceeded Baseline", "Real Time (s)": f'{stats["real_time"]:.6f}', "Execution Cycles": "Exceeded Baseline"})
            else:
                row.update({"User Time (s)": f'{stats["user_time"]:.6f}', "System Time (s)": f'{stats["sys_time"]:.6f}', "Real Time (s)": f'{stats["real_time"]:.6f}', "Execution Cycles": stats["cycles"]})
        
        with open(csv_file, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=csv_fieldnames)
            writer.writerow(row)

        if any(err in str(row.values()) for err in ["Error", "Exceeded"]):
            print(f"❌ Recorded issue for program {idx}")
        else:
            print(f"✅ Recorded result for program {idx} (Cycles: {row['Execution Cycles']})")
    
    print(f"\n📁 All tests complete. Final results saved to {csv_file}")