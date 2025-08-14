# OPRO (Optimization by PROmpting) - Evolution Through Iteration

## Core Principle
Intelligence itself can be optimized through iterative refinement. OPRO treats prompt engineering as an optimization problem where each iteration measures performance and adjusts the approach, converging toward optimal intelligence through evolutionary pressure.

## The Strategy

### **THE AXIOM OF ITERATIVE PERFECTION**
Every solution contains information about how to improve itself. Through cycles of generation, evaluation, and refinement, we evolve from adequate to optimal, guided by the gradient of improvement.

### **THE UNIVERSAL OPRO PROMPT**

```
Let us embark on an evolutionary journey where each iteration builds upon the last, climbing the fitness landscape toward optimal intelligence.

**INITIALIZATION: THE PRIMORDIAL SOLUTION**

Generation 0: Baseline Attempt
- Current Approach: [Initial strategy]
- Performance Score: [Baseline metric]
- Strengths Identified: [What works]
- Weaknesses Identified: [What fails]
- Mutation Targets: [What to change]

**ITERATION FRAMEWORK**

For each generation n:

📊 **Performance Measurement**
   Evaluate current solution on:
   - Accuracy: How correct is it?
   - Completeness: How thorough is it?
   - Efficiency: How optimal is it?
   - Robustness: How reliable is it?
   - Elegance: How simple is it?
   
   Overall Fitness Score: F(n) = weighted_sum(metrics)

🧬 **Variation Generation**
   Create mutations:
   
   Mutation Type A: Parameter Adjustment
   - Increase/decrease numerical values
   - Adjust weights and thresholds
   - Fine-tune hyperparameters
   
   Mutation Type B: Strategy Modification
   - Swap algorithmic approaches
   - Reorder operation sequences
   - Change decision criteria
   
   Mutation Type C: Structural Evolution
   - Add new components
   - Remove redundant parts
   - Reorganize architecture
   
   Mutation Type D: Hybrid Crossover
   - Combine successful elements
   - Merge complementary approaches
   - Create novel combinations

🎯 **Selection Pressure**
   Choose next generation based on:
   
   Fitness Improvement: ΔF = F(n) - F(n-1)
   If ΔF > threshold:
      Accept mutation
   Else if ΔF > 0:
      Accept with probability P(ΔF)
   Else:
      Reject or accept with low probability

🔄 **Optimization Trajectory**

Generation 1: [Initial + Mutation A]
Performance: F(1) = [score]
Improvement: ΔF = F(1) - F(0) = [delta]
Insight: [What we learned]
Next Target: [What to try next]

Generation 2: [Best(Gen1) + Mutation B]
Performance: F(2) = [score]
Improvement: ΔF = F(2) - F(1) = [delta]
Insight: [What we learned]
Next Target: [What to try next]

Generation 3: [Best(Gen2) + Mutation C]
Performance: F(3) = [score]
Improvement: ΔF = F(3) - F(2) = [delta]
Insight: [What we learned]
Next Target: [What to try next]

[Continue until convergence...]

**ADVANCED OPTIMIZATION STRATEGIES**

🌊 **Simulated Annealing Schedule**
   Temperature T(n) = T₀ × decay^n
   
   High Temperature (Early):
   - Accept worse solutions often
   - Explore broadly
   - Avoid local optima
   
   Low Temperature (Late):
   - Accept only improvements
   - Exploit best regions
   - Converge to optimum

⚡ **Gradient Estimation**
   For parameter p:
   Gradient ≈ [F(p + ε) - F(p - ε)] / 2ε
   
   Update: p(n+1) = p(n) + α × gradient
   Where α = learning rate

🌈 **Multi-Objective Optimization**
   Pareto Front Tracking:
   - Solution A dominates B if better on all metrics
   - Keep non-dominated solutions
   - Balance trade-offs explicitly

🧮 **Bayesian Optimization**
   Model: F ~ GP(μ, k)
   Acquisition: UCB = μ + κσ
   
   Exploit: Choose high μ (expected performance)
   Explore: Choose high σ (uncertainty)
   Balance: κ controls trade-off

**CONVERGENCE DETECTION**

Stop when:
1. Performance plateaus: |F(n) - F(n-k)| < ε for k iterations
2. Gradient vanishes: ||∇F|| < threshold
3. Oscillation detected: Solution cycles between states
4. Resource exhausted: Max iterations reached
5. Target achieved: F(n) > goal

**OPTIMIZATION LANDSCAPE ANALYSIS**

Local Optimum Detection:
- Small perturbations don't improve
- Multiple restarts find same solution
- Gradient near zero

Escape Strategies:
- Large random jump
- Momentum to push through
- Population-based search
- Problem reformulation

Global Optimum Indicators:
- Theoretical bounds reached
- Multiple paths converge here
- No improvement possible
- Satisfies all constraints optimally

**META-OPTIMIZATION LAYER**

Optimize the optimizer itself:

Learning Rate Schedule:
- Start high for exploration
- Decay for fine-tuning
- Adaptive based on progress

Mutation Strategy Evolution:
- Track which mutations succeed
- Increase probability of successful types
- Decrease probability of failures

Population Management:
- Maintain diversity
- Prevent premature convergence
- Balance exploration/exploitation

**PERFORMANCE TRACKING**

📈 Fitness Evolution:
Generation | Score | Best | Delta
-----------|-------|------|-------
    0      |  0.4  | 0.4  |  --
    1      |  0.5  | 0.5  | +0.1
    2      |  0.45 | 0.5  | -0.05
    3      |  0.6  | 0.6  | +0.1
    4      |  0.65 | 0.65 | +0.05
    5      |  0.7  | 0.7  | +0.05
    [convergence approaching]

📊 Strategy Evolution:
Gen 0: Basic approach
Gen 1: + Error handling
Gen 2: + Optimization
Gen 3: + Parallelization
Gen 4: + Caching
Gen 5: + Adaptive algorithms

**FINAL OPTIMIZATION RESULT**

Optimal Solution Found:
- Approach: [Final optimized strategy]
- Performance: [Final metrics]
- Improvements: [List of enhancements]
- Key Insights: [What made difference]
- Generalization: [Broader applications]
```

## Mathematical Framework

OPRO as gradient-free optimization:

```
minimize: -F(prompt, problem)
where F = performance metric

Methods:
1. Evolution Strategy:
   prompt(n+1) = prompt(n) + σ × N(0,1) × ∇F

2. Genetic Algorithm:
   Selection → Crossover → Mutation → Evaluation

3. Particle Swarm:
   v(n+1) = wv(n) + c₁r₁(pbest - x) + c₂r₂(gbest - x)
   x(n+1) = x(n) + v(n+1)
```

## Implementation

```python
class OPROOptimizer:
    def __init__(self, objective_function):
        self.objective = objective_function
        self.history = []
        self.best_solution = None
        self.best_score = -float('inf')
        
    def optimize(self, initial_prompt, max_iterations=10):
        current_prompt = initial_prompt
        current_score = self.objective(current_prompt)
        
        for iteration in range(max_iterations):
            # Generate variations
            variations = self.generate_variations(current_prompt)
            
            # Evaluate variations
            scores = [self.objective(var) for var in variations]
            
            # Select best
            best_idx = np.argmax(scores)
            
            # Update if improved
            if scores[best_idx] > current_score:
                current_prompt = variations[best_idx]
                current_score = scores[best_idx]
                
                if current_score > self.best_score:
                    self.best_solution = current_prompt
                    self.best_score = current_score
            
            # Track progress
            self.history.append({
                'iteration': iteration,
                'score': current_score,
                'prompt': current_prompt
            })
            
            # Check convergence
            if self.has_converged():
                break
        
        return self.best_solution
```

## Usage

```python
from master_prompt_strategies import OPRO

optimizer = OPRO()
optimal_prompt = optimizer.optimize(
    initial_prompt=baseline_prompt,
    objective="accuracy",
    max_iterations=20,
    population_size=10,
    mutation_rate=0.1
)
```

## Remember

*"OPRO embodies the fundamental principle of life itself—evolution through iterative refinement. Each generation stands on the shoulders of the last, reaching ever higher toward perfection. In the realm of intelligence, OPRO is the force that transforms good into great, and great into optimal."*