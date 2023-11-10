#import tensorflow as tf
import GAME_OBJ
import asyncio

"""
SCRIPT FOR AI

NN SHAPE
INPUTS (x11): 
Ray Distance x8
Reward_distance
player_angle
player_speed

OUTPUTS(x4):
FORWARD
RIGHT
LEFT
BACK
"""


async def main():

    await asyncio.gather(
        asyncio.to_thread(GAME_OBJ.main()),
        print_something()
    )


async def print_something():
    print("hi")

asyncio.run(main())
