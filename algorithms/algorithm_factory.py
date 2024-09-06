# algorithms/algorithm_factory.py
from .yolo import YOLOAlgorithm
from .on_duty import OnDutyAlgorithm

def algorithm_factory(algorithm, model):
    """
    Factory function to create an algorithm handler based on the algorithm string.
    
    Args:
        algorithm (str): The algorithm name corresponding to a handler.
        model: The loaded model instance.
        
    Returns:
        An instance of a handler that can process video frames with the given model.
    """
    algorithm_classes = {
        'yolo': YOLOAlgorithm,
        'on_duty': OnDutyAlgorithm,
        # Add more algorithm-to-handler mappings as needed
    }
    
    algorithm_class = algorithm_classes.get(algorithm.lower())
    
    if algorithm_class is None:
        raise ValueError(f"Algorithm {algorithm} is not defined.")
    
    return algorithm_class(model)

