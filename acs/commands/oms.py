"""
Add the
[OMS](https://blogs.technet.microsoft.com/momteam/2015/11/03/announcing-linux-docker-container-management-with-oms/)
monitoring solution to the cluster.

Visit http://mms.microsoft.com and sign up for a free OMS
account. Then click "Settings" and then "Connected Sources". You will
need to copy your Workspace ID and your Workspace Primary Key into
your config file. Finally, run the `install` command to install OMS on
each of your agents (please note that this command restarts the Docker
Engine and thus any containers on it will be stopped).

only supported for systemd Linux OS

Usage:
  oms <command> [help] [options]

Commands:
  install                Install the OMS monitoring agent on all ACS agents

Options:

Help:
  For help using the oms command please open an issue at 
  https://github.com/rgardler/acs-scripts

"""

from docopt import docopt
from inspect import getmembers, ismethod
from json import dumps

from .base import Base

class Oms(Base):

  def run(self):
      args = docopt(__doc__, argv=self.options)
      # print("Global args")
      # print(args)
      self.args = args

      command = self.args["<command>"]
      result = None
      methods = getmembers(self, predicate = ismethod)
      for name, method in methods:
          if name == command:
              result = method()
          if result is None:
            result = command + " returned no results"

      if result:
          print(result)
      else:
          print("Unknown command: '" + command + "'")
          self.help()

  def install(self):
      """Install the OMS agent on all ACS agents

      """

      
      ips = Base.getAgentIPs(self)
      for ip in ips:
        self.log.debug("Installing OMS on: " + ip)
        
        result = ""

        workspace_id = self.config.get('OMS', "workspace_id")
        workspace_key = self.config.get('OMS', "workspace_primary_key")
        cmd = "sudo docker run --privileged -d -v /var/run/docker.sock:/var/run/docker.sock -e WSID=" +workspace_id + " -e KEY=" + workspace_primary_key + " -h=`hostname` -p 127.0.0.1:25224:25224/udp -p 127.0.0.1:25225:25225 --name=\"omsagent\" --log-driver=none --restart=always microsoft/oms:Test"
	# FIXME: do some error checking
        result = self.executeOnAgent(cmd, ip)

	cmd ="sudo systemctl enable docker.service"
	cmd ="sudo cp -pr /etc/systemd/system/multi-user.target.wants/docker.service /etc/systemd/system"
	cmd ="sudo sed -i -e '5 i\Environment=\"DOCKER_OPTS=--log-driver=fluentd --log-opt fluentd-address=localhost:25225\"' /etc/systemd/system/docker.service.d/execstart.conf"
	cmd ="sudo sed -i -e '/^ExecStart/ s/$/ $DOCKER_OPTS/' /etc/systemd/system/docker.service.d/execstart.conf" 
	# FIXME: do some error checking
        result = self.executeOnAgent(cmd, ip)

        cmd = "sudo systemctl daemon-reload"
	cmd = "sudo systemctl restart docker.service"
        # FIXME: do some error checking
        result = self.executeOnAgent(cmd, ip)

        result = "OMS installed on all agents (though we don't actually do error checking on the install at this point, so be vigilant)"
        return result

  def help(self):
    print(__doc__)
