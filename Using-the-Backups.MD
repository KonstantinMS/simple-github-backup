# Using the Backups

The backup script creates mirror clones (also called bare repositories) of your GitHub repositories. A mirror clone contains all branches, tags, and refs exactly as they exist on GitHub, but without a working directory (you don't see the actual files). This format is ideal for backups because it's a complete, compressible copy of the entire repository history.

Here’s how you can work with these backups:

## 1. Create a Working Clone from a Mirror
If you need to browse the code, edit files, or run the project, create a normal (non‑bare) clone from the mirror:
```bash
cd /path/to/backup/folder          # e.g., github_backup_2026-03-14
git clone repo-name.git repo-name-working
```
Now you have a standard Git repository in ```repo-name-working``` with all files checked out.

## 2. Update a Mirror Manually
Although the scheduler updates all mirrors automatically on each run, you can also update a mirror manually:
```bash
cd repo-name.git
git remote update
```
This fetches any new commits, branches, and tags from the remote (GitHub) into your mirror.

## 3. Update Your Working Clone from the Mirror
If you already have a working clone created from the mirror (as in step 1) and the mirror has been updated, simply pull changes into your working clone:
```bash
cd repo-name-working
git pull
```
Because the working clone’s ```origin``` points to the local mirror, ```git pull``` will retrieve the latest changes from that mirror.
## 4. Restore a Repository to GitHub (or Another Remote)
If the original GitHub repository is lost, you can recreate it from your backup. First, create a new empty repository on GitHub (or any Git host), then push the entire mirror to it:
```bash
cd repo-name.git
git push --mirror https://github.com/your-username/new-repo.git
```
The ```--mirror``` flag ensures that all branches, tags, and references are pushed exactly as they are in the backup.

## 5. Archive Backups for Long‑Term Storage
Mirror folders can be compressed to save space and preserve them for offsite storage:
```bash
tar -czf github_backup_2026-03-14.tar.gz github_backup_2026-03-14
```
## Important Notes
Mirror clones consume about the same disk space as the full repository history (the ```.git``` folder in a normal clone).

They are self‑contained and can be moved, copied, or archived without any additional Git configuration.

If you ever need to convert a mirror back to a normal repository (with a working tree), simply clone it as shown in step 1.

The backup script does **not** compress or encrypt backups – you may want to add that yourself for sensitive data.