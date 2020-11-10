# reverse_shell_2.0
**This repository is meant for educational purposes.
Any illegal use is strictly forbidden and the writer shall not be held accountable to any persons stupid decisions.**

reverse_shell_2.0 is program where the server sends commands to the client and the client dutifully executes the commands, returning the results to the server.

reverse_shell_2.0 contains 2 main folders/directories and those are server and client folders. 
File server/server.py (as the name suggests) creates a running instance of a server on your machine
while file client/client.py creates a client instance that connects to an already running server.
**Note that the server should always be run first otherwise the client will have no endpoint to connect to and will exit 'gracefully' with a bunch load of ERRORS!**

The server is responsible for accepting incoming connections from clients and sending commands to be executed on the clients side.
The client waits for incomming messages/commands, executes them on the machine (whatever the command is) and returns a result to the server.Result can either be of type succes or fail.
If the client receives an 'exit' command from the server, then the program exits. It exists on both sides; the server and client side. Dont want to keep open connections pending do we?
 
### Program dependencies
This program requires that you have python and other dependencies installed. By other dependencies i mean;
1. socket
2. sys
3. subprocess
4. pickle 
5. logging
6. time

Note: Most of these modules are already built-in modules so you should have a breeze running the program.

### How to run program
1. Open your command prompt.
2. Navigate to directory server/ and type 'python server.py'
3. Open another instance of a command prompt
4. Navigate to directory client/ and type 'python client.py'
5. Type the commands you want executed on the server shell and watch them get run on the client.

> Today we do the difficult. Tomorrow we do the impossible. ~Caleb Mwasikira

Happy hacking!
