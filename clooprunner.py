import subprocess
import os

def store_c_code_lines(c_file):
    """Read and store each non-empty line of the C code in a list."""
    with open(c_file, 'r') as f:
        code_lines = [line.rstrip('\n') for line in f if line.strip() != ""]
    return code_lines

def write_c_code_from_lines(code_lines, output_file):
    """Write the stored code lines to a new C file."""
    with open(output_file, 'w') as f:
        for line in code_lines:
            f.write(line + '\n')
    print(f"Wrote {len(code_lines)} lines to {output_file}")

def run_c_code(c_file):
    """Compile and run the C code, printing its output."""
    base = os.path.splitext(os.path.basename(c_file))[0]
    executable = f"./{base}"

    # Compile the C code
    compile_cmd = ["gcc", c_file, "-o", base]
    try:
        subprocess.check_call(compile_cmd)
    except subprocess.CalledProcessError:
        print("Compilation failed.")
        return

    # Run the executable
    try:
        result = subprocess.run([executable], capture_output=True, text=True)
        print("Program output:")
        print(result.stdout)
        if result.stderr:
            print("Program errors:", result.stderr)
    except Exception as e:
        print(f"Error running the program: {e}")

def run_c_code_and_store_lines(c_file):
    code_lines = store_c_code_lines(c_file)

    # Print the stored lines (optional)
    print("C code lines:")
    for i, line in enumerate(code_lines, 1):
        print(f"{i}: {line}")

    run_c_code(c_file)
    return code_lines

if __name__ == "__main__":
    c_file = "test.c"  # Use the path to test.c
    code_lines = store_c_code_lines(c_file)
    print("Stored C code lines:")
    for i, line in enumerate(code_lines, 1):
        print(f"{i}: {line}")

    # Example: Write the stored lines to a new file
    output_file = "output.c"
    write_c_code_from_lines(code_lines, output_file)