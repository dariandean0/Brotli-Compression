# Context Modeling for Brotli Compression
# Simple first order context modeling for symbol prediction

from collections import defaultdict, Counter
from typing import Dict, Tuple

class ContextModel:
    # Initialize context model
    def __init__(self, order: int = 1):
        self.order = order
        self.contexts: Dict[Tuple, Counter] = defaultdict(Counter)
    
    # Train context model on data
    # Analyze the data to learn which symbols typically follow certain contexts.
    def train(self, data: bytes):
        # Need at least order+1 bytes to build contexts
        if len(data) <= self.order:
            return
        
        # Build context table
        for i in range(len(data) - self.order):
            # Extract context
            context = tuple(data[i:i + self.order])
            
            next_symbol = data[i + self.order]
            self.contexts[context][next_symbol] += 1
    
    # Get probability distribution for next symbol given context
    def predict_probabilities(self, context: Tuple[int, ...]) -> Dict[int, float]:
        if context not in self.contexts:
            return {i: 1.0 / 256 for i in range(256)}
        
        total = sum(self.contexts[context].values())
        return {symbol: count / total 
                for symbol, count in self.contexts[context].items()}
    
    # Get context aware frequencies for Huffman tree
    def get_adaptive_frequencies(self, data: bytes) -> Dict[int, int]:
        # Start with base frequency counts
        base_freq = Counter(data)
        
        # Adjust frequencies based on context predictability
        for i in range(self.order, len(data)):
            context = tuple(data[i - self.order:i])
            symbol = data[i]
            
            # Check if this symbol is predictable from its context
            if context in self.contexts and symbol in self.contexts[context]:
                # Calculate how predictable this symbol is
                context_prob = (self.contexts[context][symbol] / 
                              sum(self.contexts[context].values()))
                
                if context_prob > 0.7:
                    # Very predictable: significantly boost frequency
                    base_freq[symbol] = int(base_freq[symbol] * 1.5)
                elif context_prob > 0.5:
                    # Somewhat predictable: moderate boost
                    base_freq[symbol] = int(base_freq[symbol] * 1.2)
        
        return dict(base_freq)
    
    # Get statistics about learned contexts
    def get_context_statistics(self) -> Dict[str, any]:
        total_contexts = len(self.contexts)
        total_observations = sum(sum(counter.values()) 
                                for counter in self.contexts.values())
        
        # Find most predictable contexts
        most_predictable = []
        for context, counter in self.contexts.items():
            if sum(counter.values()) > 0:
                max_prob = max(counter.values()) / sum(counter.values())
                most_predictable.append((context, max_prob))
        
        most_predictable.sort(key=lambda x: x[1], reverse=True)
        
        return {
            'total_contexts': total_contexts,
            'total_observations': total_observations,
            'avg_observations_per_context': total_observations / total_contexts if total_contexts > 0 else 0,
            'top_5_predictable_contexts': most_predictable[:5]
        }
    
    def serialize(self) -> bytes:
        import pickle # using pickle for simplicity and time
        
        data = {
            'order': self.order,
            'contexts': dict(self.contexts)
        }
        return pickle.dumps(data)
    
    def deserialize(self, data: bytes):
        import pickle # using pickle for simplicity and time
        
        loaded = pickle.loads(data)
        self.order = loaded['order']
        self.contexts = defaultdict(Counter, loaded['contexts'])

# Utility function to analyze context modeling benefit
def analyze_context_benefit(data: bytes, order: int = 1) -> Dict[str, float]:
    if len(data) <= order:
        return {'entropy_reduction': 0.0, 'predictable_ratio': 0.0}
    
    model = ContextModel(order=order)
    model.train(data)
    
    # Calculate how many symbols are highly predictable
    predictable_count = 0
    total_count = 0
    
    for i in range(order, len(data)):
        context = tuple(data[i - order:i])
        symbol = data[i]
        total_count += 1
        
        probs = model.predict_probabilities(context)
        if symbol in probs and probs[symbol] > 0.5:
            predictable_count += 1
    
    predictable_ratio = predictable_count / total_count if total_count > 0 else 0.0
    
    # Estimate entropy reduction
    base_entropy = 8.0  # bits per byte for uniform distribution
    estimated_entropy = base_entropy * (1 - predictable_ratio * 0.3)
    entropy_reduction = (base_entropy - estimated_entropy) / base_entropy
    
    return {
        'entropy_reduction': entropy_reduction,
        'predictable_ratio': predictable_ratio,
        'contexts_learned': len(model.contexts),
        'recommendation': 'beneficial' if predictable_ratio > 0.3 else 'marginal'
    }
