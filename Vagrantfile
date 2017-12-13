# -*- mode: ruby -*-
# vi: set ft=ruby :


unless Vagrant.has_plugin?("vagrant-docker-compose")
  system("vagrant plugin install vagrant-docker-compose")
  puts "Dependencies installed, please try the command again."
  exit
end

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|
  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://vagrantcloud.com/search.
  config.vm.define "payments" do |payments|
      payments.vm.box = "ubuntu/xenial64"
      # set up network ip and port forwarding
      payments.vm.network "forwarded_port", guest: 5000, host: 5000, host_ip: "127.0.0.1"
      payments.vm.network "private_network", ip: "192.168.33.10"

      # Windows users need to change the permissions explicitly so that Windows doesn't
      # set the execute bit on all of your files which messes with GitHub users on Mac and Linux
      payments.vm.synced_folder "./", "/vagrant", owner: "ubuntu", mount_options: ["dmode=755,fmode=644"]

      payments.vm.provider "virtualbox" do |vb|
        # Customize the amount of memory on the VM:
        vb.memory = "512"
        vb.cpus = 1
      end
  end



  # Copy your .gitconfig file so that your git credentials are correct
  if File.exists?(File.expand_path("~/.gitconfig"))
    config.vm.provision "file", source: "~/.gitconfig", destination: "~/.gitconfig"
  end

  # Copy your ssh keys file so that your git credentials are correct
  if File.exists?(File.expand_path("~/.ssh/id_rsa"))
    config.vm.provision "file", source: "~/.ssh/id_rsa", destination: "~/.ssh/id_rsa"
  end

  # Enable provisioning with a shell script. Additional provisioners such as
  # Puppet, Chef, Ansible, Salt, and Docker are also available. Please see the
  # documentation for more information about their specific syntax and use.

  ######################################################################
  # Add Python Flask environment
  ######################################################################
  # Setup a Python development environment
  config.vm.provision "shell", inline: <<-SHELL
    wget -q -O - https://packages.cloudfoundry.org/debian/cli.cloudfoundry.org.key | sudo apt-key add -
    echo "deb http://packages.cloudfoundry.org/debian stable main" | sudo tee /etc/apt/sources.list.d/cloudfoundry-cli.list
    apt-get update
    apt-get install phantomjs
    apt-get install -y git python-pip python-dev build-essential cf-cli libmysqlclient-dev
    pip install --upgrade pip
    apt-get -y autoremove

    # Make vi look nice ;-)
    sudo -H -u ubuntu echo "colorscheme desert" > ~/.vimrc
    # Install app dependencies
    cd /vagrant
    sudo pip install -r requirements.txt
    
    # Install PhantomJS for Selenium browser support
    echo "\n***********************************"
    echo " Installing PhantomJS for Selenium"
    echo "***********************************\n"
    sudo apt-get install -y chrpath libssl-dev libxft-dev
    
    # PhantomJS https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2
    cd ~
    export PHANTOM_JS="phantomjs-2.1.1-linux-x86_64"
    wget https://bitbucket.org/ariya/phantomjs/downloads/$PHANTOM_JS.tar.bz2
    sudo tar xvjf $PHANTOM_JS.tar.bz2
    sudo mv $PHANTOM_JS /usr/local/share
    sudo ln -sf /usr/local/share/$PHANTOM_JS/bin/phantomjs /usr/local/bin
    rm -f $PHANTOM_JS.tar.bz2
  SHELL

  ######################################################################
  # Add MySQL docker container
  ######################################################################
  config.vm.provision "shell", inline: <<-SHELL
    # Prepare MySQL data share
    sudo mkdir -p /var/lib/mysql
    sudo chown ubuntu:ubuntu /var/lib/mysql
  SHELL
  # Add MySQL docker container
  config.vm.provision "docker" do |d|
    d.pull_images "mariadb"
    d.run "mariadb",
      args: "-p 3306:3306 --restart=always -d --name mariadb -v /var/lib/mysql:/var/lib/mysql -e MYSQL_ROOT_PASSWORD=passw0rd -e MYSQL_DATABASE=payments"
  end

  # # Add Docker compose
  # # Note: you need to install the vagrant-docker-compose or this will fail!
  # # vagrant plugin install vagrant-docker-compose
  # # config.vm.provision :docker_compose, yml: "/vagrant/docker-compose.yml", run: "always"
  # # config.vm.provision :docker_compose, yml: "/vagrant/docker-compose.yml", rebuild: true, run: "always"
  # config.vm.provision :docker_compose

  # # Install Docker Compose after Docker Engine
  # config.vm.provision "shell", privileged: false, inline: <<-SHELL
  #   sudo pip install docker-compose
  #   # Install the IBM Container plugin as vagrant
  #   sudo -H -u vagrant bash -c "echo Y | cf install-plugin https://static-ice.ng.bluemix.net/ibm-containers-linux_x64"
  # SHELL

end
