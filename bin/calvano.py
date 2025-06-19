#!/usr/bin/env python3
"""
Calvano Q-learning simulation command-line interface.

Provides convenient subcommands for running simulations and analysis.
"""

import argparse
import os
import sys
import subprocess
from pathlib import Path


def get_src_path():
    """Get the path to the src directory."""
    script_dir = Path(__file__).parent
    src_dir = script_dir.parent / "src"
    return str(src_dir)


def run_main_with_args(args_list):
    """Run the main.py script with given arguments."""
    src_path = get_src_path()
    main_script = os.path.join(src_path, "main.py")
    
    # Add src to Python path
    sys.path.insert(0, src_path)
    
    # Prepare command
    cmd = [sys.executable, main_script] + args_list
    
    # Execute
    result = subprocess.run(cmd)
    return result.returncode


def cmd_run(args):
    """Handle 'calvano run' subcommand."""
    main_args = [
        "--config", args.config,
        "--mode", args.mode
    ]
    
    if args.output:
        main_args.extend(["--output", args.output])
    
    if args.n_runs:
        main_args.extend(["--n-runs", str(args.n_runs)])
    
    if args.dry_run:
        main_args.append("--dry-run")
    
    return run_main_with_args(main_args)


def cmd_analyse(args):
    """Handle 'calvano analyse' subcommand."""
    main_args = [
        "--config", args.config,
        "--mode", "analyse",
        "--logdir", args.logdir
    ]
    
    if args.output:
        main_args.extend(["--output", args.output])
    
    # Add deep analysis mode if requested
    if hasattr(args, 'analysis_mode') and args.analysis_mode == "deep":
        main_args.extend(["--analysis-mode", "deep"])
    
    return run_main_with_args(main_args)


def cmd_benchmark(args):
    """Handle 'calvano benchmark' subcommand."""
    main_args = [
        "--config", args.config,
        "--mode", "benchmark"
    ]
    
    if args.fortran:
        main_args.extend(["--fortran", args.fortran])
    
    if args.python:
        main_args.extend(["--python", args.python])
    
    if args.seed:
        main_args.extend(["--seed", str(args.seed)])
    
    if args.tolerance:
        main_args.extend(["--tolerance", str(args.tolerance)])
    
    if args.output:
        main_args.extend(["--output", args.output])
    
    return run_main_with_args(main_args)


def cmd_full(args):
    """Handle 'calvano full' subcommand (alias for run --mode full)."""
    main_args = [
        "--config", args.config,
        "--mode", "full"
    ]
    
    if args.output:
        main_args.extend(["--output", args.output])
    
    if args.n_runs:
        main_args.extend(["--n-runs", str(args.n_runs)])
    
    if args.dry_run:
        main_args.append("--dry-run")
    
    return run_main_with_args(main_args)


def cmd_benchmark_paper(args):
    """Handle 'calvano benchmark-paper' subcommand."""
    try:
        # Import the compare_paper module
        src_path = get_src_path()
        sys.path.insert(0, src_path)
        from benchmark.compare_paper import compare_to_paper
        
        # Run the comparison directly
        compare_to_paper(args.results, args.eps)
        return 0
    except Exception as e:
        print(f"❌ Paper parity test failed: {e}")
        return 1


def cmd_paper(args):
    """Handle 'calvano paper' subcommand."""
    try:
        # Import paper output modules
        src_path = get_src_path()
        sys.path.insert(0, src_path)
        from paper_outputs.make_tables import generate_all_tables
        from paper_outputs.make_figures import generate_all_figures
        from paper_outputs.stats_tests import generate_statistical_tests
        
        # Determine logdir
        if args.logdir:
            logdir = args.logdir
        else:
            # Find most recent run
            runs_dir = Path("runs")
            if runs_dir.exists():
                run_dirs = [d for d in runs_dir.iterdir() if d.is_dir()]
                if run_dirs:
                    logdir = str(sorted(run_dirs, key=lambda x: x.stat().st_mtime)[-1])
                else:
                    print("❌ No run directories found. Please run simulation first.")
                    return 1
            else:
                print("❌ No runs directory found. Please run simulation first.")
                return 1
        
        print(f"📊 Generating paper outputs from: {logdir}")
        
        # Create timestamped output directory
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"paper_outputs/{timestamp}"
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. Run deep analysis if needed (optional step)
        if not args.skip_analysis:
            print("🔍 Running deep analysis...")
            try:
                analyse_args = [
                    "--config", "configs/base.json",  # Fallback config
                    "--logdir", logdir,
                    "--mode", "deep",
                    "--output", output_dir
                ]
                if hasattr(args, 'config') and args.config:
                    analyse_args[1] = args.config
                
                run_main_with_args(["--mode", "analyse"] + analyse_args[1:])
            except Exception as e:
                print(f"⚠ Deep analysis failed, continuing: {e}")
        
        # 2. Generate tables
        print("📋 Generating tables...")
        try:
            generate_all_tables(logdir, output_dir)
        except Exception as e:
            print(f"⚠ Table generation failed: {e}")
        
        # 3. Generate figures
        print("📈 Generating figures...")
        try:
            generate_all_figures(logdir, output_dir)
        except Exception as e:
            print(f"⚠ Figure generation failed: {e}")
        
        # 4. Generate statistical tests
        print("📊 Running statistical tests...")
        try:
            generate_statistical_tests(logdir, output_dir)
        except Exception as e:
            print(f"⚠ Statistical tests failed: {e}")
        
        print(f"\n✅ Paper outputs generated in: {output_dir}")
        print(f"📁 Tables: {output_dir}/tables/")
        print(f"📁 Figures: {output_dir}/figures/")
        
        return 0
        
    except Exception as e:
        print(f"❌ Paper generation failed: {e}")
        return 1


def cmd_sweep(args):
    """Handle 'calvano sweep' subcommand."""
    try:
        # Import sweep modules
        src_path = get_src_path()
        sys.path.insert(0, src_path)
        from experiments.sweep import run_parameter_sweep
        from experiments.aggregate_sweep import aggregate_parameter_sweep
        
        # Determine config file
        config_file = args.config if hasattr(args, 'config') and args.config else "configs/base.json"
        if not os.path.exists(config_file):
            # Try to find a config file
            possible_configs = ["tests/ci_small.json", "configs/base.json"]
            for cfg in possible_configs:
                if os.path.exists(cfg):
                    config_file = cfg
                    break
            else:
                print("❌ No configuration file found")
                return 1
        
        print(f"🚀 Starting parameter sweep")
        print(f"  Grid: {args.grid}")
        print(f"  Config: {config_file}")
        print(f"  Jobs: {args.njobs}")
        
        # 1. Run parameter sweep
        sweep_result = run_parameter_sweep(
            grid_path=args.grid,
            base_config_path=config_file,
            output_dir="runs",
            n_jobs=args.njobs,
            timeout=args.timeout if hasattr(args, 'timeout') else 300
        )
        
        if sweep_result['failed_runs'] > 0:
            print(f"⚠ {sweep_result['failed_runs']} runs failed")
        
        # 2. Aggregate results
        sweep_dir = sweep_result['output_directory']
        print(f"📊 Aggregating results from: {sweep_dir}")
        
        try:
            aggregate_result = aggregate_parameter_sweep(sweep_dir, sweep_dir)
            
            if 'error' in aggregate_result:
                print(f"⚠ Aggregation failed: {aggregate_result['error']}")
            else:
                print(f"✅ Sweep completed successfully")
                print(f"📁 Results: {sweep_dir}")
                print(f"📋 Summary: {aggregate_result.get('grid_summary_csv', 'N/A')}")
        
        except Exception as e:
            print(f"⚠ Aggregation failed: {e}")
        
        return 0 if sweep_result['failed_runs'] == 0 else 1
        
    except Exception as e:
        print(f"❌ Parameter sweep failed: {e}")
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Calvano Q-learning simulation and analysis toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full simulation and analysis pipeline
  calvano run --config config.json --mode full
  
  # Run simulation only
  calvano run --config config.json --mode simulate --n-runs 50
  
  # Analyze existing results
  calvano analyse --config config.json --logdir runs/20250613_120045
  
  # Deep analysis with advanced features
  calvano analyse --config config.json --logdir runs/20250613_120045 --mode deep
  
  # Benchmark against Fortran implementation
  calvano benchmark --fortran path/to/output.csv --python runs/20250613_120045
  
  # Quick full pipeline (alias)
  calvano full --config configs/base.json
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # 'run' subcommand
    run_parser = subparsers.add_parser("run", help="Run simulation with specified mode")
    run_parser.add_argument("--config", type=str, required=True, 
                           help="Path to configuration JSON file")
    run_parser.add_argument("--mode", type=str, choices=["simulate", "analyse", "full"], 
                           default="simulate", help="Execution mode")
    run_parser.add_argument("--output", type=str, 
                           help="Output directory (default: auto-generated)")
    run_parser.add_argument("--n-runs", type=int, 
                           help="Number of simulation runs (overrides config)")
    run_parser.add_argument("--dry-run", action="store_true", 
                           help="Dry run mode (validate only)")
    run_parser.set_defaults(func=cmd_run)
    
    # 'analyse' subcommand
    analyse_parser = subparsers.add_parser("analyse", help="Analyze existing simulation results")
    analyse_parser.add_argument("--config", type=str, required=True,
                               help="Path to configuration JSON file")
    analyse_parser.add_argument("--logdir", type=str, required=True,
                               help="Directory containing simulation logs")
    analyse_parser.add_argument("--mode", type=str, choices=["standard", "deep"], 
                               default="standard", dest="analysis_mode",
                               help="Analysis mode: standard or deep")
    analyse_parser.add_argument("--output", type=str,
                               help="Output directory (default: auto-generated)")
    analyse_parser.set_defaults(func=cmd_analyse)
    
    # 'benchmark' subcommand
    benchmark_parser = subparsers.add_parser("benchmark", help="Benchmark against Fortran implementation")
    benchmark_parser.add_argument("--config", type=str, required=True,
                                 help="Path to configuration JSON file")
    benchmark_parser.add_argument("--fortran", type=str, required=True,
                                 help="Path to Fortran output CSV file")
    benchmark_parser.add_argument("--python", type=str,
                                 help="Path to Python simulation results (optional)")
    benchmark_parser.add_argument("--seed", type=int, default=12345,
                                 help="Random seed for comparison (default: 12345)")
    benchmark_parser.add_argument("--tolerance", type=float, default=1e-12,
                                 help="Error tolerance epsilon (default: 1e-12)")
    benchmark_parser.add_argument("--output", type=str,
                                 help="Output directory for benchmark report")
    benchmark_parser.set_defaults(func=cmd_benchmark)
    
    # 'full' subcommand (alias for run --mode full)
    full_parser = subparsers.add_parser("full", help="Run full simulation and analysis pipeline")
    full_parser.add_argument("--config", type=str, required=True,
                            help="Path to configuration JSON file")
    full_parser.add_argument("--output", type=str,
                            help="Output directory (default: auto-generated)")
    full_parser.add_argument("--n-runs", type=int,
                            help="Number of simulation runs (overrides config)")
    full_parser.add_argument("--dry-run", action="store_true",
                            help="Dry run mode (validate only)")
    full_parser.set_defaults(func=cmd_full)
    
    # 'benchmark-paper' subcommand
    benchmark_paper_parser = subparsers.add_parser("benchmark-paper", help="Compare results to paper values")
    benchmark_paper_parser.add_argument("--results", type=str, required=True,
                                       help="Path to summary.json")
    benchmark_paper_parser.add_argument("--eps", type=float, default=1e-3,
                                       help="Tolerance for comparison (default: 1e-3)")
    benchmark_paper_parser.set_defaults(func=cmd_benchmark_paper)
    
    # 'paper' subcommand
    paper_parser = subparsers.add_parser("paper", help="Generate paper outputs")
    paper_parser.add_argument("--logdir", type=str,
                               help="Directory containing simulation logs")
    paper_parser.add_argument("--skip-analysis", action="store_true",
                               help="Skip deep analysis")
    paper_parser.set_defaults(func=cmd_paper)
    
    # 'sweep' subcommand
    sweep_parser = subparsers.add_parser("sweep", help="Run parameter sweep")
    sweep_parser.add_argument("--config", type=str,
                               help="Path to configuration JSON file")
    sweep_parser.add_argument("--grid", type=str, required=True,
                               help="Path to grid JSON file")
    sweep_parser.add_argument("--njobs", type=int, default=os.cpu_count(),
                               help="Number of jobs (default: CPU count)")
    sweep_parser.add_argument("--timeout", type=int, default=300,
                               help="Timeout in seconds (default: 300)")
    sweep_parser.set_defaults(func=cmd_sweep)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute the appropriate command
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main()) 