#!/bin/sh
# Runs only inside Debian Installer with its fixed /target and readonly /cdrom.
set -eu
printf "%s\n" BP22-LATE-BEGIN >/dev/hvc0
test -b /dev/vda
test -d /target/etc
test -d /cdrom/bp22
mkdir -p /target/var/tmp/bp22-packages /target/opt/desktop
cp /cdrom/bp22/extra/*.deb /target/var/tmp/bp22-packages/
printf "%s\n" BP22-LATE-PACKAGES >/dev/hvc0
in-target /bin/sh -c 'exec apt-get -y --no-install-recommends install /var/tmp/bp22-packages/*.deb'
in-target apt-get check
printf "%s\n" BP22-LATE-ACCOUNTS >/dev/hvc0
in-target groupadd --gid 10000 desktop
in-target useradd --uid 10000 --gid 10000 --home-dir /home/desktop --no-create-home --shell /usr/sbin/nologin desktop
in-target passwd --lock root
# Fail before marking the build complete if any unintended human login exists.
awk -F: '$1 == "root" { found=1; if ($2 !~ /^[!*]/) exit 1 } END { if (!found) exit 1 }' /target/etc/shadow
awk -F: '$3 >= 1000 && $3 < 65534 { if ($1 != "desktop" || $3 != 10000 || $7 != "/usr/sbin/nologin") exit 1; found++ } END { if (found != 1) exit 1 }' /target/etc/passwd
printf "%s\n" BP22-LATE-ACCOUNT-CHECKS-PASSED >/dev/hvc0
cp /cdrom/bp22/fixed/action.py /cdrom/bp22/fixed/start.py /cdrom/bp22/fixed/fixture.html /target/opt/desktop/
chmod 0755 /target/opt/desktop
chmod 0644 /target/opt/desktop/*
cp /cdrom/bp22/desktop.service /cdrom/bp22/desktop-action.socket /cdrom/bp22/desktop-action@.service /target/etc/systemd/system/
printf "%s\n" BP22-LATE-SERVICES >/dev/hvc0
in-target systemctl enable desktop.service desktop-action.socket
# Do not install host credentials, shell servers, extra disks or networking.
# Change only the installed root and EFI mounts to read-only; keep their UUIDs.
printf "%s\n" BP22-LATE-READONLY-MOUNTS >/dev/hvc0
sed -i -e '\|[[:space:]]/[[:space:]]|s/[[:space:]]errors=remount-ro[[:space:]]/ ro,noatime /' \
       -e '\|[[:space:]]/boot/efi[[:space:]]|s/umask=0077/ro,umask=0077/' /target/etc/fstab
mkdir -p /target/home/desktop
cat >>/target/etc/fstab <<'EOF'
tmpfs /home/desktop tmpfs rw,nosuid,nodev,mode=0700,uid=10000,gid=10000,size=768M 0 0
tmpfs /tmp tmpfs rw,nosuid,nodev,mode=1777,size=256M 0 0
tmpfs /var/tmp tmpfs rw,nosuid,nodev,mode=1777,size=128M 0 0
tmpfs /var/log tmpfs rw,nosuid,nodev,mode=0755,size=64M 0 0
tmpfs /var/cache tmpfs rw,nosuid,nodev,mode=0755,size=128M 0 0
EOF
# The runtime uses the same virtio disk, made read-only after installation.
# These modules must be loaded before initramfs discovers the root device.
printf '%s\n' virtio_pci virtio_blk >>/target/etc/initramfs-tools/modules
in-target update-initramfs -u
printf "%s\n" BP22-LATE-BLOCK-DRIVER >/dev/hvc0
# EFI remains bootable from a fresh variable store.
printf "%s\n" BP22-LATE-EFI-BOOT >/dev/hvc0
in-target grub-install --target=arm64-efi --efi-directory=/boot/efi --removable --no-nvram
in-target update-grub
printf "%s\n" BP22-LATE-EFI-PASSED >/dev/hvc0
rm -r /target/var/tmp/bp22-packages
sync
printf "%s\n" BP22-LATE-COMPLETE >/dev/hvc0
