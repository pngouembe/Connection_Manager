# Connection_Manager
## How to use
The usage is similar for the client and for the server side.


Make your own copy of the config files located in config folder.


Fill them with the appropriate information. 
Comments on the template files should help you fill the various fields 


Run the command you need from the src directory:

```bash
cd src
python3 Connection_manager_client.py --cfg_file <path to your config file>
```

Or

```bash
cd src
python3 Connection_manager_server.py --cfg_file <path to your config file> --rsrc_file <path to resource file>
```
