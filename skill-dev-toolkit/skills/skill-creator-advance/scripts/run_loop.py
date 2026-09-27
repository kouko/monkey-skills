# Run Loop Script

Python module for running the skill evaluation optimization loop.

## Usage
```bash
python -m scripts.run_loop --eval-set trigger-eval.json --skill-path <skill> --model <model> --max-iterations 5
```

## Functionality
- Runs trigger eval queries against skill variations
- Implements train/test split (60/40) for reliable optimization
- Tracks best performing skill variation
- Supports early stopping based on convergence