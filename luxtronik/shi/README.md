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
 Note for "available fields" vs "version-dependent fields":
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


Do not read/write the same field-instance multiple times within one send-list,
because this would perform several operations on the same memory.
Example:
    Read, Write 10, Read
will result in
    Read=20, Write=20, Read=...
The last value assigned to the related field before send() will be written
The last read value will be stored within the field after send().


if you want to do something like this, then you have to create independent fields/vectors



## Using aliases

Instead of the predefined names, any (hashable) values can also be used.
However, these must be registered beforehand. This also makes it possible
to "overwrite" existing names or register indices.

There are two ways to register:

- **global**:
  The aliases are registered in the `LuxtronikDefinitionsList`.
  They are then available in every newly created data vector.

```
from luxtronik.shi import create_modbus_tcp
from luxtronik.shi.holdings import HOLDINGS_DEFINITIONS

HOLDINGS_DEFINITIONS.register_alias(holding_definition_to_alias, any_hashable_alias)

shi = create_modbus_tcp('your.lux.ip.addr')
shi.inputs.register_alias(input_definition_to_alias, any_hashable_alias)

data = shi.read()
print(data.holdings[any_hashable_alias].value)
print(data.inputs[any_hashable_alias].value)
```

- **local**:
  The aliases can also only be registered in a specific data vector.

```
from luxtronik.shi import create_modbus_tcp

shi = create_modbus_tcp('your.lux.ip.addr')

data = shi.read()
data.holdings.register_alias(holding_definition_to_alias, any_hashable_alias)
print(data.holdings[any_hashable_alias].value)
print(data.inputs[any_hashable_alias].value)    << throws a KeyError
```

## Alternative use cases

### Latest or specific version

It is possible to create the data vector/data object yourself,
but there is no guarantee that the fields they contains
will match the current firmware version of the controller.

Use a specific versions:
```
from luxtronik.shi import create_modbus_tcp
from luxtronik.shi.holdings import Holdings

shi = create_modbus_tcp('your.lux.ip.addr', version="3.92.0")
holdings = Holdings("3.92.0")
shi.read_holdings(holdings)

# inputs is created with version "3.92.0"
inputs = shi.read_inputs()
```

The special tag "latest" is used to generate the interface
using the latest supported version:
```
from shi import create_modbus_tcp

shi = create_modbus_tcp('your.lux.ip.addr', version="latest")
...
```

### Trial-and-error mode

If you pass `None’ as the version, you set the interface to trial-and-error mode.
This means that no attempt is made to bundle read or write accesses,
but that all available fields/definitions are read or written individually (possibly twice).
Errors will occur, but as many operations as possible will be attempted.

```
from luxtronik.shi import create_modbus_tcp
from luxtronik.shi.interface import LuxtronikSmartHomeData

shi = create_modbus_tcp('your.lux.ip.addr', version=None)

data = LuxtronikSmartHomeData(version=None)
shi.read(data)

holdings = shi.create_holdings()
holdings[1].value = 22.0
holdings[2].value =  5.0
shi.write_holdings(holdings)
```

## Customization

Add your own definitions

safe / none-safe


## Implementation Details

### Definition vs. field

- **Definition**:
  A definition describes a data field. This includes, among other things,
  the register index where to find the related raw data,
  the number of required registers, the usable names
  and meta-information about the appropriate controller version.

- **Field**:
  A field contains the data that has been read or is to be written
  and makes the raw data available in a user-friendly format.

### Register vs. fields vs. data-blocks

- **Register**:
  A single 16‑bit word addressable by an index.
  Registers are the atomic unit of transfer.

- **Field**:
  Logically related registers. A field can comprise
  one register or several consecutive registers.

- **Data Block**:
  A contiguous address range containing one or more fields.
  Data blocks are used to perform bulk read or write operations in a
  single sequential transfer to minimize communication overhead.

```
Index
      +------------+      +------------+      +------------+
0x00  | Register 0 |      | Field 0    |      | Data block |
      +------------+      +------------+      +            +
0x01  | Register 1 |      | Field 1    |      |            |
      +------------+      +            +      +            +
0x02  | Register 2 |      |            |      |            |
      +------------+      +------------+      +------------+
0x03  Register 3 do not exist

0x04  Register 4 do not exist
      +------------+      +------------+      +------------+
0x05  | Register 5 |      | Field 5    |      | Data block |
      +------------+      +            +      +            +
0x06  | Register 6 |      |            |      |            |
      +------------+      +------------+      +------------+
0x07  Register 7 do not exist

0x08  Register 8 do not exist
      +------------+      +------------+      +------------+
0x09  | Register 9 |      | Field 9    |      | Data block |
      +------------+      +------------+      +------------+
...
```

### Available definition vs. version-dependent definition

- **Available definitions**:
  All definitions contained in the `LuxtronikDefinitionsList` are designated
  with the term "available definitions". This includes all definitions ever used.

- **Version-dependent definitions**:
  The definitions themselves may contain version information specifying
  in which version the described field is included. This is used to
  determine a subset that matches a specific firmware version of the controller.
  Fields without version information are always included.
  Note: If the desired version is "None",
  all "available" are considered as "version-dependent".

```
Available:
- {index: 0, since: 1.0, until: 2.9}
- {index: 1, since: 2.2            }
- {index: 4,             until: 1.5}
- {index: 5, since: 2.4, until: 3.0}
- {index: 6, since: 1.3            }
- {index: 8,                       }
- {index: 9,             until: 2.0}

Version-dependent on v0.3:
- {index: 4,             until: 1.5}
- {index: 8,                       }
- {index: 9,             until: 2.0}

Version-dependent on v1.1:
- {index: 0, since: 1.0, until: 2.9}
- {index: 4,             until: 1.5}
- {index: 8,                       }
- {index: 9,             until: 2.0}

Version-dependent on v2.6:
- {index: 0, since: 1.0, until: 2.9}
- {index: 1, since: 2.2            }
- {index: 5, since: 2.4, until: 3.0}
- {index: 6, since: 1.3            }
- {index: 8,                       }

Version-dependent on v3.2:
- {index: 1, since: 2.2            }
- {index: 6, since: 1.3            }
- {index: 8,                       }

Version-dependent on None:
- {index: 0, since: 1.0, until: 2.9}
- {index: 1, since: 2.2            }
- {index: 4,             until: 1.5}
- {index: 5, since: 2.4, until: 3.0}
- {index: 6, since: 1.3            }
- {index: 8,                       }
- {index: 9,             until: 2.0}
```

### Data-blocks vs. telegrams

- **Data-blocks**:
  A data block bundles all fields that can be read or written together.
  However, when writing, only fields for which the user has set data are bundled.
  The resulting address space can be read with a single telegram,
  or the contiguous raw data can be written with a single telegram.

- **Telegrams**:
  A telegram defines a read or write operation to be performed.
  Several telegrams can be handled in one transmission.
