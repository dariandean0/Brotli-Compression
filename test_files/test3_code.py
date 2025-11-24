#!/usr/bin/env python3
"""
Sample Python code for compression testing
Contains typical programming patterns with repetitive structures
"""

class DataProcessor:
    def __init__(self, name, config):
        self.name = name
        self.config = config
        self.data = []
        self.results = []
        
    def process(self, input_data):
        """Process input data and return results"""
        for item in input_data:
            if self.validate(item):
                processed = self.transform(item)
                self.data.append(processed)
                self.results.append(processed)
        return self.results
    
    def validate(self, item):
        """Validate item before processing"""
        if item is None:
            return False
        if not isinstance(item, (int, float, str)):
            return False
        return True
    
    def transform(self, item):
        """Transform item according to config"""
        if isinstance(item, str):
            return item.upper()
        elif isinstance(item, (int, float)):
            return item * 2
        return item

def main():
    processor = DataProcessor("test", {"mode": "default"})
    data = [1, 2, 3, "hello", "world", 4.5, 6.7]
    results = processor.process(data)
    print(f"Results: {results}")
    
if __name__ == "__main__":
    main()
