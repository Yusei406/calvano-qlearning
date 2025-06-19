"""
Mock Q-learning simulation module for testing.

This is a simplified implementation for testing the Phase 2 analysis pipeline.
The full Q-learning implementation would be much more complex.
"""

import numpy as np
from typing import Dict, List, Optional

# Handle imports for both package and standalone usage
try:
    from .params import SimParams
    from .dtype_policy import DTYPE, array, zeros
except ImportError:
    from params import SimParams
    from dtype_policy import DTYPE, array, zeros


def run_simulation(params: SimParams) -> Dict:
    """
    Mock Q-learning simulation run.
    
    Args:
        params: Simulation parameters
        
    Returns:
        Dictionary containing simulation results
    """
    # Set random seed for reproducibility
    if hasattr(params, 'rng_seed'):
        np.random.seed(params.rng_seed)
    
    # Mock simulation - generate synthetic results
    n_agents = params.n_agents
    n_episodes = getattr(params, 'max_episodes', 1000)
    
    # Generate mock price and profit histories
    price_history = []
    profit_history = []
    
    # Start with random prices, converge towards Nash-like equilibrium
    current_prices = np.random.uniform(0.3, 0.7, n_agents)
    nash_target = 0.5  # Mock Nash equilibrium price
    
    for episode in range(n_episodes):
        # Simple convergence dynamics - move towards Nash equilibrium with noise
        convergence_rate = 0.01
        noise_level = 0.05 * (1 - episode / n_episodes)  # Decreasing noise
        
        # Update prices
        for agent in range(n_agents):
            # Move towards Nash equilibrium
            current_prices[agent] += convergence_rate * (nash_target - current_prices[agent])
            # Add noise
            current_prices[agent] += np.random.normal(0, noise_level)
            # Keep in valid range
            current_prices[agent] = np.clip(current_prices[agent], 0.0, 1.0)
        
        price_history.append(current_prices.copy())
        
        # Mock profit calculation (simplified demand model)
        demands = []
        for agent in range(n_agents):
            other_prices = [current_prices[j] for j in range(n_agents) if j != agent]
            # Simple linear demand: higher own price = lower demand, higher competitor prices = higher demand
            demand = params.a_param - current_prices[agent] + params.lambda_param * np.mean(other_prices)
            demand = max(0.0, demand)  # Non-negative demand
            demands.append(demand)
        
        profits = [current_prices[i] * demands[i] for i in range(n_agents)]
        profit_history.append(profits)
    
    # Convert to arrays
    price_history = np.array(price_history)
    profit_history = np.array(profit_history)
    
    # Calculate convergence metrics
    final_prices = price_history[-1]
    final_profits = profit_history[-1]
    
    # Simple convergence check - low price volatility in final episodes
    final_window = 100
    if len(price_history) >= final_window:
        recent_prices = price_history[-final_window:]
        price_volatility = np.std(recent_prices, axis=0).mean()
        price_converged = price_volatility < getattr(params, 'conv_tolerance', 1e-3)
    else:
        price_volatility = 1.0
        price_converged = False
    
    # Mock Nash and cooperative distances
    nash_distance = np.abs(final_prices - nash_target).mean()
    coop_distance = np.abs(final_prices - 0.8).mean()  # Mock cooperative price
    
    # Determine overall convergence
    strategy_converged = price_converged  # Simplified
    overall_converged = price_converged and nash_distance < 0.1
    
    # Mock convergence time
    convergence_time = None
    if overall_converged:
        # Find when prices stabilized
        for t in range(len(price_history) - final_window, len(price_history)):
            if t > 0:
                volatility = np.std(price_history[max(0, t-50):t], axis=0).mean()
                if volatility < getattr(params, 'conv_tolerance', 1e-3):
                    convergence_time = t
                    break
    
    # Return results in expected format
    result = {
        'price_converged': price_converged,
        'strategy_converged': strategy_converged,
        'overall_converged': overall_converged,
        'final_prices': array(final_prices),
        'final_profits': array(final_profits),
        'price_history': price_history,
        'profit_history': profit_history,
        'nash_distance': nash_distance,
        'coop_distance': coop_distance,
        'convergence_time': convergence_time,
        'final_volatility': price_volatility,
        'n_episodes': n_episodes
    }
    
    return result


def run_multiple_simulations(params: SimParams, n_runs: int) -> List[Dict]:
    """
    Run multiple simulation instances.
    
    Args:
        params: Simulation parameters
        n_runs: Number of simulation runs
        
    Returns:
        List of simulation result dictionaries
    """
    results = []
    
    for run_id in range(n_runs):
        # Vary random seed for each run
        if hasattr(params, 'rng_seed'):
            np.random.seed(params.rng_seed + run_id)
        
        result = run_simulation(params)
        result['run_id'] = run_id
        results.append(result)
    
    return results


def compute_theoretical_nash_price(params: SimParams) -> float:
    """
    Compute theoretical Nash equilibrium price.
    
    Args:
        params: Simulation parameters
        
    Returns:
        Nash equilibrium price
    """
    # Simplified theoretical calculation
    # In the actual implementation, this would involve solving the Nash equilibrium
    if params.demand_model == "logit":
        # Mock calculation for logit demand
        return 0.5
    else:
        # Default Nash price
        return 0.5


def compute_theoretical_coop_price(params: SimParams) -> float:
    """
    Compute theoretical cooperative (collusive) price.
    
    Args:
        params: Simulation parameters
        
    Returns:
        Cooperative equilibrium price
    """
    # Simplified theoretical calculation
    # Cooperative price is typically higher than Nash
    if params.demand_model == "logit":
        # Mock calculation for cooperative outcome
        return 0.8
    else:
        # Default cooperative price
        return 0.8 