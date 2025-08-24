import itertools

def generate_legal_permutations(pairs):
    """
    Generates all legal interleavings of the given ordered pairs using recursion.
    """
    indices = [0] * len(pairs)
    
    def find_permutations_recursive(current_permutation):
        if len(current_permutation) == len(pairs) * 2:
            yield tuple(current_permutation)
            return
        for i, pair in enumerate(pairs):
            if indices[i] < len(pair):
                element_to_add = pair[indices[i]]
                current_permutation.append(element_to_add)
                indices[i] += 1
                yield from find_permutations_recursive(current_permutation)
                indices[i] -= 1
                current_permutation.pop()
    yield from find_permutations_recursive([])

def generate_all_combinations():
    """
    Generates and returns all legal loop and tile size combinations.
    Returns:
        list: List of combination dictionaries.
    """
    loop_dimension_pairs = [('i_t', 'i'), ('j_t', 'j'), ('k_t', 'k')]
    TILE_SIZES = [8, 16, 32, 64, 128, 256, 512]
    all_legal_orders = list(generate_legal_permutations(loop_dimension_pairs))
    all_combinations = []
    for order in all_legal_orders:
        for size in TILE_SIZES:
            combination = {
                'order': order,
                'tiles': {
                    'i': size,
                    'j': size,
                    'k': size
                }
            }
            all_combinations.append(combination)
    return all_combinations

# Example usage if run directly
if __name__ == "__main__":
    all_combinations = generate_all_combinations()
    total_combinations = len(all_combinations)
    print(f"\nSuccessfully generated and stored {total_combinations} combinations.")
    print("\n--- Example of Data Retrieval ---")
    print("Here are the first 3 stored combinations:")
    for i, combo in enumerate(all_combinations[:3]):
        print(f"  Combination {i+1}:")
        print(f"    Order: {combo['order']}")
        print(f"    Tiles: {combo['tiles']}")
    print("\nHere is a specific combination (e.g., the 100th one):")
    if total_combinations >= 100:
        combo_100 = all_combinations[99]
        print(f"  Combination 100:")
        print(f"    Order: {combo_100['order']}")
        print(f"    Tiles: {combo_100['tiles']}")
