"""
Property tree utilities for building and manipulating vDC property structures
"""

from typing import Any, Dict, List, Union
from .genericVDC_pb2 import PropertyElement as PBPropertyElement, PropertyValue as PBPropertyValue


class PropertyValue:
    """Helper class for creating PropertyValue objects with type safety"""
    
    @staticmethod
    def from_python(value: Any) -> PBPropertyValue:
        """
        Convert a Python value to a PropertyValue protobuf object.
        
        Args:
            value: Python value (bool, int, float, str, bytes)
            
        Returns:
            PropertyValue protobuf object with appropriate field set
        """
        pv = PBPropertyValue()
        
        if isinstance(value, bool):
            pv.v_bool = value
        elif isinstance(value, int):
            # Use signed or unsigned based on value
            if value < 0:
                pv.v_int64 = value
            else:
                pv.v_uint64 = value
        elif isinstance(value, float):
            pv.v_double = value
        elif isinstance(value, str):
            pv.v_string = value
        elif isinstance(value, bytes):
            pv.v_bytes = value
        else:
            raise TypeError(f"Unsupported property value type: {type(value)}")
        
        return pv
    
    @staticmethod
    def to_python(pv: PBPropertyValue) -> Any:
        """
        Convert a PropertyValue protobuf object to a Python value.
        
        Args:
            pv: PropertyValue protobuf object
            
        Returns:
            Python value (bool, int, float, str, or bytes)
        """
        if pv.HasField('v_bool'):
            return pv.v_bool
        elif pv.HasField('v_uint64'):
            return pv.v_uint64
        elif pv.HasField('v_int64'):
            return pv.v_int64
        elif pv.HasField('v_double'):
            return pv.v_double
        elif pv.HasField('v_string'):
            return pv.v_string
        elif pv.HasField('v_bytes'):
            return pv.v_bytes
        else:
            return None


class PropertyElement:
    """Helper class for building PropertyElement trees"""
    
    @staticmethod
    def create(name: str, value: Any = None, elements: List[PBPropertyElement] = None) -> PBPropertyElement:
        """
        Create a PropertyElement with the given name, value, and/or child elements.
        
        Args:
            name: Property name
            value: Optional value (converted to PropertyValue)
            elements: Optional list of child PropertyElement objects
            
        Returns:
            PropertyElement protobuf object
        """
        pe = PBPropertyElement()
        pe.name = name
        
        if value is not None:
            pe.value.CopyFrom(PropertyValue.from_python(value))
        
        if elements:
            pe.elements.extend(elements)
        
        return pe


def build_property_tree(data: Dict[str, Any]) -> List[PBPropertyElement]:
    """
    Build a property tree from a nested dictionary structure.
    
    Args:
        data: Dictionary representing the property tree
              Keys are property names
              Values can be primitives (bool, int, float, str, bytes) or nested dicts
              
    Returns:
        List of PropertyElement objects
        
    Example:
        >>> tree = build_property_tree({
        ...     "dSUID": "123456789...",
        ...     "name": "My Device",
        ...     "output": {
        ...         "value": 75.0,
        ...         "mode": 1
        ...     }
        ... })
    """
    elements = []
    
    for name, value in data.items():
        if isinstance(value, dict):
            # Nested structure - recurse
            child_elements = build_property_tree(value)
            elements.append(PropertyElement.create(name, elements=child_elements))
        else:
            # Leaf value
            elements.append(PropertyElement.create(name, value=value))
    
    return elements


def property_tree_to_dict(elements: List[PBPropertyElement]) -> Dict[str, Any]:
    """
    Convert a property tree to a nested dictionary.
    
    Args:
        elements: List of PropertyElement objects
        
    Returns:
        Dictionary representation of the property tree
    """
    result = {}
    
    for elem in elements:
        if elem.elements:
            # Has children - recurse
            result[elem.name] = property_tree_to_dict(elem.elements)
        elif elem.HasField('value'):
            # Has value - convert to Python
            result[elem.name] = PropertyValue.to_python(elem.value)
        else:
            # Empty node
            result[elem.name] = None
    
    return result
