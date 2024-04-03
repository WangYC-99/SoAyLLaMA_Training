import os
import time
import shutil

def delete_folders_with_prefix(root_folder, prefix):
    for root, dirs, files in os.walk(root_folder, topdown=False):
        for dir_name in dirs:
            if dir_name.startswith(prefix):
                folder_path = os.path.join(root, dir_name)
                shutil.rmtree(folder_path)
                print(f"Deleted folder: {folder_path}")

if __name__ == '__main__':
    root_folder = "/workspace/mzy/home_mzy/parameters"
    prefix_to_delete = "global_step"

    for i in range(6000):  # run for 6000 times
        print(f'run {i + 1}')
        delete_folders_with_prefix(root_folder, prefix_to_delete)

        # time interval is 30 secs
        time.sleep(30)
