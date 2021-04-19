# Enumerator

Simple expandable alternative to Python standard _enum_

Allows simple creation of single-tiered containers and multi-tiered JSON-like objects.

## Examples

```python
>> from enumerator import enum_factory, sequence_factory, enum_factory_currying, sequence_factory_currying
>> FOX = enum_factory('quick', 'brown', 'fox', action='jumps', times=8)
>> FOX.BROWN
'BROWN'

>> COUNT = sequence_factory('zero', 'one', 'two', 'three')
>> COUNT.ONE
1

>> SZ = sequence_factory_currying(value_converter=lambda v: 1024 ** v)\
                                 ('B', 'KB', 'MB', 'GB', 'TB')
>> SZ.MB
1048576

>> Q = enum_factory(**{'Are': {'you': 'sure'}})
>> Q.ARE.YOU
'sure'
```
