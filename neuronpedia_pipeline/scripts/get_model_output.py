"""
Get Model Output Prediction
Uses transformers to actually run the model and get the predicted output
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import json
from pathlib import Path
import argparse

def get_model_prediction(prompt, model_name="google/gemma-2-2b", top_k=5):
    """
    Get the model's actual output prediction

    Args:
        prompt: Input prompt
        model_name: HuggingFace model name
        top_k: Number of top predictions to return

    Returns:
        dict with predictions and probabilities
    """
    print(f"Loading model: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto" if torch.cuda.is_available() else None
    )

    # Tokenize
    inputs = tokenizer(prompt, return_tensors="pt")
    if torch.cuda.is_available():
        inputs = {k: v.cuda() for k, v in inputs.items()}

    print(f"Running inference on: '{prompt}'")

    # Get logits
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits[0, -1, :]  # Last token logits

    # Get top k predictions
    probs = torch.softmax(logits, dim=-1)
    top_probs, top_indices = torch.topk(probs, top_k)

    predictions = []
    for prob, idx in zip(top_probs, top_indices):
        token = tokenizer.decode([idx])
        predictions.append({
            'token': token.strip(),
            'probability': float(prob),
            'token_id': int(idx)
        })

    return {
        'prompt': prompt,
        'model': model_name,
        'top_predictions': predictions,
        'top_answer': predictions[0]['token'],
        'confidence': predictions[0]['probability']
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get model output prediction')
    parser.add_argument('--prompt', type=str, required=True, help='Input prompt')
    parser.add_argument('--model', type=str, default='google/gemma-2-2b', help='Model name')
    parser.add_argument('--top-k', type=int, default=5, help='Number of top predictions')
    parser.add_argument('--output', type=str, help='Output JSON file')

    args = parser.parse_args()

    result = get_model_prediction(args.prompt, args.model, args.top_k)

    print("\n" + "="*60)
    print("MODEL OUTPUT PREDICTION")
    print("="*60)
    print(f"\nPrompt: '{result['prompt']}'")
    print(f"\n✓ Top Answer: '{result['top_answer']}' (confidence: {result['confidence']:.1%})")
    print(f"\nTop {args.top_k} Predictions:")
    for i, pred in enumerate(result['top_predictions'], 1):
        print(f"  {i}. '{pred['token']}' ({pred['probability']:.1%})")

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n[OK] Saved to: {output_path}")
