"""
Parameter management for Calvano Q-learning simulation.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
import numpy as np


class SimParams:
    """Simulation parameters container with backward compatibility."""
    
    def __init__(self, *args, **kwargs):
        """
        Initialize parameters from configuration dictionary or individual keywords.
        
        Args:
            *args: Positional arguments (first can be config dict)
            **kwargs: Individual parameter values
        """
        # Handle dict input (new API)
        if len(args) == 1 and isinstance(args[0], dict):
            config = args[0]
            kwargs.update(config)
        
        # Set defaults first
        self.n_agents = kwargs.pop('n_agents', 2)
        self.n_actions = kwargs.pop('n_actions', 11) 
        self.n_prices = kwargs.pop('n_prices', 11)  # For backward compatibility
        self.n_states = kwargs.pop('n_states', 121)
        self.state_depth = kwargs.pop('state_depth', 1)
        self.q_strategy = kwargs.pop('q_strategy', "R")
        
        # Additional parameters for backward compatibility
        self.n_runs = kwargs.pop('n_runs', 50)
        self.max_episodes = kwargs.pop('max_episodes', 2000)
        self.alpha = kwargs.pop('alpha', 0.1)
        self.delta = kwargs.pop('delta', 0.95)
        self.epsilon = kwargs.pop('epsilon', 0.1)
        self.lambda_param = kwargs.pop('lambda_param', 0.5)
        self.a_param = kwargs.pop('a_param', 1.0)
        self.demand_model = kwargs.pop('demand_model', "logit")
        self.rng_seed = kwargs.pop('rng_seed', 42)
        self.q_init_strategy = kwargs.pop('q_init_strategy', "R")
        self.conv_window = kwargs.pop('conv_window', 1000)
        self.conv_tolerance = kwargs.pop('conv_tolerance', 1e-4)
        self.save_q_tables = kwargs.pop('save_q_tables', False)
        self.save_detailed_logs = kwargs.pop('save_detailed_logs', True)
        
        # Store any extra parameters
        self.extra = kwargs
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert parameters to dictionary."""
        return {
            'n_agents': self.n_agents,
            'n_actions': self.n_actions,
            'n_prices': self.n_prices,
            'n_states': self.n_states,
            'state_depth': self.state_depth,
            'q_strategy': self.q_strategy,
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
            'save_detailed_logs': self.save_detailed_logs,
            **self.extra
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