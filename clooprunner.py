import subprocess
import os
from find_order import generate_all_combinations

def store_c_code_lines(c_file):
    """Read and store each non-empty line of the C code in a list."""
    with open(c_file, 'r') as f:
        code_lines = [line.rstrip('\n') for line in f if line.strip() != ""]
    return code_lines

def add_tiling_to_code_lines(code_lines, tile_size, loop_order):
    """
    Insert tiling logic into the code lines for a 3D loop nest.
    The loops are generated in the exact order given by loop_order.
    """
    new_lines = []
    tile_size_defined = False

    # Insert #define TILE_SIZE before main
    for idx, line in enumerate(code_lines):
        if not tile_size_defined and "int main()" in line:
            new_lines.append(f"#define TILE_SIZE {tile_size}")
            tile_size_defined = True
        new_lines.append(line)

    code_lines = new_lines
    new_lines = []
    in_main = False
    loop_start_idx = -1
    loop_end_idx = -1
    brace_count = 0

    # Find the start and end of the original 3D loop nest
    for idx, line in enumerate(code_lines):
        if "int main()" in line:
            in_main = True
        if in_main and "for (i =" in line:
            loop_start_idx = idx
            break

    # Find the end of the loop nest (by matching braces)
    if loop_start_idx != -1:
        for idx in range(loop_start_idx, len(code_lines)):
            brace_count += code_lines[idx].count("{")
            brace_count -= code_lines[idx].count("}")
            if brace_count == 0:
                loop_end_idx = idx
                break

    # Prepare loop variable mapping
    tile_vars = {'i': 'i_t', 'j': 'j_t', 'k': 'k_t'}
    dim_vars = {'i': 'DEPTH', 'j': 'HEIGHT', 'k': 'WIDTH'}

    # Helper to generate loop line
    def loop_line(var, indent):
        if var.endswith('_t'):
            base = var[0]
            return f"{indent}for ({var} = 0; {var} < {dim_vars[base]}; {var} += TILE_SIZE) {{"
        else:
            tvar = tile_vars[var]
            return f"{indent}for ({var} = {tvar}; {var} < {tvar} + TILE_SIZE && {var} < {dim_vars[var]}; {var}++) {{"

    if loop_start_idx != -1 and loop_end_idx != -1:
        # Copy lines up to the start of the loop nest
        new_lines.extend(code_lines[:loop_start_idx])
        # Insert tiling loops using TILE_SIZE with required variable names and order
        new_lines.append("    // --- Added tiling example ---")
        new_lines.append(f"    int i_t, j_t, k_t;")
        indent = "    "
        # Open all loops in the order specified
        for var in loop_order:
            new_lines.append(loop_line(var, indent))
            indent += "    "
        # Extract the body of the original innermost loop
        body_indent = indent
        in_body = False
        for orig_line in code_lines[loop_start_idx:loop_end_idx+1]:
            if "for (k =" in orig_line:
                in_body = True
                continue
            if in_body:
                if orig_line.strip() == "}":
                    continue
                new_lines.append(body_indent + orig_line.lstrip())
        # Close all opened braces (reverse order)
        for i in range(len(loop_order)):
            indent = indent[:-4]
            new_lines.append(f"{indent}}}")
        new_lines.append("    // --- End tiling example ---")
        # Copy the rest of the code after the loop nest
        new_lines.extend(code_lines[loop_end_idx+1:])
    else:
        # If no loop found, just return the original code
        new_lines = code_lines

    return new_lines

def write_c_code_from_lines(code_lines, output_file):
    """Write the stored code lines to a new C file."""
    with open(output_file, 'w') as f:
        for line in code_lines:
            f.write(line + '\n')
    print(f"Wrote {len(code_lines)} lines to {output_file}")

if __name__ == "__main__":
    c_file = "test.c"  # Use the path to test.c
    code_lines = store_c_code_lines(c_file)

    # Create output folder if it doesn't exist
    output_folder = "tiled_c_outputs"
    os.makedirs(output_folder, exist_ok=True)

    # Get all combinations from find_order
    combinations = generate_all_combinations()
    for idx, combo in enumerate(combinations, 1):
        loop_order = combo['order']
        tile_size = combo['tiles']['i']  # All tile sizes are the same in this setup
        tiled_code_lines = add_tiling_to_code_lines(code_lines, tile_size, loop_order)
        output_file = os.path.join(output_folder, f"tiled_output_{idx}.c")
        write_c_code_from_lines(tiled_code_lines, output_file)