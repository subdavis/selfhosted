# Expand LVM to fill disk on ubuntu

Occasionally I end up with an LVM that doesn't fill the physical disk. [This blog contains the solution](http://ryandoyle.net/posts/expanding-a-lvm-partition-to-fill-remaining-drive-space/)

In summary:

``` bash
df -h
sudo lvresize -l +100%FREE /dev/mapper/ubuntu--vg-ubuntu--lv
sudo resize2fs /dev/mapper/ubuntu--vg-ubuntu--lv
```
