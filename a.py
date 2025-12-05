import transformers
print("Transformers version:", transformers.__version__)

from transformers import TrainingArguments
import inspect

# Kiểm tra các tham số mà TrainingArguments chấp nhận
sig = inspect.signature(TrainingArguments.__init__)
params = list(sig.parameters.keys())

if 'evaluation_strategy' in params:
    print("✓ evaluation_strategy is supported")
else:
    print("✗ evaluation_strategy is NOT supported")
    
if 'evaluate_during_training' in params:
    print("✓ evaluate_during_training is supported (old)")