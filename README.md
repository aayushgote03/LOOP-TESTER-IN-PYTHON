Of course\! Here's an interactive and user-friendly guide for your Loop Analyser tool in Markdown format.

-----

# 🚀 Loop Performance Analyser 🚀

Welcome\! This tool automates the process of finding the optimal **tile size** and **loop order** for a given C code, helping you boost its performance through loop tiling. It generates various tiled versions of your code, compiles them, and benchmarks their execution cycles to find the champion configuration. 🏆

-----

## ⚙️ Step 1: Generate Tiled Code Combinations

The first step is to create all the possible tiled versions of your source code. The `tile_generator.py` script handles this by iterating through different tile sizes and loop permutations.

  * **What it does:** Reads a base C file (e.g., `test.c`) and generates 640 unique, tiled versions.
  * **Tile Sizes Used:** It currently tests sizes from the set `{8, 16, 32, 64, 128, 256, 512}`.
  * **Output:** All generated C files are saved in a new folder named `tiled_c_outputs`.

To run the generator, open your terminal and execute the following command:

```bash
python tile_generator.py
```

✅ **Success\!** You should now have a `tiled_c_outputs` directory filled with C files, each representing a unique tiling strategy.

> **💡 Pro Tip:** You can customize the tile sizes and other parameters by editing the `find_order.py` file.

-----

## 📊 Step 2: Compile, Run, and Analyse

Now that you have all the code variations, it's time to see which one performs best. The `looprun2.py` script compiles each file, measures its performance, and compares it against a highly optimized baseline.

  * **What it does:**
    1.  Compiles every single `.c` file inside the `tiled_c_outputs` folder.
    2.  Measures the execution cycles for each compiled program.
    3.  Compares these cycles to a baseline version of `test.c` compiled with Polly's `-O3` flag for a fair comparison.
  * **Output:** The results are neatly organized and saved into a CSV file for easy analysis.

To start the analysis, run this command in your terminal:

```bash
python looprun2.py
```

🎉 **All Done\!** A CSV results file has been generated. You can now open this file in any spreadsheet program (like Excel, Google Sheets, or LibreOffice Calc) to sort and find the combination of tile size and loop order that resulted in the lowest execution cycles—the fastest version of your code\!
