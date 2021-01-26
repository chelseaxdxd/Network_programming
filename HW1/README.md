# Bulletin Board System HW1

## Getting Started
First run ```./server <address>```
<br> then run ```chmod u+x npdemo.sh```
* Python3: ```./npdemo.sh “python3 client.py” <address> <port>```
* C: ```gcc -o client client.c``` then ```./npdemo.sh ./client <address> <port>```

ex.```./npdemo.sh “python3 client.py” 127.0.0.1 7890```

## Funtions
* **TCP: login / logout / list-user / exit**
* **UDP: register/whoami**

| Command format | Result     | Show messages|
|:-------------:|:-------------:|:-------------:|
| register \<username> \<email> \<password>   | Success |Register successfully.
||Fail| Username is already used. |
|login \<username> \<password>|Success |Welcome, \<username>.
||Fail (1)|Please logout first.|
||Fail (2)|Login failed.|
|logout|Success|Bye, \<username>.|
||Fail|Please login first.|
|whoami|Success|\<username>|
||Fail|Please login first.|
|list-user||Name Email<br> \<Name1> \<Email1> <br> \<Name2> \<Email2> <br>.........................
|exit||


 

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install foobar
```

## Usage

```python
import foobar

foobar.pluralize('word') # returns 'words'
foobar.pluralize('goose') # returns 'geese'
foobar.singularize('phenomena') # returns 'phenomenon'
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
