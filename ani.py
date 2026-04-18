import json
import matplotlib.pyplot as plt
import numpy as np

def plot_master_results(json_filepath, path):
    with open(json_filepath, "r") as f:
        data = json.load(f)

    protocol = data["protocol"]
    runs = data["runs"]

    for target_state, results in runs.items():
        # 1. Extract statevector dictionaries
        ideal = results.get("ideal_execution") or {}
        noisy = results.get("noisy_execution") or {}
        real = results.get("real_execution")

        # 2. Aggregate all unique basis state strings for the X-axis
        all_bins = set(ideal.keys()) | set(noisy.keys())
        if real:
            all_bins |= set(real.keys())
        all_bins = sorted(list(all_bins))

        # 3. Map values to bins
        ideal_vals = [ideal.get(b, 0) for b in all_bins]
        noisy_vals = [noisy.get(b, 0) for b in all_bins]

        # 4. Configure dynamic axes
        x = np.arange(len(all_bins))
        fig, ax = plt.subplots(figsize=(10, 6))

        if real:
            width = 0.25
            real_vals = [real.get(b, 0) for b in all_bins]
            ax.bar(x - width, ideal_vals, width, label='Ideal', color='#2ca02c')
            ax.bar(x, noisy_vals, width, label='Noisy Model', color='#d62728')
            ax.bar(x + width, real_vals, width, label='Real QPU', color='#1f77b4')
        else:
            width = 0.35
            ax.bar(x - width/2, ideal_vals, width, label='Ideal', color='#2ca02c')
            ax.bar(x + width/2, noisy_vals, width, label='Noisy Model', color='#d62728')

        # 5. Format and render
        ax.set_ylabel('Shot Counts (out of 1024)')
        ax.set_title(f"{protocol} Results - Target: '{target_state}'")
        ax.set_xticks(x)
        ax.set_xticklabels(all_bins)
        ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        filename = f"{path}{protocol.replace(' ', '_')}_{target_state}_plot.png"
        plt.savefig(filename, dpi=300)
        print(f"[+] Saved {filename}")
        plt.close()

if __name__ == "__main__":
    plot_master_results("json_files/sdc_master_results.json", path="output_files/sdc/")
    # You can also call it for TP:
    plot_master_results("json_files/tp_master_results.json", path="output_files/tp/")