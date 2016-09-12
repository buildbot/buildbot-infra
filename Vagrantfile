# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile made from
# https://github.com/brd/packer-freebsd
# https://github.com/wunki/vagrant-freebsd

require 'yaml'

Vagrant.configure("2") do |config|
  if Vagrant.has_plugin?("vagrant-proxyconf")
      if ENV.has_key?('http_proxy')
          config.proxy.http     = ENV['http_proxy']
      end
      if ENV.has_key?('https_proxy')
          config.proxy.https    = ENV['https_proxy']
      end
      if ENV.has_key?('no_proxy')
          config.proxy.no_proxy = ENV['no_proxy']
      end
  end
  config.vm.guest = :freebsd
  config.vm.box = 'freebsd/FreeBSD-10.3-STABLE'
  config.ssh.shell = "sh"
  config.vm.synced_folder ".", "/vagrant", disabled: true
  config.vm.base_mac = "080027D14C66"

  config.vm.define "service1" do |service1|
      service1.vm.network "private_network", ip: "192.168.80.230"
  end
  config.vm.define "service2" do |service2|
      service2.vm.network "private_network", ip: "192.168.80.231"
  end
  config.vm.define "service3" do |service3|
      service3.vm.network "private_network", ip: "192.168.80.232"
  end

  config.vm.provider :virtualbox do |vb, override|
    vb.customize ["modifyvm", :id, "--memory", "1024"]
    vb.customize ["modifyvm", :id, "--cpus", "4"]
    vb.customize ["modifyvm", :id, "--hwvirtex", "on"]
    vb.customize ["modifyvm", :id, "--audio", "none"]
    vb.customize ["modifyvm", :id, "--nictype1", "virtio"]
    vb.customize ["modifyvm", :id, "--nictype2", "virtio"]
  end

  #
  # Run Ansible from the Vagrant Host
  #
  config.vm.provision "ansible" do |ansible|
      ansible.playbook = "vagrant.yml"
      ansible.vault_password_file = "~/.vault-password"
    end
end
