There are two ways to connect the host to the VM.

1. Open the VM directly in Virtual Machine Manager

This does not require SSH, an IP address, or port forwarding:

Open Virtual Machine Manager.
Double-click ubuntu25.04.
Click the Start ▶ button.
Click Show graphical console at the top-left.
Log in to Ubuntu in the VM window.

Virt-manager’s console displays the VM’s virtual screen directly.

2. Connect from the host terminal using SSH

Because you have:

libvirt 8.0.0

and:

<interface type="user">

the newer <backend type="passt"> method is unavailable. You can instead use QEMU’s older built-in hostfwd configuration.

The final result will be:

Host 127.0.0.1:7777 → VM port 4242

QEMU officially supports forwarding a host port such as 7777 to guest SSH port 4242.

Step 1: Shut down the VM

The VM must show:

Shutoff

Do not edit the network while the VM is running.

Step 2: Open the complete XML

In Virtual Machine Manager:

Open ubuntu25.04.
Click Show virtual hardware details.
Select Overview.
Open the XML tab.

You must edit the complete domain XML, not only the network-device XML.

Step 3: Change the first line

Change:

<domain type="kvm">

to:

<domain type="kvm"
        xmlns:qemu="http://libvirt.org/schemas/domain/qemu/1.0">

Libvirt uses this namespace to permit QEMU-specific command-line arguments.

Step 4: Remove the existing interface block

Delete this entire block:

<interface type="user">
  <mac address="52:54:00:b4:48:6f"/>
  <model type="virtio"/>
  <address type="pci"
           domain="0x0000"
           bus="0x01"
           slot="0x00"
           function="0x0"/>
</interface>

Do not keep it, because the replacement configuration will create the network interface itself.

Step 5: Add the forwarding configuration

Add this after </devices> and immediately before </domain>:

<qemu:commandline>
  <qemu:arg value="-netdev"/>
  <qemu:arg value="user,id=net0,hostfwd=tcp:127.0.0.1:7777-:4242"/>

  <qemu:arg value="-device"/>
  <qemu:arg value="virtio-net-pci,netdev=net0,mac=52:54:00:b4:48:6f"/>
</qemu:commandline>

The end of your XML should therefore look like:

    <rng model="virtio">
      <backend model="random">/dev/urandom</backend>
      <address type="pci"
               domain="0x0000"
               bus="0x06"
               slot="0x00"
               function="0x0"/>
    </rng>
  </devices>

  <qemu:commandline>
    <qemu:arg value="-netdev"/>
    <qemu:arg value="user,id=net0,hostfwd=tcp:127.0.0.1:7777-:4242"/>

    <qemu:arg value="-device"/>
    <qemu:arg value="virtio-net-pci,netdev=net0,mac=52:54:00:b4:48:6f"/>
  </qemu:commandline>
</domain>

Click Apply.

This QEMU argument means:

tcp:127.0.0.1:7777-:4242
    └──── host ────┘  └guest port
Step 6: Install SSH inside the VM

Start the VM through Virtual Machine Manager and open its graphical console.

Inside Ubuntu, run:

sudo apt update
sudo apt install openssh-server
sudo systemctl enable --now ssh

Check that SSH is listening:

sudo ss -lntp | grep ':4242'

You should see something similar to:

LISTEN 0 128 0.0.0.0:4242

Find your Ubuntu VM username:

whoami
Step 7: Connect from the host

On the host machine:

ssh -p 7777 VM_USERNAME@127.0.0.1

For example:

ssh -p 7777 thitran@127.0.0.1


I put my image of OverRide.iso in the home/thitran/sgoinfre/OverRide.iso, and I created the storage of home/thitran/sgoinfre/Overide.qcow2 of 5GB so now how I can install VM so that it recognized the image of OverRide.iso for the second time of runing the VM?

Your first run worked because the VM booted directly from:

/home/thitran/sgoinfre/OverRide.iso

On the second run, your CD-ROM was empty:

file   cdrom   sda   -

Therefore, SeaBIOS tried the empty Overide.qcow2 disk and reported “not a bootable disk.”

Fix it permanently
1. Stop the VM

Because it is currently stuck at the BIOS error screen:

virsh -c qemu:///session destroy ubuntu25.04
2. Insert the ISO persistently

Run:

virsh -c qemu:///session change-media \
  ubuntu25.04 \
  sda \
  /home/thitran/sgoinfre/OverRide.iso \
  --insert \
  --config

The important option is:

--config

It updates the persistent VM configuration, so the ISO remains attached after shutting down and starting the VM again. Libvirt documents that change-media --config changes the configuration used at the VM’s next startup.

Verify it:

virsh -c qemu:///session domblklist ubuntu25.04 --details

It should now show:

Type   Device   Target   Source
---------------------------------------------------------------
file   disk     vda      /home/thitran/sgoinfre/Overide.qcow2
file   cdrom    sda      /home/thitran/sgoinfre/OverRide.iso

Linux filenames are case-sensitive, so keep the exact spelling:

OverRide.iso
3. Put the CD-ROM first in the boot order

In Virtual Machine Manager:

Open ubuntu25.04.
Click Show virtual hardware details.
Open Boot Options.
Enable both:
CD-ROM
Hard Disk
Move CD-ROM above Hard Disk.
Click Apply.

Libvirt allows devices to be assigned a boot order, and Virt-Manager exposes this through its Boot Options screen.

Also select the CD-ROM device in the hardware list and confirm that its source is:

/home/thitran/sgoinfre/OverRide.iso
4. Start the VM
virsh -c qemu:///session start ubuntu25.04

Then open the console in Virt-Manager, or run:

virt-viewer -c qemu:///session ubuntu25.04

It should boot back to the OverRide login screen.

Important distinction: ISO versus QCOW2

Your files have different purposes:

File	Purpose
OverRide.iso	Bootable OverRide system
Overide.qcow2	Empty writable virtual hard disk
