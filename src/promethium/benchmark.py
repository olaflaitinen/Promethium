# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import argparse
import time
import numpy as np
from promethium.core.models import SeismicTrace
from promethium.signal.filters import bandpass_filter

def run_benchmark(dataset_type: str, scenario: str):
    print(f"Running Benchmark | Dataset: {dataset_type} | Scenario: {scenario}")
    
    # Generate synthetic data
    n_traces = 1000
    n_samples = 2000
    data = np.random.randn(n_traces, n_samples).astype(np.float32)
    
    print(f"Generated {n_traces} traces with {n_samples} samples.")
    
    start_time = time.time()
    
    # Simple processing loop emulation
    for i in range(n_traces):
        _ = bandpass_filter(data[i], lowcut=5.0, highcut=50.0, fs=500.0, order=4)
        
    end_time = time.time()
    duration = end_time - start_time
    throughput = n_traces / duration
    
    print(f"Processing Complete.")
    print(f"Duration: {duration:.4f} seconds")
    print(f"Throughput: {throughput:.2f} traces/sec")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Promethium Benchmarking Tool")
    parser.add_argument("--dataset", type=str, default="synthetic", help="Dataset type")
    parser.add_argument("--scenario", type=str, default="A", help="Benchmark scenario")
    
    args = parser.parse_args()
    run_benchmark(args.dataset, args.scenario)
