#!/bin/sh
# Installer only: use Debian cdrom-detect's existing mounted-media path.
export PATH=/bin:/sbin:/usr/bin:/usr/sbin
mount -t proc proc /proc || exec /init
mount -t sysfs sysfs /sys || exec /init
mount -t devtmpfs devtmpfs /dev || exec /init
modprobe virtio_pci
modprobe virtio_blk
modprobe virtio_console
steps=0
while [ ! -c /dev/hvc0 ] && [ "$steps" -lt 15 ]; do
    sleep 1
    steps=$((steps + 1))
done
(
printf '%s\n' BP22-MEDIA-INIT
for module in xhci_hcd xhci_pci usb_storage sd_mod isofs; do
    modprobe "$module"
    printf 'BP22-MODULE %s %s\n' "$module" "$?"
done
steps=0
while [ ! -b /dev/sda ] && [ "$steps" -lt 15 ]; do
    sleep 1
    steps=$((steps + 1))
done
printf '%s\n' BP22-GUEST-PARTITIONS
cat /proc/partitions
mkdir -p /cdrom
if [ -b /dev/sda ] && [ "$(cat /sys/class/block/sda/ro)" = 1 ]; then
    if mount -t iso9660 -o ro /dev/sda /cdrom &&
        [ -f /cdrom/.disk/id/367c3d0c-fa76-4fb5-8c1f-210f504532ba ] &&
        [ "$(sha256sum /cdrom/bp22/preseed.cfg)" = "4da7885186bb7256c42774f592d67a3de6b2eccce3ae31c517c1bb3c4889d2dc  /cdrom/bp22/preseed.cfg" ] &&
        [ "$(sha256sum /preseed.cfg)" = "4da7885186bb7256c42774f592d67a3de6b2eccce3ae31c517c1bb3c4889d2dc  /preseed.cfg" ]; then
        printf '%s\n' BP22-VERIFIED-DERIVED-MEDIA
    else
        printf '%s\n' BP22-MEDIA-MOUNT-OR-IDENTITY-FAILED
        umount /cdrom 2>/dev/null || true
    fi
else
    printf '%s\n' BP22-EXPECTED-READONLY-MEDIA-ABSENT
fi
) >/dev/hvc0 2>&1
umount /dev
umount /sys
umount /proc
exec /init
