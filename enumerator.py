import collections
import re
from operator import itemgetter

def enum_factory_currying(value_converter=None, 
                          field_converter=str.upper, 
                          ordered=False):
    """
    Wraps creation of enum-like constants container - with conversion function(s)
    
    :param value_converter: function to convert values - no conversion on default
    :param field_converter: function to convert field names - uppercase on default
    :param ordered: on True, order fields by values
    :return: function that builds container
    """
    def _tokenizer(word):
        """
        "Tokenize" string - convert to valid Python name
        
        :param word: word to tokenize
        :return: tokenised string value
        """
        return field_converter(re.sub('\W+', '_', word))

    def field_by_value(self, value):
        """
        Get mapper's symbolic name from value
        
        :param value: value to locate
        :return: values symbolic name
        :raises: ValueError, if value does not belong to enum
        """
        field = next((k for k, v in self._asdict().items() if v == value), None)
        if field is not None:
            return field
        raise ValueError(f'Undefined value "{value}" in enumeration')
    
    def value_processor(value):
        """
        Processes enumerated value according to its type and value_converter
        Allows recursive creation of JSON objects
        
        :param value: value to add to enum
        :return: processed value
        """
        if isinstance(value, dict):
            if value_converter is not None:
                return value_converter(**value)
            return enum_factory(**value)
        return value_converter(value) if value_converter is not None else value
   
    def enum_namer(l_):
        """
        Generates unique name for enum object
        
        :param l_: list of field names
        :return: name
        """
        return '_ENUM{:x}'.format(abs(hash(tuple(l_))))
    
    def _enum_builder(*fields, **kw_consts):
        """
        Wraps Enum creation constants, use-cases below may be mixed
         - For list of strings - tokenized string -> string
         - For keyword pairs - tokenized field name -> value

         IMPORTANT! each string used as a field name must be tokenizable,
                    i.e. used as source for valid Python ID,
                    spaces and alphanumeric literals, 
                    first character - alpha or underscore

        :param fields: constant strings to be wrapped
        :param kw_consts: identifier-values pairs to be wrapped
        :return: Enum object
        """
        if kw_consts:
            kw_pairs = sorted(kw_consts.items(), key=itemgetter(1)) if ordered \
                        else kw_consts.items()
            kw_keys, kw_values = [list(s) for s in zip(*kw_pairs)]
        else:
            kw_keys = []
            kw_values = []

        fields = list(fields)
        field_names = [_tokenizer(f) for f in fields + kw_keys]
        enum_values = [value_processor(v) for v in fields + kw_values]
        enum_factory = collections.namedtuple(enum_namer(field_names), field_names)
        enum_factory.__call__ = field_by_value  # Reverse values by calling object

        return enum_factory(*enum_values)

    return _enum_builder


# Non-currying mapper - for convenience
enum_factory = enum_factory_currying()

# Incremental integer mapper - for numeric sequence creation
def sequence_factory_currying(value_converter=lambda x: x, field_converter=str.upper):
    """
    Wraps convenient creation of integer enum-like sequence container
    
    :param value_converter: function to convert values
    :return: function that builds container
    """
    def _sequence_builder(*symbolic_names, start_value=0, step=1):
        """
        Maps symbolic names to sequence of integers
        
        :param symbolic_names: names for mapping
        :param start_value: initial value of sequence
        :param step: sequence step
        :return: enum-like symbol-2-integer mapper
        """
        sequence_kwargs = dict((name, value * step) 
                               for value, name in 
                               enumerate(symbolic_names, start_value))
        return enum_factory_currying(value_converter=value_converter, 
                                     field_converter=field_converter, 
                                     ordered=True)(**sequence_kwargs)
    return _sequence_builder


# Non-currying mapper - for convenience
sequence_factory = sequence_factory_currying()

import configparser
def load_ini(source):
    """
    Loads INI file as 2-tiered JSON object
    
    :param source: configurations (as a string)
    :return: config object
    """
    def convert_config_value(value):
        """
        Conver configuration value to an appropriate type
        
        :param value: value as received from configuration file
        :return: converted value
        """
        boolean_value = {'true': True, 'false': False}.get(value.lower())
        if boolean_value is not None:
            return boolean_value
        
        for numeric_type in (int, float):
            try:
                converted_value = numeric_type(value)
                return converted_value
            except ValueError:
                pass
        return value
    
    config_obj = configparser.ConfigParser()
    config_obj.read_string(source)
    ini_value_converter = enum_factory_currying(value_converter=convert_config_value,
                                                field_converter=str.lower)
    config_loader = enum_factory_currying(value_converter=ini_value_converter)

    return config_loader(**{name: dict(section) 
                            for name, section in config_obj.items()})

import json
def load_json(source, field_converter=str.upper):
    """
    Create immutable JSON object from source string
      
    :param source: serialized JSON
    :param field_converter: field names' converter
    :return: JSON object
    """
    config_object = json.loads(source)
    return enum_factory_currying(field_converter=field_converter)(**config_object)