# Reproducing Calvano et al. (2020) Results

This guide describes how to reproduce the results from the Q-learning oligopoly simulation.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run simulation with default configuration
calvano run --config configs/base.json --mode full

# Generate paper outputs
calvano paper --logdir runs/$(ls -1dt runs/* | head -1)
```

## Step-by-Step Instructions

### 1. Environment Setup

Ensure you have Python 3.8+ and required dependencies:

```bash
pip install -r requirements.txt
```

### 2. Configuration

Edit `configs/base.json` to adjust simulation parameters:

- `n_episodes`: Number of learning episodes (default: 20000)
- `learning_rate`: Q-learning rate (default: 0.15) 
- `discount_factor`: Discount factor γ (default: 0.95)
- `exploration_rate`: ε-greedy exploration (default: 0.05)
- `n_firms`: Number of firms (default: 2)
- `memory_length`: Memory horizon (default: 1)

### 3. Run Simulation

```bash
# Full pipeline (simulation + analysis)
calvano run --config configs/base.json --mode full --n-runs 10

# Simulation only
calvano run --config configs/base.json --mode simulate --n-runs 10

# Analysis of existing results
calvano analyse --config configs/base.json --logdir runs/20241205_143022
```

### 4. Generate Paper Outputs

```bash
# Generate all tables, figures, and statistical tests
calvano paper --logdir runs/20241205_143022

# Skip deep analysis (faster)
calvano paper --logdir runs/20241205_143022 --skip-analysis
```

### 5. Parameter Sweeps

```bash
# Run parameter sweep
calvano sweep --grid tests/example_grid.json --njobs 4

# Custom sweep configuration
cat > my_grid.json << EOF
{
  "learning_rate": [0.1, 0.15, 0.2],
  "discount_factor": [0.9, 0.95],
  "exploration_rate": [0.01, 0.05]
}
EOF

calvano sweep --grid my_grid.json --njobs 8
```

### 6. Validation

```bash
# Compare results to Calvano et al. (2020) values
calvano benchmark-paper --results runs/20241205_143022/summary.json --eps 1e-3

# Stricter tolerance
calvano benchmark-paper --results runs/20241205_143022/summary.json --eps 1e-2
```

## Expected Results

### Key Metrics (Calvano et al. 2020 Table 1)

- **Nash Price**: 0.500 ± 0.010
- **Cooperation Gap**: 0.300 ± 0.020
- **Convergence Rate**: 0.9265 ± 0.050
- **Mean Profit**: 0.250 ± 0.010

### Output Structure

```
runs/20241205_143022/
├── config.json          # Simulation configuration
├── logs/                 # Detailed simulation logs
│   ├── firm_0.csv
│   └── firm_1.csv
├── summary.json          # Key metrics
├── figures/              # Analysis plots
│   ├── convergence.png
│   ├── price_trajectory.png
│   └── profit_evolution.png
└── tables/              # Summary statistics
    ├── summary_stats.csv
    └── convergence_analysis.csv
```

### Paper Outputs

```
paper_outputs/20241205_143545/
├── tables/              # LaTeX/CSV tables
│   ├── table1.tex      # Main results
│   ├── table2.tex      # Parameter sensitivity
│   └── table3.tex      # Convergence analysis
├── figures/             # Publication-ready figures
│   ├── figure1.png     # Convergence plots (2×2)
│   └── figure2.png     # Profit analysis (1×2)
└── stats_tests.txt      # Statistical test results
```

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Ensure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Config validation error**: Check JSON syntax in configuration files
   ```bash
   python -c "import json; json.load(open('configs/base.json'))"
   ```

3. **Memory issues**: Reduce `n_episodes` or `n_runs` for large simulations

4. **Plot display issues**: Set matplotlib backend
   ```bash
   export MPLBACKEND=Agg  # For headless environments
   ```

### Performance Tips

- Use `--njobs` parameter for parallel parameter sweeps
- Set `--skip-analysis` for faster paper output generation
- Use smaller configurations for testing (see `tests/ci_small.json`)

## Citation

If using this code for research, please cite:

> Calvano, E., Calzolari, G., Denicolò, V., & Pastorello, S. (2020). 
> Artificial intelligence, algorithmic pricing, and collusion. 
> American Economic Review, 110(10), 3267-3297. 