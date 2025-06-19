"""
Parameter management for Calvano Q-learning simulation.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
import numpy as np


class SimParams:
    """Simulation parameters container."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize parameters from configuration dictionary.
        
        Args:
            config: Configuration dictionary with parameter values
        """
        if config is None:
            config = {}
        
        # Set defaults first
        self.n_agents = 2
        self.n_actions = 11
        self.n_states = 121
        self.n_runs = 50
        self.max_episodes = 2000
        self.alpha = 0.1
        self.delta = 0.95
        self.epsilon = 0.1
        self.lambda_param = 0.5
        self.a_param = 1.0
        self.demand_model = "logit"
        self.rng_seed = 42
        self.q_init_strategy = "R"
        self.conv_window = 1000
        self.conv_tolerance = 1e-4
        self.save_q_tables = False
        self.save_detailed_logs = True
        
        # Override with config values
        for key, value in config.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert parameters to dictionary."""
        return {
            'n_agents': self.n_agents,
            'n_actions': self.n_actions,
            'n_states': self.n_states,
            'n_runs': self.n_runs,
            'max_episodes': self.max_episodes,
            'alpha': self.alpha,
            'delta': self.delta,
            'epsilon': self.epsilon,
            'lambda_param': self.lambda_param,
            'a_param': self.a_param,
            'demand_model': self.demand_model,
            'rng_seed': self.rng_seed,
            'q_init_strategy': self.q_init_strategy,
            'conv_window': self.conv_window,
            'conv_tolerance': self.conv_tolerance,
            'save_q_tables': self.save_q_tables,
            'save_detailed_logs': self.save_detailed_logs
        }


@dataclass
class SimResults:
    """Simulation results container."""
    
    # Convergence results
    converged: Optional[np.ndarray] = None
    time_to_convergence: Optional[np.ndarray] = None
    index_strategies: Optional[np.ndarray] = None
    cycle_length: Optional[np.ndarray] = None
    cycle_states: Optional[np.ndarray] = None
    
    # Profit matrices
    pi: Optional[np.ndarray] = None
    nash_profits: Optional[np.ndarray] = None
    coop_profits: Optional[np.ndarray] = None
    pg: Optional[np.ndarray] = None
    
    # Q-learning results
    Q_matrices: Optional[list] = None
    strategies: Optional[list] = None 