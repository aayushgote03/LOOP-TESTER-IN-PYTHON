import os
import re
# Assuming find_order.py with generate_all_combinations() is in the same directory
from find_order import generate_all_combinations

def store_c_code_lines(c_file):
    """Read and store each non-empty line of the C code in a list."""
    try:
        with open(c_file, 'r') as f:
            code_lines = [line.rstrip('\n') for line in f if line.strip() != ""]
        return code_lines
    except FileNotFoundError:
        print(f"Error: The file '{c_file}' was not found.")
        return None

def add_cycle_counter_logic(code_lines):
    """
    Injects the rdtsc function and main() variables for cycle counting.
    This prepares the code before tiling is applied.
    """
    # C code for the helper function
    helper_func_c_code = [
        "",
        "// On x86/x64, we can use inline assembly to get the cycle count.",
        "// This function includes a serializing instruction (`cpuid`) to prevent",
        "// out-of-order execution from affecting the measurement.",
        "static inline unsigned long long rdtsc_serialized(void) {",
        "    unsigned int low, high;",
        "    // cpuid is a serializing instruction that forces the CPU",
        "    // to complete all pending operations before proceeding.",
        '    asm volatile ("cpuid" : : : "%rax", "%rbx", "%rcx", "%rdx");',
        "    // rdtsc reads the time-stamp counter into edx:eax.",
        '    asm volatile ("rdtsc" : "=a" (low), "=d" (high));',
        "    return ((unsigned long long)high << 32) | low;",
        "}",
        ""
    ]
    
    modified_lines = []
    main_vars_added = False
    
    # Find the include line to insert the helper function after it
    include_idx = -1
    for i, line in enumerate(code_lines):
        if "#include <stdio.h>" in line:
            include_idx = i
            break
            
    if include_idx != -1:
        modified_lines.extend(code_lines[:include_idx + 1])
        modified_lines.extend(helper_func_c_code)
        modified_lines.extend(code_lines[include_idx + 1:])
    else: # Fallback if no include is found
        modified_lines = helper_func_c_code + code_lines

    # Now find main to insert variable declarations
    final_lines = []
    for line in modified_lines:
        final_lines.append(line)
        if "int main" in line and not main_vars_added:
            final_lines.append("    unsigned long long start_cycles, end_cycles;")
            main_vars_added = True
            
    return final_lines

def find_3d_loop_nest(code_lines, nest_number=1):
    """
    Find the start and end of the N-th 3-level nested for-loop inside main.
    Returns (start_idx, end_idx, loop_vars) or (None, None, None) if not found.
    """
    in_main = False
    brace_depth = 0
    loop_stack = []
    start_idx = None
    end_idx = None
    loop_vars = []
    found_nests = 0

    for idx, line in enumerate(code_lines):
        if "int main" in line:
            in_main = True

        if not in_main:
            continue

        # Track brace depth relative to main's entry
        if in_main and "{" in line and brace_depth == 0:
            brace_depth = 1 # Entered main
            continue

        brace_depth += line.count("{")
        brace_depth -= line.count("}")

        stripped = line.strip()
        if stripped.startswith("for ("):
            # A simple regex to be more robust against 'int i = 0' vs 'int i=0'
            match = re.search(r'for\s*\(\s*int\s+([a-zA-Z0-9_]+)', stripped)
            if match:
                var = match.group(1)
                loop_stack.append((idx, var))
                if len(loop_stack) == 1:
                    start_idx = idx
                if len(loop_stack) == 3:
                    loop_vars = [v for _, v in loop_stack]
                    found_nests += 1
                    if found_nests == nest_number:
                        # Find the end of this 3-level nest
                        inner_loop_line = loop_stack[-1][0]
                        nest_brace_level = 0
                        in_nest = False
                        for j in range(inner_loop_line, len(code_lines)):
                            if "{" in code_lines[j]:
                                if not in_nest: in_nest = True
                                nest_brace_level += code_lines[j].count("{")
                            if "}" in code_lines[j]:
                                nest_brace_level -= code_lines[j].count("}")
                            if in_nest and nest_brace_level == 0:
                                end_idx = j + 2 # Point to the last } of the outer loop
                                return start_idx, end_idx, loop_vars
                    # Reset after finding a complete nest to search for the next one
                    loop_stack = []; start_idx = None; end_idx = None; loop_vars = []
        
        # If we exit main, stop searching
        if brace_depth <= 0 and in_main:
            break

    return None, None, None


def add_tiling_to_code_lines(code_lines, tile_size, loop_order):
    """
    Replace only the second 3D loop nest (processing phase) with a tiled version,
    and wrap it with cycle counting calls.
    """
    # Find the second 3D loop nest (the processing one)
    start_idx, end_idx, loop_vars = find_3d_loop_nest(code_lines, nest_number=2)
    
    if start_idx is None or end_idx is None or len(loop_vars) != 3:
        print("Warning: Could not find the second 3-level deep for-loop in main(). Tiling not applied.")
        return code_lines

    var_map = {loop_vars[0]: 'i', loop_vars[1]: 'j', loop_vars[2]: 'k'}
    tile_vars = {'i': 'i_t', 'j': 'j_t', 'k': 'k_t'}

    # Detect dimension macros from code_lines above main
    macro_map = {}
    for line in code_lines:
        if "#define" in line:
            parts = line.split()
            if len(parts) >= 3:
                macro = parts[1]
                if macro.lower().startswith("depth"): macro_map['i'] = macro
                elif macro.lower().startswith("height"): macro_map['j'] = macro
                elif macro.lower().startswith("width"): macro_map['k'] = macro
        if "int main" in line:
            break

    dim_vars = {
        'i': macro_map.get('i', 'DEPTH'),
        'j': macro_map.get('j', 'HEIGHT'),
        'k': macro_map.get('k', 'WIDTH')
    }

    new_lines = []
    new_lines.extend(code_lines[:start_idx])
    
    # --- Add cycle counting and tiling ---
    new_lines.append("    // --- Start cycle measurement ---")
    new_lines.append("    start_cycles = rdtsc_serialized();")
    new_lines.append("")
    new_lines.append("    // --- Added tiling example ---")
    new_lines.append(f"    #define TILE_SIZE {tile_size}")
    indent = "    "

    for var_name in loop_order:
        is_tile_loop = var_name.endswith('_t')
        base_var = var_name[0]
        if is_tile_loop:
            new_lines.append(f"{indent}for (int {var_name} = 0; {var_name} < {dim_vars[base_var]}; {var_name} += TILE_SIZE) {{")
        else:
            tile_var = tile_vars[base_var]
            new_lines.append(f"{indent}for (int {base_var} = {tile_var}; {base_var} < {tile_var} + TILE_SIZE && {base_var} < {dim_vars[base_var]}; {base_var}++) {{")
        indent += "    "

    # Find the start of the innermost loop body from the original code
    innermost_loop_start_line, innermost_loop_end_line = -1, -1
    brace_count = 0
    in_body = False
    for i in range(start_idx, end_idx + 1):
        if "for" in code_lines[i] and var_map[loop_vars[2]] in code_lines[i]:
            innermost_loop_start_line = i
            break

    if innermost_loop_start_line != -1:
        for i in range(innermost_loop_start_line, end_idx + 1):
            if "{" in code_lines[i]:
                if not in_body:
                    in_body = True
                    innermost_loop_start_line = i + 1
                brace_count += 1
            if "}" in code_lines[i]:
                brace_count -= 1
                if in_body and brace_count == 0:
                    innermost_loop_end_line = i
                    break
    
    # Copy the body of the innermost loop
    if innermost_loop_start_line != -1 and innermost_loop_end_line != -1:
        body_indent = indent
        for i in range(innermost_loop_start_line, innermost_loop_end_line):
            orig_line = code_lines[i]
            if not orig_line.strip(): continue
            line = orig_line
            # Replace original loop variables with standardized i, j, k
            for orig, new in var_map.items():
                line = re.sub(rf'\b{orig}\b', new, line)
            new_lines.append(body_indent + line.lstrip())

    # Close all the loops
    for _ in range(len(loop_order)):
        indent = indent[:-4]
        new_lines.append(f"{indent}}}")
    new_lines.append("    // --- End tiling example ---")
    new_lines.append("")
    new_lines.append("    // --- End cycle measurement ---")
    new_lines.append("    end_cycles = rdtsc_serialized();")
    new_lines.append('    printf("Execution cycles for tiled loop: %llu\\n", end_cycles - start_cycles);')

    # Append the rest of the code, skipping the original loop's lines
    new_lines.extend(code_lines[end_idx + 1:])
    return new_lines


def write_c_code_from_lines(code_lines, output_file):
    """Write the stored code lines to a new C file."""
    with open(output_file, 'w') as f:
        for line in code_lines:
            f.write(line + '\n')
    print(f"Successfully wrote tiled code to {output_file}")


if __name__ == "__main__":
    c_file = "test.c" # The name of your input C file
    code_lines = store_c_code_lines(c_file)

    if code_lines:
        output_folder = "tiled_c_outputs"
        os.makedirs(output_folder, exist_ok=True)

        # First, add the generic cycle counter definitions to the code
        base_code_with_counters = add_cycle_counter_logic(code_lines)
        
        # Assume generate_all_combinations exists and returns a list of dicts
        # e.g., [{'order': ['i_t', 'j_t', 'k_t', 'i', 'j', 'k'], 'tiles': {'i': 8, 'j': 8, 'k': 8}}]
        combinations = generate_all_combinations()
        
        for idx, combo in enumerate(combinations, 1):
            # Start with a fresh copy of the code that already has the counter logic
            fresh_code_lines = list(base_code_with_counters)
            
            loop_order = combo['order']
            tile_size = combo['tiles']['i'] # Assuming uniform tile size for simplicity
            
            # Apply tiling and add the start/stop measurement calls around the loop
            tiled_code_lines = add_tiling_to_code_lines(fresh_code_lines, tile_size, loop_order)
            
            output_file = os.path.join(output_folder, f"tiled_output_{idx}.c")
            write_c_code_from_lines(tiled_code_lines, output_file)