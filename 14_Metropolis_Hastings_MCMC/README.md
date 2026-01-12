# Metropolis-Hastings MCMC for Poisson Distribution

## Project Overview
This project implements the Metropolis-Hastings algorithm, a Markov Chain Monte Carlo (MCMC) method for sampling from probability distributions. Specifically, it samples from a Poisson distribution and demonstrates convergence behavior through visualization.

## Technical Skills Demonstrated

### Statistical Computing
- **Markov Chain Monte Carlo (MCMC)**: Sampling from complex distributions
- **Metropolis-Hastings Algorithm**: Classic MCMC sampler
- **Convergence Analysis**: Understanding burn-in and mixing
- **Probability Theory**: Poisson distribution, acceptance ratios

### Data Science
- **Python Programming**: NumPy for numerical computing
- **Visualization**: Matplotlib for distribution analysis
- **Statistical Analysis**: Evaluating sampler performance
- **Jupyter Notebooks**: Interactive data analysis

### Algorithm Design
- **Random Walk**: Proposal distribution design
- **Acceptance-Rejection**: Metropolis acceptance criterion
- **Burn-in Period**: Removing initial transient samples
- **Convergence Diagnostics**: Visual assessment of mixing

## Project Structure
```
Metropolis_Hastings_Poisson.ipynb
└── Single notebook containing:
    ├── Target distribution definition
    ├── Metropolis-Hastings implementation
    ├── Sampling execution
    └── Convergence visualization (4 histograms)
```

## Key Features

### 1. Target Distribution: Poisson(λ=10)
```python
def target_distribution(x, lam=10):
    """
    Poisson probability mass function.
    P(X=x) = (λ^x * e^(-λ)) / x!
    """
    return (lam**x) / factorial(x)
```

### 2. Metropolis-Hastings Implementation
```python
def metropolis_hastings_poisson(n_samples=10000, lam=10):
    """
    MCMC sampling from Poisson distribution using M-H algorithm.
    
    Args:
        n_samples: Number of samples to generate
        lam: Poisson parameter λ (mean and variance)
        
    Returns:
        Array of samples from Poisson(λ)
    """
    samples = []
    x = 0  # Initial state
    
    for i in range(n_samples):
        # Proposal: Random walk on integers
        if x == 0:
            y = np.random.choice([0, 1])  # Can't go negative
        else:
            y = np.random.choice([x - 1, x + 1])  # ±1 step
        
        # Acceptance ratio: P(y) / P(x)
        acceptance_ratio = target_distribution(y, lam) / target_distribution(x, lam)
        alpha = min(1, acceptance_ratio)
        
        # Accept or reject
        if np.random.rand() < alpha:
            x = y  # Accept proposal
        
        samples.append(x)
    
    return np.array(samples)
```

### 3. Convergence Visualization
Four histograms showing convergence over time:
- **Samples 25-50**: Early burn-in period
- **Samples 50-100**: Still converging
- **Samples 500-1000**: Approaching stationary distribution
- **Samples 5000-10000**: Converged to target distribution

## Technical Implementation

### Complete Implementation
```python
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import factorial

def target_distribution(x, lam=10):
    """Poisson PMF: P(X=x) = (λ^x * e^(-λ)) / x!"""
    return (lam**x) / factorial(x)

def metropolis_hastings_poisson(n_samples=10000, lam=10):
    """
    Metropolis-Hastings sampler for Poisson distribution.
    
    Proposal Distribution:
        - Random walk on integers: q(y|x) = 0.5 if |y-x| = 1
        - Symmetric proposal: q(y|x) = q(x|y)
        
    Acceptance Probability:
        - α(x→y) = min(1, P(y)/P(x))
        - Simplified because proposal is symmetric
    """
    samples = []
    x = 0  # Start at 0
    
    for i in range(n_samples):
        # Propose new state (random walk)
        if x == 0:
            y = np.random.choice([0, 1])
        else:
            y = np.random.choice([x - 1, x + 1])
        
        # Compute acceptance probability
        acceptance_ratio = target_distribution(y, lam) / target_distribution(x, lam)
        alpha = min(1, acceptance_ratio)
        
        # Accept or reject with probability α
        if np.random.rand() < alpha:
            x = y
        
        samples.append(x)
    
    return np.array(samples)

# Generate samples
np.random.seed(0)
samples = metropolis_hastings_poisson()

def plot_histogram(samples, start, end, title):
    """Plot histogram of sample range."""
    plt.hist(samples[start:end], bins=range(0, 21), density=True, 
             alpha=0.75, color='blue', edgecolor='black')
    plt.title(title)
    plt.xlabel('Sample Value')
    plt.ylabel('Frequency')
    plt.show()

# Visualize convergence
plot_histogram(samples, 25, 50, 'Histogram of Samples {X25, ..., X50}')
plot_histogram(samples, 50, 100, 'Histogram of Samples {X50, ..., X100}')
plot_histogram(samples, 500, 1000, 'Histogram of Samples {X500, ..., X1000}')
plot_histogram(samples, 5000, 10000, 'Histogram of Samples {X5000, ..., X10000}')
```

## Technical Environment
- **Language**: Python 3.x
- **Libraries**: 
  - NumPy: Numerical computing
  - Matplotlib: Visualization
  - SciPy: Factorial function
- **Platform**: Jupyter Notebook

## Skills & Technologies
- **Python Programming**: NumPy, Matplotlib, SciPy
- **MCMC Methods**: Metropolis-Hastings algorithm
- **Probability**: Poisson distribution, acceptance ratios
- **Statistical Computing**: Random sampling, convergence
- **Data Visualization**: Histograms, distribution plots
- **Jupyter Notebooks**: Interactive computing

## Algorithm Details

### Metropolis-Hastings Framework

**General Algorithm:**
1. Start with initial state x₀
2. For t = 1 to N:
   - Propose new state y ~ q(y|xₜ₋₁)
   - Compute acceptance ratio: α = min(1, π(y)q(xₜ₋₁|y) / π(xₜ₋₁)q(y|xₜ₋₁))
   - Accept y with probability α, else stay at xₜ₋₁

**For Poisson with Random Walk:**
- Proposal q(y|x) is symmetric: q(y|x) = q(x|y)
- Acceptance ratio simplifies to: α = min(1, P(y) / P(x))
- This is called **Metropolis algorithm** (special case)

### Proposal Distribution Design

**Random Walk Proposal:**
```
q(y|x) = 0.5  if y = x + 1
         0.5  if y = x - 1  (when x > 0)
         0.5  if y = 1      (when x = 0)
         0.5  if y = 0      (when x = 0)
```

**Properties:**
- Symmetric: q(y|x) = q(x|y)
- Ensures irreducibility (can reach any state)
- Simple to implement
- May converge slowly (small steps)

### Convergence Analysis

**Burn-in Period:**
- Initial samples don't represent target distribution
- Depends on starting point and proposal
- Visual inspection: first ~50-500 samples

**Mixing:**
- How quickly chain explores state space
- Good mixing: rapid traversal
- Poor mixing: slow, stuck in regions

**Stationary Distribution:**
- Long-run distribution equals target
- Achieved after sufficient iterations
- Independent of initial state (given enough time)

## Theoretical Background

### Poisson Distribution
```
P(X = k) = (λ^k * e^(-λ)) / k!

where:
- λ > 0 is the rate parameter
- E[X] = λ (mean)
- Var[X] = λ (variance)
```

**Properties:**
- Discrete distribution on {0, 1, 2, ...}
- Models count data (arrivals, events)
- Sum of Poissons is Poisson
- Limit of Binomial as n→∞, p→0, np→λ

### Why MCMC?
For complex distributions:
- Direct sampling may be difficult/impossible
- Normalization constant unknown
- High-dimensional spaces
- MCMC provides approximate samples

### Detailed Balance
Key property ensuring correctness:
```
π(x) P(x→y) = π(y) P(y→x)

where P(x→y) = q(y|x) * α(x→y)
```

If detailed balance holds, π is the stationary distribution.

## Convergence Diagnostics

### Visual Inspection
- **Trace plots**: Plot samples over time
- **Histograms**: Compare to true distribution
- **Autocorrelation**: Measure dependence

### Quantitative Measures
1. **Effective Sample Size (ESS)**
   - Accounts for autocorrelation
   - ESS < N due to dependence

2. **Gelman-Rubin Statistic (R̂)**
   - Compare multiple chains
   - R̂ ≈ 1 indicates convergence

3. **Geweke Diagnostic**
   - Compare early and late samples
   - Should be similar if converged

## Visualization Results

### Expected Behavior:
1. **Early samples (25-50)**: 
   - Poor approximation
   - May be far from λ=10 mean
   - High variance

2. **Intermediate (500-1000)**:
   - Better approximation
   - Distribution shape emerging
   - Centered around λ=10

3. **Late samples (5000-10000)**:
   - Good approximation
   - Matches Poisson(10) well
   - Bell-shaped, centered at 10

## Applications of MCMC

### Statistics
- **Bayesian Inference**: Posterior sampling
- **Missing Data**: EM algorithm alternative
- **Mixture Models**: Component assignment
- **Hierarchical Models**: Complex posteriors

### Machine Learning
- **Latent Variable Models**: VAEs, probabilistic PCA
- **Neural Networks**: Bayesian neural networks
- **Reinforcement Learning**: Policy evaluation
- **Gaussian Processes**: Hyperparameter inference

### Physics
- **Statistical Mechanics**: Gibbs sampling
- **Lattice Field Theory**: QCD simulations
- **Ising Model**: Phase transitions

### Biology
- **Phylogenetics**: Tree reconstruction
- **Population Genetics**: Parameter estimation
- **Systems Biology**: Pathway inference

### Finance
- **Option Pricing**: Complex derivatives
- **Risk Management**: VaR estimation
- **Portfolio Optimization**: Robust strategies

## Improvements & Extensions

### Better Proposals
```python
# Adaptive proposal based on recent acceptance rate
if acceptance_rate < 0.2:
    step_size *= 0.9  # Smaller steps
elif acceptance_rate > 0.5:
    step_size *= 1.1  # Larger steps
```

### Hamiltonian Monte Carlo (HMC)
- Uses gradient information
- More efficient exploration
- Faster convergence

### Gibbs Sampling
- Special case of M-H
- Always accept (α = 1)
- Sample each variable conditionally

### Parallel Tempering
- Multiple chains at different "temperatures"
- Improves mixing for multimodal distributions
- Periodic swaps between chains

## Performance Analysis

### Computational Complexity
- **Per iteration**: O(1) for Poisson
- **Total**: O(N) for N samples
- **Memory**: O(N) to store samples

### Acceptance Rate
```python
acceptance_rate = np.mean(np.diff(samples) != 0)
print(f"Acceptance rate: {acceptance_rate:.2%}")
```

**Rule of thumb:**
- 20-50% acceptance is good
- Too high: small steps, slow exploration
- Too low: most proposals rejected, inefficient

### Autocorrelation
```python
from statsmodels.tsa.stattools import acf

autocorr = acf(samples, nlags=100)
plt.plot(autocorr)
plt.xlabel('Lag')
plt.ylabel('Autocorrelation')
plt.show()
```

**Interpretation:**
- Fast decay: good mixing
- Slow decay: high correlation, poor mixing

## Learning Outcomes
This project demonstrates:
- Implementation of MCMC algorithms
- Understanding of convergence behavior
- Practical sampling from distributions
- Data visualization for diagnostics
- Statistical computing with Python

## Real-World Impact
MCMC is used in:
- **Google**: PageRank (early versions)
- **Netflix**: Recommendation systems
- **Finance**: Risk modeling
- **Pharmaceuticals**: Clinical trial analysis
- **Climate Science**: Parameter estimation
- **Genomics**: Sequence alignment

## Further Reading

### Books
- "MCMC in Practice" by Gilks, Richardson, Spiegelhalter
- "Handbook of Markov Chain Monte Carlo" by Brooks et al.
- "Bayesian Data Analysis" by Gelman et al.

### Papers
- Metropolis et al. (1953): Original paper
- Hastings (1970): Generalization
- Gelman & Rubin (1992): Convergence diagnostic

### Software
- **PyMC3**: Probabilistic programming in Python
- **Stan**: Bayesian inference with HMC
- **JAGS**: Gibbs sampling
- **emcee**: Ensemble MCMC sampler

