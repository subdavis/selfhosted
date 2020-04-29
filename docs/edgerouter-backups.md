# Backing up EdgeRouter X

On commit, save the router config to an external server

* scp will push the file to the remote over ssh.
* SSH keys don't work, so must use password.
* Create a user `edgerouter-backup` on the target host.
* [Only allow password login for a specific user](https://serverfault.com/questions/307407/ssh-allow-password-for-one-user-rest-only-allow-public-keys)
* [Set Up automatic backups](https://help.ui.com/hc/en-us/articles/204960084-EdgeMAX-Manage-the-configuration-file)

``` bash
configure
set system config-management commit-archive location "scp://edgerouter-backup:password@host.lan/path/to/parent"
commit ; save
```

Now you can back up the local files with duplicati.
