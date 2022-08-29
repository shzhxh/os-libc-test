import pkgutil

from postwork import postwork
from prework import prework
from run import run
from utils import Env, loge
from pygrading import Job
import os


if __name__ == '__main__':
    env = Env()
    env.load_config()
    loge("Docker, enter main\n\n")
    try:
        job = Job(prework=prework, run=run, postwork=postwork, config=env.config)
        job.start()
        job.print()
    except Exception as e:
        print(env.config)
        raise e

