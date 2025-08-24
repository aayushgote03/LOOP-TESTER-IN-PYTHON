import os
import re
import itertools

def generate_tiled_combinations(
    outer_dims=['t'],
    spatial_dims=['i', 'j'],
    tile_sizes=[32, 64]
):
    """
    Generates loop orders where outer_dims are not tiled, and spatial_dims are.
    Example output order: ['t', 'i_t', 'j_t', 'i', 'j']
    """
    combinations = []
    
    # Get all permutations for the order of tile loops (e.g., (i_t, j_t) or (j_t, i_t))
    tile_loop_perms = list(itertools.permutations([f"{d}_t" for d in spatial_dims]))
    
    # Get all permutations for the order of point loops (e.g., (i, j) or (j, i))
    point_loop_perms = list(itertools.permutations(spatial_dims))

    # For every combination of tile and point loop orders...
    for tile_perm in tile_loop_perms:
        for point_perm in point_loop_perms:
            # The final order is always outer loops + tile loops + point loops
            final_order = list(outer_dims) + list(tile_perm) + list(point_perm)
            
            for ts in tile_sizes:
                # Tile sizes only apply to spatial dimensions
                tiles = {d: ts for d in spatial_dims}
                combinations.append({
                    'order': final_order,
                    'tiles': tiles
                })
    return combinations

def store_c_code_lines(c_file):
    """Read and store each line of the C code in a list."""
    try:
        with open(c_file, 'r') as f:
            return [line.rstrip('\n') for line in f]
    except FileNotFoundError:
        print(f"Error: The file '{c_file}' was not found.")
        return None

def find_scop_region(code_lines):
    """Find the start and end line indices of the #pragma scop region."""
    start_idx, end_idx = -1, -1
    for i, line in enumerate(code_lines):
        if "#pragma scop" in line:
            start_idx = i
        elif "#pragma endscop" in line:
            end_idx = i
            break
    if start_idx != -1 and end_idx != -1:
        return start_idx, end_idx
    return None, None

def parse_loops_in_scop(scop_lines):
    """Parses for-loops inside a scop region to extract their properties."""
    loop_pattern = re.compile(
        r"for\s*\(\s*.*?\s*(\w+)\s*=\s*([^;]+);\s*\1\s*([<=]+)\s*([^;]+);\s*.*?\s*\)"
    )
    loops, body_start_line = [], 0
    for i, line in enumerate(scop_lines):
        match = loop_pattern.search(line)
        if match:
            loops.append({
                "var": match.group(1), "start": match.group(2).strip(),
                "op": match.group(3), "bound": match.group(4).strip(),
            })
            body_start_line = i + 1
    body_lines = [line for line in scop_lines[body_start_line:] if line.strip() and "}" not in line]
    return loops, body_lines

def apply_tiling_to_scop(code_lines, combo):
    """Replaces the #pragma scop region with a tiled and reordered version."""
    start_idx, end_idx = find_scop_region(code_lines)
    if start_idx is None:
        print("Warning: #pragma scop region not found.")
        return code_lines

    scop_lines = code_lines[start_idx + 1: end_idx]
    original_loops, body_lines = parse_loops_in_scop(scop_lines)
    if not original_loops:
        print("Warning: No loops found in scop region.")
        return code_lines

    loop_map = {loop['var']: loop for loop in original_loops}
    loop_order = combo['order']
    tile_size = next(iter(combo['tiles'].values())) # Use one uniform tile size

    new_scop_lines, indent = [], "    "
    
    for var_name in loop_order:
        base_var = var_name.replace('_t', '')
        if base_var not in loop_map: continue
        
        orig_loop = loop_map[base_var]
        start, op, bound = orig_loop['start'], orig_loop['op'], orig_loop['bound']
        
        if var_name.endswith('_t'):
            # Case 1: This is a tile loop (e.g., i_t)
            line = f"{indent}for (int {var_name} = {start}; {var_name} {op} {bound}; {var_name} += {tile_size}) {{"
        else:
            tile_var = f"{base_var}_t"
            if tile_var in loop_order:
                # Case 2: This is a tiled point loop (e.g., i, and i_t exists)
                condition = f"{base_var} < {tile_var} + {tile_size} && {base_var} {op} {bound}"
                line = f"{indent}for (int {base_var} = {tile_var}; {condition}; {base_var}++) {{"
            else:
                # Case 3: This is a regular, non-tiled loop (e.g., t)
                line = f"{indent}for (int {base_var} = {start}; {base_var} {op} {bound}; {base_var}++) {{"
        
        new_scop_lines.append(line)
        indent += "    "
        
    for line in body_lines: new_scop_lines.append(indent + line.strip())
    for _ in range(len(loop_order)):
        indent = indent[:-4]
        new_scop_lines.append(f"{indent}}}")

    return code_lines[:start_idx + 1] + new_scop_lines + code_lines[end_idx:]

def write_c_code_from_lines(code_lines, output_file):
    """Write the stored code lines to a new C file."""
    with open(output_file, 'w') as f:
        f.write('\n'.join(code_lines))
    print(f"Successfully wrote tiled code to {output_file}")

if __name__ == "__main__":
    c_file = "../stencils/seidel-2d/seidel-2d.c"
    code_lines = store_c_code_lines(c_file)

    if code_lines:
        output_folder = "tiled_c_outputs"
        os.makedirs(output_folder, exist_ok=True)

        # Define which loops are outer/temporal and which are inner/spatial
        combinations = generate_tiled_combinations(
            outer_dims=['t'],
            spatial_dims=['i', 'j'],
            tile_sizes=[64]
        )
        
        print(f"Found {len(combinations)} valid tiling combinations.")
        
        # This will now generate files like tiled_seidel_t_it_jt_i_j_64.c
        for combo in combinations:
            fresh_code_lines = list(code_lines)
            tiled_code_lines = apply_tiling_to_scop(fresh_code_lines, combo)
            
            order_str = "_".join(combo['order'])
            ts = next(iter(combo['tiles'].values()))
            output_file = os.path.join(output_folder, f"tiled_seidel_{order_str}_{ts}.c")
            write_c_code_from_lines(tiled_code_lines, output_file)