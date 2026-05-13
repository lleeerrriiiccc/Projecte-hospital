#### ESTOS SCRIPTS NO FUNCIONAN SON SOLO PARA EL REPO LOS ARCHIVOS ORIGINALES ESTAN EN EL SERVIDOR ####

import utils
import os
import subprocess
import datetime
import drive_manager



def backup_db():
    try:
        utils.log_backup('full_backup.log', 'INFO', 'Starting database backup...')
        backup_path = '/bck/full/full_backup-{}.sql.gz'.format(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        dump_command = 'pg_dumpall -U postgres | gzip > {}'.format(backup_path)
        # Execute the dump command
        subprocess.run(dump_command, shell=True, check=True)
        if os.path.exists(backup_path):
            utils.log_backup('full_backup.log', 'INFO', 'Database backup completed successfully.')
            uploaded_file_id = drive_manager.upload_backup(backup_path, '1C6Aoh2nVZ3CPhUNCpSZxTk3z0IrHj4Q0')
            if uploaded_file_id:
                utils.log_backup('full_backup.log', 'INFO', f'Backup uploaded successfully. File ID: {uploaded_file_id}')
            else:
                utils.log_backup('full_backup.log', 'ERROR', 'Failed to upload backup to Google Drive.')
        else:
            utils.log_backup('full_backup.log', 'ERROR', 'Database backup failed: Backup file not found.')
    except Exception as e:
        utils.log_backup('full_backup.log', 'ERROR', f'Error during database backup: {str(e)}')

if __name__ == '__main__':
    backup_db()