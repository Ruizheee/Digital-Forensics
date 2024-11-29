import tarfile
import subprocess
import os

class ContainerImager:
    def __init__(self):
        pass

    def size_checker(self, tar_path):

        buffer_mb = 100

        tar_size_in_bytes = os.path.getsize(tar_path)
        tar_size_in_mb = tar_size_in_bytes / (1024 * 1024)
        total_size_in_mb = tar_size_in_mb + buffer_mb

        return int(total_size_in_mb)

    def create_disk_image(self, tar_path, image_path, mount_dir="/mnt"):
        # Create a blank disk image
        print("Creating blank disk image...")

        size_mb = self.size_checker(tar_path)
        subprocess.run(["dd", "if=/dev/zero", f"of={image_path}", "bs=1M", f"count={size_mb}"], check=True)
        
        # Format the image with an ext4 filesystem
        print("Formatting the disk image with ext4 filesystem...")
        subprocess.run(["mkfs.ext4", image_path], check=True)
        
        # Mount the image
        print("Mounting the disk image...")
        os.makedirs(mount_dir, exist_ok=True)
        subprocess.run(["sudo", "mount", "-o", "loop", image_path, mount_dir], check=True)
        
        try:
            # Extract tar contents to the mounted image
            print("Extracting tar contents to disk image...")
            with tarfile.open(tar_path, "r") as tar:
                tar.extractall(path=mount_dir)
            print("Extraction complete.")
        
        finally:
            # Unmount the image
            print("Unmounting the disk image...")
            subprocess.run(["sudo", "umount", mount_dir], check=True)
            print("Disk image created successfully.")

'''
# Usage
tar_path = "output.tar"     # Path to the exported container tar file
image_path = "disk_image.img"  # Path to the resulting disk image
create_disk_image(tar_path, image_path)
'''
