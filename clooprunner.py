import os
import re
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

        brace_depth += line.count("{")
        brace_depth -= line.count("}")

        stripped = line.strip()
        if stripped.startswith("for ("):
            var = stripped.split("for (")[1].split("=")[0].strip().split()[-1]
            loop_stack.append((idx, var))
            if len(loop_stack) == 1:
                start_idx = idx
            if len(loop_stack) == 3:
                nest_brace = 0
                for j in range(idx, len(code_lines)):
                    nest_brace += code_lines[j].count("{")
                    nest_brace -= code_lines[j].count("}")
                    if nest_brace == 0:
                        end_idx = j
                        break
                loop_vars = [v for _, v in loop_stack]
                found_nests += 1
                if found_nests == nest_number:
                    return start_idx, end_idx, loop_vars
                # Reset for next search
                loop_stack = []
                start_idx = None
                end_idx = None
                loop_vars = []
        if brace_depth == 0 and in_main and "main" in code_lines[idx]:
            pass

    return None, None, None

def add_tiling_to_code_lines(code_lines, tile_size, loop_order):
    """
    Replace only the second 3D loop nest (processing phase) with a tiled version.
    """
    # Find the second 3D loop nest
    start_idx, end_idx, loop_vars = find_3d_loop_nest(code_lines, nest_number=2)
    if start_idx is None or end_idx is None or len(loop_vars) != 3:
        print("Warning: No 3-level deep for-loop found in main().")
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
                if macro.lower().startswith("depth") or macro.lower().startswith("z_size"):
                    macro_map['i'] = macro
                elif macro.lower().startswith("height") or macro.lower().startswith("y_size"):
                    macro_map['j'] = macro
                elif macro.lower().startswith("width") or macro.lower().startswith("x_size"):
                    macro_map['k'] = macro
        if "int main" in line:
            break

    if 'i' not in macro_map: macro_map['i'] = 'DEPTH'
    if 'j' not in macro_map: macro_map['j'] = 'HEIGHT'
    if 'k' not in macro_map: macro_map['k'] = 'WIDTH'
    dim_vars = {'i': macro_map['i'], 'j': macro_map['j'], 'k': macro_map['k']}

    new_lines = []
    new_lines.extend(code_lines[:start_idx])
    new_lines.append("    // --- Added tiling example ---")
    new_lines.append(f"    #define TILE_SIZE {tile_size}")
    indent = "    "

    for var_name in loop_order:
        is_tile_loop = var_name.endswith('_t')
        base_var = var_name[0]
        if is_tile_loop:
            new_lines.append(f"{indent}for (int {var_name} = 0; {var_name} < {dim_vars[base_var]}; {var_name} += TILE_SIZE) {{")
            indent += "    "
        else:
            tile_var = tile_vars[base_var]
            new_lines.append(f"{indent}for (int {base_var} = {tile_var}; {base_var} < {tile_var} + TILE_SIZE && {base_var} < {dim_vars[base_var]}; {base_var}++) {{")
            indent += "    "

    loop_level = 0
    innermost_loop_start_line = -1
    for line_num in range(start_idx, end_idx + 1):
        if code_lines[line_num].strip().startswith("for ("):
            loop_level += 1
            if loop_level == 3:
                innermost_loop_start_line = line_num
                break

    if innermost_loop_start_line != -1:
        body_indent = indent
        for i in range(innermost_loop_start_line + 1, end_idx):
            orig_line = code_lines[i]
            if not orig_line.strip(): continue
            line = orig_line
            for orig, new in var_map.items():
                line = re.sub(rf'\b{orig}\b', new, line)
            new_lines.append(body_indent + line.lstrip())

    for _ in range(len(loop_order)):
        indent = indent[:-4]
        new_lines.append(f"{indent}}}")
    new_lines.append("    // --- End tiling example ---")

    # Skip as many closing braces as the original 3D nest had
    rest = code_lines[end_idx+1:]
    braces_skipped = 0
    for line in rest:
        if line.strip() == "}" and braces_skipped < len(loop_vars):
            braces_skipped += 1
            continue
        new_lines.append(line)
    # Ensure the last closing brace for main is present
    if not any(line.strip() == "}" for line in new_lines[-3:]):
        new_lines.append("}")
    return new_lines

def write_c_code_from_lines(code_lines, output_file):
    """Write the stored code lines to a new C file."""
    with open(output_file, 'w') as f:
        for line in code_lines:
            f.write(line + '\n')
    print(f"Successfully wrote tiled code to {output_file}")

if __name__ == "__main__":
    c_file = "test.c"
    code_lines = store_c_code_lines(c_file)

    if code_lines:
        output_folder = "tiled_c_outputs"
        os.makedirs(output_folder, exist_ok=True)

        combinations = generate_all_combinations()
        for idx, combo in enumerate(combinations, 1):
            fresh_code_lines = list(code_lines)
            loop_order = combo['order']
            tile_size = combo['tiles']['i']
            
            tiled_code_lines = add_tiling_to_code_lines(fresh_code_lines, tile_size, loop_order)
            
            output_file = os.path.join(output_folder, f"tiled_output_{idx}.c")
            write_c_code_from_lines(tiled_code_lines, output_file)