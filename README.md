# Modbus-Toolbox

Modbus-Toolbox is a Python package that contains modbus functions. 

## Installation and updating
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install Toolbox like below. 
Rerun this command to check for and install  updates .
```bash
pip install git+https://github.com/marcosdh1987/modbus_toolbox
```

## Usage
Features:
* functions.get_rtu_data  --> get data from the RTU device 

#### Demo of some of the features:
```python
import modbus_toolbox

ip_add = '192.168.0.10'
port_d = 502
data = toolbox.functions.get_rtu_data(ip=ip_add, port=port_d):
print(data)
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)