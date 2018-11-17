# Speed Skydiving data analysis and scoring


The setup includes a Jupyter Lab dockerized implementation with local data
storage and single user access credentials.  This is a zero-install setup as long as
Docker is already available in the target system.


### Requirements

**Audience:**  Developers who'll work on improving the SSScoring notebooks.

* Latest Docker for Linux, MacOS, or Windows
* Firefox, Chrome, Safari, or any modern browser
* Basic knowledge of [Jupyter Lab](https://jupyter-notebook.readthedocs.io/en/stable/index.html)
  or Jupyter Notebook


### Optional extras

* [FlySightViewer.app](http://www.flysight.ca/extras.htm) for viewing the
  FlySight CSV files
* Microsoft Excel to view the scoring tables
* [FlySafe](https://www.facebook.com/FlySafeApp/) for distance analysis


## Scoring Lab


### First time launch

Docker will pull the latest version of Jupyter Lab and run it.  This process may
take between 30 seconds and a few minutes, depending on the available Internet
bandwidth.

First time run generates a token to set the notebook password.  This password is
necessary to open the run-time environment because this notebook can run in a
server open to the whole Internet, if desired.  The password set up is a
one-time event.

To generate the first time password and start the Jupyter Lab, open a terminal
shell in the `SSScoring` directory, then execute:

```bash
docker-compose up --remove-orphans || docker-compose rm -f
```

This is a good time for the user to get some coffee ☕️ if they have a slow
Internet connection.

Jupyter Lab starts when the download is complete, and shows the legend:

```
notebook    |     Copy/paste this URL into your browser when you connect for the first time,
notebook    |     to login with a token:
notebook    |         http://b8b27455b503:8888/?token=6c7546c58eff46029e095ea0f8e95f5006fd66dfd9fa63d6&token=6c7546c58eff46029e095ea0f8e95f5006fd66dfd9fa63d6
```

Generate a new password and validate the first-time installation:

1. Log on to **http://localhost:8888/lab** on your web browser
1. Enter the token in the _Setup a Password_ section, and enter a password of
   choice.  The token, in our example, is the string of numbers and letters
   after `token=`, or `6c7546c58eff46029e095ea0f8e95f5006fd66dfd9fa63d6` in the
   example
1. Click on _Login and set new password_

![Password set up and token browser example](https://raw.githubusercontent.com/pr3d4t0r/basdtracks2018/master/images/token-password-setup.png) 

The web browser displays the Jupyter Lab main view and launcher:

![Jupyter Lab sample screen](https://raw.githubusercontent.com/pr3d4t0r/SSScoring/master/images/lab-first-run.png) 

End the Jupyter Lab container by exiting the Jupyter Lab and terminating the process:

1. Go to **http://localhost:8888/tree**
1. Click on the _Logout_ button at the top right corner
1. Go to the terminal and stop the Jupyter container by pressing Ctrl-C
1. Respond "y" to the _Going to remove notebook_ prompt

Done!  Validate that the first time run was successful by executing:

```bash
if [[ -e "scoring/_jupyter/jupyter_notebook_config.json" ]]; then echo 'Success!'; else echo "Failed - try again"; fi
```


### Working with data

The process is super simple now:

1. Start the Jupyter Lab container
1. Log on to Jupyter at `http://localhost:8888/lab`
1. Play with the data to your heart's content!

To start:

```bash
docker-compose up --remove-orphans ; docker-compose rm -f
```

When done, kill the process with Ctrl-C or turn off the computer.  That's it!


## FAQ

1. **I couldn't write the password file or create new notebooks - what's up?** -
   The notebook needs full file system admin permissions because the container
   and Jupyter run under two different privilege levels.  To solve, run this 
   command:

   ```
   chmod 777 ./scoring && \
   mkdir -p ./scoring/_jupyter && \
   chmod 777 -Rfv ./scoring/_jupyter
   ```

1. **Does SSScoring support Windows?** - Sort of.  All the tools used for analyzing the
   competition data are supposed to work under Windows, but the developers
   don't have Windows systems to test.  Fork the project or ask to join if you'd
   like to help!


# License and copyright

The code and sample data are released under the BSD 3-clause license.  All the
code is &copy; 2018 by GitHub users pr3d4t0r and project contributors.

