import subprocess
import os

def run_c_code_and_store_lines(c_file):
    # Read and store each non-empty line of the C code in a list
    with open(c_file, 'r') as f:
        code_lines = [line.rstrip('\n') for line in f if line.strip() != ""]

    # Print the stored lines (optional)
    print("C code lines:")
    for i, line in enumerate(code_lines, 1):
        print(f"{i}: {line}")

    # Get the base name without extension
    base = os.path.splitext(os.path.basename(c_file))[0]
    executable = f"./{base}"

    # Compile the C code
    compile_cmd = ["gcc", c_file, "-o", base]
    try:
        subprocess.check_call(compile_cmd)
    except subprocess.CalledProcessError:
        print("Compilation failed.")
        return code_lines

    # Run the executable
    try:
        result = subprocess.run([executable], capture_output=True, text=True)
        print("Program output:")
        print(result.stdout)
        if result.stderr:
            print("Program errors:", result.stderr)
    except Exception as e:
        print(f"Error running the program: {e}")

    return code_lines

if __name__ == "__main__":
    c_file = "test.c"  # Use the path to test.c directly
    code_lines = run_c_code_and_store_lines(c_file)