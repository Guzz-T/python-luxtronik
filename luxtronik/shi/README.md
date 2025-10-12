# Smart-Home-Interface

## Common usage

Either use the top-level element Luxtronik or create your own instance of the smart-home-interface using

### Creation

The smart-home-interface source code is located inside a module named `shi`.
Currently the luxtronik controller only supports modbus-TCP as protocol.

```
from luxtronik.shi import create_modbus_tcp

shi = create_modbus_tcp('your.lux.ip.addr')
```

### Read

 (Example with inputs, holdings work analog)
 Note for "available fields" vs "valid fields":
  each controller version may support different / new fields
  ... (see trial-and-error-mode)

__Read all fields:__
```
# Recommended if only one data-vector is used:
# First create the data-vector that contains all valid fields
inputs = shi.create_inputs()
# ... and afterwards read the data into those fields
shi.read_inputs(inputs)
print(inputs)
```
```
# Recommended if all data-vectors are used:
# First create the data-object that contains all supported data-vectors
# which contains all valid fields
data = shi.create_data()
# ... and afterwards read the data into those fields
shi.read(data)
print(data.inputs)
```
```
# This creates a new data-vector on every read that contains all valid fields
inputs = shi.read_inputs()
print(inputs)
```
```
# This creates a new data-object on every read
# that contains all supported data-vectors which contains all valid fields
data = shi.read()
print(data.inputs)
```
each example results in
```
>> ...
```

__Read single field (or a subset):__
```
op_mode = shi.read_input('operation_mode')
print(op_mode)
```
```
op_mode = shi.read_input(2)
print(op_mode)

```
```
op_mode = shi.create_input('operation_mode')
shi.read_input(op_mode)
print(op_mode)

```

each example results in
```
>> ...
```


__Read a subset:__
```
inputs = shi.create_empty_inputs()
op_mode = inputs.add('operation_mode')
// ... add other
shi.read_inputs(inputs)
print(op_mode)
print(inputs.get(2))
print(inputs['operation_mode'])
```

each example results in
```
>> ...
```



## Using aliases

# global, all new created input-data-vector can use alias
INPUTS_DEFINITIONS.register_alias(...)

# local
input = shi.create_empty_inputs()
op_mode = input.add(name)
input.register_alias(op_mode, alias)
input.add(name, alias)





### Alternative use case: Trial-and-error mode

contains all available fields
read one-after-another so that read errors in one field do not affect another

```

```


```
from shi import create_modbus_tcp

shi = create_modbus_tcp('your.lux.ip.addr', version=None)
```


```
inputs = Inputs()
shi.read_inputs(inputs)
print(inputs)

data = LuxtronikSmartHomeData()
shi.read(data)
print(data.inputs)
```

### Alternative use case: Latest or specific version

latest: possible to create data-vectors directly, but there may be not valid fields

```
from shi import create_modbus_tcp

shi = create_modbus_tcp('your.lux.ip.addr', version="3.92.0")
```
```
from shi import create_modbus_tcp

shi = create_modbus_tcp('your.lux.ip.addr', version="latest")
```

## Implementation Details