import os
import tarfile
import datetime
import shutil
import utils
import drive_manager


ARCHIVE_DIR = '/share/archive'
DEST_DIR = '/bck/archive'


def gather_todays_files(src_dir):
    today = datetime.date.today()
    files = []
    if not os.path.isdir(src_dir):
        return files

    for fname in os.listdir(src_dir):
        path = os.path.join(src_dir, fname)
        if not os.path.isfile(path):
            continue
        mtime = datetime.date.fromtimestamp(os.path.getmtime(path))
        if mtime == today:
            files.append(path)
    return files


def make_archive(file_paths, dest_dir):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)

    date_str = datetime.date.today().isoformat()
    archive_name = f'wal-{date_str}.tar.gz'
    archive_path = os.path.join(dest_dir, archive_name)

    with tarfile.open(archive_path, 'w:gz') as tar:
        for p in file_paths:
            tar.add(p, arcname=os.path.basename(p))

    return archive_path


def backup_wal():
    utils.log_backup('wal_backup.log', 'INFO', 'Starting WAL backup...')
    files = gather_todays_files(ARCHIVE_DIR)
    if not files:
        utils.log_backup('wal_backup.log', 'INFO', 'No WAL files found for today; nothing to do.')
        return

    try:
        archive_path = make_archive(files, DEST_DIR)
        utils.log_backup('wal_backup.log', 'INFO', f'WAL archive created: {archive_path}')

        # Upload to Drive (use WAL_FOLDER_ID)
        uploaded_id = drive_manager.upload_to_folder(archive_path, '1dntDRPKchxaMr3ic5nUh2y_szF1UprCX')
        utils.log_backup('wal_backup.log', 'INFO', f'WAL archive uploaded. File ID: {uploaded_id}')
    except Exception as e:
        utils.log_backup('wal_backup.log', 'ERROR', f'Error during WAL backup: {e}')


if __name__ == '__main__':
    backup_wal()

