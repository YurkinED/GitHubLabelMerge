import json
import logging
import os
import glm
import csv
import argparse
import github

merged_dict = []
labels_def = []
def download_and_merge_labels():
    label_list = []
    for keys in repo_keys:
        hub = glm.GithubLabelMaker(keys[2], keys[0], keys[1])
        labels_def = hub.get_labels()
        if labels_def:
            logging.info("dumping labels to '{0}'".format(args.backup))
            label_list.append(json.dumps(labels_def, indent=2))
        else:
            logging.info("no labels found")

    for val in label_list:
        for k in json.loads(val):
            t = 0
            for i_md in merged_dict:
                if i_md['name'] == k['name']:
                    t = 1
            if t == 0:
                merged_dict.append(k)

def update_labels():
    for keys in repo_keys:
        hub = glm.GithubLabelMaker(keys[2], keys[0], keys[1])
        for label_def in labels_def:
            if label_def['description'] == None:
                label_def['description'] = ''
            hub.update_label(label_def)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description='Sync GitHub labelsbetween repos')
    p.add_argument('-b', '--backup', help='backup')
    p.add_argument('-r', '--restore', help='restore')
    p.add_argument('-s', '--sync', help='sync', action='store_true')
    p.add_argument('-f', '--force', help='force', action='store_true')
    p.add_argument('-re', '--repo', help='repo', required=True)
    args = p.parse_args()

    if (args.backup and args.restore) or (args.sync and args.restore) or (args.sync and args.backup):
        print("Param error. please use one of backup, restore, sync ")
        exit(0)

    if args.backup:
        print("Start backup in "+args.backup)

    if args.restore:
        print("Start restore from "+args.restore)

    if args.sync:
        print("Sync started")


    #Check opportunity to connect to repos
    repo_keys=[]
    with open(args.repo, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        for row in reader:
            try:
                hub = glm.GithubLabelMaker(row[2], row[0], row[1])
                print(str(row) + "Good connect")
                repo_keys.append(row)
            except github.GithubException:
                print(str(row) + "Error ")
                if not args.force:
                    print('Error with repo '+ row[1])
                    exit(0)

        if repo_keys == 0:
            print('No keys')
            exit(0)

    if args.backup:
        assert args.backup.endswith('json')
        download_and_merge_labels()
        #Merge array of JSON and save
        with open(args.backup, 'w', encoding='utf-8') as f:
            f.write(json.dumps(merged_dict, indent=2))

    #Restore labels to all repos
    if args.restore:
        logging.info("creating labels from '%s'", args.restore)
        assert os.path.isfile(args.restore)
        labels_def_files = [args.restore]
        for labels_file in labels_def_files:
            with open(labels_file, 'r') as f:
                labels_def = json.load(f)
                update_labels()


    # Restore labels to all repos
    if args.sync:
        download_and_merge_labels()
        labels_def = merged_dict
        update_labels()



print("Finish file")