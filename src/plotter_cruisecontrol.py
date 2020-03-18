import os
import random
import pickle

import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-d", "--dir", dest="dirname",
                    help="model's directory")
parser.add_argument("--triplots", default=False, action="store_true" , help="Generate triplots")
parser.add_argument("--hist", default=False, action="store_true" , help="Generate histograms")
args = parser.parse_args()
    
with open(os.path.join(args.dirname, 'sims.pkl'), 'rb') as f:
    records = pickle.load(f)

def hist(up, down, filename):
    fig, ax = plt.subplots(1, 2, figsize=(8, 3), sharex=True)

    config = {
        'norm_hist': True,
        'bins': range(0, 100, 20),
        'color': 'b',
        'kde': False,
        'axlabel': '% of $v_c$ in limits',
    }
    sns.distplot(up, **config, ax=ax[0]).set_title('Hill')
    sns.distplot(down, **config, ax=ax[1]).set_title('Valley')

    fig.tight_layout()
    fig.savefig(os.path.join(args.dirname, filename), dpi=150)

def plot(space, sim_time, sim_agent_pos, sim_agent_vel, sim_agent_acc, filename):
    fig, ax = plt.subplots(1, 3, figsize=(12, 3))

    ax[0].scatter(sim_agent_pos[0], space['pos'][0], color='g', label='start')
    ax[0].scatter(sim_agent_pos[-1], space['pos'][-1], color='r', label='end')
    ax[0].plot(space['x'], space['y'], zorder=-1)
    ax[0].set(xlabel='space (m)', ylabel='elevation (m)')
    ax[0].axis('equal')
    ax[0].legend()

    ax[1].axhline(4.90, ls='--', color='r')
    ax[1].axhline(5.10, ls='--', color='r')
    ax[1].plot(sim_time, sim_agent_vel)
    ax[1].set(xlabel='time (s)', ylabel='velocity (m/s)')

    ax[2].plot(sim_time, np.clip(sim_agent_acc, -3, 3))
    ax[2].set(xlabel='time (s)', ylabel='acceleration ($m/s^2$)')

    fig.tight_layout()
    fig.savefig(os.path.join(args.dirname, filename), dpi=150)

if args.triplots:
    n = random.randrange(len(records))
    print('up:', records[n]['up']['init'])
    plot(records[n]['up']['space'], records[n]['up']['sim_t'], records[n]['up']['sim_ag_pos'], records[n]['up']['sim_ag_vel'], records[n]['up']['sim_ag_acc'], 'triplot_pulse.png')

    print('down:', records[n]['down']['init'])
    plot(records[n]['down']['space'], records[n]['down']['sim_t'], records[n]['down']['sim_ag_pos'], records[n]['down']['sim_ag_vel'], records[n]['down']['sim_ag_acc'], 'triplot_step_up.png')


if args.hist:
    size = len(records)
    up_pct = np.zeros_like(records[0]['up']['sim_ag_vel'])
    down_pct = np.zeros_like(records[0]['down']['sim_ag_vel'])

    for i in range(size):
        t = records[i]['up']['sim_ag_vel']
        up_pct = up_pct + np.logical_and(t > 4.9, t < 5.1)
        t = records[i]['down']['sim_ag_vel']
        down_pct = down_pct + np.logical_and(t > 4.9, t < 5.1)

    hist(up_pct, down_pct, 'pct_histogram.png')
