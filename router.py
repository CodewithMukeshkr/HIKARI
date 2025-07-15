import re
import random
from collections import defaultdict
from model_registry import MODEL_REGISTRY

# Token usage tracker with corrected limits (1-3% safety reduction)
# Format: "model-name": limit_in_tokens (original_limit -> safety_reduced_limit)
MODEL_TOKEN_LIMITS = {
    # Top tier models (90M+ tokens) - B = Billion
    "deepseek/deepseek-chat-v3-0324:free": 94000000000,  # 94.1B -> 94B

    # High tier models (30M+ tokens) - B = Billion
    "deepseek/deepseek-r1:free": 36000000000,  # 36.7B -> 36B

    # Mid-high tier models (5M+ tokens) - B = Billion
    "tngtech/deepseek-r1t-chimera:free": 6800000000,  # 6.85B -> 6.8B
    "google/gemini-2.0-flash-exp:free": 5600000000,  # 5.63B -> 5.6B
    "deepseek/deepseek-chat:free": 5200000000,  # 5.25B -> 5.2B

    # Mid tier models (1M+ tokens) - B = Billion
    "qwen/qwen3-235b-a22b:free": 4800000000,  # 4.85B -> 4.8B
    "microsoft/mai-ds-r1:free": 3700000000,  # 3.79B -> 3.7B
    "meta-llama/llama-4-maverick:free": 3400000000,  # 3.43B -> 3.4B
    "google/gemma-3-27b-it:free": 1940000000,  # 1.95B -> 1.94B
    "deepseek/deepseek-prover-v2:free": 1780000000,  # 1.8B -> 1.78B
    "deepseek/deepseek-r1-distill-llama-70b:free": 1680000000,  # 1.69B -> 1.68B
    "qwen/qwq-32b:free": 1590000000,  # 1.6B -> 1.59B
    "mistralai/mistral-nemo:free": 1430000000,  # 1.44B -> 1.43B
    "qwen/qwen3-14b:free": 1250000000,  # 1.26B -> 1.25B
    "nvidia/llama-3.1-nemotron-ultra-253b-v1:free": 1120000000,  # 1.13B -> 1.12B
    "mistralai/mistral-small-3.1-24b-instruct:free": 1030000000,  # 1.04B -> 1.03B
    "meta-llama/llama-3.3-70b-instruct:free": 1010000000,  # 1.02B -> 1.01B

    # Lower-mid tier models (100K+ tokens) - M = Million
    "deepseek/deepseek-r1-zero:free": 800000000,  # 808M -> 800M
    "meta-llama/llama-4-scout:free": 760000000,  # 764M -> 760M
    "deepseek/deepseek-v3-base:free": 740000000,  # 748M -> 740M
    "deepseek/deepseek-r1-distill-qwen-32b:free": 740000000,  # 747M -> 740M
    "qwen/qwen2.5-vl-72b-instruct:free": 690000000,  # 697M -> 690M
    "mistralai/devstral-small:free": 645000000,  # 650M -> 645M
    "qwen/qwen3-30b-a3b:free": 610000000,  # 617M -> 610M
    "meta-llama/llama-3.3-8b-instruct:free": 470000000,  # 474M -> 470M
    "qwen/qwen-2.5-72b-instruct:free": 420000000,  # 425M -> 420M
    "qwen/qwen-2.5-coder-32b-instruct:free": 390000000,  # 392M -> 390M
    "qwen/qwen3-32b:free": 375000000,  # 379M -> 375M
    "nousresearch/deephermes-3-mistral-24b-preview:free": 374000000,  # 377M -> 374M
    "thudm/glm-4-32b:free": 338000000,  # 341M -> 338M
    "thudm/glm-z1-32b:free": 280000000,  # 283M -> 280M
    "google/gemma-3-12b-it:free": 238000000,  # 240M -> 238M
    "nvidia/llama-3.3-nemotron-super-49b-v1:free": 184000000,  # 186M -> 184M
    "agentica-org/deepcoder-14b-preview:free": 183000000,  # 185M -> 183M
    "microsoft/phi-4-reasoning-plus:free": 145000000,  # 147M -> 145M
    "qwen/qwen3-8b:free": 126000000,  # 127M -> 126M
    "mistralai/mistral-7b-instruct:free": 110000000,  # 111M -> 110M
    "qwen/qwen2.5-vl-32b-instruct:free": 103000000,  # 104M -> 103M

    # Lower tier models (10K+ tokens) - M = Million
    "qwen/qwen3-4b:free": 90500000,  # 91.5M -> 90.5M
    "opengvlab/internvl3-14b:free": 88300000,  # 89.2M -> 88.3M
    "qwen/qwen2.5-vl-3b-instruct:free": 87200000,  # 88.1M -> 87.2M
    "shisa-ai/shisa-v2-llama3.3-70b:free": 86600000,  # 87.5M -> 86.6M
    "deepseek/deepseek-r1-distill-qwen-14b:free": 67000000,  # 67.7M -> 67M
    "google/gemma-2-9b-it:free": 64200000,  # 64.9M -> 64.2M
    "cognitivecomputations/dolphin3.0-mistral-24b:free": 59600000,  # 60.2M -> 59.6M
    "meta-llama/llama-3.1-8b-instruct:free": 56500000,  # 57.1M -> 56.5M
    "open-r1/olympiccoder-32b:free": 50800000,  # 51.3M -> 50.8M
    "qwen/qwen-2.5-7b-instruct:free": 49300000,  # 49.8M -> 49.3M
    "meta-llama/llama-3.1-405b:free": 43400000,  # 43.8M -> 43.4M
    "google/gemma-3-4b-it:free": 42300000,  # 42.7M -> 42.3M
    "mistralai/mistral-small-24b-instruct-2501:free": 37400000,  # 37.8M -> 37.4M
    "arliai/qwq-32b-arliai-rpr-v1:free": 37300000,  # 37.7M -> 37.3M
    "nousresearch/deephermes-3-llama-3-8b-preview:free": 26900000,  # 27.2M -> 26.9M
    "cognitivecomputations/dolphin3.0-r1-mistral-24b:free": 24000000,  # 24.2M -> 24M
    "microsoft/phi-4-reasoning:free": 17000000,  # 17.2M -> 17M
    "google/gemma-3n-e4b-it:free": 15400000,  # 15.6M -> 15.4M
    "qwen/qwen-2.5-vl-7b-instruct:free": 14800000,  # 14.9M -> 14.8M
    "opengvlab/internvl3-2b:free": 14300000,  # 14.4M -> 14.3M
    "meta-llama/llama-3.2-3b-instruct:free": 14200000,  # 14.3M -> 14.2M
    "moonshotai/kimi-vl-a3b-thinking:free": 12400000,  # 12.5M -> 12.4M
    "google/gemma-3-1b-it:free": 10000000,  # 10.1M -> 10M
    "rekaai/reka-flash-3:free": 9000000,  # 9.07M -> 9M
    "meta-llama/llama-3.2-1b-instruct:free": 6300000,  # 6.39M -> 6.3M
    "featherless/qwerky-72b:free": 5200000,  # 5.25M -> 5.2M
    "moonshotai/moonlight-16b-a3b-instruct:free": 2300000,  # 2.31M -> 2.3M


    # Fallback
    "cohere": 10000000  # estimation with safety margin
}

# Runtime token usage counter
model_token_usage = defaultdict(int)


def get_model_for_category(category):
    #Get an available model from the specified category
    models = MODEL_REGISTRY.get(category, [])
    print(f"[ROUTER] Looking for models in category '{category}': {len(models)} available")

    # Shuffle models to distribute load
    available_models = models.copy()
    random.shuffle(available_models)

    for model in available_models:
        limit = MODEL_TOKEN_LIMITS.get(model, 1_000_000)  # Default limit if not found
        current_usage = model_token_usage[model]

        if current_usage < limit:
            print(f"[ROUTER] Selected {model} (usage: {current_usage:,}/{limit:,} tokens)")
            return model
        else:
            print(f"[ROUTER] {model} at capacity ({current_usage:,}/{limit:,} tokens)")

    print(f"[ROUTER] No available models in category '{category}'")
    return None


def increment_usage(model, tokens):
    #Track token usage for a model
    model_token_usage[model] += tokens
    limit = MODEL_TOKEN_LIMITS.get(model, 1_000_000)
    print(f"[TOKENS] {model}: +{tokens:,} -> total {model_token_usage[model]:,}/{limit:,}")


def classify_task_with_meta_router(user_input):
    #Classify user input into appropriate model category
    user_lower = user_input.lower()

    if re.search(r"\d+\s*[\+\-\*/]\s*\d+", user_lower) or "solve" in user_lower or "equation" in user_lower:
        return "math"

    # Coding-related keywords
    if any(word in user_lower for word in [
        'code', 'program', 'function', 'debug', 'script', 'programming',
        'python', 'javascript', 'html', 'css', 'algorithm', 'bug', 'syntax'
    ]):
        return "coding"

    # Math-related keywords
    elif any(word in user_lower for word in [
        'math', 'calculate', 'equation', 'solve', 'formula', 'number',
        'addition', 'subtraction', 'multiplication', 'division', 'algebra'
    ]):
        return "math"

    # Reasoning-related keywords
    elif any(word in user_lower for word in [
        'analyze', 'explain', 'why', 'how', 'reason', 'logic', 'think',
        'understand', 'compare', 'evaluate', 'assess'
    ]):
        return "reasoning"

    # Logic-related keywords
    elif any(word in user_lower for word in [
        'if then', 'because', 'therefore', 'logic', 'premise', 'conclusion',
        'argument', 'proof', 'deduction'
    ]):
        return "logic"

    # Language-related keywords
    elif any(word in user_lower for word in [
        'translate', 'language', 'french', 'spanish', 'german', 'chinese',
        'japanese', 'korean', 'italian', 'portuguese', 'russian'
    ]):
        return "languages"

    # Default to chat for general conversation
    else:
        return "chat"


def choose_model(user_input, category=None):
    #Choose the best available model for the given input
    try:
        if not category:
            category = classify_task_with_meta_router(user_input)

        print(f"[ROUTER] Classified task as: {category}")

        model = get_model_for_category(category)

        # If no model available in primary category, try fallback categories
        if not model:
            fallback_categories = ["chat", "other", "meta-router"]
            for fallback in fallback_categories:
                if fallback != category:
                    print(f"[ROUTER] Trying fallback category: {fallback}")
                    model = get_model_for_category(fallback)
                    if model:
                        category = fallback
                        break

        if model:
            print(f"[ROUTER] Final selection: {model} for category: {category}")
            return model, category
        else:
            print("[ROUTER] No models available in any category")
            return None, None

    except Exception as e:
        print(f"[ROUTER ERROR] {e}")
        return None, None


def get_usage_stats():
    #Get current usage statistics for all models
    stats = {}
    for model, usage in model_token_usage.items():
        limit = MODEL_TOKEN_LIMITS.get(model, 1_000_000)
        percentage = (usage / limit) * 100 if limit > 0 else 0
        stats[model] = {
            'usage': usage,
            'limit': limit,
            'percentage': percentage
        }
    return stats


def reset_usage():
    #Reset all token usage counters (use with caution)
    global model_token_usage
    model_token_usage = defaultdict(int)
    print("[ROUTER] All usage counters reset")