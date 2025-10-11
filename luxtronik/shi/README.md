# Smart-Home-Interface

## Common usage

Either use the top-level element Luxtronik or create your own instance of the smart-home-interface using

### Creation

```
from shi import create_modbus_tcp

shi = create_modbus_tcp('your.lux.ip.addr')
```

### Read

Read all available (Example with inputs, holdings work analog)
```
inputs = shi.read_inputs()
print(inputs)

inputs = shi.create_inputs()
shi.read_inputs(inputs)
print(inputs)

data = shi.read()
print(data.inputs)

data = shi.create_data()
shi.read(data)
print(data.inputs)

```

latest: possible to create data-vectors directly, but there may be not valid fields

```
inputs = Inputs()
shi.read_inputs(inputs)
print(inputs)

data = LuxtronikSmartHomeData()
shi.read(data)
print(data.inputs)
```




each block results in
```
>> ...
```


Read single (or a subset) (all versioned)
```
op_mode = shi.read_input('operation_mode')
print(op_mode)

op_mode = shi.read_input(2)
print(op_mode)

op_mode = shi.create_input('operation_mode')
shi.read_input(op_mode)
print(op_mode)

inputs = Inputs.empty()
op_mode = inputs.add('operation_mode')
// ... add other
shi.read_inputs(inputs)
print(op_mode)
print(inputs.get(2))
print(inputs['operation_mode'])
```

each block results in
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

### Use case: Trial-and-error mode

contains all available fields
read one-after-another so that read errors in one field do not affect another

```

```


```
from shi import create_modbus_tcp_versioned

shi = create_modbus_tcp_versioned('your.lux.ip.addr')
```

### Use case: Specific version

```
from shi import create_modbus_tcp_versioned

shi = create_modbus_tcp_versioned('your.lux.ip.addr')
```

## Implementation Details