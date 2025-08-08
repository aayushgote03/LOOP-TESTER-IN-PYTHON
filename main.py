from find_order import generate_all_combinations

if __name__ == "__main__":
    combinations = generate_all_combinations()
    print(f"Total combinations: {len(combinations)}")
    # Print all combinations
    for i, combo in enumerate(combinations, 1):
        print(f"Combination {i}: {combo}")